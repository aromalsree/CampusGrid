from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.utils import timezone
from django.contrib import messages
from datetime import timedelta
from userops.form import UserRegForm

User = get_user_model()


def home(request):
    featured_products = []
    categories = []
    listing_count = 0
    try:
        from market.models import Listing, Category
        featured_products = Listing.objects.filter(
            status=Listing.ListingStatus.ACTIVE
        ).select_related('seller', 'category').prefetch_related('images').order_by('-created_at')[:8]
        categories = Category.objects.filter(is_active=True)
        listing_count = Listing.objects.filter(status=Listing.ListingStatus.ACTIVE).count()
    except Exception:
        pass

    context = {
        'featured_products': featured_products,
        'categories': categories,
        'listing_count': listing_count,
    }
    return render(request, 'home/index.html', context)


def contact(request):
    if request.method == 'POST':
        required_fields = ('name', 'email', 'subject', 'message')
        if all(request.POST.get(field, '').strip() for field in required_fields):
            messages.success(request, 'Thanks for reaching out. The CampusGrid team will get back to you soon.')
            return redirect('contact')
        messages.error(request, 'Please complete all contact form fields.')

    return render(request, 'home/contact.html')


def is_admin(user):
    return user.is_authenticated and (user.is_superuser or user.user_roles == 'ADMIN')


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    admin_users = User.objects.filter(user_roles='ADMIN').count()
    recent_users = User.objects.order_by('-date_joined')[:10]
    
    # Users joined in last 7 days
    week_ago = timezone.now() - timedelta(days=7)
    new_users_week = User.objects.filter(date_joined__gte=week_ago).count()
    
    context = {
        'total_users': total_users,
        'active_users': active_users,
        'admin_users': admin_users,
        'new_users_week': new_users_week,
        'recent_users': recent_users,
    }
    return render(request, 'admin/dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def admin_users(request):
    query = request.GET.get('q', '')
    role_filter = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')
    
    users = User.objects.all().order_by('-date_joined')
    
    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(institution__icontains=query)
        )
    
    if role_filter:
        users = users.filter(user_roles=role_filter)
    
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(users, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'role_filter': role_filter,
        'status_filter': status_filter,
        'total_count': users.count(),
    }
    return render(request, 'admin/users.html', context)


@login_required
@user_passes_test(is_admin)
def admin_user_add(request):
    if request.method == 'POST':
        form = UserRegForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_roles = request.POST.get('user_roles', 'USER')
            user.is_staff = user.user_roles == 'ADMIN'
            user.save()
            messages.success(request, f"User {user.username} was created successfully.")
            return redirect('admin_users')
        messages.error(request, "Please correct the errors below to create the user.")
    else:
        form = UserRegForm()

    return render(request, 'admin/add_user.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def admin_user_toggle_status(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        if user == request.user:
            messages.error(request, "You cannot change your own status.")
        else:
            user.is_active = not user.is_active
            user.save()
            status = "activated" if user.is_active else "deactivated"
            messages.success(request, f"User {user.username} has been {status}.")
    return redirect('admin_users')


@login_required
@user_passes_test(is_admin)
def admin_user_change_role(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        new_role = request.POST.get('role')
        if new_role in ['USER', 'ADMIN'] and user != request.user:
            user.user_roles = new_role
            user.is_staff = (new_role == 'ADMIN')
            user.save()
            messages.success(request, f"User {user.username} role changed to {new_role}.")
        else:
            messages.error(request, "Invalid role or cannot change own role.")
    return redirect('admin_users')


# for testing html pls use the test view
def test(request):
    return render(request, "dashboard/wishlist.html")


def about(request):
    return render(request, 'home/about.html')