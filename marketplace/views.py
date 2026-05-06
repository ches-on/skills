from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden, JsonResponse
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.models import User
from .models import (
    Listing, Profile, ROLE_CHOICES, ServiceCategory,
    Product, ProductCategory, Cart, CartItem, Order, OrderItem, ProductImage,
    ServicePortfolioImage
)
from .forms import (
    ListingForm, RegisterForm, ProfileForm,
    ProductForm, CartAddProductForm
)


# ========== HELPER FUNCTIONS ==========

def get_role_display(user):
    """Get the display name of the user's role"""
    if hasattr(user, 'profile'):
        return user.profile.get_role_display()
    return 'Customer'


# ========== EXISTING LISTING VIEWS ==========

def home(request):
    search_query = request.GET.get('q', '')
    category_filter = request.GET.get('category', '')

    listings = Listing.objects.all()

    if search_query:
        listings = listings.filter(
            Q(title__icontains=search_query) | Q(skill_name__icontains=search_query)
        )

    if category_filter:
        listings = listings.filter(category__id=category_filter)

    paginator = Paginator(listings, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'category_filter': category_filter,
        'categories': ServiceCategory.objects.all(),
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
    # Only providers can create services
    if not request.user.profile.is_provider:
        messages.error(request, 'Only service providers can create listings.')
        return redirect('home')

    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.created_by = request.user
            listing.save()
            # Handle portfolio image uploads
            portfolio_images = form.cleaned_data.get('portfolio_images')
            if portfolio_images:
                for img in portfolio_images:
                    ServicePortfolioImage.objects.create(service=listing, image=img)
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
            # Handle portfolio image uploads
            portfolio_images = form.cleaned_data.get('portfolio_images')
            if portfolio_images:
                for img in portfolio_images:
                    ServicePortfolioImage.objects.create(service=listing, image=img)
            messages.success(request, 'Listing updated successfully!')
            return redirect('listing_detail', pk=listing.pk)
    else:
        form = ListingForm(instance=listing)

    # Get existing portfolio images
    portfolio_images = listing.portfolio_images.all()
    context = {
        'form': form,
        'listing': listing,
        'portfolio_images': portfolio_images,
    }
    return render(request, 'marketplace/edit_listing.html', context)


@login_required
def delete_service_image(request, pk):
    if request.method == 'POST':
        image_id = request.POST.get('image_id')
        image = get_object_or_404(ServicePortfolioImage, id=image_id, service__created_by=request.user)
        image.delete()
        messages.success(request, 'Portfolio image deleted successfully!')
        return redirect('edit_listing', pk=pk)
    return redirect('edit_listing', pk=pk)


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
    """Role-based dashboard - shows different content based on user role"""
    user_role = request.user.profile.role

    context = {}

    if user_role == 'provider':
        # Providers see their services
        listings = Listing.objects.filter(created_by=request.user)
        context['listings'] = listings
        context['dashboard_type'] = 'provider'
    elif user_role == 'merchant':
        # Merchants see their products
        products = Product.objects.filter(seller=request.user)
        context['products'] = products
        context['dashboard_type'] = 'merchant'
    else:
        # Customers see nothing (or could see their orders)
        context['dashboard_type'] = 'customer'

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
            role = form.cleaned_data.get('role')
            user.profile.role = role
            user.profile.save()
            login(request, user)
            messages.success(request, 'Registration successful! You are now logged in.')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'marketplace/register.html', {'form': form})


# ========== PRODUCT VIEWS ==========

def product_list(request):
    search_query = request.GET.get('q', '')
    category_filter = request.GET.get('category', '')

    products = Product.objects.filter(stock__gt=0)

    if search_query:
        products = products.filter(name__icontains=search_query)

    if category_filter:
        products = products.filter(category__id=category_filter)

    categories = ProductCategory.objects.all()

    paginator = Paginator(products, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'category_filter': category_filter,
        'search_query': search_query,
    }
    return render(request, 'marketplace/products/list.html', context)


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    is_seller = request.user.is_authenticated and request.user == product.seller
    form = CartAddProductForm()
    context = {
        'product': product,
        'is_seller': is_seller,
        'form': form,
    }
    return render(request, 'marketplace/products/detail.html', context)


