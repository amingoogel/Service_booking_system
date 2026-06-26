from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            if request.user.is_admin_user and 'admin' in roles:
                return view_func(request, *args, **kwargs)
            if request.user.role in roles:
                return view_func(request, *args, **kwargs)
            messages.error(request, 'شما دسترسی به این بخش را ندارید.')
            return redirect('home')
        return wrapper
    return decorator
