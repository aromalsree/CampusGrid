from django.shortcuts import render, redirect, get_object_or_404, Http404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from typing import List, Dict, Any, Optional
from .forms import ListingForm
from .psudodeta import SAMPLE_PRODUCTS, SAMPLE_CATEGORIES



def _get_active_products():
    """
    Returns active database listings together with the sample catalog so demo
    products remain available alongside real student listings.
    """
    try:
        from .models import Listing
        qs = Listing.objects.filter(
            status=Listing.ListingStatus.ACTIVE
        ).select_related('seller', 'category').prefetch_related('images')
        return list(qs) + SAMPLE_PRODUCTS
    except Exception:
        return list(SAMPLE_PRODUCTS)


def _get_active_categories():
    """
    Attempts to query Category model if defined in market.models,
    otherwise falls back gracefully to SAMPLE_CATEGORIES.
    """
    try:
        from .models import Category
        qs = Category.objects.filter(is_active=True)
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
    condition_filter = request.GET.get('condition', '').strip().lower()
    search_query = request.GET.get('q', '').strip().lower()
    page_number = request.GET.get('page', 1)

    type_aliases = {
        'sell': 'SALE',
        'sale': 'SALE',
        'rental': 'RENT',
        'rent': 'RENT',
        'service': 'SERVICE',
        'digital': 'DIGITAL',
    }
    condition_aliases = {
        'brand_new': 'NEW',
        'new': 'NEW',
        'like_new': 'LIKE_NEW',
        'good': 'GOOD',
        'fair': 'FAIR',
        'poor': 'POOR',
    }
    normalized_type = type_aliases.get(type_filter, '')
    normalized_condition = condition_aliases.get(condition_filter, '')

    raw_products = _get_active_products()

    filtered_products = []
    for product in raw_products:
        if hasattr(product, 'category'):
            product_category = product.category.slug
            product_type = str(product.listing_type).lower()
            product_condition = str(product.condition).lower()
            title = product.title.lower()
            desc = product.description.lower()
            location = product.location.lower()
        else:
            product_category = product.get('category', '')
            if isinstance(product_category, dict):
                product_category = product_category.get('slug', '')
            elif hasattr(product_category, 'slug'):
                product_category = product_category.slug
            product_type = str(product.get('listing_type', '')).lower()
            product_condition = str(product.get('condition', '')).lower()
            title = product.get('title', '').lower()
            desc = product.get('description', '').lower()
            location = product.get('campus', '').lower()

        if category_filter and str(product_category).lower() != category_filter:
            continue
        if type_filter and product_type not in {type_filter, normalized_type.lower()}:
            continue
        if condition_filter and product_condition not in {condition_filter, normalized_condition.lower()}:
            continue
        if search_query and search_query not in title and search_query not in desc and search_query not in location:
            continue
        filtered_products.append(product)

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
    item1 = None
    item2 = None
    all_products = []

    try:
        from .models import Listing
        all_products = list(Listing.objects.filter(status=Listing.ListingStatus.ACTIVE).order_by('title'))
        if item1_id:
            item1 = Listing.objects.filter(pk=int(item1_id)).first() if str(item1_id).isdigit() else Listing.objects.filter(slug=item1_id).first()
        if item2_id:
            item2 = Listing.objects.filter(pk=int(item2_id)).first() if str(item2_id).isdigit() else Listing.objects.filter(slug=item2_id).first()
    except Exception:
        pass

    if not all_products:
        all_products = _get_active_products()

    context = {
        'all_products': all_products,
        'item1_id': item1_id,
        'item2_id': item2_id,
        'item1': item1,
        'item2': item2,
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


from .models import NeedRequest, NeedOffer
from .forms import NeedRequestForm, NeedOfferForm


def need_board_view(request):
    """
    Publicly browsable Campus Need Board (Reverse Marketplace).
    Displays student requests to buy, borrow, or find tutoring/gear.
    """
    type_filter = request.GET.get('type', '').strip().upper()
    urgency_filter = request.GET.get('urgency', '').strip().upper()
    category_slug = request.GET.get('category', '').strip().lower()
    status_filter = request.GET.get('status', 'OPEN').strip().upper()
    search_query = request.GET.get('q', '').strip()
    page_number = request.GET.get('page', 1)

    qs = NeedRequest.objects.select_related('requester', 'category').all()

    # Status filter (defaults to open needs unless user explicitly asks for all or fulfilled)
    if status_filter == 'ALL':
        pass
    elif status_filter == 'FULFILLED':
        qs = qs.filter(status=NeedRequest.Status.FULFILLED)
    elif status_filter == 'CLOSED':
        qs = qs.filter(status=NeedRequest.Status.CLOSED)
    else:
        status_filter = 'OPEN'
        qs = qs.filter(status=NeedRequest.Status.OPEN)

    # Type filter (BUY, BORROW, SERVICE)
    if type_filter in NeedRequest.RequestType.values:
        qs = qs.filter(request_type=type_filter)
    else:
        type_filter = ''

    # Urgency filter (URGENT, MODERATE, FLEXIBLE)
    if urgency_filter in NeedRequest.Urgency.values:
        qs = qs.filter(urgency=urgency_filter)
    else:
        urgency_filter = ''

    # Category filter
    if category_slug:
        qs = qs.filter(category__slug=category_slug)

    # Search keyword
    if search_query:
        from django.db.models import Q
        qs = qs.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(requester__username__icontains=search_query)
        )

    # Live Campus Metrics
    try:
        total_open_count = NeedRequest.objects.filter(status=NeedRequest.Status.OPEN).count()
        urgent_count = NeedRequest.objects.filter(
            status=NeedRequest.Status.OPEN,
            urgency=NeedRequest.Urgency.URGENT
        ).count()
        fulfilled_count = NeedRequest.objects.filter(status=NeedRequest.Status.FULFILLED).count()
    except Exception:
        total_open_count = 0
        urgent_count = 0
        fulfilled_count = 0

    paginator = Paginator(qs, 9)
    page_obj = paginator.get_page(page_number)

    categories_list = []
    try:
        categories_list = Category.objects.filter(is_active=True)
    except Exception:
        pass

    context = {
        'need_requests': page_obj.object_list,
        'page_obj': page_obj,
        'categories': categories_list,
        'selected_type': type_filter,
        'selected_urgency': urgency_filter,
        'selected_category': category_slug,
        'selected_status': status_filter,
        'search_query': search_query,
        'total_open_count': total_open_count,
        'urgent_count': urgent_count,
        'fulfilled_count': fulfilled_count,
        'active_tab': 'requests',
    }
    return render(request, 'need_board/index.html', context)


