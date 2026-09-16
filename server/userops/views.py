from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .form import UserRegForm


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
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'user/login.html', {'form': form})


def logout_view(request):
    """
    Handle user logout and redirect to home.
    """
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')


# Aliases for convenience
register_view = register
user_register = register
