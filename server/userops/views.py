from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from .form import LoginForm
from django.contrib import messages
from .form import UserRegForm
from django.views import View
from django.utils.http import url_has_allowed_host_and_scheme


class RegisterView(View):
    def get(self,request):
        form = UserRegForm()
        return render(request, 'user/register.html', {'form': form})
        

    def post(self, request):
        form = UserRegForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to CampusGrid, {user.username}! Your account has been registered.")
            return redirect('home')

        messages.error(request, "Please correct the errors below to create your account.")
        return render(request, 'user/register.html', {'form': form})



def register(request):
    """
    Handle user registration using UserRegForm and render templates/user/register.html
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserRegForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to CampusGrid, {user.username}! Your account has been registered.")
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                if field != '__all__':
                    for error in errors:
                        messages.error(request, error)
    else:
        form = UserRegForm()

    return render(request, 'user/register.html', {'form': form})


def login_view(request):
    """
    Handle user login using AuthenticationForm and render templates/user/login.html
    """
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.user_roles == 'ADMIN':
            return redirect('admin_dashboard')
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            if user.is_superuser or user.user_roles == 'ADMIN':
                return redirect('admin_dashboard')
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url and url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()

    return render(request, 'user/login.html', {'form': form})


def logout_view(request):
    """
    Handle user logout and redirect to home.
    """
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')


from django.contrib.auth.decorators import login_required

@login_required
def dashboard_view(request):
    user = request.user
    user_listings = []
    active_count = 0
    wishlist_count = 0
    try:
        from market.models import Listing, Wishlist
        user_listings = Listing.objects.filter(seller=user).order_by('-created_at')
        active_count = user_listings.filter(status=Listing.ListingStatus.ACTIVE).count()
        wishlist_count = Wishlist.objects.filter(user=user).count()
    except Exception:
        pass

    context = {
        'user_listings': user_listings,
        'active_listings_count': active_count,
        'wishlist_count': wishlist_count,
        'active_tab': 'overview',
    }
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def listings_view(request):
    user = request.user
    user_listings = []
    try:
        from market.models import Listing
        user_listings = Listing.objects.filter(seller=user).order_by('-created_at')
    except Exception:
        pass

    return render(request, 'dashboard/listings.html', {
        'user_listings': user_listings,
        'active_tab': 'listings',
    })


@login_required
def wishlist_view(request):
    user = request.user
    wishlist_items = []
    try:
        from market.models import Wishlist
        wishlist_items = Wishlist.objects.filter(user=user).select_related('listing').order_by('-created_at')
    except Exception:
        pass

    return render(request, 'dashboard/wishlist.html', {
        'wishlist_items': wishlist_items,
        'active_tab': 'wishlist',
    })


@login_required
def notifications_view(request):
    return render(request, 'dashboard/notifications.html', {
        'active_tab': 'notifications',
    })


@login_required
def requests_view(request):
    user_requests = []
    try:
        from market.models import NeedRequest
        user_requests = NeedRequest.objects.filter(requester=request.user).order_by('-created_at')
    except Exception:
        pass

    return render(request, 'dashboard/requests.html', {
        'user_requests': user_requests,
        'active_tab': 'requests',
    })



@login_required
def profile_view(request):
    if request.method == 'POST':
        institution = request.POST.get('institution', '').strip()
        phone = request.POST.get('phone', '').strip()
        user = request.user
        if institution:
            user.institution = institution
        if phone:
            user.phone = phone
        user.save()
        messages.success(request, "Your profile changes have been saved.")
        return redirect('profile')

    return render(request, 'user/profile.html', {
        'active_tab': 'profile',
    })


@login_required
def settings_view(request):
    if request.method == 'POST':
        messages.success(request, "Your account and notification settings have been updated.")
        return redirect('settings')

    return render(request, 'user/settings.html', {
        'active_tab': 'settings',
    })

