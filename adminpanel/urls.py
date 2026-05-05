from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='admin_dashboard'),

    # User management
    path('users/', views.user_list, name='admin_user_list'),
    path('users/<int:pk>/', views.user_detail, name='admin_user_detail'),
    path('users/add/', views.user_add, name='admin_user_add'),

    # Service management
    path('services/', views.service_list, name='admin_service_list'),
    path('services/<int:pk>/edit/', views.service_edit, name='admin_service_edit'),
    path('services/<int:pk>/delete/', views.service_delete, name='admin_service_delete'),

    # Product management
    path('products/', views.product_list, name='admin_product_list'),
    path('products/<int:pk>/edit/', views.product_edit, name='admin_product_edit'),
    path('products/<int:pk>/delete/', views.product_delete, name='admin_product_delete'),

    # Category management
    path('categories/', views.category_list, name='admin_category_list'),
    path('categories/add/', views.category_add, name='admin_category_add'),
    path('categories/<int:pk>/edit/', views.category_edit, name='admin_category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='admin_category_delete'),

    # Order management
    path('orders/', views.order_list, name='admin_order_list'),
    path('orders/<int:pk>/', views.order_detail, name='admin_order_detail'),
]
