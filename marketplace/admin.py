from django.contrib import admin
from .models import Listing

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'location', 'created_by', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['title', 'description', 'location']
    date_hierarchy = 'created_at'
