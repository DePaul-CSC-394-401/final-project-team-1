from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Profile, Wallet
from django.contrib.auth import authenticate, login
from django.db import IntegrityError
from .models import Products, UserCart, saveProducts, UserReviews, Class
from .forms import ClassForm, ProductsForm
from django.db import models
from datetime import datetime
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import EmailUpdateForm  
from django.shortcuts import get_object_or_404
from django.shortcuts import render, get_object_or_404, redirect
from .forms import EditListingForm, Walletform, ReviewForm
from .forms import EmailUpdateForm, ProfileUpdateForm  # Add ProfileUpdateForm

from datetime import timedelta  # Add this at the top of the file

from datetime import timedelta

from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import BadHeaderError


# Index view
def index(request):
    return render(request, 'index.html')
    
# Listings view
def listings(request):
    query = request.GET.get('q')
    location = request.GET.get('location')
    price_sort = request.GET.get('price')
    date_sort = request.GET.get('date_listed')
    category = request.GET.get('category')
    class_swap = request.GET.get('class_swap')
    senior_firesale = request.GET.get('senior_firesale')

    # Only show products that are still available and not sold
    products = Products.objects.filter(
        (models.Q(available_until__isnull=True) | models.Q(available_until__gt=datetime.now())) & 
        models.Q(is_sold=False) &  # Filter out sold products
        models.Q(on_hold=False)    # Filter out products that are on hold
    )

    if query:
        products = products.filter(name__icontains=query)
    if location:
        products = products.filter(user__profile__campus=location)
    if price_sort == 'min':
        products = products.order_by('price')
    elif price_sort == 'max':
        products = products.order_by('-price')
    if date_sort == 'newest':
        products = products.order_by('-made_available')
    elif date_sort == 'oldest':
        products = products.order_by('made_available')
    if category:
        products = products.filter(category=category)
    
    if class_swap:
        user_profile = Profile.objects.get(user=request.user)
        user_classes = user_profile.classes.all()
        print(f"User classes: {user_classes}")  # Debug print
        if user_classes.exists():
            products = products.filter(associated_classes__in=user_classes).distinct()
            print(f"Filtered products: {products}")  # Debug print
        else:
            products = Products.objects.none()  # No products if user has no classes
    
    if senior_firesale:
        products = products.filter(is_senior_firesale=True)

    context = {'products': products}
    return render(request, 'explore.html', context)

def view_listing(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    return render(request, 'product_detail.html', {'product': product})



# Signup view
def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm-password']
        year = request.POST['year']
        campus = request.POST['campus']
        graduating = request.POST.get('graduating', False) == 'on'

        if password == confirm_password:
            try:
                user = User.objects.create_user(username=username, email=email, password=password)
                profile = Profile(user=user, year=year, campus=campus, graduating=graduating)
                profile.save()
                
                # Send Welcome Email
                subject = 'Welcome to DePaul Marketplace!'
                message = render_to_string('emails/welcome_email.html', {
                    'username': user.username,
                })
                try:
                    send_mail(
                        subject,
                        '',  # Plain text message (optional)
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        fail_silently=False,
                        html_message=message,  # HTML message content
                    )
                except BadHeaderError:
                    print("Invalid header found.")

                messages.success(request, 'Account created successfully! Please log in.')
                return redirect('userlogin')
            except IntegrityError:
                # Show the error message on the same signup page
                messages.error(request, "Username already exists. Please try a different username.")
                return render(request, 'signup.html')
        else:
            messages.error(request, "Passwords do not match.")
            return render(request, 'signup.html')
    return render(request, 'signup.html')

# Login view
def userlogin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('landing')
        else:
            messages.error(request, "Invalid login credentials.")
    return render(request, 'login.html')



def addProduct(request):
    form = ProductsForm()
    if request.method == 'POST':
        form = ProductsForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user
            
            # Check if the user is graduating
            user_profile = Profile.objects.get(user=request.user)
            if form.cleaned_data['is_senior_firesale'] and not user_profile.graduating:
                form.add_error('is_senior_firesale', 'Only graduating students can add products to the senior firesale.')
                messages.error(request, 'Only graduating students can add products to the senior firesale.')
            else:
                availability_duration = form.cleaned_data.get('availability_duration', None)
                if availability_duration:
                    product.available_until = datetime.now() + timedelta(hours=availability_duration)
                
                product.save()
                
                # Process associated classes
                class_names = form.cleaned_data['associated_classes']
                if class_names:
                    class_names_list = [name.strip() for name in class_names.split(',')]
                    for class_name in class_names_list:
                        class_obj, created = Class.objects.get_or_create(name=class_name)
                        product.associated_classes.add(class_obj)
                
                return redirect('/explore')
    
    context = {'ProductsForm': form}
    return render(request, 'add_listing.html', context)

def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Products, id=product_id)
        cart_items = UserCart.objects.filter(user=request.user, products=product)
        if not cart_items.exists():
            UserCart.objects.create(
                user=request.user,
                products=product,
            )
        return redirect('explore')
    return render(request, 'cart')

