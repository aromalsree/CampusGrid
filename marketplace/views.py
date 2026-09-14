import os
import mimetypes
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse, Http404, JsonResponse, FileResponse
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator
from django.utils import timezone
from django.conf import settings

from .models import (
    UserProfile, Category, Product, ProductImage, ElectronicsSpecification,
    Cart, CartItem, Wishlist, WishlistItem, Order, OrderItem,
    Rental, Review, Notification, Report, SemesterBundle, BundleItem,
    StudentRequest, DigitalDownload, ServiceBooking
)
from .forms import (
    UserRegistrationForm, UserProfileForm, ProductForm,
    ElectronicsSpecificationForm, SemesterBundleForm, StudentRequestForm,
    ReviewForm, ReportForm, RentalRequestForm, ServiceBookingForm, CheckoutForm
)
from .services import (
    compare_electronics_products, check_rental_conflict, build_whatsapp_inquiry_url
)

# --------------------------------------------------------------------------
# 1. HOMEPAGE & GLOBAL
# --------------------------------------------------------------------------
def index(request):
    selected_campus = request.session.get('selected_campus', 'All Campuses')
    
    products_qs = Product.objects.filter(is_available=True).select_related('category', 'seller', 'seller__profile')
    if selected_campus != 'All Campuses':
        products_qs = products_qs.filter(campus=selected_campus)
        
    featured_products = products_qs.filter(product_type='PHYSICAL')[:8]
    urgent_deals = products_qs.filter(is_urgent=True)[:6]
    semester_bundles = SemesterBundle.objects.filter(is_available=True)[:4]
    digital_assets = products_qs.filter(product_type='DIGITAL')[:4]
    academic_services = products_qs.filter(product_type='SERVICE')[:4]
    recent_requests = StudentRequest.objects.filter(status='OPEN')[:4]
    categories = Category.objects.filter(is_active=True)[:8]

    # Pre-select comparison teaser electronics items if available
    electronics_items = Product.objects.filter(
        electronics_spec__isnull=False, is_available=True
    ).select_related('electronics_spec')[:2]
    
    p1_teaser = electronics_items[0] if len(electronics_items) > 0 else None
    p2_teaser = electronics_items[1] if len(electronics_items) > 1 else None

    context = {
        'featured_products': featured_products,
        'urgent_deals': urgent_deals,
        'semester_bundles': semester_bundles,
        'digital_assets': digital_assets,
        'academic_services': academic_services,
        'recent_requests': recent_requests,
        'categories': categories,
        'p1_teaser': p1_teaser,
        'p2_teaser': p2_teaser,
    }
    return render(request, 'marketplace/index.html', context)


def set_campus(request):
    campus = request.GET.get('campus', 'All Campuses')
    request.session['selected_campus'] = campus
    next_url = request.GET.get('next', '/')
    return redirect(next_url)