@login_required
def create_need_request(request):
    """
    Allows authenticated students to post a new item or service request.
    """
    if request.method == 'POST':
        form = NeedRequestForm(request.POST)
        if form.is_valid():
            need_request = form.save(commit=False)
            need_request.requester = request.user
            need_request.save()
            messages.success(
                request,
                f"Your request '{need_request.title}' is now live on the Campus Need Board!"
            )
            return redirect('market:need_request_detail', pk=need_request.pk)
        else:
            messages.error(request, "Please correct the errors in the form below.")
    else:
        form = NeedRequestForm()

    return render(request, 'need_board/create.html', {
        'form': form,
        'active_tab': 'requests',
    })


def need_request_detail(request, pk):
    """
    Detailed view of a single student need request with peer offers and contact methods.
    """
    need_request = get_object_or_404(
        NeedRequest.objects.select_related('requester', 'category'),
        pk=pk
    )
    offers = need_request.offers.select_related('responder').order_by('-created_at')
    offer_form = NeedOfferForm()

    return render(request, 'need_board/detail.html', {
        'need_request': need_request,
        'offers': offers,
        'offer_form': offer_form,
        'active_tab': 'requests',
    })


@login_required
def toggle_need_status(request, pk):
    """
    Allows the request owner to mark their request as FULFILLED or reopen as OPEN.
    """
    need_request = get_object_or_404(NeedRequest, pk=pk, requester=request.user)

    if request.method == 'POST':
        action = request.POST.get('action', '')
        if action == 'reopen':
            need_request.status = NeedRequest.Status.OPEN
            messages.info(request, f"Request '{need_request.title}' has been reopened.")
        else:
            need_request.status = NeedRequest.Status.FULFILLED
            messages.success(request, f"Awesome! '{need_request.title}' marked as fulfilled.")
        need_request.save()

    return redirect('market:need_request_detail', pk=need_request.pk)


@login_required
def create_need_offer(request, pk):
    """
    Allows campus peers to submit an offer or note to the requester.
    """
    need_request = get_object_or_404(NeedRequest, pk=pk)

    if request.method == 'POST':
        form = NeedOfferForm(request.POST)
        if form.is_valid():
            offer = form.save(commit=False)
            offer.need_request = need_request
            offer.responder = request.user
            offer.save()
            messages.success(
                request,
                f"Your response has been sent to {need_request.requester.username}! They can now reach out to you."
            )
        else:
            messages.error(request, "Please provide a valid message for your offer.")

    return redirect('market:need_request_detail', pk=need_request.pk)


