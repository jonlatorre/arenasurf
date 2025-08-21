"""
Mixins de seguridad para la aplicación Arena Surf Center
"""
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin que requiere que el usuario esté autenticado y sea miembro del staff
    """
    
    def test_func(self):
        return self.request.user.is_staff
    
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            messages.error(self.request, 'Debes iniciar sesión para acceder a esta página.')
            return redirect('account_login')
        
        messages.error(
            self.request, 
            'No tienes permisos para acceder a esta sección. Se requiere acceso de staff.'
        )
        return redirect('home')


def staff_required(function=None, redirect_url='home'):
    """
    Decorador que requiere que el usuario sea miembro del staff
    """
    def check_staff(user):
        if not user.is_authenticated:
            return False
        return user.is_staff
    
    def decorator(view_func):
        def wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Debes iniciar sesión para acceder a esta página.')
                return redirect('account_login')
            
            if not request.user.is_staff:
                messages.error(
                    request, 
                    'No tienes permisos para acceder a esta sección. Se requiere acceso de staff.'
                )
                return redirect(redirect_url)
            
            return view_func(request, *args, **kwargs)
        return wrapped_view
    
    if function:
        return decorator(function)
    return decorator


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin que requiere que el usuario sea superusuario (para acciones críticas)
    """
    
    def test_func(self):
        return self.request.user.is_superuser
    
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            messages.error(self.request, 'Debes iniciar sesión para acceder a esta página.')
            return redirect('account_login')
        
        messages.error(
            self.request, 
            'No tienes permisos para realizar esta acción. Se requiere acceso de administrador.'
        )
        return redirect('home')


def admin_required(function=None, redirect_url='home'):
    """
    Decorador que requiere que el usuario sea superusuario
    """
    def decorator(view_func):
        def wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Debes iniciar sesión para acceder a esta página.')
                return redirect('account_login')
            
            if not request.user.is_superuser:
                messages.error(
                    request, 
                    'No tienes permisos para realizar esta acción. Se requiere acceso de administrador.'
                )
                return redirect(redirect_url)
            
            return view_func(request, *args, **kwargs)
        return wrapped_view
    
    if function:
        return decorator(function)
    return decorator
