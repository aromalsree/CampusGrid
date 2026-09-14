import urllib.parse
from decimal import Decimal
from django.db.models import Q
from .models import Product, ElectronicsSpecification, Rental

def compare_electronics_products(product1_id, product2_id):
    """
    Compares two electronics products and calculates objective specification winners.
    Returns comparison matrix context with winner badges.
    """
    p1_id = product1_id.id if hasattr(product1_id, 'id') else product1_id
    p2_id = product2_id.id if hasattr(product2_id, 'id') else product2_id
    try:
        p1 = Product.objects.select_related('electronics_spec', 'seller', 'seller__profile', 'category').get(id=p1_id)
        p2 = Product.objects.select_related('electronics_spec', 'seller', 'seller__profile', 'category').get(id=p2_id)
    except (Product.DoesNotExist, ValueError, TypeError):
        return None

    spec1 = getattr(p1, 'electronics_spec', None)
    spec2 = getattr(p2, 'electronics_spec', None)

    # Comparison matrix rows
    matrix = []

    # 1. Price comparison (Lower is better)
    p1_price_win = p1.price < p2.price
    p2_price_win = p2.price < p1.price
    matrix.append({
        'feature': 'Price (INR)',
        'val1': f"₹{p1.price:,.2f}",
        'val2': f"₹{p2.price:,.2f}",
        'win1': p1_price_win,
        'win2': p2_price_win,
        'badge1': '✓ Lower Price' if p1_price_win else None,
        'badge2': '✓ Lower Price' if p2_price_win else None,
    })

    # Condition map
    cond_order = {'LIKE_NEW': 3, 'GOOD': 2, 'FAIR': 1, 'NOT_APPLICABLE': 0}
    c1_score = cond_order.get(p1.condition, 0)
    c2_score = cond_order.get(p2.condition, 0)
    matrix.append({
        'feature': 'Condition',
        'val1': p1.get_condition_display(),
        'val2': p2.get_condition_display(),
        'win1': c1_score > c2_score,
        'win2': c2_score > c1_score,
        'badge1': '✓ Mint Condition' if c1_score > c2_score else None,
        'badge2': '✓ Mint Condition' if c2_score > c1_score else None,
    })

    if spec1 and spec2:
        # Processor
        matrix.append({
            'feature': 'Processor',
            'val1': spec1.processor,
            'val2': spec2.processor,
            'win1': False,
            'win2': False,
            'badge1': None,
            'badge2': None,
        })

        # RAM
        r1_win = spec1.ram_gb > spec2.ram_gb
        r2_win = spec2.ram_gb > spec1.ram_gb
        matrix.append({
            'feature': 'RAM Memory',
            'val1': f"{spec1.ram_gb} GB",
            'val2': f"{spec2.ram_gb} GB",
            'win1': r1_win,
            'win2': r2_win,
            'badge1': '✓ More RAM' if r1_win else None,
            'badge2': '✓ More RAM' if r2_win else None,
        })

        # Storage
        s1_win = spec1.storage_gb > spec2.storage_gb
        s2_win = spec2.storage_gb > spec1.storage_gb
        matrix.append({
            'feature': 'Storage Capacity',
            'val1': f"{spec1.storage_gb} GB ({spec1.get_storage_type_display()})",
            'val2': f"{spec2.storage_gb} GB ({spec2.get_storage_type_display()})",
            'win1': s1_win,
            'win2': s2_win,
            'badge1': '✓ Higher Storage' if s1_win else None,
            'badge2': '✓ Higher Storage' if s2_win else None,
        })

        # Battery Health
        b1_win = spec1.battery_health_percent > spec2.battery_health_percent
        b2_win = spec2.battery_health_percent > spec1.battery_health_percent
        matrix.append({
            'feature': 'Battery Health Capacity',
            'val1': f"{spec1.battery_health_percent}%",
            'val2': f"{spec2.battery_health_percent}%",
            'win1': b1_win,
            'win2': b2_win,
            'badge1': '✓ Better Battery Health' if b1_win else None,
            'badge2': '✓ Better Battery Health' if b2_win else None,
        })

        # Usage Duration (Lower is newer/better)
        u1_win = spec1.usage_duration_months < spec2.usage_duration_months
        u2_win = spec2.usage_duration_months < spec1.usage_duration_months
        matrix.append({
            'feature': 'Usage Duration',
            'val1': f"{spec1.usage_duration_months} months",
            'val2': f"{spec2.usage_duration_months} months",
            'win1': u1_win,
            'win2': u2_win,
            'badge1': '✓ Less Used' if u1_win else None,
            'badge2': '✓ Less Used' if u2_win else None,
        })

        # Display
        matrix.append({
            'feature': 'Display & Resolution',
            'val1': spec1.display_specs,
            'val2': spec2.display_specs,
            'win1': False,
            'win2': False,
            'badge1': None,
            'badge2': None,
        })

        # OS
        matrix.append({
            'feature': 'Operating System',
            'val1': spec1.operating_system,
            'val2': spec2.operating_system,
            'win1': False,
            'win2': False,
            'badge1': None,
            'badge2': None,
        })

    # Summary score calculation
    p1_total_wins = sum(1 for row in matrix if row['win1'])
    p2_total_wins = sum(1 for row in matrix if row['win2'])

    return {
        'p1': p1,
        'p2': p2,
        'spec1': spec1,
        'spec2': spec2,
        'matrix': matrix,
        'p1_wins': p1_total_wins,
        'p2_wins': p2_total_wins,
    }


def check_rental_conflict(product, start_date, end_date, exclude_rental_id=None):
    """
    Checks if a product has conflicting approved/active rentals during the target date window.
    Accounts for all active blocking states: APPROVED, ACTIVE, RETURN_DUE.
    """
    product_obj = Product.objects.get(id=product) if isinstance(product, int) else product
    conflicting = Rental.objects.filter(
        product=product_obj,
        status__in=['APPROVED', 'ACTIVE', 'RETURN_DUE'],
        start_date__lte=end_date,
        end_date__gte=start_date
    )
    if exclude_rental_id:
        conflicting = conflicting.exclude(id=exclude_rental_id)
    return conflicting.exists()


def build_whatsapp_inquiry_url(product, request_user=None, custom_msg=None):
    """
    Builds a pre-filled WhatsApp click-to-chat URL without exposing raw contact unnecessarily.
    """
    seller_profile = getattr(product.seller, 'profile', None)
    if not seller_profile or not seller_profile.whatsapp_number:
        return None
        
    clean_number = "".join(filter(str.isdigit, seller_profile.whatsapp_number))
    if not clean_number:
        return None
        
    buyer_name = request_user.username if request_user and request_user.is_authenticated else "Campus Student"
    
    if custom_msg:
        text = custom_msg
    elif product.product_type == 'SERVICE':
        text = f"Hi {product.seller.username}, I am {buyer_name} on CampusGrid. I am interested in booking your academic service: '{product.title}' (Rate: ₹{product.price}). Are you available?"
    elif product.allows_rental:
        text = f"Hi {product.seller.username}, I saw your listing '{product.title}' on CampusGrid. Is it available for rent/buy at {product.campus}?"
    else:
        text = f"Hi {product.seller.username}, I am {buyer_name} on CampusGrid. I am interested in purchasing your listing '{product.title}' listed for ₹{product.price}."
        
    encoded_text = urllib.parse.quote(text)
    return f"https://wa.me/{clean_number}?text={encoded_text}"