# --------------------------------------------------------------------------
# 2. MARKETPLACE CATALOGUE & PRODUCT DETAIL
# --------------------------------------------------------------------------
def product_list(request):
    query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '')
    product_type = request.GET.get('type', '')
    buy_or_rent = request.GET.get('deal', '')
    condition = request.GET.get('condition', '')
    campus_filter = request.GET.get('campus', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    is_urgent = request.GET.get('urgent', '')
    verified_only = request.GET.get('verified', '')
    sort_by = request.GET.get('sort', 'newest')

    products = Product.objects.filter(is_available=True).select_related('category', 'seller', 'seller__profile')

    if query:
        products = products.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(campus__icontains=query) |
            Q(category__name__icontains=query)
        )

    if category_slug:
        products = products.filter(category__slug=category_slug)

    if product_type:
        products = products.filter(product_type=product_type)

    if buy_or_rent:
        if buy_or_rent == 'BUY':
            products = products.filter(buy_or_rent__in=['BUY', 'BOTH'])
        elif buy_or_rent == 'RENT':
            products = products.filter(buy_or_rent__in=['RENT', 'BOTH'])

    if condition:
        products = products.filter(condition=condition)

    if campus_filter and campus_filter != 'All Campuses':
        products = products.filter(campus=campus_filter)

    if min_price:
        try:
            products = products.filter(price__gte=Decimal(min_price))
        except:
            pass

    if max_price:
        try:
            products = products.filter(price__lte=Decimal(max_price))
        except:
            pass

    if is_urgent == '1':
        products = products.filter(is_urgent=True)

    if verified_only == '1':
        products = products.filter(seller__profile__verification_status='VERIFIED')

    # Sorting
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'popular':
        products = products.order_by('-views_count')
    else:
        products = products.order_by('-created_at')

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.filter(is_active=True)

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'query': query,
        'current_category': category_slug,
        'current_type': product_type,
        'current_deal': buy_or_rent,
        'current_condition': condition,
        'current_campus': campus_filter,
        'current_sort': sort_by,
        'min_price': min_price,
        'max_price': max_price,
        'is_urgent': is_urgent,
        'verified_only': verified_only,
        'total_count': paginator.count,
    }
    return render(request, 'marketplace/product_list.html', context)


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related('seller', 'seller__profile', 'category', 'electronics_spec')
        .prefetch_related('additional_images', 'reviews', 'reviews__reviewer', 'reviews__reviewer__profile'),
        slug=slug
    )
    
    # Increment view count
    Product.objects.filter(id=product.id).update(views_count=product.views_count + 1)

    # WhatsApp Link
    whatsapp_url = build_whatsapp_inquiry_url(product, request.user)

    # Check if user already reviewed
    user_has_reviewed = False
    is_buyer_or_renter = False
    if request.user.is_authenticated:
        user_has_reviewed = product.reviews.filter(reviewer=request.user).exists()
        has_ordered = OrderItem.objects.filter(order__buyer=request.user, product=product).exists()
        has_rented = Rental.objects.filter(renter=request.user, product=product, status__in=['ACTIVE', 'RETURNED']).exists()
        is_buyer_or_renter = has_ordered or has_rented

    # Related items
    related_products = Product.objects.filter(
        category=product.category, is_available=True
    ).exclude(id=product.id)[:4]

    # Review & Rental Forms
    review_form = ReviewForm()
    rental_form = RentalRequestForm()
    report_form = ReportForm()

    context = {
        'product': product,
        'whatsapp_url': whatsapp_url,
        'user_has_reviewed': user_has_reviewed,
        'is_buyer_or_renter': is_buyer_or_renter,
        'related_products': related_products,
        'review_form': review_form,
        'rental_form': rental_form,
        'report_form': report_form,
    }
    return render(request, 'marketplace/product_detail.html', context)


# --------------------------------------------------------------------------
# 3. SMART ELECTRONICS COMPARISON ENGINE
# --------------------------------------------------------------------------
def compare_view(request):
    p1_id = request.GET.get('p1')
    p2_id = request.GET.get('p2')

    comparison_data = None
    if p1_id and p2_id:
        comparison_data = compare_electronics_products(p1_id, p2_id)

    # Available electronics products for dropdown selectors
    all_electronics = Product.objects.filter(
        electronics_spec__isnull=False, is_available=True
    ).select_related('electronics_spec', 'seller')

    context = {
        'comparison': comparison_data,
        'all_electronics': all_electronics,
        'selected_p1_id': p1_id,
        'selected_p2_id': p2_id,
    }
    return render(request, 'marketplace/compare.html', context)


# --------------------------------------------------------------------------
# 4. CART & CHECKOUT
# --------------------------------------------------------------------------
@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('product', 'product__seller')

    context = {
        'cart': cart,
        'items': items,
    }
    return render(request, 'marketplace/cart.html', context)


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_available=True)
    
    # Self-purchase prevention
    if product.seller == request.user:
        messages.error(request, "You cannot purchase or add your own listing to cart.")
        return redirect('marketplace:product_detail', slug=product.slug)

    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        if product.product_type == 'PHYSICAL':
            cart_item.quantity += 1
            cart_item.save()
    messages.success(request, f"Added '{product.title}' to your cart!")

    next_url = request.GET.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('marketplace:cart_view')


@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product_title = cart_item.product.title
    cart_item.delete()
    messages.info(request, f"Removed '{product_title}' from your cart.")
    return redirect('marketplace:cart_view')


