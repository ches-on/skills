from django.contrib import admin
from .models import (
    Listing, Profile,
    Product, ProductCategory, Cart, CartItem, Order, OrderItem
)


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'location', 'created_by', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['title', 'description', 'location']
    date_hierarchy = 'created_at'


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone', 'location']
    list_filter = ['role']
    search_fields = ['user__username', 'phone', 'location']


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'seller', 'created_at']
    list_filter = ['category', 'seller']
    search_fields = ['name', 'description']
    date_hierarchy = 'created_at'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at']
    search_fields = ['user__username']


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'quantity']
    list_filter = ['cart__user']
    search_fields = ['product__name']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_price', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'id']
    date_hierarchy = 'created_at'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price']
    list_filter = ['order__status']
    search_fields = ['product__name']
