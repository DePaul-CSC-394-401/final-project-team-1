
from django.urls import path
from . import views
from django.contrib import admin
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.userlogin, name='index'),
    path('landing', views.landing, name='landing'),
    path('explore/', views.listings, name='explore'),
    path('explore/', views.listings, name='listings'),
    path('product/<int:product_id>/', views.view_listing, name='product_detail'),
    path('signup', views.signup, name='signup'),
    path('userlogin', views.userlogin, name='userlogin'),
    path('add_listing', views.addProduct, name='add_listing'),
    path('cart/', views.view_cart, name='cart'),
    path('add', views.add_to_cart, name='add_to_cart'),
    path('pay', views.payment, name='payment'),
    path('remove', views.remove, name='remove'),
    path('profile/', views.profile_settings, name='profile_settings'),

    path('profile-management/', views.profile_management, name='profile_management'),


    path('logout/', LogoutView.as_view(next_page='userlogin'), name='logout'),
    path('listing/<int:listing_id>/edit/', views.edit_listing, name='edit_listing'),  # Updated for clarity
    path('delete_listing/<int:id>/', views.delete_listing, name='delete_listing'),
    path('user/<int:user_id>/listings/', views.user_listings, name='user_listings'),

    path('wallet', views.wallet, name='wallet'),

    path('relist/<int:product_id>/', views.relist_product, name='relist_product'),


    path('product_holded/<str:pk>/', views.hold_products, name='product_holded'),
    path('hold_products/', views.hold_listings, name='hold_products'),
    path('product_restore/<str:pk>/', views.restoreProduct, name='product_restore'),
    path('product_saved', views.saved_products, name='product_saved'),
    path('saved_products/', views.saved_listings, name='saved_products'),
    path('unsave_product', views.unsaveProduct, name='unsave_product'),
    path('wallet', views.wallet, name='wallet'),
    path('about', views.about, name='about'),
    path('edit/<int:review_id>/', views.editreview, name='editreview'),
    path('delete/<int:review_id>/', views.deletereview, name='deletereview')
]