@login_required
def update_cart_quantity(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        try:
            qty = int(request.POST.get('quantity', 1))
            if qty > 0:
                cart_item.quantity = qty
                cart_item.save()
                messages.success(request, "Cart quantity updated.")
            else:
                cart_item.delete()
                messages.info(request, "Item removed from cart.")
        except ValueError:
            pass
    return redirect('marketplace:cart_view')


@login_required
def checkout_view(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or cart.items.count() == 0:
        messages.warning(request, "Your cart is currently empty.")
        return redirect('marketplace:product_list')

    user_profile = getattr(request.user, 'profile', None)

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            total = cart.total_price
            order = Order.objects.create(
                buyer=request.user,
                total_amount=total,
                payment_method=form.cleaned_data['payment_method'],
                payment_status='COMPLETED' if form.cleaned_data['payment_method'] == 'RAZORPAY' else 'PENDING',
                order_status='PLACED',
                full_name=form.cleaned_data['full_name'],
                phone=form.cleaned_data['phone'],
                campus=form.cleaned_data['campus'],
                delivery_location_notes=form.cleaned_data['delivery_location_notes'],
            )

            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_title=item.product.title,
                    price_at_purchase=item.product.price,
                    quantity=item.quantity,
                    is_rental=item.is_rental,
                    item_type=item.product.product_type
                )
                if item.product.product_type == 'DIGITAL':
                    DigitalDownload.objects.create(
                        user=request.user,
                        product=item.product,
                        order=order
                    )
                Notification.objects.create(
                    user=item.product.seller,
                    notification_type='ORDER',
                    title=f"New Order Placed for {item.product.title}!",
                    message=f"Student {request.user.username} placed order #{order.order_number} for ₹{item.product.price}.",
                    link=f"/orders/{order.id}/"
                )

            cart.items.all().delete()

            Notification.objects.create(
                user=request.user,
                notification_type='ORDER',
                title=f"Order #{order.order_number} Confirmed!",
                message=f"Your order for ₹{order.total_amount:,.2f} has been placed successfully.",
                link=f"/orders/{order.id}/"
            )

            messages.success(request, f"Order #{order.order_number} successfully placed!")
            return redirect('marketplace:order_detail', order_id=order.id)
    else:
        initial_data = {
            'full_name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
            'phone': user_profile.phone_number if user_profile else '',
            'campus': user_profile.campus if user_profile else '',
        }
        form = CheckoutForm(initial=initial_data)

    context = {
        'cart': cart,
        'form': form,
        'razorpay_key': settings.RAZORPAY_KEY_ID,
    }
    return render(request, 'marketplace/checkout.html', context)


# --------------------------------------------------------------------------
# 5. ORDERS & RENTALS
# --------------------------------------------------------------------------
@login_required
def orders_list(request):
    orders = Order.objects.filter(buyer=request.user).prefetch_related('items', 'items__product')
    incoming_orders = Order.objects.filter(items__product__seller=request.user).distinct()
    
    context = {
        'orders': orders,
        'incoming_orders': incoming_orders,
    }
    return render(request, 'marketplace/orders.html', context)


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order.objects.prefetch_related('items', 'items__product'), id=order_id)
    
    is_buyer = order.buyer == request.user
    is_seller = order.items.filter(product__seller=request.user).exists()
    is_admin = request.user.is_staff

    if not (is_buyer or is_seller or is_admin):
        messages.error(request, "You are not authorized to view this order.")
        return redirect('marketplace:orders_list')

    context = {
        'order': order,
        'is_buyer': is_buyer,
        'is_seller': is_seller,
    }
    return render(request, 'marketplace/order_detail.html', context)


@login_required
def rent_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_available=True)

    if product.seller == request.user:
        messages.error(request, "You cannot rent your own product.")
        return redirect('marketplace:product_detail', slug=product.slug)

    if not product.allows_rental or not product.rent_daily_rate:
        messages.error(request, "This product is not eligible for rental.")
        return redirect('marketplace:product_detail', slug=product.slug)

    if request.method == 'POST':
        form = RentalRequestForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']

            if end_date < start_date:
                messages.error(request, "Return date cannot be earlier than start date.")
                return redirect('marketplace:product_detail', slug=product.slug)

            if check_rental_conflict(product, start_date, end_date):
                messages.error(request, "This item is already booked for the selected date range. Please select another slot.")
                return redirect('marketplace:product_detail', slug=product.slug)

            days = max((end_date - start_date).days + 1, 1)
            total_rent = product.rent_daily_rate * days

            rental = Rental.objects.create(
                product=product,
                renter=request.user,
                owner=product.seller,
                start_date=start_date,
                end_date=end_date,
                daily_rate=product.rent_daily_rate,
                total_rent=total_rent,
                status='REQUESTED',
                notes=form.cleaned_data['notes']
            )

            Notification.objects.create(
                user=product.seller,
                notification_type='RENTAL',
                title=f"Rental Request for {product.title}",
                message=f"Student {request.user.username} requested rental from {start_date} to {end_date} (₹{total_rent}).",
                link="/seller/"
            )

            messages.success(request, f"Rental request submitted to {product.seller.username} for ₹{total_rent} ({days} days)!")
            return redirect('marketplace:rentals_list')

    return redirect('marketplace:product_detail', slug=product.slug)


