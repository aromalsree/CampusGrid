from django.urls import path
from . import views

app_name = 'market'

urlpatterns = [
    # Marketplace Catalogue / Product Listings
    path('products/', views.MarketView.as_view(), name='product_list'),
    path('products/', views.MarketView.as_view(), name='products'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(),name='product_id'),
    

    # Create Product Listing
    path('create/', views.create_listing, name='create_listing'),
    path('products/create/', views.create_listing, name='create_listing_prefixed'),
    path('seller/products/add/', views.create_listing, name='seller_products_add'),

    # Category Directory
    path('categories/', views.categories, name='categories'),
    path('products/categories/', views.categories, name='products_categories'),

    # Hardware Comparison Matrix
    path('compare/', views.compare, name='compare'),
    path('products/compare/', views.compare, name='products_compare'),

    # Campus Need Board (Reverse Marketplace)
    path('requests/', views.need_board_view, name='requests'),
    path('requests/board/', views.NeedBoardListView.as_view(), name='need_board'),
    path('requests/create/', views.create_need_request, name='create_need_request'),
    path('requests/<int:pk>/', views.need_request_detail, name='need_request_detail'),
    path('requests/<int:pk>/fulfill/', views.toggle_need_status, name='toggle_need_status'),
    path('requests/<int:pk>/offer/', views.create_need_offer, name='create_need_offer'),

    # Product Details (supports pk / integer id, slug, or generic string)
    
   
]
