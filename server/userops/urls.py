from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.login_view, name='login'),
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='user/password_reset.html',
            email_template_name='user/password_reset_email.txt',
            success_url='/password-reset/done/',
        ),
        name='password_reset',
    ),
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='user/password_reset_done.html',
        ),
        name='password_reset_done',
    ),
    path(
        'password-reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='user/password_reset_confirm.html',
            success_url='/password-reset/complete/',
        ),
        name='password_reset_confirm',
    ),
    path(
        'password-reset/complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='user/password_reset_complete.html',
        ),
        name='password_reset_complete',
    ),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/listings/', views.listings_view, name='dashboard_listings'),
    path('dashboard/wishlist/', views.wishlist_view, name='dashboard_wishlist'),
    path('dashboard/notifications/', views.notifications_view, name='dashboard_notifications'),
    path('dashboard/requests/', views.requests_view, name='dashboard_requests'),
    path('profile/', views.profile_view, name='profile'),
    path('settings/', views.settings_view, name='settings'),
]