@login_required
def rentals_list(request):
    my_rentals = Rental.objects.filter(renter=request.user).select_related('product', 'owner')
    received_rentals = Rental.objects.filter(owner=request.user).select_related('product', 'renter')

    context = {
        'my_rentals': my_rentals,
        'received_rentals': received_rentals,
    }
    return render(request, 'marketplace/rentals.html', context)


@login_required
def update_rental_status(request, rental_id):
    rental = get_object_or_404(Rental, id=rental_id)
    if rental.owner != request.user and not request.user.is_staff:
        messages.error(request, "Unauthorized to change rental status.")
        return redirect('marketplace:rentals_list')

    new_status = request.POST.get('status')
    valid_transitions = dict(Rental.RENTAL_STATUSES).keys()
    if new_status in valid_transitions:
        rental.status = new_status
        rental.save()

        Notification.objects.create(
            user=rental.renter,
            notification_type='RENTAL',
            title=f"Rental Status Updated: {rental.product.title}",
            message=f"Your rental status is now: {rental.get_status_display()}.",
            link="/rentals/"
        )
        messages.success(request, f"Rental status changed to '{rental.get_status_display()}'.")
    return redirect('marketplace:rentals_list')


# --------------------------------------------------------------------------
# 6. WISHLIST
# --------------------------------------------------------------------------
@login_required
def wishlist_view(request):
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    items = wishlist.items.select_related('product', 'product__seller', 'product__category')

    context = {
        'wishlist': wishlist,
        'items': items,
    }
    return render(request, 'marketplace/wishlist.html', context)


@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)

    item = WishlistItem.objects.filter(wishlist=wishlist, product=product).first()
    if item:
        item.delete()
        added = False
        msg = f"Removed '{product.title}' from wishlist."
    else:
        WishlistItem.objects.create(wishlist=wishlist, product=product)
        added = True
        msg = f"Added '{product.title}' to wishlist!"

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'added': added, 'message': msg, 'total_count': wishlist.total_items})

    messages.info(request, msg)
    next_url = request.GET.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('marketplace:wishlist_view')


