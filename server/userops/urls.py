from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/admin/', views.AdminDashboard.as_view(), name='admin_dashboard'),
    path('dashboard/user/', views.UserDashboard.as_view(), name='user_dashboard'),
    path('dashboard/wishlist/', views.wishlist_view, name='wishlist'),
    path('dashboard/wishlist/<int:listing_id>/', views.toggle_wishlist, name="add_wishlist"),
    path('dashboard/listings/', views.UserListingsListView.as_view(), name='dashboard_listings'),
    path('dashboard/requests/', views.UserNeedRequestsListView.as_view(), name='dashboard_requests'),
    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),
    
]