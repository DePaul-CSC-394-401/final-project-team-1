from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Profile
from django.contrib.auth import authenticate, login
from django.db import IntegrityError

# Index view
def index(request):
    return render(request, 'index.html')

# Listings view
def listings(request):
    return render(request, 'explore.html')

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
                login(request, user)
                return redirect('login')
            except IntegrityError:
                messages.error(request, "Username already taken.")
        else:
            messages.error(request, "Passwords do not match.")
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
