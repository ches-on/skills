from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import HttpResponseForbidden
from django.contrib.auth.forms import UserCreationForm

from marketplace.models import (
    Listing, Profile, ROLE_CHOICES,
    Product, ProductCategory, Order, OrderItem,
    ServicePortfolioImage
)
from marketplace.forms import ProfileForm, RegisterForm
from .decorators import admin_required


# ========== DASHBOARD ==========

@admin_required
def dashboard(request):
    # Summary statistics
    total_users = User.objects.count()
    total_services = Listing.objects.count()
    total_products = Product.objects.count()
    total_orders = Order.objects.count()

    # Recent items
    recent_users = User.objects.all().order_by('-date_joined')[:5]
    recent_orders = Order.objects.all().order_by('-created_at')[:5]

    context = {
        'total_users': total_users,
        'total_services': total_services,
        'total_products': total_products,
        'total_orders': total_orders,
        'recent_users': recent_users,
        'recent_orders': recent_orders,
    }
    return render(request, 'adminpanel/dashboard.html', context)


# ========== USER MANAGEMENT ==========

@admin_required
def user_list(request):
    search_query = request.GET.get('q', '')
    role_filter = request.GET.get('role', '')

    users = User.objects.all().select_related('profile').order_by('-date_joined')

    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    if role_filter:
        users = users.filter(profile__role=role_filter)

    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'role_filter': role_filter,
        'role_choices': ROLE_CHOICES,
    }
    return render(request, 'adminpanel/users.html', context)


@admin_required
def user_detail(request, pk):
    user = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        # Update role
        new_role = request.POST.get('role')
        if new_role in ['customer', 'provider', 'merchant']:
            user.profile.role = new_role
            user.profile.save()
            messages.success(request, f'User role updated to {new_role}.')
            return redirect('admin_user_detail', pk=pk)

        # Delete user
        if request.POST.get('delete_user') == 'true':
            username = user.username
            if user.is_superuser:
                messages.error(request, 'Cannot delete superuser.')
            else:
                user.delete()
                messages.success(request, f'User {username} deleted successfully.')
                return redirect('admin_user_list')

    context = {
        'target_user': user,
        'role_choices': ROLE_CHOICES,
        'listings': Listing.objects.filter(created_by=user),
        'products': Product.objects.filter(seller=user),
        'orders': Order.objects.filter(user=user)[:10],
    }
    return render(request, 'adminpanel/user_detail.html', context)


@admin_required
def user_add(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Set role from POST
            role = request.POST.get('role', 'customer')
            if role in ['customer', 'provider', 'merchant']:
                user.profile.role = role
                user.profile.save()
            messages.success(request, f'User "{user.username}" created successfully.')
            return redirect('admin_user_list')
    else:
        form = UserCreationForm()

    context = {
        'form': form,
        'role_choices': ROLE_CHOICES,
    }
    return render(request, 'adminpanel/user_form.html', context)


# ========== SERVICE MANAGEMENT ==========

@admin_required
def service_list(request):
    search_query = request.GET.get('q', '')
    category_filter = request.GET.get('category', '')

    services = Listing.objects.all().select_related('created_by').order_by('-created_at')

    if search_query:
        services = services.filter(
            Q(title__icontains=search_query) |
            Q(skill_name__icontains=search_query)
        )

    if category_filter:
        services = services.filter(category=category_filter)

    paginator = Paginator(services, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'category_filter': category_filter,
        'categories': Listing.CATEGORY_CHOICES,
    }
    return render(request, 'adminpanel/services.html', context)


@admin_required
def service_edit(request, pk):
    service = get_object_or_404(Listing, pk=pk)

    if request.method == 'POST':
        title = request.POST.get('title')
        category = request.POST.get('category')
        skill_name = request.POST.get('skill_name')
        description = request.POST.get('description')
        contact = request.POST.get('contact')
        location = request.POST.get('location')

        if title:
            service.title = title
            service.category = category
            service.skill_name = skill_name
            service.description = description
            service.contact = contact
            service.location = location
            service.save()
            messages.success(request, 'Service updated successfully.')
            return redirect('admin_service_list')

    context = {
        'service': service,
        'categories': Listing.CATEGORY_CHOICES,
    }
    return render(request, 'adminpanel/service_edit.html', context)


@admin_required
def service_delete(request, pk):
    service = get_object_or_404(Listing, pk=pk)

    if request.method == 'POST':
        title = service.title
        service.delete()
        messages.success(request, f'Service "{title}" deleted successfully.')
        return redirect('admin_service_list')

    return render(request, 'adminpanel/service_confirm_delete.html', {'service': service})


@admin_required
def service_portfolio(request, pk):
    service = get_object_or_404(Listing, pk=pk)

    if request.method == 'POST':
        image_id = request.POST.get('image_id')
        if image_id:
            img = get_object_or_404(ServicePortfolioImage, id=image_id, service=service)
            img.delete()
            messages.success(request, 'Portfolio image deleted successfully.')
            return redirect('admin_service_portfolio', pk=pk)

    context = {
        'service': service,
        'portfolio_images': service.portfolio_images.all(),
    }
    return render(request, 'adminpanel/service_portfolio.html', context)


# ========== PRODUCT MANAGEMENT ==========

@admin_required
def product_list(request):
    search_query = request.GET.get('q', '')
    category_filter = request.GET.get('category', '')

    products = Product.objects.all().select_related('seller', 'category').order_by('-created_at')

    if search_query:
        products = products.filter(name__icontains=search_query)

    if category_filter:
        products = products.filter(category__id=category_filter)

    paginator = Paginator(products, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'category_filter': category_filter,
        'categories': ProductCategory.objects.all(),
    }
    return render(request, 'adminpanel/products.html', context)


@admin_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock = request.POST.get('stock')

        if name:
            product.name = name
            product.category_id = category_id
            product.description = description
            try:
                product.price = float(price)
                product.stock = int(stock)
            except (ValueError, TypeError):
                pass
            product.save()
            messages.success(request, 'Product updated successfully.')
            return redirect('admin_product_list')

    context = {
        'product': product,
        'categories': ProductCategory.objects.all(),
    }
    return render(request, 'adminpanel/product_edit.html', context)


@admin_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f'Product "{name}" deleted successfully.')
        return redirect('admin_product_list')

    return render(request, 'adminpanel/product_confirm_delete.html', {'product': product})


