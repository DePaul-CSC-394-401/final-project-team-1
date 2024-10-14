from django.urls import path
from . import views
from django.contrib import admin
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.index, name='index'),
    path('explore/', views.listings, name='explore'),
    path('signup', views.signup, name='signup'),
    path('userlogin', views.userlogin, name='userlogin'),
    path('add_listing', views.addProduct, name='add_listing'),
    path('cart/', views.view_cart, name='cart'),
    path('add', views.add_to_cart, name='add_to_cart'),
    path('pay', views.payment, name='payment'),
    path('profile/', views.profile_settings, name='profile_settings'),
<<<<<<< HEAD
    path('logout/', LogoutView.as_view(next_page='userlogin'), name='logout'),
=======
    

    path('delete_listing/<int:id>/', views.delete_listing, name='delete_listing'),
    path('user/<int:user_id>/', views.user_listings, name='user_listings'),

>>>>>>> 48d404b (User Listings)
]
