from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden, JsonResponse
from django.db.models import Q
from django.conf import settings
from .models import (
    Listing, Profile, CATEGORY_CHOICES,
    Product, ProductCategory, Cart, CartItem, Order, OrderItem
)
from .forms import (
    ListingForm, RegisterForm, ProfileForm,
    ProductForm, CartAddProductForm
)


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
    products = Product.objects.filter(seller=request.user)
    context = {
        'listings': listings,
        'products': products,
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
    if not request.user.profile.is_provider:
        messages.error(request, 'Only providers can create products.')
        return redirect('product_list')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
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
def seller_dashboard(request):
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
