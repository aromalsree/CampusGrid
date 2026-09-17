from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import App_users


@admin.register(App_users)
class AppUsersAdmin(UserAdmin):
	list_display = ('username', 'email', 'user_roles', 'institution', 'is_active')
	list_filter = ('user_roles', 'is_active', 'is_staff', 'is_superuser')
	search_fields = ('username', 'email', 'institution')
	fieldsets = UserAdmin.fieldsets + (
		('Campus Profile', {'fields': ('user_roles', 'institution', 'phone')}),
	)
	add_fieldsets = UserAdmin.add_fieldsets + (
		('Campus Profile', {'fields': ('email', 'user_roles', 'institution', 'phone')}),
	)
