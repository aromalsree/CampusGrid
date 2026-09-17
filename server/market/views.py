from django.shortcuts import render, redirect, get_object_or_404, Http404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from typing import List, Dict, Any, Optional
from .forms import ListingForm



def _get_active_products():
    """
    Attempts to query the Product model if defined in market.models,
    otherwise falls back gracefully to SAMPLE_PRODUCTS.
    """
    try:
        from .models import Product
        qs = Product.objects.all()
        if qs.exists():
            return qs
    except Exception:
        pass
    return SAMPLE_PRODUCTS


def _get_active_categories():
    """
    Attempts to query Category model if defined in market.models,
    otherwise falls back gracefully to SAMPLE_CATEGORIES.
    """
    try:
        from .models import Category
        qs = Category.objects.all()
        if qs.exists():
            return qs
    except Exception:
        pass
    return SAMPLE_CATEGORIES


def product_list(request):
    """
    Renders the marketplace catalogue (templates/marketplace/products.html)
    with support for category filtering, listing type filtering, search queries,
    and pagination.
    """
    category_filter = request.GET.get('category', '').strip().lower()
    type_filter = request.GET.get('type', '').strip().lower()
    search_query = request.GET.get('q', '').strip().lower()
    page_number = request.GET.get('page', 1)

    raw_products = _get_active_products()

    # If raw_products is a Django QuerySet
    if hasattr(raw_products, 'filter'):
        qs = raw_products
        if category_filter:
            qs = qs.filter(category__iexact=category_filter)
        if type_filter:
            qs = qs.filter(listing_type__iexact=type_filter)
        if search_query:
            from django.db.models import Q
            qs = qs.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(campus__icontains=search_query)
            )
        filtered_products = list(qs)
    else:
        # Working with dictionary items
        filtered_products = []
        for p in raw_products:
            # Category filter
            if category_filter and p.get('category', '').lower() != category_filter:
                continue
            # Listing type filter (e.g. 'sell', 'rental')
            if type_filter and p.get('listing_type', '').lower() != type_filter:
                continue
            # Search filter
            if search_query:
                title = p.get('title', '').lower()
                desc = p.get('description', '').lower()
                campus = p.get('campus', '').lower()
                if search_query not in title and search_query not in desc and search_query not in campus:
                    continue
            filtered_products.append(p)

    paginator = Paginator(filtered_products, 6)
    page_obj = paginator.get_page(page_number)

    context = {
        'products': page_obj.object_list,
        'page_obj': page_obj,
        'selected_category': category_filter,
        'selected_type': type_filter,
        'search_query': search_query,
    }
    return render(request, 'marketplace/products.html', context)


def product_detail(request, slug_or_id=None, pk=None, slug=None):
    """
    Renders individual product details (templates/marketplace/product_detail.html).
    Resolves product by primary key or slug.
    """
    identifier = str(pk or slug or slug_or_id or '').strip()

    # Attempt to query database if model is present
    try:
        from .models import Product
        if identifier.isdigit():
            product = Product.objects.filter(pk=int(identifier)).first()
        else:
            product = Product.objects.filter(slug=identifier).first()
        if product:
            return render(request, 'marketplace/product_detail.html', {'product': product})
    except Exception:
        pass

    # Search in sample products
    product = None
    for p in SAMPLE_PRODUCTS:
        if str(p.get('id')) == identifier or str(p.get('slug')) == identifier:
            product = p
            break

    # Fallback to the first sample product if not found or identifier is empty
    if not product and SAMPLE_PRODUCTS:
        product = SAMPLE_PRODUCTS[0]

    return render(request, 'marketplace/product_detail.html', {'product': product})


def categories(request):
    """
    Renders the categories index (templates/marketplace/categories.html).
    """
    active_categories = _get_active_categories()
    return render(request, 'marketplace/categories.html', {'categories': active_categories})


def compare(request):
    """
    Renders the hardware comparison engine (templates/marketplace/compare.html).
    """
    item1_id = request.GET.get('item1')
    item2_id = request.GET.get('item2')
    context = {
        'item1_id': item1_id,
        'item2_id': item2_id,
    }
    return render(request, 'marketplace/compare.html', context)


@login_required
def create_listing(request):
    """
    Renders and processes the create listing form for authenticated students.
    Saves the listing with the logged-in user as the seller, handles image
    uploads via ListingImage if provided, and redirects on success.
    """
    if request.method == "POST":
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.seller = request.user
            listing.save()
            form.save_m2m()

            # Process optional image uploads (via ListingImage)
            uploaded_images = request.FILES.getlist("images") or request.FILES.getlist("image")
            if uploaded_images:
                try:
                    from .models import ListingImage
                    for i, img_file in enumerate(uploaded_images):
                        ListingImage.objects.create(
                            listing=listing,
                            image=img_file,
                            is_primary=(i == 0)
                        )
                except Exception:
                    pass

            messages.success(request, f"Listing '{listing.title}' published successfully!")

            # Safe redirect hierarchy: product_detail -> products catalogue -> home
            try:
                return redirect("market:product_detail", slug_or_id=listing.slug or listing.id)
            except Exception:
                pass
            try:
                return redirect("market:products")
            except Exception:
                pass
            return redirect("home")
        else:
            messages.error(request, "Please correct the errors below to publish your listing.")
    else:
        form = ListingForm()

    return render(
        request,
        "marketplace/product_listing.html",
        {"form": form}
    )


# Aliases for convenience and flexible routing
products = product_list
catalogue = product_list
product_detail_view = product_detail
category_list = categories
compare_view = compare
add_listing = create_listing
post_listing = create_listing

