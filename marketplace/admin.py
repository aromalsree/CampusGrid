from django.contrib import admin
from .models import (
    UserProfile, Category, Product, ProductImage, ElectronicsSpecification,
    Cart, CartItem, Wishlist, WishlistItem, Order, OrderItem,
    Rental, Review, Notification, Report, SemesterBundle, BundleItem,
    StudentRequest, DigitalDownload, ServiceBooking
)

@admin.action(description='Approve selected student verifications')
def approve_verification(modeladmin, request, queryset):
    queryset.update(verification_status='VERIFIED')

@admin.action(description='Set selected listings to urgent clearance')
def mark_urgent(modeladmin, request, queryset):
    queryset.update(is_urgent=True)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'campus', 'phone_number', 'verification_status', 'is_seller', 'created_at']
    list_filter = ['verification_status', 'campus', 'is_seller']
    search_fields = ['user__username', 'user__email', 'campus', 'phone_number']
    actions = [approve_verification]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon', 'is_active', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['is_active']
    search_fields = ['name']

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ElectronicsSpecificationInline(admin.StackedInline):
    model = ElectronicsSpecification
    can_delete = False
    max_num = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'seller', 'category', 'price', 'product_type', 'condition', 'campus', 'buy_or_rent', 'is_available', 'is_urgent', 'created_at']
    list_filter = ['product_type', 'buy_or_rent', 'condition', 'is_available', 'is_urgent', 'category', 'campus']
    search_fields = ['title', 'description', 'seller__username', 'campus']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ProductImageInline, ElectronicsSpecificationInline]
    actions = [mark_urgent]

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'buyer', 'total_amount', 'payment_method', 'payment_status', 'order_status', 'created_at']
    list_filter = ['order_status', 'payment_status', 'payment_method', 'campus']
    search_fields = ['order_number', 'buyer__username', 'full_name', 'phone']

@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ['product', 'renter', 'owner', 'start_date', 'end_date', 'total_rent', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['product__title', 'renter__username', 'owner__username']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'reviewer', 'rating', 'is_verified_purchase', 'created_at']
    list_filter = ['rating', 'is_verified_purchase']
    search_fields = ['product__title', 'reviewer__username', 'comment']

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'reporter', 'reason', 'status', 'created_at']
    list_filter = ['status', 'reason']
    search_fields = ['product__title', 'reporter__username', 'details', 'admin_notes']

class BundleItemInline(admin.TabularInline):
    model = BundleItem
    extra = 2

@admin.register(SemesterBundle)
class SemesterBundleAdmin(admin.ModelAdmin):
    list_display = ['title', 'seller', 'semester', 'course', 'price', 'campus', 'is_available', 'created_at']
    list_filter = ['semester', 'campus', 'is_available']
    search_fields = ['title', 'course', 'seller__username']
    inlines = [BundleItemInline]

@admin.register(StudentRequest)
class StudentRequestAdmin(admin.ModelAdmin):
    list_display = ['title', 'requester', 'category', 'max_budget', 'campus', 'status', 'created_at']
    list_filter = ['status', 'campus', 'category']
    search_fields = ['title', 'description', 'requester__username']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read']
    search_fields = ['title', 'user__username', 'message']

@admin.register(DigitalDownload)
class DigitalDownloadAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'download_count', 'last_downloaded_at']
    search_fields = ['product__title', 'user__username']

@admin.register(ServiceBooking)
class ServiceBookingAdmin(admin.ModelAdmin):
    list_display = ['service_product', 'client', 'provider', 'preferred_date', 'total_amount', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['service_product__title', 'client__username', 'provider__username']

admin.site.register(Cart)
admin.site.register(Wishlist)
admin.site.register(ElectronicsSpecification)