@login_required
def digital_download_view(request, slug):
    product = get_object_or_404(Product, slug=slug, product_type='DIGITAL')

    is_owner = product.seller == request.user
    has_purchased = OrderItem.objects.filter(
        order__buyer=request.user,
        product=product,
        order__payment_status='COMPLETED'
    ).exists()

    if not (is_owner or has_purchased or request.user.is_staff):
        messages.error(request, "Protected Content: You must complete purchase for this digital asset before downloading.")
        return redirect('marketplace:product_detail', slug=product.slug)

    if not product.digital_file:
        raise Http404("Digital file is currently being processed by the seller.")

    download_log, _ = DigitalDownload.objects.get_or_create(
        user=request.user, product=product
    )
    download_log.download_count += 1
    download_log.save()

    file_path = product.digital_file.path
    if not os.path.exists(file_path):
        raise Http404("Digital asset file not found on disk.")

    mime_type, _ = mimetypes.guess_type(file_path)
    response = FileResponse(open(file_path, 'rb'), content_type=mime_type or 'application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
    return response


# --------------------------------------------------------------------------
# 8. SEMESTER BUNDLES & STUDENT REQUESTS
# --------------------------------------------------------------------------
def semester_bundles_list(request):
    bundles = SemesterBundle.objects.filter(is_available=True).prefetch_related('items', 'seller', 'seller__profile')
    context = {'bundles': bundles}
    return render(request, 'marketplace/bundles.html', context)


def bundle_detail(request, slug):
    bundle = get_object_or_404(SemesterBundle.objects.prefetch_related('items', 'seller', 'seller__profile'), slug=slug)
    context = {'bundle': bundle}
    return render(request, 'marketplace/bundle_detail.html', context)


@login_required
def create_bundle(request):
    if request.method == 'POST':
        form = SemesterBundleForm(request.POST, request.FILES)
        if form.is_valid():
            bundle = form.save(commit=False)
            bundle.seller = request.user
            bundle.save()
            messages.success(request, f"Semester Bundle '{bundle.title}' published successfully!")
            return redirect('marketplace:bundle_detail', slug=bundle.slug)
    else:
        form = SemesterBundleForm()
    return render(request, 'marketplace/add_bundle.html', {'form': form})


@login_required
def edit_bundle(request, bundle_id):
    bundle = get_object_or_404(SemesterBundle, id=bundle_id, seller=request.user)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_item':
            item_title = request.POST.get('item_title')
            item_type = request.POST.get('item_type', 'TEXTBOOK')
            if item_title:
                BundleItem.objects.create(bundle=bundle, title=item_title, item_type=item_type)
                messages.success(request, f"Added '{item_title}' to bundle.")
            return redirect('marketplace:edit_bundle', bundle_id=bundle.id)
        elif action == 'remove_item':
            item_id = request.POST.get('item_id')
            BundleItem.objects.filter(id=item_id, bundle=bundle).delete()
            messages.info(request, "Item removed from bundle.")
            return redirect('marketplace:edit_bundle', bundle_id=bundle.id)
        else:
            form = SemesterBundleForm(request.POST, request.FILES, instance=bundle)
            if form.is_valid():
                form.save()
                messages.success(request, f"Bundle '{bundle.title}' updated successfully!")
                return redirect('marketplace:bundle_detail', slug=bundle.slug)
    else:
        form = SemesterBundleForm(instance=bundle)
    return render(request, 'marketplace/edit_bundle.html', {'bundle': bundle, 'form': form})


@login_required
def delete_bundle(request, bundle_id):
    bundle = get_object_or_404(SemesterBundle, id=bundle_id, seller=request.user)
    if request.method == 'POST':
        title = bundle.title
        bundle.delete()
        messages.success(request, f"Semester bundle '{title}' was deleted.")
        return redirect('marketplace:semester_bundles_list')
    return redirect('marketplace:bundle_detail', slug=bundle.slug)


def student_requests_list(request):
    requests_qs = StudentRequest.objects.all().select_related('requester', 'requester__profile', 'category')
    
    campus = request.GET.get('campus')
    if campus and campus != 'All Campuses':
        requests_qs = requests_qs.filter(campus=campus)
        
    context = {
        'requests': requests_qs,
        'form': StudentRequestForm(),
    }
    return render(request, 'marketplace/requests.html', context)


@login_required
def create_request(request):
    if request.method == 'POST':
        form = StudentRequestForm(request.POST)
        if form.is_valid():
            req = form.save(commit=False)
            req.requester = request.user
            req.save()
            messages.success(request, "Your request was published on the Student Need Board!")
            return redirect('marketplace:student_requests_list')
    return redirect('marketplace:student_requests_list')


@login_required
def close_student_request(request, request_id):
    req = get_object_or_404(StudentRequest, id=request_id, requester=request.user)
    if request.method == 'POST':
        req.status = request.POST.get('status', 'CLOSED')
        req.save()
        messages.info(request, f"Request '{req.title}' marked as {req.get_status_display()}.")
    return redirect('marketplace:student_requests_list')


# --------------------------------------------------------------------------
# 9. ACADEMIC SERVICES & BOOKINGS
# --------------------------------------------------------------------------
@login_required
def book_service_session(request, product_id):
    product = get_object_or_404(Product, id=product_id, product_type='SERVICE', is_available=True)

    if product.seller == request.user:
        messages.error(request, "You cannot book your own academic service.")
        return redirect('marketplace:product_detail', slug=product.slug)

    if request.method == 'POST':
        form = ServiceBookingForm(request.POST)
        if form.is_valid():
            hours = form.cleaned_data['estimated_hours']
            rate_type = product.service_rate_type or 'FLAT'
            if rate_type == 'PER_HOUR':
                total = product.price * hours
            else:
                total = product.price

            booking = ServiceBooking.objects.create(
                service_product=product,
                client=request.user,
                provider=product.seller,
                preferred_date=form.cleaned_data['preferred_date'],
                preferred_time=form.cleaned_data['preferred_time'],
                rate_type=rate_type,
                estimated_hours=hours,
                total_amount=total,
                client_notes=form.cleaned_data['client_notes']
            )

            Notification.objects.create(
                user=product.seller,
                notification_type='SYSTEM',
                title=f"New Mentorship/Service Booking Request!",
                message=f"Student {request.user.username} requested a session for '{product.title}' on {booking.preferred_date}.",
                link="/seller/"
            )

            messages.success(request, f"Session booking request submitted to {product.seller.username}!")
            return redirect('marketplace:product_detail', slug=product.slug)
    return redirect('marketplace:product_detail', slug=product.slug)


# --------------------------------------------------------------------------
# 10. REVIEWS & REPORTS
# --------------------------------------------------------------------------
@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if product.seller == request.user:
        messages.error(request, "You cannot review your own listing.")
        return redirect('marketplace:product_detail', slug=product.slug)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review, created = Review.objects.update_or_create(
                product=product,
                reviewer=request.user,
                defaults={
                    'rating': form.cleaned_data['rating'],
                    'comment': form.cleaned_data['comment'],
                    'is_verified_purchase': True,
                }
            )
            Notification.objects.create(
                user=product.seller,
                notification_type='REVIEW',
                title=f"New {review.rating}★ Review for {product.title}",
                message=f"{request.user.username} wrote a review: '{review.comment[:50]}...'",
                link=f"/products/{product.slug}/"
            )
            messages.success(request, "Your review has been submitted!")
    return redirect('marketplace:product_detail', slug=product.slug)


@login_required
def report_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if product.seller == request.user:
        messages.error(request, "You cannot report your own listing.")
        return redirect('marketplace:product_detail', slug=product.slug)

    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.product = product
            report.save()
            messages.success(request, "Report submitted for admin review. Thank you for keeping CampusGrid safe.")
    return redirect('marketplace:product_detail', slug=product.slug)


# --------------------------------------------------------------------------
# 11. NOTIFICATIONS
# --------------------------------------------------------------------------
@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    context = {'notifications': notifications}
    return render(request, 'marketplace/notifications.html', context)


@login_required
def mark_notification_read(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id, user=request.user)
    notif.is_read = True
    notif.save()
    if notif.link:
        return redirect(notif.link)
    return redirect('marketplace:notifications_view')


@login_required
def mark_all_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    messages.success(request, "All notifications marked as read.")
    return redirect('marketplace:notifications_view')


# --------------------------------------------------------------------------
# 12. DASHBOARD & SELLER CONTROL CENTER
# --------------------------------------------------------------------------
@login_required
def dashboard(request):
    user_campus = request.user.profile.campus if hasattr(request.user, 'profile') else 'Main Campus'
    orders_count = Order.objects.filter(buyer=request.user).count()
    rentals_count = Rental.objects.filter(renter=request.user).count()
    wishlist_count = Wishlist.objects.filter(user=request.user).first()
    wishlist_items_count = wishlist_count.total_items if wishlist_count else 0
    requests_count = StudentRequest.objects.filter(requester=request.user).count()
    downloads_count = DigitalDownload.objects.filter(user=request.user).count()

    recent_orders = Order.objects.filter(buyer=request.user)[:5]
    active_rentals = Rental.objects.filter(renter=request.user, status__in=['APPROVED', 'ACTIVE'])

    # Rich marketplace recommendations for dashboard
    recommended_products = Product.objects.filter(is_available=True).exclude(seller=request.user).select_related('category', 'seller')[:6]
    trending_products = Product.objects.filter(is_available=True, product_type='PHYSICAL').select_related('category', 'seller')[:4]
    urgent_deals = Product.objects.filter(is_available=True, is_urgent=True).select_related('category', 'seller')[:3]
    recent_bundles = SemesterBundle.objects.filter(is_available=True).select_related('seller')[:3]
    recent_requests = StudentRequest.objects.filter(status='OPEN').select_related('requester')[:3]
    digital_assets = Product.objects.filter(is_available=True, product_type='DIGITAL').select_related('seller')[:3]
    electronics_compare = Product.objects.filter(is_available=True, electronics_spec__isnull=False).select_related('electronics_spec')[:2]

    context = {
        'orders_count': orders_count,
        'rentals_count': rentals_count,
        'wishlist_items_count': wishlist_items_count,
        'requests_count': requests_count,
        'downloads_count': downloads_count,
        'recent_orders': recent_orders,
        'active_rentals': active_rentals,
        'recommended_products': recommended_products,
        'trending_products': trending_products,
        'urgent_deals': urgent_deals,
        'recent_bundles': recent_bundles,
        'recent_requests': recent_requests,
        'digital_assets': digital_assets,
        'electronics_compare': electronics_compare,
        'user_campus': user_campus,
    }
    return render(request, 'marketplace/dashboard.html', context)


@login_required
def seller_dashboard(request):
    my_products = Product.objects.filter(seller=request.user)
    total_listings = my_products.count()
    active_listings = my_products.filter(is_available=True).count()
    
    completed_items = OrderItem.objects.filter(
        product__seller=request.user, order__order_status='COMPLETED'
    )
    total_sales_revenue = sum(item.subtotal for item in completed_items)
    
    rental_revenue = sum(
        r.total_rent for r in Rental.objects.filter(owner=request.user, status__in=['APPROVED', 'ACTIVE', 'RETURNED'])
    )
    total_revenue = total_sales_revenue + rental_revenue

    incoming_orders = Order.objects.filter(items__product__seller=request.user).distinct()[:5]
    pending_rentals = Rental.objects.filter(owner=request.user, status='REQUESTED')
    service_bookings = ServiceBooking.objects.filter(provider=request.user).order_by('-created_at')[:5]

    context = {
        'my_products': my_products,
        'products': my_products,
        'total_listings': total_listings,
        'active_listings': active_listings,
        'total_revenue': total_revenue,
        'incoming_orders': incoming_orders,
        'pending_rentals': pending_rentals,
        'service_bookings': service_bookings,
    }
    return render(request, 'marketplace/seller_dashboard.html', context)


@login_required
def add_product(request):
    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES)
        spec_form = ElectronicsSpecificationForm(request.POST)

        if product_form.is_valid():
            product = product_form.save(commit=False)
            product.seller = request.user
            if not product.campus and hasattr(request.user, 'profile'):
                product.campus = request.user.profile.campus
            product.save()

            # Additional gallery images
            additional_files = request.FILES.getlist('additional_images')
            for f in additional_files:
                ProductImage.objects.create(product=product, image=f)

            # Check if electronics specs provided
            has_processor = bool(request.POST.get('processor'))
            if has_processor and spec_form.is_valid():
                spec = spec_form.save(commit=False)
                spec.product = product
                spec.save()

            messages.success(request, f"Listing '{product.title}' created successfully!")
            return redirect('marketplace:product_detail', slug=product.slug)
    else:
        product_form = ProductForm()
        spec_form = ElectronicsSpecificationForm()

    return render(request, 'marketplace/add_product.html', {
        'form': product_form,
        'product_form': product_form,
        'spec_form': spec_form,
    })


