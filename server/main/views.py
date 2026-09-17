from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.utils import timezone
from django.contrib import messages
from datetime import timedelta

User = get_user_model()


def home(request):
    featured_products = []
    categories = []
    listing_count = 0
    try:
        from market.models import Listing, Category
        featured_products = Listing.objects.filter(
            status=Listing.ListingStatus.ACTIVE
        ).select_related('seller', 'category').prefetch_related('images').order_by('-created_at')[:6]
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


# for testing html pls use the test view
def test(request):
    return render(request, "dashboard/wishlist.html")