def view_cart(request):
    cart_list = UserCart.objects.filter(user=request.user)
    total = 0
    for item in cart_list:
        total += item.products.price
    context = {'cart_list': cart_list, 'total': total}
    return render(request, 'cart.html', context)

def payment(request):
    if request.method == 'POST':
        cart_items = UserCart.objects.filter(user=request.user)
        wallet = get_object_or_404(Wallet, user=request.user)
        total = sum(item.products.price for item in cart_items)

        if wallet.balance >= total:
            if cart_items.exists():
                wallet.balance -= total
                wallet.save()

                for item in cart_items:
                    product = item.products
                    mark_as_sold(product.id)

                    # Notify the seller
                    send_purchase_confirmation(
                        seller_email=product.user.email,
                        listing_title=product.name,
                        buyer_name=request.user.username
                    )

                    # Email content for buyer
                    buyer_subject = 'Order Confirmation'
                    buyer_message = render_to_string('emails/buyer_confirmation.html', {
                        'buyer_name': request.user.username,
                        'product': product,
                        'total': total,
                    })

                    try:
                        # Send confirmation email to the buyer with HTML content
                        send_mail(
                            buyer_subject,
                            '',  # Leave the plain text message empty or add a simple fallback if needed
                            settings.DEFAULT_FROM_EMAIL,
                            [request.user.email],
                            fail_silently=False,
                            html_message=buyer_message  # This ensures the email is rendered as HTML
                        )
                    except BadHeaderError:
                        print("Invalid header found.")

                cart_items.delete()

                messages.success(request, 'Thank you for your purchase!')
            else:
                messages.error(request, 'Your cart is empty.')
        else:
            messages.error(request, 'Not enough money, please add more funds to your wallet.')

    return redirect('cart')

def mark_as_sold(product_id):
    product = Products.objects.get(id=product_id)
    product.is_sold = True
    product.save()


def remove(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Products, id=product_id)
        cart_items = UserCart.objects.filter(user=request.user, products=product)
        if cart_items.exists():
            cart_items.delete()
        return redirect('cart')
    return render (request, 'cart')

def profile_settings(request):
    # Get all listings for the current user that are not on hold
    user_listings = Products.objects.filter(user=request.user, on_hold=False)
    
    # Separate the listings into current and sold listings
    current_listings = user_listings.filter(is_sold=False)  # Current active listings
    sold_listings = user_listings.filter(is_sold=True)      # Sold listings

    return render(request, 'profile.html', {
        'current_listings': current_listings,
        'sold_listings': sold_listings,
    })



def profile_management(request):
    # Existing email and password forms
    email_form = EmailUpdateForm(instance=request.user)
    password_form = PasswordChangeForm(user=request.user)

    # New profile form for introduction
    profile_form = ProfileUpdateForm(instance=request.user.profile)
    class_form = ClassForm()  # Initialize class_form for GET requests

    if request.method == 'POST':
        # Handle Email Update
        if 'update_email' in request.POST:
            email_form = EmailUpdateForm(request.POST, instance=request.user)
            if email_form.is_valid():
                email_form.save()
                messages.success(request, 'Your email was successfully updated!')
                return redirect('profile_management')

        # Handle Password Change
        if 'change_password' in request.POST:
            password_form = PasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Your password was successfully updated!')
                return redirect('profile_management')

        # Handle Profile (Introduction) Update
        if 'update_profile' in request.POST:
            profile_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
            if profile_form.is_valid():
                profile_form.campus = profile_form.cleaned_data.get('campus')
                profile_form.save()
                messages.success(request, 'Your profile introduction was successfully updated!')
                return redirect('profile_management')
            
        # Handle Class Addition
        if 'class_add' in request.POST:
            class_form = ClassForm(request.POST)
            if class_form.is_valid():
                class_name = class_form.cleaned_data['class_name']
                class_obj, created = Class.objects.get_or_create(name=class_name)
                profile = Profile.objects.get(user=request.user)
                profile.classes.add(class_obj)
                return redirect('profile_management')

    return render(request, 'profile_management.html', {
        'email_form': email_form,
        'password_form': password_form,
        'profile_form': profile_form,  # Pass the new profile form
        'class_form': class_form,  # Ensure class_form is always passed to the template
    })

def delete_listing(request, id):
    listing = get_object_or_404(Products, id=id, user=request.user)
    if request.method == 'POST':
        listing.delete()
        return redirect('profile_settings')