@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    spec_instance = getattr(product, 'electronics_spec', None)

    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES, instance=product)
        spec_form = ElectronicsSpecificationForm(request.POST, instance=spec_instance)

        if product_form.is_valid():
            product_form.save()
            
            additional_files = request.FILES.getlist('additional_images')
            for f in additional_files:
                ProductImage.objects.create(product=product, image=f)

            has_processor = bool(request.POST.get('processor'))
            if has_processor:
                if spec_form.is_valid():
                    spec = spec_form.save(commit=False)
                    spec.product = product
                    spec.save()
            messages.success(request, f"Updated '{product.title}' successfully!")
            return redirect('marketplace:product_detail', slug=product.slug)
    else:
        product_form = ProductForm(instance=product)
        spec_form = ElectronicsSpecificationForm(instance=spec_instance) if spec_instance else ElectronicsSpecificationForm()

    return render(request, 'marketplace/edit_product.html', {
        'product': product,
        'form': product_form,
        'product_form': product_form,
        'spec_form': spec_form,
    })


@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    if request.method == 'POST':
        title = product.title
        product.delete()
        messages.success(request, f"Listing '{title}' was deleted successfully.")
    return redirect('marketplace:seller_dashboard')


@login_required
def delete_product_image(request, image_id):
    img = get_object_or_404(ProductImage, id=image_id, product__seller=request.user)
    product_id = img.product.id
    if request.method == 'POST':
        img.delete()
        messages.info(request, "Image removed from gallery.")
    return redirect('marketplace:edit_product', product_id=product_id)


