from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages


def login_view(request):
    """
    User login view with HTMX support
    Clears global filter session on every login for consistent behavior
    """
    if request.user.is_authenticated:
        # If user is already authenticated and tries to access login page,
        # redirect to dashboard (session remains intact for current session)
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Clear global filter session data before login
            # This ensures fresh start for every login (especially important for Global Level users)
            session_keys_to_clear = ['global_company_id', 'global_brand_id', 'global_store_id']
            for key in session_keys_to_clear:
                if key in request.session:
                    del request.session[key]
            
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            
            # Get next URL or default to dashboard
            next_url = request.POST.get('next') or request.GET.get('next') or '/dashboard/'
            
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'auth/login.html')


@login_required
def logout_view(request):
    """
    User logout view - Clear all session data including global filters
    """
    # Clear global filter session data before logout
    session_keys_to_clear = ['global_company_id', 'global_brand_id', 'global_store_id']
    for key in session_keys_to_clear:
        if key in request.session:
            del request.session[key]
    
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('auth:login')
