from .models import Cart, Wishlist, Notification, Product, SemesterBundle

def global_context(request):
    cart_count = 0
    wishlist_count = 0
    unread_notifications_count = 0
    recent_notifications = []
    
    if request.user.is_authenticated:
        # Cart count
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart_count = cart.total_items
            
        # Wishlist count
        wishlist = Wishlist.objects.filter(user=request.user).first()
        if wishlist:
            wishlist_count = wishlist.total_items
            
        # Notifications
        user_notifications = Notification.objects.filter(user=request.user)
        unread_notifications_count = user_notifications.filter(is_read=False).count()
        recent_notifications = user_notifications.order_by('-created_at')[:5]
        
    # Campus List for campus selector
    default_campuses = [
        'All Campuses',
        'Tech University Main Campus',
        'Engineering Campus West',
        'City Science & Arts College',
        'South Medical & Lab Campus',
        'North Institute of Technology'
    ]
    
    # Campus Pulse items (5 most recent active items across products and bundles)
    recent_products = Product.objects.filter(is_available=True).order_by('-created_at')[:5]
    pulse_items = []
    for p in recent_products:
        badge_text = "Just Listed"
        if p.is_urgent:
            badge_text = "Urgent Moving-Out"
        elif p.product_type == 'DIGITAL':
            badge_text = "Digital Asset"
        elif p.product_type == 'SERVICE':
            badge_text = "Academic Service"
        elif p.buy_or_rent in ['RENT', 'BOTH']:
            badge_text = "Fast Rent"
            
        pulse_items.append({
            'badge': badge_text,
            'title': p.title,
            'price': p.price,
            'campus': p.campus,
            'url': f"/products/{p.slug}/",
            'type': p.product_type
        })
        
    selected_campus = request.session.get('selected_campus', 'All Campuses')
    
    return {
        'cart_count': cart_count,
        'wishlist_count': wishlist_count,
        'unread_notifications_count': unread_notifications_count,
        'recent_notifications': recent_notifications,
        'campus_list': default_campuses,
        'campus_pulse_items': pulse_items,
        'selected_campus': selected_campus,
    }