@login_required
def toggle_product_availability(request, product_id):
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    if request.method == 'POST' or request.GET.get('confirm') == '1':
        product.is_available = not product.is_available
        product.save()
        status_str = "Available" if product.is_available else "Deactivated"
        messages.info(request, f"Product '{product.title}' marked as {status_str}.")
    return redirect('marketplace:seller_dashboard')


# --------------------------------------------------------------------------
# 13. AUTHENTICATION & PROFILE
# --------------------------------------------------------------------------
def register_view(request):
    if request.user.is_authenticated:
        return redirect('marketplace:dashboard')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            profile = user.profile
            profile.campus = form.cleaned_data['campus']
            profile.phone_number = form.cleaned_data['phone_number']
            profile.whatsapp_number = form.cleaned_data['whatsapp_number']
            profile.save()

            login(request, user)

            if profile.is_pending_verification:
                messages.success(request, f"Welcome {user.username}! Academic email detected — verification request submitted.")
            else:
                messages.success(request, f"Welcome to CampusGrid, {user.username}!")
            return redirect('marketplace:dashboard')
    else:
        form = UserRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('marketplace:dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            next_url = request.GET.get('next', 'marketplace:dashboard')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been successfully signed out.")
    return redirect('marketplace:login')


@login_required
def user_profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            request.user.first_name = form.cleaned_data.get('first_name', '')
            request.user.last_name = form.cleaned_data.get('last_name', '')
            request.user.save()
            messages.success(request, "Your profile was updated successfully!")
            return redirect('marketplace:user_profile')
    else:
        initial = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        }
        form = UserProfileForm(instance=profile, initial=initial)

    context = {
        'profile': profile,
        'form': form,
    }
    return render(request, 'marketplace/profile.html', context)


