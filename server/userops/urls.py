from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/listings/', views.listings_view, name='dashboard_listings'),
    path('dashboard/wishlist/', views.wishlist_view, name='dashboard_wishlist'),
    path('dashboard/notifications/', views.notifications_view, name='dashboard_notifications'),
    path('dashboard/requests/', views.requests_view, name='dashboard_requests'),
    path('profile/', views.profile_view, name='profile'),
    path('settings/', views.settings_view, name='settings'),
]