@login_required
def create_product(request):
    # Only merchants can create products
    if not request.user.profile.is_merchant:
        messages.error(request, 'Only merchants can create products.')
        return redirect('product_list')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            # Handle multiple image uploads from form
            images = form.cleaned_data.get('images', [])
            if images:
                for idx, image in enumerate(images):
                    ProductImage.objects.create(
                        product=product,
                        image=image,
                        is_primary=(idx == 0)  # First image is primary
                    )
            messages.success(request, 'Product created successfully!')
            return redirect('product_detail', pk=product.pk)
    else:
        form = ProductForm()
    return render(request, 'marketplace/products/create.html', {'form': form})


@login_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.user != product.seller:
        return HttpResponseForbidden('You are not allowed to edit this product.')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            # Handle multiple image uploads from form
            images = form.cleaned_data.get('images', [])
            if images:
                for img in images:
                    ProductImage.objects.create(
                        product=product,
                        image=img,
                        is_primary=False
                    )
            messages.success(request, 'Product updated successfully!')
            return redirect('product_detail', pk=product.pk)
    else:
        form = ProductForm(instance=product)
    return render(request, 'marketplace/products/edit.html', {'form': form, 'product': product})


@login_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.user != product.seller:
        return HttpResponseForbidden('You are not allowed to delete this product.')

    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('seller_dashboard')
    return render(request, 'marketplace/products/delete.html', {'product': product})


@login_required
def delete_product_image(request, pk):
    if request.method == 'POST':
        image_id = request.POST.get('image_id')
        image = get_object_or_404(ProductImage, id=image_id, product__seller=request.user)
        image.delete()
        messages.success(request, 'Image deleted successfully!')
    return redirect('edit_product', pk=pk)


@login_required
def seller_dashboard(request):
    """Dashboard for merchants to manage their products"""
    # Only merchants should access this
    if not request.user.profile.is_merchant:
        messages.error(request, 'Access denied. This page is for merchants only.')
        return redirect('home')

    products = Product.objects.filter(seller=request.user)
    context = {
        'products': products,
    }
    return render(request, 'marketplace/products/dashboard.html', context)


# ========== CART VIEWS ==========

@login_required
def cart_view(request):
    cart = request.user.cart
    items = cart.items.all()
    context = {
        'cart': cart,
        'items': items,
    }
    return render(request, 'marketplace/products/cart.html', context)


@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = CartAddProductForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            cart_item, created = CartItem.objects.get_or_create(
                cart=request.user.cart,
                product=product,
                defaults={'quantity': quantity}
            )
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            messages.success(request, f'Added {quantity} x {product.name} to cart.')
    return redirect('cart')


@login_required
def remove_from_cart(request, pk):
    cart_item = get_object_or_404(CartItem, pk=pk, cart=request.user.cart)
    if request.method == 'POST':
        cart_item.delete()
        messages.success(request, 'Item removed from cart.')
    return redirect('cart')


@login_required
def update_cart_item(request, pk):
    cart_item = get_object_or_404(CartItem, pk=pk, cart=request.user.cart)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()
    return redirect('cart')


# ========== ORDER VIEWS ==========

@login_required
def checkout(request):
    cart = request.user.cart
    if cart.total_items == 0:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart')

    if request.method == 'POST':
        order = Order.objects.create(
            user=request.user,
            total_price=cart.total_price
        )
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            # Reduce stock
            item.product.stock -= item.quantity
            item.product.save()
        # Clear cart
        cart.items.all().delete()
        messages.success(request, f'Order #{order.id} placed successfully!')
        return redirect('order_detail', pk=order.pk)

    return render(request, 'marketplace/products/checkout.html', {'cart': cart})


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, 'marketplace/products/order_detail.html', {'order': order})


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'marketplace/products/my_orders.html', {'orders': orders})


# ========== ACCOUNT MANAGEMENT ==========

@login_required
def delete_account(request):
    """Allow users to delete their own account"""
    if request.method == 'POST':
        user = request.user
        # Logout the user first
        logout(request)
        # Delete the user (this will cascade delete profile, cart, etc. due to on_delete=models.CASCADE)
        user.delete()
        messages.success(request, 'Your account has been deleted successfully.')
        return redirect('home')

    return render(request, 'marketplace/delete_account.html')
