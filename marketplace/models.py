from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.db.models import Avg
import uuid

protected_storage = FileSystemStorage(location=getattr(settings, 'PROTECTED_MEDIA_ROOT', settings.BASE_DIR / 'protected_media'))

class UserProfile(models.Model):
    VERIFICATION_CHOICES = [
        ('UNVERIFIED', 'Unverified'),
        ('PENDING', 'Pending Verification'),
        ('VERIFIED', 'Verified Student'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    campus = models.CharField(max_length=200, default='Tech University Campus', help_text="User's College/University Campus")
    phone_number = models.CharField(max_length=20, blank=True, help_text="Contact number")
    whatsapp_number = models.CharField(max_length=20, blank=True, help_text="WhatsApp contact number (with country code e.g. 919876543210)")
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_CHOICES, default='UNVERIFIED')
    is_seller = models.BooleanField(default=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(blank=True, max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_verification_status_display()})"

    @property
    def is_verified_student(self):
        return self.verification_status == 'VERIFIED'

    @property
    def is_pending_verification(self):
        return self.verification_status == 'PENDING'

    def get_whatsapp_number_clean(self):
        if not self.whatsapp_number:
            return ""
        return "".join(c for c in self.whatsapp_number if c.isdigit())


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    icon = models.CharField(max_length=50, default='package', help_text="Lucide icon name (e.g. laptop, smartphone, book-open, zap, cpu, gamepad-2, home)")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def active_products_count(self):
        return self.products.filter(is_available=True).count()


class Product(models.Model):
    PRODUCT_TYPES = [
        ('PHYSICAL', 'Physical Product'),
        ('DIGITAL', 'Digital Asset / Notes'),
        ('SERVICE', 'Academic Service'),
    ]

    CONDITIONS = [
        ('LIKE_NEW', 'Like New (Mint)'),
        ('GOOD', 'Good (Minor wear)'),
        ('FAIR', 'Fair (Functional)'),
        ('NOT_APPLICABLE', 'Not Applicable'),
    ]

    BUY_OR_RENT_CHOICES = [
        ('BUY', 'Buy Only'),
        ('RENT', 'Rent Only'),
        ('BOTH', 'Buy or Rent'),
    ]

    SERVICE_RATE_TYPES = [
        ('FLAT', 'Flat Session Rate'),
        ('PER_HOUR', 'Hourly Rate'),
    ]

    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Selling price or base service fee in INR (₹)")
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPES, default='PHYSICAL')
    condition = models.CharField(max_length=20, choices=CONDITIONS, default='GOOD')
    campus = models.CharField(max_length=200, default='Main Campus')
    
    # Rental features
    buy_or_rent = models.CharField(max_length=10, choices=BUY_OR_RENT_CHOICES, default='BUY')
    rent_daily_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Daily rental rate in INR (₹)")
    rent_monthly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Monthly rental rate in INR (₹)")
    
    # Status flags
    is_available = models.BooleanField(default=True)
    is_urgent = models.BooleanField(default=False, help_text="Urgent Moving-Out Clearance deal")
    
    # Media & Files
    primary_image = models.ImageField(upload_to='products/', blank=True, null=True)
    digital_file = models.FileField(storage=protected_storage, upload_to='digital_assets/', blank=True, null=True, help_text="Protected asset file (ZIP, PDF, Code)")
    sample_preview_pdf = models.FileField(upload_to='samples/', blank=True, null=True, help_text="Safe preview sample for buyers")
    
    # Service fields
    service_rate_type = models.CharField(max_length=20, choices=SERVICE_RATE_TYPES, blank=True, null=True)
    service_duration_info = models.CharField(max_length=100, blank=True, help_text="e.g. 1 hour session / Full Semester Guidance")
    
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            unique_str = uuid.uuid4().hex[:6]
            self.slug = f"{base_slug}-{unique_str}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def is_electronics(self):
        return hasattr(self, 'electronics_spec') and self.electronics_spec is not None

    @property
    def average_rating(self):
        avg = self.reviews.aggregate(avg=Avg('rating'))['avg']
        return round(avg, 1) if avg else 0.0

    @property
    def review_count(self):
        return self.reviews.count()

    @property
    def allows_rental(self):
        return self.buy_or_rent in ['RENT', 'BOTH']

    @property
    def allows_purchase(self):
        return self.buy_or_rent in ['BUY', 'BOTH']


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='additional_images')
    image = models.ImageField(upload_to='products/')
    caption = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.product.title}"


