from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
from django.db.models import Q
from .models import Listing, Profile, CATEGORY_CHOICES
from .forms import ListingForm, RegisterForm, ProfileForm


def home(request):
    search_query = request.GET.get('q', '')
    category_filter = request.GET.get('category', '')

    listings = Listing.objects.all()

    if search_query:
        listings = listings.filter(
            Q(title__icontains=search_query) | Q(skill_name__icontains=search_query)
        )

    if category_filter:
        listings = listings.filter(category=category_filter)

    paginator = Paginator(listings, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'category_filter': category_filter,
        'categories': CATEGORY_CHOICES,
    }
    return render(request, 'marketplace/home.html', context)


def listing_detail(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    show_contact = request.GET.get('show_contact') == '1'
    is_owner = request.user.is_authenticated and request.user == listing.created_by
    context = {
        'listing': listing,
        'show_contact': show_contact,
        'is_owner': is_owner,
    }
    return render(request, 'marketplace/detail.html', context)


@login_required
def create_listing(request):
    if not request.user.profile.is_provider:
        messages.error(request, 'Only providers can create listings.')
        return redirect('home')

    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.created_by = request.user
            listing.save()
            messages.success(request, 'Listing created successfully!')
            return redirect('listing_detail', pk=listing.pk)
    else:
        form = ListingForm()
    return render(request, 'marketplace/create.html', {'form': form})


@login_required
def edit_listing(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    if request.user != listing.created_by:
        return HttpResponseForbidden('You are not allowed to edit this listing.')

    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES, instance=listing)
        if form.is_valid():
            form.save()
            messages.success(request, 'Listing updated successfully!')
            return redirect('listing_detail', pk=listing.pk)
    else:
        form = ListingForm(instance=listing)
    return render(request, 'marketplace/edit_listing.html', {'form': form, 'listing': listing})


@login_required
def delete_listing(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    if request.user != listing.created_by:
        return HttpResponseForbidden('You are not allowed to delete this listing.')

    if request.method == 'POST':
        listing.delete()
        messages.success(request, 'Listing deleted successfully!')
        return redirect('dashboard')
    return render(request, 'marketplace/delete_listing.html', {'listing': listing})


@login_required
def dashboard(request):
    listings = Listing.objects.filter(created_by=request.user)
    context = {
        'listings': listings,
    }
    return render(request, 'marketplace/dashboard.html', context)


@login_required
def profile(request):
    profile = request.user.profile
    return render(request, 'marketplace/profile.html', {'profile': profile})


@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'marketplace/edit_profile.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Set role from form
            role = form.cleaned_data.get('role')
            user.profile.role = role
            user.profile.save()
            login(request, user)
            messages.success(request, 'Registration successful! You are now logged in.')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'marketplace/register.html', {'form': form})