# --------------------------------------------------------------------------
# 14. ADMIN & MODERATION
# --------------------------------------------------------------------------
@login_required
def moderation_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, "Access restricted to administrators.")
        return redirect('marketplace:dashboard')

    pending_verifications = UserProfile.objects.filter(verification_status='PENDING')
    reports = Report.objects.filter(status__in=['PENDING', 'REVIEWING'])

    context = {
        'pending_verifications': pending_verifications,
        'pending_reports': reports,
        'reports': reports,
    }
    return render(request, 'marketplace/moderation.html', context)


@login_required
def admin_approve_verification(request, profile_id):
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('marketplace:dashboard')

    profile = get_object_or_404(UserProfile, id=profile_id)
    profile.verification_status = 'VERIFIED'
    profile.save()

    Notification.objects.create(
        user=profile.user,
        notification_type='VERIFICATION',
        title="Student Verification Approved! 🎓",
        message="Congratulations! Your student credentials have been verified. You now display the Verified Student badge.",
        link="/profile/"
    )
    messages.success(request, f"Verified student status approved for {profile.user.username}!")
    return redirect('marketplace:moderation_dashboard')


@login_required
def admin_resolve_report(request, report_id):
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('marketplace:dashboard')

    report = get_object_or_404(Report, id=report_id)
    action = request.POST.get('action') or request.GET.get('action_type') or request.GET.get('action')

    if action in ['resolve_disable', 'DEACTIVATE_PRODUCT', 'deactivate']:
        report.status = 'RESOLVED'
        report.admin_notes = "Listing disabled due to violation."
        report.product.is_available = False
        report.product.save()
        messages.warning(request, f"Report resolved: Listing '{report.product.title}' has been disabled.")
    elif action in ['reject', 'DISMISS', 'dismiss']:
        report.status = 'REJECTED'
        report.admin_notes = "No violation detected."
        messages.info(request, f"Report on '{report.product.title}' marked as dismissed.")
    
    report.save()
    return redirect('marketplace:moderation_dashboard')

