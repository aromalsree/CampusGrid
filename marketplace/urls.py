from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'marketplace'

urlpatterns = [
    # 1. Homepage & Global
    path('', views.index, name='index'),
    path('set-campus/', views.set_campus, name='set_campus'),

    # 2. Marketplace & Products
    path('products/', views.product_list, name='product_list'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),
    path('products/<slug:slug>/download/', views.digital_download_view, name='digital_download'),

    # 3. Smart Comparison Engine
    path('compare/', views.compare_view, name='compare'),

    # 4. Cart & Checkout
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('checkout/', views.checkout_view, name='checkout'),

    # 5. Orders & Rentals
    path('orders/', views.orders_list, name='orders_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('rent/<int:product_id>/', views.rent_product, name='rent_product'),
    path('rentals/', views.rentals_list, name='rentals_list'),
    path('rentals/<int:rental_id>/update/', views.update_rental_status, name='update_rental_status'),

    # 6. Wishlist
    path('wishlist/', views.wishlist_view, name='wishlist_view'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),

    # 7. Semester Bundles
    path('bundles/', views.semester_bundles_list, name='semester_bundles_list'),
    path('bundles/create/', views.create_bundle, name='create_bundle'),
    path('bundles/<slug:slug>/', views.bundle_detail, name='bundle_detail'),
    path('bundles/<int:bundle_id>/edit/', views.edit_bundle, name='edit_bundle'),
    path('bundles/<int:bundle_id>/delete/', views.delete_bundle, name='delete_bundle'),

    # 8. Student Requests Board
    path('requests/', views.student_requests_list, name='student_requests_list'),
    path('requests/create/', views.create_request, name='create_request'),
    path('requests/<int:request_id>/close/', views.close_student_request, name='close_student_request'),

    # 9. Academic Services
    path('services/book/<int:product_id>/', views.book_service_session, name='book_service_session'),

    # 10. Reviews & Reports
    path('products/<int:product_id>/review/', views.add_review, name='add_review'),
    path('products/<int:product_id>/report/', views.report_product, name='report_product'),

    # 11. Notifications
    path('notifications/', views.notifications_view, name='notifications_view'),
    path('notifications/<int:notif_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),

    # 12. Seller & Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('seller/', views.seller_dashboard, name='seller_dashboard'),
    path('seller/products/add/', views.add_product, name='add_product'),
    path('seller/products/<int:product_id>/edit/', views.edit_product, name='edit_product'),
    path('seller/products/<int:product_id>/delete/', views.delete_product, name='delete_product'),
    path('seller/products/<int:product_id>/toggle/', views.toggle_product_availability, name='toggle_product_availability'),
    path('seller/images/<int:image_id>/delete/', views.delete_product_image, name='delete_product_image'),

    # 13. Authentication & Profile
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.user_profile_view, name='user_profile'),

    # Password Reset Routes
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),

    # 14. Moderation / Admin
    path('moderation/', views.moderation_dashboard, name='moderation_dashboard'),
    path('moderation/verify/<int:profile_id>/', views.admin_approve_verification, name='admin_approve_verification'),
    path('moderation/report/<int:report_id>/', views.admin_resolve_report, name='admin_resolve_report'),
]