def user_listings(request, user_id):
    user = get_object_or_404(User, id=user_id)
    listings = Products.objects.filter(user=user)
    reviews = UserReviews.objects.filter(user2 = user)
    form = ReviewForm()
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.user2 = user
            review.save()
        else:
            form = ReviewForm()
        
    return render(request, 'user_listings.html', {'user': user, 'listings': listings, 'reviews' : reviews, 'form':form})



def edit_listing(request, listing_id):
    listing = get_object_or_404(Products, id=listing_id, user=request.user)
    if request.method == 'POST':
        form = ProductsForm(request.POST, request.FILES, instance=listing)
        if form.is_valid():
            form.save()
            return redirect('profile_settings')
    else:
        form = ProductsForm(instance=listing)
    return render(request, 'edit_listing.html', {'form': form})

# View to see listings on hold
def hold_listings(request):
    products = Products.objects.filter(user=request.user, on_hold=True)
    return render(request, 'hold_products.html', {'products': products})

# To put a product on hold
def hold_products(request, pk):
    listings = Products.objects.get(id=pk)
    if request.method == 'POST':  
        listings.on_hold = True  
        listings.save()  
        return redirect('profile_settings')  
    return redirect('profile') 

def restoreProduct(request, pk):
    listings = Products.objects.get(id=pk)
    listings.on_hold = False 
    listings.save()
    return redirect('hold_products') 

# View to see listings archived
def saved_listings(request):
    products = saveProducts.objects.filter(user=request.user)
    return render(request, 'saved_products.html', {'products': products})

# To archive a Product
def saved_products(request):
    if request.method == 'POST': 
        saved_id = request.POST.get('saved_id')
        product = get_object_or_404(Products, id=saved_id)
        listings = saveProducts.objects.filter(user=request.user, products=product)
        if not listings.exists():
            saveProducts.objects.create(
                user=request.user,
                products=product,
            )
        return redirect('explore')  
    return redirect(request, 'saved_products') 

def unsaveProduct(request):
    if request.method == 'POST':
        saved_id = request.POST.get('saved_id')
        product = get_object_or_404(Products, id=saved_id)
        listings = saveProducts.objects.filter(user=request.user, products=product)
        if listings.exists():
            listings.delete()
        return redirect('saved_products')
    return redirect('saved_products') 


def wallet(request):
    try:
        money = Wallet.objects.get(user=request.user)
    except Wallet.DoesNotExist:
        money = Wallet.objects.create(user=request.user, balance = 0)
    if request.method == 'POST':
        form = Walletform(request.POST)
        if form.is_valid():
            current = form.cleaned_data['money']
            money.balance += (current)
            money.save()
            return redirect('wallet')
    else:
        form = Walletform()
    return render(request, 'wallet.html', {'form': form, 'wallet' : money})


def relist_product(request, product_id):
    product = get_object_or_404(Products, id=product_id, user=request.user, is_sold=True)
    
    if request.method == 'POST':
        # Mark the product as not sold anymore
        product.is_sold = False
        product.available_until = None  # Optionally reset the availability time or set a new time
        product.save()

        messages.success(request, f'{product.name} has been successfully relisted!')
        return redirect('profile_settings')
    
    return render(request, 'profile.html')

def landing(request):
    return render(request, 'landing.html')

def about(request):
    return render (request, 'about.html')
'''
def send_purchase_confirmation(seller_email, listing_title, buyer_name):
    try:
        seller_subject = f'Your listing "{listing_title}" has been purchased!'
        seller_message = render_to_string('emails/seller_notification.html', {
            'listing_title': listing_title,
            'buyer_name': buyer_name,
        })

        send_mail(
            seller_subject,
            seller_message,
            settings.DEFAULT_FROM_EMAIL,
            [seller_email],
            fail_silently=False,
        )
    except BadHeaderError:
        print("Invalid header found.")
'''

def send_purchase_confirmation(seller_email, listing_title, buyer_name):
    try:
        seller_subject = f'Your listing "{listing_title}" has been purchased!'
        
        # Render the HTML content for the email
        seller_message = render_to_string('emails/seller_notification.html', {
            'listing_title': listing_title,
            'buyer_name': buyer_name,
        })

        # Send the email with the rendered HTML content
        send_mail(
            seller_subject,
            '',  # Leave the plain text message empty or include a simple fallback message
            settings.DEFAULT_FROM_EMAIL,
            [seller_email],
            fail_silently=False,
            html_message=seller_message  # This ensures the email is rendered as HTML
        )
    except BadHeaderError:
        print("Invalid header found.")


def editreview(request,review_id):
    review = get_object_or_404(UserReviews,id=review_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('explore')
    else:
        form = ReviewForm(instance=review)
    return render(request,'edit_review.html',{'form':form})

def deletereview(reqest,review_id):
    review = get_object_or_404(UserReviews,id=review_id)
    if reqest.method == 'POST':
        review.delete()
        return redirect('explore')
    return render(reqest,"user_listings.html")