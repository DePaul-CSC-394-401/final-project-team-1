from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Profile, Wallet
from django.contrib.auth import authenticate, login
from django.db import IntegrityError
from .models import Products, UserCart
from .forms import ProductsForm
from django.db import models
from datetime import datetime
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import EmailUpdateForm  
from django.shortcuts import get_object_or_404
from django.shortcuts import render, get_object_or_404, redirect
from .forms import EditListingForm, Walletform
from .forms import EmailUpdateForm, ProfileUpdateForm  # Add ProfileUpdateForm

from datetime import timedelta  # Add this at the top of the file

from datetime import timedelta



# Index view
def index(request):
    return render(request, 'index.html')

# Listings view
def listings(request):
    query = request.GET.get('q')
    location = request.GET.get('location')
    price_sort = request.GET.get('price')
    date_sort = request.GET.get('date_listed')

    # Only show products that are still available
    products = Products.objects.filter(
        models.Q(available_until__isnull=True) | models.Q(available_until__gt=datetime.now()), on_hold=False
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

    context = {'products': products}
    return render(request, 'explore.html', context)


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
            return redirect('explore')
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

            # Handle availability duration
            duration = request.POST.get('availability_duration')  # Get availability duration
            if duration:  # If a duration was set
                hours = int(duration)
                product.available_until = datetime.now() + timedelta(hours=hours)  # Set available_until

            product.save()
            return redirect('/explore')
    
    context = {'ProductsForm': form}
    return render(request, 'add_listing.html', context)

def addProduct(request):
    form = ProductsForm()
    if request.method == 'POST':
        form = ProductsForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False) 
            product.user = request.user
            
            # Capture availability duration from the form (it will be in hours or days, for example)
            availability_duration = form.cleaned_data.get('availability_duration', None)
            
            if availability_duration:
                # Calculate the available_until time by adding the duration to the current time
                product.available_until = datetime.now() + timedelta(hours=availability_duration)
            
            product.save()  # Save the product with the available_until field
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
        cart_list = UserCart.objects.filter(user=request.user)
        total = 0
        for item in cart_list:
            total += item.products.price
        if wallet.balance >= total:
            if cart_items.exists():
                wallet.balance-=total
                wallet.save()
                for items in cart_items:
                    items.products.delete()
                cart_items.delete()

            messages.success(request, 'Thank you for your purchase')
        else:
            messages.success(request, 'Not enough money, your broke')
    return redirect('cart')

def remove(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Products, id=product_id)
        cart_items = UserCart.objects.filter(user=request.user, products=product)
        if cart_items.exists():
            cart_items.delete()
        return redirect('cart')
    return render (request, 'cart')


@login_required
def profile_settings(request):
    user_listings = Products.objects.filter(user=request.user, on_hold=False)
    return render(request, 'profile.html', {
        'listings': user_listings,
    })

def profile_management(request):
    # Existing email and password forms
    email_form = EmailUpdateForm(instance=request.user)
    password_form = PasswordChangeForm(user=request.user)

    # New profile form for introduction
    profile_form = ProfileUpdateForm(instance=request.user.profile)

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
                profile_form.save()
                messages.success(request, 'Your profile introduction was successfully updated!')
                return redirect('profile_management')

    return render(request, 'profile_management.html', {
        'email_form': email_form,
        'password_form': password_form,
        'profile_form': profile_form,  # Pass the new profile form
    })

def delete_listing(request, id):
    listing = get_object_or_404(Products, id=id, user=request.user)
    if request.method == 'POST':
        listing.delete()
        return redirect('profile_settings')


def user_listings(request, user_id):
    user = get_object_or_404(User, id=user_id)
    listings = Products.objects.filter(user=user)
    return render(request, 'user_listings.html', {'user': user, 'listings': listings})


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

