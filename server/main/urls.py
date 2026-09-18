
from django.urls import path
from . import views
urlpatterns = [
    path('', views.home,name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('user/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('user/admin/users/', views.admin_users, name='admin_users'),
    path('user/admin/users/add/', views.admin_user_add, name='admin_user_add'),
    path('user/admin/users/<int:user_id>/toggle-status/', views.admin_user_toggle_status, name='admin_user_toggle_status'),
    path('user/admin/users/<int:user_id>/change-role/', views.admin_user_change_role, name='admin_user_change_role'),
    # path('test/', views.test, name="test")
]
