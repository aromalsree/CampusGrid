from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, Cart, Wishlist, Product, StudentRequest, Notification

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        email = instance.email.lower()
        # Academic email detection (.edu, .ac.in, etc.)
        is_academic = email.endswith('.edu') or '.ac.in' in email or '.edu.' in email or email.endswith('.edu.in')
        status = 'PENDING' if is_academic else 'UNVERIFIED'
        
        UserProfile.objects.get_or_create(
            user=instance,
            defaults={
                'verification_status': status,
                'campus': 'Tech University Campus'
            }
        )
        Cart.objects.get_or_create(user=instance)
        Wishlist.objects.get_or_create(user=instance)

@receiver(post_save, sender=Product)
def match_product_with_student_requests(sender, instance, created, **kwargs):
    if created and instance.is_available:
        # Look for open requests matching category or title keyword
        matching_requests = StudentRequest.objects.filter(
            status='OPEN',
            max_budget__gte=instance.price
        )
        if instance.category:
            matching_requests = matching_requests.filter(category=instance.category)
            
        for req in matching_requests[:5]:
            if req.requester != instance.seller:
                Notification.objects.create(
                    user=req.requester,
                    notification_type='MATCHING_REQUEST',
                    title=f"New Match for Your Request: {req.title[:30]}...",
                    message=f"A new item '{instance.title}' was just listed for ₹{instance.price}, matching your budget request!",
                    link=f"/products/{instance.slug}/"
                )