# ========== CATEGORY MANAGEMENT ==========

@admin_required
def category_list(request):
    search_query = request.GET.get('q', '')

    # Product categories
    product_categories = ProductCategory.objects.all().annotate(
        num_products=Count('products')
    )

    if search_query:
        product_categories = product_categories.filter(name__icontains=search_query)

    context = {
        'product_categories': product_categories,
        'service_categories': Listing.CATEGORY_CHOICES,
        'search_query': search_query,
    }
    return render(request, 'adminpanel/categories.html', context)


@admin_required
def category_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')

        if name:
            if ProductCategory.objects.filter(name=name).exists():
                messages.error(request, 'Category with this name already exists.')
            else:
                ProductCategory.objects.create(name=name, description=description)
                messages.success(request, f'Category "{name}" created successfully.')
                return redirect('admin_category_list')

    return render(request, 'adminpanel/category_form.html')


@admin_required
def category_edit(request, pk):
    category = get_object_or_404(ProductCategory, pk=pk)

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')

        if name:
            if ProductCategory.objects.filter(name=name).exclude(pk=pk).exists():
                messages.error(request, 'Category with this name already exists.')
            else:
                category.name = name
                category.description = description
                category.save()
                messages.success(request, f'Category "{name}" updated successfully.')
                return redirect('admin_category_list')

    context = {
        'category': category,
    }
    return render(request, 'adminpanel/category_form.html', context)


@admin_required
def category_delete(request, pk):
    category = get_object_or_404(ProductCategory, pk=pk)

    if request.method == 'POST':
        name = category.name
        # Check if any products use this category
        if category.products.exists():
            messages.error(request, f'Cannot delete category "{name}" because it has products. Remove products first.')
        else:
            category.delete()
            messages.success(request, f'Category "{name}" deleted successfully.')
            return redirect('admin_category_list')

    return render(request, 'adminpanel/category_confirm_delete.html', {'category': category})


# ========== ORDER MANAGEMENT ==========

@admin_required
def order_list(request):
    search_query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')

    orders = Order.objects.all().select_related('user').order_by('-created_at')

    if search_query:
        orders = orders.filter(
            Q(user__username__icontains=search_query) |
            Q(id__icontains=search_query)
        )

    if status_filter:
        orders = orders.filter(status=status_filter)

    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'adminpanel/orders.html', context)


@admin_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['pending', 'completed', 'cancelled']:
            order.status = new_status
            order.save()
            messages.success(request, f'Order status updated to {order.get_status_display()}.')
            return redirect('admin_order_detail', pk=pk)

    context = {
        'order': order,
        'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'adminpanel/order_detail.html', context)
