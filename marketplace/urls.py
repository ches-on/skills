from django.urls import path
from . import views

urlpatterns = [
    # Existing listing URLs
    path('', views.home, name='home'),
    path('listing/<int:pk>/', views.listing_detail, name='listing_detail'),
    path('create/', views.create_listing, name='create_listing'),
    path('listing/<int:pk>/edit/', views.edit_listing, name='edit_listing'),
    path('listing/<int:pk>/delete/', views.delete_listing, name='delete_listing'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('register/', views.register, name='register'),

    # Product URLs
    path('products/', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('products/create/', views.create_product, name='create_product'),
    path('product/<int:pk>/edit/', views.edit_product, name='edit_product'),
    path('product/<int:pk>/delete/', views.delete_product, name='delete_product'),
    path('seller/dashboard/', views.seller_dashboard, name='seller_dashboard'),

    # Cart URLs
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:pk>/', views.update_cart_item, name='update_cart_item'),

    # Order URLs
    path('checkout/', views.checkout, name='checkout'),
    path('order/<int:pk>/', views.order_detail, name='order_detail'),
    path('my-orders/', views.my_orders, name='my_orders'),
]