class ElectronicsSpecification(models.Model):
    STORAGE_TYPES = [
        ('NVME_SSD', 'NVMe SSD'),
        ('SSD', 'SATA SSD'),
        ('HDD', 'Hard Disk Drive'),
        ('UFS', 'UFS Fast Flash'),
        ('EMMC', 'eMMC'),
    ]

    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='electronics_spec')
    processor = models.CharField(max_length=150, help_text="e.g. Apple M1 8-Core / Intel Core i7-1185G7")
    ram_gb = models.PositiveIntegerField(help_text="RAM in Gigabytes (e.g. 8, 16, 32)")
    storage_gb = models.PositiveIntegerField(help_text="Storage in Gigabytes (e.g. 256, 512, 1024)")
    storage_type = models.CharField(max_length=20, choices=STORAGE_TYPES, default='NVME_SSD')
    battery_health_percent = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        default=90,
        help_text="Battery Maximum Capacity % (1-100)"
    )
    usage_duration_months = models.PositiveIntegerField(default=12, help_text="Used duration in months")
    display_specs = models.CharField(max_length=200, help_text="e.g. 13.3-inch Retina Display (2560x1600)")
    graphics = models.CharField(max_length=150, blank=True, help_text="e.g. Integrated Apple 7-Core / NVIDIA RTX 3050")
    operating_system = models.CharField(max_length=100, default='macOS / Windows 11')
    extra_specs = models.TextField(blank=True, help_text="Ports, charger included, cycle count, warranty status")

    def __str__(self):
        return f"Specs for {self.product.title}"


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        return sum(item.item_total for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    is_rental = models.BooleanField(default=False)
    rental_days = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity}x {self.product.title} in Cart"

    @property
    def item_total(self):
        if self.is_rental and self.product.rent_daily_rate:
            return self.product.rent_daily_rate * self.rental_days * self.quantity
        return self.product.price * self.quantity


class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wishlist')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Wishlist of {self.user.username}"

    @property
    def total_items(self):
        return self.items.count()


class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('wishlist', 'product')

    def __str__(self):
        return f"{self.product.title} on {self.wishlist.user.username}'s Wishlist"


class Order(models.Model):
    PAYMENT_METHODS = [
        ('COD', 'Cash on Campus Handover (COD)'),
        ('RAZORPAY', 'Razorpay Secure Payment'),
    ]

    PAYMENT_STATUSES = [
        ('PENDING', 'Pending Payment'),
        ('COMPLETED', 'Payment Completed'),
        ('FAILED', 'Payment Failed'),
    ]

    ORDER_STATUSES = [
        ('PLACED', 'Order Placed'),
        ('CONFIRMED', 'Confirmed by Seller'),
        ('READY', 'Ready for Pickup / Handover'),
        ('COMPLETED', 'Completed & Handed Over'),
        ('CANCELLED', 'Cancelled'),
    ]

    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=50, unique=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='COD')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUSES, default='PENDING')
    order_status = models.CharField(max_length=20, choices=ORDER_STATUSES, default='PLACED')
    
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    campus = models.CharField(max_length=200)
    delivery_location_notes = models.TextField(blank=True, help_text="Hostel room, campus library, cafeteria, etc.")
    
    razorpay_order_id = models.CharField(max_length=100, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"CG-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.order_number} by {self.buyer.username}"

    @property
    def has_digital_items(self):
        return self.items.filter(item_type='DIGITAL').exists()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    product_title = models.CharField(max_length=255)
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    is_rental = models.BooleanField(default=False)
    item_type = models.CharField(max_length=20, default='PHYSICAL')

    def __str__(self):
        return f"{self.quantity}x {self.product_title} in Order #{self.order.order_number}"

    @property
    def subtotal(self):
        return self.price_at_purchase * self.quantity


class Rental(models.Model):
    RENTAL_STATUSES = [
        ('REQUESTED', 'Rental Requested'),
        ('APPROVED', 'Approved by Owner'),
        ('ACTIVE', 'Active / In Possession'),
        ('RETURN_DUE', 'Return Due Soon'),
        ('RETURNED', 'Successfully Returned'),
        ('CANCELLED', 'Cancelled'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='rentals')
    renter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rentals_made')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rentals_received')
    start_date = models.DateField()
    end_date = models.DateField()
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2)
    total_rent = models.DecimalField(max_digits=10, decimal_places=2)
    deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=RENTAL_STATUSES, default='REQUESTED')
    notes = models.TextField(blank=True, help_text="Handover notes / condition check")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Rental of {self.product.title} to {self.renter.username}"

    @property
    def duration_days(self):
        return max((self.end_date - self.start_date).days + 1, 1)


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_written')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    is_verified_purchase = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'reviewer')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.rating}★ review for {self.product.title} by {self.reviewer.username}"


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('ORDER', 'Order Notification'),
        ('RENTAL', 'Rental Notification'),
        ('VERIFICATION', 'Verification Update'),
        ('MATCHING_REQUEST', 'Matching Request Found'),
        ('REVIEW', 'Review Received'),
        ('DIGITAL_READY', 'Digital Asset Ready'),
        ('SYSTEM', 'System Announcement'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES, default='SYSTEM')
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.notification_type}] {self.title} -> {self.user.username}"


