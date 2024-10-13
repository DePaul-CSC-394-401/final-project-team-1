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

# Index view
def index(request):
    return render(request, 'index.html')

# Listings view
def listings(request):
    products = Products.objects.all()
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
        graduating = request.POST.get('graduating', False)  == 'on'

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
            return redirect('index')
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
                user = request.user,
                products = product,
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
            cart_items.delete()
        messages.success(request, 'Thank you for your purchase')
    return redirect('cart')