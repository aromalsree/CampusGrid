from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from .form import LoginForm
from django.contrib import messages
from .models import App_users
from .form import UserRegForm, LoginForm
from django.views import View
from django.utils.http import url_has_allowed_host_and_scheme
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta
# html path to var
register_template = 'user/register.html'
login_template = 'user/login.html'

class RegisterView(View):
    def get(self,request):
        form = UserRegForm()
        return render(request, register_template, {'form': form})
        

    def post(self, request):
        form = UserRegForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to CampusGrid, {user.username}! Your account has been registered.")
            return redirect('home')

        messages.error(request, "Please correct the errors below to create your account.")
        return render(request, 'user/register.html', {'form': form})


def is_admin(user):
    return user.is_authenticated and (user.is_superuser or user.user_roles == 'ADMIN')




 
class LoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, login_template, {'form':form})

    def post(self, request):
        form = LoginForm(request=request,data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home")
            
        return render(request, login_template, {'form':form})



def logout_view(request):
    """
    Handle user logout and redirect to home.
    """
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')

class AdminDashboard(LoginRequiredMixin ,View):
    login_url="login"
    def get(self, request):
        total_users = App_users.objects.count()
        active_users = App_users.objects.filter(is_active=True).count()
        admin_users = App_users.objects.filter(user_roles='ADMIN').count()
        recent_users = App_users.objects.order_by('-date_joined')[:10]

        # Users joined in last 7 days
        week_ago = timezone.now() - timedelta(days=7)
        new_users_week = App_users.objects.filter(date_joined__gte=week_ago).count()

        context = {
            'total_users': total_users,
            'active_users': active_users,
            'admin_users': admin_users,
            'new_users_week': new_users_week,
            'recent_users': recent_users,
        }
        return render(request, 'admin/dashboard.html', context)


class UserDashboard(LoginRequiredMixin, View):
    login_url="login"
    def get(self, request):
        query = request.GET.get('q', '')
        role_filter = request.GET.get('role', '')
        status_filter = request.GET.get('status', '')

        users = App_users.objects.all().order_by('-date_joined')

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
