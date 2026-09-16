from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Category(models.Model):
    """
    Marketplace category for grouping student listings (e.g. Electronics, Books, Notes).
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "market"
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Listing(models.Model):
    """
    Primary campus marketplace listing representing an item, rental, service, or digital resource.
    """
    class ListingType(models.TextChoices):
        SALE = "SALE", "For Sale"
        RENT = "RENT", "For Rent"
        SERVICE = "SERVICE", "Academic Service"
        DIGITAL = "DIGITAL", "Digital Asset"

    class ListingStatus(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        ACTIVE = "ACTIVE", "Active"
        RESERVED = "RESERVED", "Reserved"
        SOLD = "SOLD", "Sold"
        RENTED = "RENTED", "Rented"
        EXPIRED = "EXPIRED", "Expired"
        CANCELLED = "CANCELLED", "Cancelled"

    class Condition(models.TextChoices):
        NEW = "NEW", "Brand New"
        LIKE_NEW = "LIKE_NEW", "Like New"
        GOOD = "GOOD", "Good"
        FAIR = "FAIR", "Fair"
        POOR = "POOR", "Poor"

    class RentalPeriod(models.TextChoices):
        DAY = "DAY", "Per Day"
        MONTH = "MONTH", "Per Month"
        SEMESTER = "SEMESTER", "Per Semester"

    # Core Relationships
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="listings"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="listings"
    )

    # Descriptive Content
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField()

    # Pricing & Modality
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))]
    )
    listing_type = models.CharField(
        max_length=20,
        choices=ListingType.choices,
        default=ListingType.SALE,
        db_index=True
    )
    condition = models.CharField(
        max_length=20,
        choices=Condition.choices,
        blank=True
    )
    rental_period = models.CharField(
        max_length=20,
        choices=RentalPeriod.choices,
        blank=True
    )

    # Campus & Handover Logistics
    location = models.CharField(
        max_length=150,
        blank=True,
        help_text="Campus building, department, or handover spot"
    )
    is_negotiable = models.BooleanField(default=False)
    is_urgent = models.BooleanField(default=False, db_index=True)

    # Lifecycle & Timestamps
    status = models.CharField(
        max_length=20,
        choices=ListingStatus.choices,
        default=ListingStatus.ACTIVE,
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "market"
        verbose_name = "Listing"
        verbose_name_plural = "Listings"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["category", "status"]),
            models.Index(fields=["seller", "status"]),
            models.Index(fields=["price"]),
        ]

    def __str__(self):
        return f"{self.title} - {self.price}"

    @property
    def primary_image(self):
        """Returns the primary image or first available image for the listing."""
        primary = self.images.filter(is_primary=True).first()
        if primary and primary.image:
            return primary.image
        first = self.images.first()
        return first.image if first and first.image else None


class ListingImage(models.Model):
    """
    Multiple photo attachments for a marketplace listing.
    """
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="images"
    )
    image = models.ImageField(upload_to="listings/images/")
    is_primary = models.BooleanField(default=False)
    alt_text = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "market"
        verbose_name = "Listing Image"
        verbose_name_plural = "Listing Images"
        ordering = ["-is_primary", "created_at"]

    def __str__(self):
        label = "Primary" if self.is_primary else "Additional"
        return f"Image for {self.listing.title} ({label})"


class Wishlist(models.Model):
    """
    User bookmarking / saving listings to their campus wishlist.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlist_items"
    )
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="wishlisted_by"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "market"
        verbose_name = "Wishlist Item"
        verbose_name_plural = "Wishlist Items"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "listing"],
                name="unique_user_listing_wishlist"
            )
        ]

    def __str__(self):
        return f"{self.user} -> {self.listing.title}"


# Backward-compatibility / semantic alias
Product = Listing
