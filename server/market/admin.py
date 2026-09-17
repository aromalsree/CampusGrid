from django.contrib import admin
from .models import Category, Listing, ListingImage, Wishlist, NeedRequest, NeedOffer


class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('is_active',)
    search_fields = ('name', 'description')


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'seller', 'category', 'listing_type', 'price', 'status', 'is_urgent', 'created_at')
    list_filter = ('status', 'listing_type', 'is_urgent', 'is_negotiable', 'category')
    search_fields = ('title', 'description', 'location', 'seller__username', 'seller__email')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ListingImageInline]
    date_hierarchy = 'created_at'


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'listing', 'created_at')
    search_fields = ('user__username', 'listing__title')


class NeedOfferInline(admin.TabularInline):
    model = NeedOffer
    extra = 0
    readonly_fields = ('created_at',)


@admin.register(NeedRequest)
class NeedRequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'requester', 'category', 'request_type', 'urgency', 'max_budget', 'status', 'created_at')
    list_filter = ('status', 'urgency', 'request_type', 'category')
    search_fields = ('title', 'description', 'location', 'requester__username', 'requester__email')
    inlines = [NeedOfferInline]
    date_hierarchy = 'created_at'


@admin.register(NeedOffer)
class NeedOfferAdmin(admin.ModelAdmin):
    list_display = ('need_request', 'responder', 'offered_price', 'created_at')
    search_fields = ('need_request__title', 'responder__username', 'message')