class Report(models.Model):
    REPORT_REASONS = [
        ('FAKE', 'Fake or Counterfeit Product'),
        ('SCAM', 'Potential Scam / Overpriced Fraud'),
        ('INCORRECT', 'Incorrect Specification / Misleading'),
        ('DUPLICATE', 'Spam / Duplicate Listing'),
        ('INAPPROPRIATE', 'Inappropriate Content / Harassment'),
        ('OTHER', 'Other Violation'),
    ]

    REPORT_STATUSES = [
        ('PENDING', 'Pending Admin Review'),
        ('REVIEWING', 'Under Review'),
        ('RESOLVED', 'Resolved (Action Taken)'),
        ('REJECTED', 'Rejected (No Violation)'),
    ]

    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_filed')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reports')
    reason = models.CharField(max_length=30, choices=REPORT_REASONS)
    details = models.TextField()
    status = models.CharField(max_length=20, choices=REPORT_STATUSES, default='PENDING')
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Report #{self.id} on {self.product.title} ({self.get_status_display()})"


class SemesterBundle(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bundles')
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    semester = models.CharField(max_length=100, help_text="e.g. 5th Semester / 3rd Semester")
    course = models.CharField(max_length=150, help_text="e.g. BCA / B.Tech CSE / Mechanical")
    campus = models.CharField(max_length=200, default='Main Campus')
    cover_image = models.ImageField(upload_to='bundles/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = f"{slugify(self.title)}-{uuid.uuid4().hex[:6]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class BundleItem(models.Model):
    ITEM_TYPES = [
        ('BOOK', 'Textbook'),
        ('NOTES', 'Handwritten / Printed Notes'),
        ('LAB_TOOL', 'Lab Equipment / Drafter Kit'),
        ('DIGITAL', 'Digital Study Material / Code'),
        ('OTHER', 'Study Aid / Calculator'),
    ]

    bundle = models.ForeignKey(SemesterBundle, on_delete=models.CASCADE, related_name='items')
    title = models.CharField(max_length=200)
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES, default='BOOK')
    notes = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.title} ({self.get_item_type_display()})"


class StudentRequest(models.Model):
    STATUS_CHOICES = [
        ('OPEN', 'Open Request'),
        ('MATCHED', 'Potential Seller Found'),
        ('CLOSED', 'Closed / Fulfilled'),
    ]

    CONTACT_PREFERENCES = [
        ('WHATSAPP', 'WhatsApp Direct Message'),
        ('IN_APP', 'CampusGrid In-App / Email'),
    ]

    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_requests')
    title = models.CharField(max_length=255, help_text="e.g. Need 5th Sem DBMS textbook under ₹400")
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    max_budget = models.DecimalField(max_digits=10, decimal_places=2, help_text="Maximum budget in INR (₹)")
    campus = models.CharField(max_length=200, default='Main Campus')
    contact_preference = models.CharField(max_length=20, choices=CONTACT_PREFERENCES, default='WHATSAPP')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} by {self.requester.username} (₹{self.max_budget})"


class DigitalDownload(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='digital_downloads')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='downloads')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    download_count = models.PositiveIntegerField(default=0)
    last_downloaded_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Download of {self.product.title} by {self.user.username}"


class ServiceBooking(models.Model):
    BOOKING_STATUSES = [
        ('REQUESTED', 'Session Requested'),
        ('ACCEPTED', 'Accepted by Mentor/Tutor'),
        ('SCHEDULED', 'Scheduled'),
        ('COMPLETED', 'Session Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    service_product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='service_bookings')
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings_requested')
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings_received')
    preferred_date = models.DateField()
    preferred_time = models.CharField(max_length=50, help_text="e.g. 4:00 PM - 5:00 PM")
    rate_type = models.CharField(max_length=20, default='FLAT')
    estimated_hours = models.PositiveIntegerField(default=1)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    client_notes = models.TextField(blank=True, help_text="Topics, problem statement, repository link")
    status = models.CharField(max_length=20, choices=BOOKING_STATUSES, default='REQUESTED')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Booking for {self.service_product.title} by {self.client.username}"

