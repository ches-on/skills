from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def admin_required(view_func):
    """
    Decorator that checks if the user is logged in and has staff status.
    Redirects to home page if not authorized.
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in to access this page.')
            return redirect('login')
        if not request.user.is_staff:
            messages.error(request, 'You do not have permission to access the admin panel.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


# Alternative: combine login_required and admin_required
def admin_login_required(view_func):
    """
    Decorator that first checks login, then checks admin status.
    """
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, 'You do not have permission to access the admin panel.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper
