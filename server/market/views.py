from django.shortcuts import render, redirect, get_object_or_404, Http404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from typing import List, Dict, Any, Optional
from .forms import ListingForm, NeedRequestForm, NeedOfferForm
from django.views import View
from .models import NeedRequest, NeedOffer, Listing
from .psudodeta import SAMPLE_PRODUCTS, SAMPLE_CATEGORIES
from django.views.generic import ListView, DetailView

from django.db.models import Q



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


class MarketView(ListView):
    model = Listing
    template_name = 'marketplace/products.html'
    context_object_name = 'products'
    paginate_by = 6

    # Translation dictionaries mapping query params to DB choices
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

    def get_queryset(self):
        qs = Listing.objects.filter(status=Listing.ListingStatus.ACTIVE)

        # 1. Extract query parameters
        category_slug = self.request.GET.get('category', '').strip().lower()
        type_filter = self.request.GET.get('type', '').strip().lower()
        condition_filter = self.request.GET.get('condition', '').strip().lower()
        search_query = self.request.GET.get('q', '').strip()

        # 2. Category filter
        if category_slug:
            qs = qs.filter(category__slug__iexact=category_slug)

        # 3. Listing Type filter using type_aliases
        if type_filter:
            target_type = self.type_aliases.get(type_filter, type_filter.upper())
            qs = qs.filter(listing_type=target_type)

        # 4. Condition filter using condition_aliases
        if condition_filter:
            target_condition = self.condition_aliases.get(condition_filter, condition_filter.upper())
            qs = qs.filter(condition=target_condition)

        # 5. Search query filter
        if search_query:
            qs = qs.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(location__icontains=search_query)
            )

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_category'] = self.request.GET.get('category', '').strip().lower()
        context['selected_type'] = self.request.GET.get('type', '').strip().lower()
        context['selected_condition'] = self.request.GET.get('condition', '').strip().lower()
        context['search_query'] = self.request.GET.get('q', '').strip()
        return context



class ProductDetailView(DetailView):
    model = Listing
    template_name = 'marketplace/product_detail.html'
    context_object_name = 'product'

    def get_object(self, queryset=None):
        # Extract identifier from URL parameters
        identifier = self.kwargs.get('pk')
            
        # 1. Attempt Database Query
        try:
            if identifier:
                product = Listing.objects.get(id=identifier)
                return product
            else:    
                return get_object_or_404(Listing, id=None)
        except Exception as e:
            messages.error(f"Error:{e}")
        



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

class NeedBoardListView(ListView):
    model = NeedRequest
    template_name = 'need_board/index.html'
    context_object_name = 'need_requests'
    paginate_by = 6

    def get_queryset(self):
        # 1. Base query with eager loading for optimization
        qs = NeedRequest.objects.select_related('requester', 'category').all()

        # 2. Extract GET filter parameters
        type_filter = self.request.GET.get('type', '').strip().upper()
        urgency_filter = self.request.GET.get('urgency', '').strip().upper()
        category_slug = self.request.GET.get('category', '').strip().lower()
        status_filter = self.request.GET.get('status', 'OPEN').strip().upper()
        search_query = self.request.GET.get('q', '').strip()

        # 3. Apply Status Filter
        if status_filter == 'ALL':
            pass
        elif status_filter == 'FULFILLED':
            qs = qs.filter(status=NeedRequest.Status.FULFILLED)
        elif status_filter == 'CLOSED':
            qs = qs.filter(status=NeedRequest.Status.CLOSED)
        else:
            qs = qs.filter(status=NeedRequest.Status.OPEN)

        # 4. Apply Type Filter
        if type_filter in NeedRequest.RequestType.values:
            qs = qs.filter(request_type=type_filter)

        # 5. Apply Urgency Filter
        if urgency_filter in NeedRequest.Urgency.values:
            qs = qs.filter(urgency=urgency_filter)

        # 6. Apply Category Filter
        if category_slug:
            qs = qs.filter(category__slug=category_slug)

        # 7. Apply Search Query
        if search_query:
            qs = qs.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(location__icontains=search_query) |
                Q(requester__username__icontains=search_query)
            )

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Live Campus Metrics
        try:
            total_open_count = NeedRequest.objects.filter(status=NeedRequest.Status.OPEN).count()
            urgent_count = NeedRequest.objects.filter(
                status=NeedRequest.Status.OPEN,
                urgency=NeedRequest.Urgency.URGENT
            ).count()
            fulfilled_count = NeedRequest.objects.filter(status=NeedRequest.Status.FULFILLED).count()
        except Exception:
            total_open_count, urgent_count, fulfilled_count = 0, 0, 0

        # Categories list
        try:
            categories_list = Category.objects.filter(is_active=True)
        except Exception:
            categories_list = []

        # Extract normalized filter params for UI context
        type_filter = self.request.GET.get('type', '').strip().upper()
        urgency_filter = self.request.GET.get('urgency', '').strip().upper()
        status_filter = self.request.GET.get('status', 'OPEN').strip().upper()

        context.update({
            'categories': categories_list,
            'selected_type': type_filter if type_filter in NeedRequest.RequestType.values else '',
            'selected_urgency': urgency_filter if urgency_filter in NeedRequest.Urgency.values else '',
            'selected_category': self.request.GET.get('category', '').strip().lower(),
            'selected_status': status_filter if status_filter in ['ALL', 'FULFILLED', 'CLOSED'] else 'OPEN',
            'search_query': self.request.GET.get('q', '').strip(),
            'total_open_count': total_open_count,
            'urgent_count': urgent_count,
            'fulfilled_count': fulfilled_count,
            'active_tab': 'requests',
        })
        return context


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

    paginator = Paginator(qs, 6)
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

@login_required
def toggle_wishlist(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)
    
    # get_or_create checks for existing Wishlist item or creates a new one
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        listing=listing
    )
    
    if not created:
        # If it already existed, remove it (toggle off)
        wishlist_item.delete()
        added = False
    else:
        added = True

    # If called via AJAX / Frontend JS
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'wishlisted': added})

    return redirect('market:product_id', id=listing.id)