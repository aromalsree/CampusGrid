import datetime
from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError

from marketplace.models import (
    UserProfile, Category, Product, ProductImage, ElectronicsSpecification,
    Cart, CartItem, Wishlist, WishlistItem, Order, OrderItem, Rental,
    StudentRequest, Notification, Review, Report, SemesterBundle, BundleItem,
    DigitalDownload, ServiceBooking
)
from marketplace.services import (
    compare_electronics_products, check_rental_conflict, build_whatsapp_inquiry_url
)
from marketplace.forms import ProductForm


class CampusGridMasterTestSuite(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Users
        self.buyer = User.objects.create_user(
            username="buyer_student",
            email="buyer@university.edu",
            password="password123"
        )
        self.seller = User.objects.create_user(
            username="seller_student",
            email="seller@university.edu",
            password="password123"
        )
        self.seller.profile.whatsapp_number = "919876543210"
        self.seller.profile.save()

        self.staff_admin = User.objects.create_user(
            username="admin_user",
            email="admin@campusgrid.edu",
            password="adminpassword",
            is_staff=True
        )

        # Categories
        self.cat_laptops = Category.objects.create(name="Laptops & Electronics", slug="laptops-electronics")
        self.cat_notes = Category.objects.create(name="Study Notes & Digital Assets", slug="notes-digital-assets")
        self.cat_services = Category.objects.create(name="Academic Services", slug="academic-services")

        # Sample Physical Product with Electronics Specs
        self.laptop = Product.objects.create(
            seller=self.seller,
            category=self.cat_laptops,
            title="MacBook Air M1",
            price=Decimal('55000.00'),
            product_type="PHYSICAL",
            buy_or_rent="BOTH",
            rent_daily_rate=Decimal('300.00'),
            condition="LIKE_NEW",
            campus="IIT Bombay",
            is_available=True
        )
        self.laptop_spec = ElectronicsSpecification.objects.create(
            product=self.laptop,
            processor="Apple M1",
            ram_gb=8,
            storage_gb=256,
            storage_type="NVME_SSD",
            battery_health_percent=94,
            usage_duration_months=12,
            display_specs="13.3-inch Retina",
            operating_system="macOS"
        )

        # Sample Digital Product
        dummy_file = SimpleUploadedFile("notes.pdf", b"%PDF-1.4 dummy content", content_type="application/pdf")
        self.digital_product = Product.objects.create(
            seller=self.seller,
            category=self.cat_notes,
            title="DSA Master Notes",
            price=Decimal('199.00'),
            product_type="DIGITAL",
            buy_or_rent="BUY",
            condition="NOT_APPLICABLE",
            campus="IIT Bombay",
            digital_file=dummy_file,
            is_available=True
        )

    # 1. Registration & Academic Email Detection
    def test_registration_and_academic_email_detection(self):
        resp = self.client.post(reverse('marketplace:register'), {
            'username': 'new_student',
            'email': 'new.student@college.edu',
            'first_name': 'New',
            'last_name': 'Student',
            'campus': 'IIT Delhi',
            'phone_number': '9876543210',
            'whatsapp_number': '9876543210',
            'password': 'safe_password_123',
            'confirm_password': 'safe_password_123',
        }, follow=True)
        self.assertEqual(resp.status_code, 200)
        u = User.objects.get(username='new_student')
        self.assertTrue(hasattr(u, 'profile'))
        self.assertTrue(hasattr(u, 'cart'))
        self.assertTrue(hasattr(u, 'wishlist'))
        self.assertEqual(u.profile.verification_status, 'PENDING')

    # 2. Login & Logout
    def test_login_and_logout_flow(self):
        login_resp = self.client.post(reverse('marketplace:login'), {
            'username': 'buyer_student',
            'password': 'password123'
        }, follow=True)
        self.assertEqual(login_resp.status_code, 200)
        self.assertTrue(login_resp.context['user'].is_authenticated)

        logout_resp = self.client.post(reverse('marketplace:logout'), follow=True)
        self.assertEqual(logout_resp.status_code, 200)
        self.assertFalse(logout_resp.context['user'].is_authenticated)

    # 3. Password Reset Route Config
    def test_password_reset_routes_accessible(self):
        resp = self.client.get(reverse('marketplace:password_reset'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'registration/password_reset_form.html')

    # 4. Product Creation & Editing (Physical, Digital, Service)
    def test_create_and_edit_service_product(self):
        self.client.login(username="seller_student", password="password123")
        create_resp = self.client.post(reverse('marketplace:add_product'), {
            'title': 'Peer Code Review Mentorship',
            'category': self.cat_services.id,
            'description': '1-on-1 Django tutoring session',
            'price': 250,
            'product_type': 'SERVICE',
            'condition': 'NOT_APPLICABLE',
            'campus': 'IIT Bombay',
            'buy_or_rent': 'BUY',
            'service_rate_type': 'PER_HOUR',
            'service_duration_info': '60 minutes',
        }, follow=True)
        self.assertEqual(create_resp.status_code, 200)
        p = Product.objects.get(title='Peer Code Review Mentorship')
        self.assertEqual(p.product_type, 'SERVICE')

        # Edit the listing
        edit_resp = self.client.post(reverse('marketplace:edit_product', kwargs={'product_id': p.id}), {
            'title': 'Peer Code Review & Architecture Mentorship',
            'category': self.cat_services.id,
            'description': 'Updated 1-on-1 tutoring session',
            'price': 300,
            'product_type': 'SERVICE',
            'condition': 'NOT_APPLICABLE',
            'campus': 'IIT Bombay',
            'buy_or_rent': 'BUY',
            'service_rate_type': 'PER_HOUR',
            'service_duration_info': '90 minutes',
        }, follow=True)
        self.assertEqual(edit_resp.status_code, 200)
        p.refresh_from_db()
        self.assertEqual(p.price, Decimal('300.00'))

    # 5. Product Image Gallery Handling
    def test_product_image_gallery_addition_and_deletion(self):
        dummy_img = SimpleUploadedFile("thumb.jpg", b"imagebytes", content_type="image/jpeg")
        gallery_img = ProductImage.objects.create(product=self.laptop, image=dummy_img)
        self.assertEqual(self.laptop.additional_images.count(), 1)

        self.client.login(username="seller_student", password="password123")
        del_resp = self.client.post(reverse('marketplace:delete_product_image', kwargs={'image_id': gallery_img.id}), follow=True)
        self.assertEqual(del_resp.status_code, 200)
        self.assertEqual(self.laptop.additional_images.count(), 0)

    # 6. Self-Dealing Rejections
    def test_self_purchase_rejection(self):
        self.client.login(username="seller_student", password="password123")
        resp = self.client.get(reverse('marketplace:add_to_cart', kwargs={'product_id': self.laptop.id}), follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(self.seller.cart.items.count(), 0)

    def test_self_rental_rejection(self):
        self.client.login(username="seller_student", password="password123")
        resp = self.client.post(reverse('marketplace:rent_product', kwargs={'product_id': self.laptop.id}), {
            'start_date': datetime.date.today() + datetime.timedelta(days=1),
            'end_date': datetime.date.today() + datetime.timedelta(days=3),
            'notes': 'Self rental'
        }, follow=True)
        self.assertEqual(Rental.objects.filter(product=self.laptop).count(), 0)

    def test_self_review_rejection(self):
        self.client.login(username="seller_student", password="password123")
        resp = self.client.post(reverse('marketplace:add_review', kwargs={'product_id': self.laptop.id}), {
            'rating': 5,
            'comment': 'Self review'
        }, follow=True)
        self.assertEqual(Review.objects.filter(product=self.laptop).count(), 0)

    def test_self_report_rejection(self):
        self.client.login(username="seller_student", password="password123")
        resp = self.client.post(reverse('marketplace:report_product', kwargs={'product_id': self.laptop.id}), {
            'reason': 'SPAM',
            'details': 'Self report'
        }, follow=True)
        self.assertEqual(Report.objects.filter(product=self.laptop).count(), 0)

    # 7. Rental Conflict Logic
    def test_rental_conflict_blocking_states(self):
        today = datetime.date.today()
        start = today + datetime.timedelta(days=10)
        end = today + datetime.timedelta(days=14)

        rental = Rental.objects.create(
            product=self.laptop, renter=self.buyer, owner=self.seller,
            start_date=start, end_date=end, daily_rate=Decimal('300'),
            total_rent=Decimal('1500'), status="APPROVED"
        )
        self.assertTrue(check_rental_conflict(self.laptop.id, start, end))
        # Adjacent non-overlapping
        after_start = end + datetime.timedelta(days=1)
        after_end = after_start + datetime.timedelta(days=2)
        self.assertFalse(check_rental_conflict(self.laptop.id, after_start, after_end))

    # 8. Digital Asset Protected Downloads
    def test_digital_download_unpurchased_rejected(self):
        self.client.login(username="buyer_student", password="password123")
        resp = self.client.get(reverse('marketplace:digital_download', kwargs={'slug': self.digital_product.slug}), follow=True)
        self.assertNotEqual(resp.headers.get("Content-Type"), "application/pdf")

    def test_digital_download_pending_payment_rejected(self):
        order = Order.objects.create(
            buyer=self.buyer, total_amount=Decimal('199.00'), payment_status='PENDING',
            order_status='PLACED', full_name="Buyer", phone="9876543210", campus="IIT Bombay"
        )
        OrderItem.objects.create(order=order, product=self.digital_product, product_title="Notes", price_at_purchase=Decimal('199'), quantity=1, item_type='DIGITAL')

        self.client.login(username="buyer_student", password="password123")
        resp = self.client.get(reverse('marketplace:digital_download', kwargs={'slug': self.digital_product.slug}), follow=True)
        self.assertNotEqual(resp.headers.get("Content-Type"), "application/pdf")

    def test_digital_download_completed_payment_allowed(self):
        order = Order.objects.create(
            buyer=self.buyer, total_amount=Decimal('199.00'), payment_status='COMPLETED',
            order_status='COMPLETED', full_name="Buyer", phone="9876543210", campus="IIT Bombay"
        )
        OrderItem.objects.create(order=order, product=self.digital_product, product_title="Notes", price_at_purchase=Decimal('199'), quantity=1, item_type='DIGITAL')

        self.client.login(username="buyer_student", password="password123")
        resp = self.client.get(reverse('marketplace:digital_download', kwargs={'slug': self.digital_product.slug}))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers.get("Content-Type"), "application/pdf")

    # 9. Wishlist Operations
    def test_wishlist_toggle(self):
        self.client.login(username="buyer_student", password="password123")
        resp = self.client.get(reverse('marketplace:toggle_wishlist', kwargs={'product_id': self.laptop.id}), follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(self.buyer.wishlist.items.count(), 1)

        # Toggle again to remove
        resp2 = self.client.get(reverse('marketplace:toggle_wishlist', kwargs={'product_id': self.laptop.id}), follow=True)
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(self.buyer.wishlist.items.count(), 0)

    # 10. Semester Bundle Management Workflow
    def test_semester_bundle_item_management(self):
        self.client.login(username="seller_student", password="password123")
        bundle = SemesterBundle.objects.create(
            seller=self.seller, title="CS Sem 4 Bundle", semester="Semester 4",
            course="Computer Science", price=Decimal('800.00'), campus="IIT Bombay"
        )
        # Add item
        resp_add = self.client.post(reverse('marketplace:edit_bundle', kwargs={'bundle_id': bundle.id}), {
            'action': 'add_item',
            'item_title': 'Operating Systems Silberschatz',
            'item_type': 'TEXTBOOK'
        }, follow=True)
        self.assertEqual(resp_add.status_code, 200)
        self.assertEqual(bundle.items.count(), 1)

        # Remove item
        item = bundle.items.first()
        resp_del = self.client.post(reverse('marketplace:edit_bundle', kwargs={'bundle_id': bundle.id}), {
            'action': 'remove_item',
            'item_id': item.id
        }, follow=True)
        self.assertEqual(resp_del.status_code, 200)
        self.assertEqual(bundle.items.count(), 0)

    # 11. Comparison Engine
    def test_comparison_matrix_and_winner(self):
        comp_laptop = Product.objects.create(
            seller=self.seller, category=self.cat_laptops, title="HP Pavilion",
            price=Decimal('48000.00'), product_type="PHYSICAL", condition="GOOD", campus="IIT Bombay"
        )
        ElectronicsSpecification.objects.create(
            product=comp_laptop, processor="Intel i5", ram_gb=16, storage_gb=512,
            storage_type="SSD", battery_health_percent=85, usage_duration_months=18,
            display_specs="15.6 FHD", operating_system="Windows 11"
        )
        comp = compare_electronics_products(self.laptop.id, comp_laptop.id)
        self.assertIsNotNone(comp)
        self.assertEqual(len(comp['matrix']), 9)

    # 12. Checkout & Order Lifecycle
    def test_cart_checkout_and_order_creation(self):
        self.client.login(username="buyer_student", password="password123")
        self.client.get(reverse('marketplace:add_to_cart', kwargs={'product_id': self.laptop.id}), follow=True)

        resp = self.client.post(reverse('marketplace:checkout'), {
            'full_name': 'Buyer Student',
            'phone': '9876543210',
            'campus': 'IIT Bombay',
            'delivery_location_notes': 'Hostel 12 Common Room',
            'payment_method': 'COD'
        }, follow=True)
        self.assertEqual(resp.status_code, 200)
        order = Order.objects.filter(buyer=self.buyer).first()
        self.assertIsNotNone(order)
        self.assertEqual(order.order_status, 'PLACED')
        self.assertEqual(order.payment_method, 'COD')

    # 13. Moderation Permissions & Actions
    def test_moderation_verification_and_report_actions(self):
        self.client.login(username="admin_user", password="adminpassword")
        # Approve student verification via POST
        verify_resp = self.client.post(reverse('marketplace:admin_approve_verification', kwargs={'profile_id': self.buyer.profile.id}), follow=True)
        self.assertEqual(verify_resp.status_code, 200)
        self.buyer.profile.refresh_from_db()
        self.assertEqual(self.buyer.profile.verification_status, 'VERIFIED')

        # Resolve report via POST
        report = Report.objects.create(reporter=self.buyer, product=self.laptop, reason="PROHIBITED", details="Test report")
        rep_resp = self.client.post(reverse('marketplace:admin_resolve_report', kwargs={'report_id': report.id}), {
            'action': 'resolve_disable'
        }, follow=True)
        self.assertEqual(rep_resp.status_code, 200)
        report.refresh_from_db()
        self.laptop.refresh_from_db()
        self.assertEqual(report.status, 'RESOLVED')
        self.assertFalse(self.laptop.is_available)

    # 14. File Upload Extension Validation
    def test_invalid_image_upload_extension_validation(self):
        bad_file = SimpleUploadedFile("exploit.exe", b"fake binary", content_type="application/octet-stream")
        form = ProductForm(data={
            'title': 'Test Item', 'price': 100, 'product_type': 'PHYSICAL',
            'buy_or_rent': 'BUY', 'condition': 'GOOD', 'campus': 'IIT Bombay',
            'description': 'Description'
        }, files={'primary_image': bad_file})
        self.assertFalse(form.is_valid())
        self.assertIn('primary_image', form.errors)
