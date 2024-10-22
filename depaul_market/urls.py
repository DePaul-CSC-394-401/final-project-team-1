from django.urls import path
from . import views
from django.contrib import admin

urlpatterns = [
    path('', views.index, name='index'),
    path('explore/', views.listings, name='explore'),
    path('signup', views.signup, name='signup'),
    path('userlogin', views.userlogin, name='userlogin'),
    path('add_listing', views.addProduct, name='add_listing'),
    path('cart/', views.view_cart, name='cart'),
    path('add', views.add_to_cart, name='add_to_cart'),
    path('remove', views.remove, name='remove'),
    path('pay', views.payment, name='payment'),
<<<<<<< Updated upstream
=======
    path('profile/', views.profile_settings, name='profile_settings'),
    path('logout/', LogoutView.as_view(next_page='userlogin'), name='logout'),
    path('listing/<int:listing_id>/edit/', views.edit_listing, name='edit_listing'),  # Updated for clarity
    path('delete_listing/<int:id>/', views.delete_listing, name='delete_listing'),
    path('user/<int:user_id>/listings/', views.user_listings, name='user_listings'),
    path('wallet', views.wallet, name='wallet'),
>>>>>>> Stashed changes
]
