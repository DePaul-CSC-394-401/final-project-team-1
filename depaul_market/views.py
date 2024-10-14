from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Profile
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
from .models import Products

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Products
from .forms import ProductsForm

from .models import Products  # Remove Listing import and replace with Products

from .forms import EditListingForm


# Index view
def index(request):
    return render(request, 'index.html')

# Listings view
def listings(request):
    query = request.GET.get('q')
    location = request.GET.get('location')
    price_sort = request.GET.get('price')
    date_sort = request.GET.get('date_listed')

    products = Products.objects.all()
    print(price_sort)
    print(location)

    if query:
        products = products.filter(name__icontains=query)
    if location:
        # Debugging: Print the initial queryset
        print(f"Initial Products: {products}")
        products = products.filter(user__profile__campus=location)
        # Debugging: Print the filtered queryset
        print(f"Filtered Products by Location: {products}")
    if price_sort == 'min':
        products = products.order_by('price')
    elif price_sort == 'max':
        products = products.order_by('-price')

        # Sort by date listed if specified
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
            if not product.made_available:
                product.made_available = datetime.now
            product.user = request.user 
            product.save()  
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

        if cart_items.exists():
            for items in cart_items:
                items.products.delete()
            cart_items.delete()

        messages.success(request, 'Thank you for your purchase')
    return redirect('cart')

def profile_settings(request):
    user_listings = Products.objects.filter(user=request.user)

    email_form = EmailUpdateForm(instance=request.user)
    password_form = PasswordChangeForm(user=request.user)

    if request.method == 'POST':
        # Handle Email Update
        if 'update_email' in request.POST:
            email_form = EmailUpdateForm(request.POST, instance=request.user)
            if email_form.is_valid():
                email_form.save()
                messages.success(request, 'Your email was successfully updated!')
                return redirect('explore')
            else:
                messages.error(request, 'There was an error updating your email.')

        # Handle Password Change
        if 'change_password' in request.POST:
            password_form = PasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Keep the user logged in
                messages.success(request, 'Your password was successfully updated!')
                return redirect('explore')
            else:
                messages.error(request, 'There was an error changing your password.')

    # Always render the forms, whether GET or POST
    return render(request, 'profile.html', {
        'email_form': email_form,
        'password_form': password_form,
        'listings': user_listings,
    })

def delete_listing(request, id):
    listing = get_object_or_404(Products, id=id, user=request.user)
    if request.method == 'POST':
        listing.delete()
        return redirect('profile_settings')
'''
def user_listings(request, user_id):
    print(f"Fetching listings for user ID: {user_id}")
    user = get_object_or_404(User, id=user_id)
    listings = Products.objects.filter(user=user)
    print(f"Found {listings.count()} listings for user {user.username}")

    return render(request, 'user_listings.html', {
        'user': user,
        'listings': listings,
    })
'''
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

