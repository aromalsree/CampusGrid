from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Category, Listing


class NeedRequestAuthenticationTests(TestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(
			username='student',
			email='student@example.com',
			password='strong-test-password',
			institution='Campus University',
		)
		self.create_url = reverse('market:create_need_request')

	def test_anonymous_user_is_sent_to_login_with_return_url(self):
		response = self.client.get(self.create_url)

		self.assertRedirects(
			response,
			f'/login/?next={self.create_url}',
			fetch_redirect_response=False,
		)

	def test_authenticated_user_can_open_create_form(self):
		self.client.force_login(self.user)

		response = self.client.get(self.create_url)

		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'need_board/create.html')


class ProductListFilterTests(TestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(
			username='catalog_student',
			email='catalog@example.com',
			password='strong-test-password',
			institution='Campus University',
		)
		self.category = Category.objects.get(slug='laptops')
		Listing.objects.create(
			seller=self.user,
			category=self.category,
			title='MacBook Pro M1',
			slug='macbook-pro-m1-test',
			description='A well maintained laptop for campus work.',
			price='58000.00',
			listing_type=Listing.ListingType.SALE,
			condition=Listing.Condition.LIKE_NEW,
		)

	def test_category_filter_uses_category_slug(self):
		response = self.client.get('/products/?category=laptops&type=&condition=')

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'MacBook Pro M1')

	def test_laptop_filter_keeps_sample_products_when_user_listings_exist(self):
		other_category = Category.objects.get(slug='notes')
		Listing.objects.create(
			seller=self.user,
			category=other_category,
			title='DSA Course Notes',
			slug='dsa-course-notes-test',
			description='Detailed notes for algorithms and data structures.',
			price='150.00',
			listing_type=Listing.ListingType.SALE,
			condition=Listing.Condition.GOOD,
		)

		response = self.client.get('/products/?category=laptops')

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'MacBook Pro M1')

	def test_sidebar_filter_aliases_match_listing_choices(self):
		response = self.client.get('/products/?category=laptops&type=sell&condition=like_new')

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'MacBook Pro M1')

	def test_categories_page_shows_all_active_categories(self):
		response = self.client.get('/categories/')

		self.assertEqual(response.status_code, 200)
		for category in Category.objects.filter(is_active=True):
			self.assertContains(response, f'/products/?category={category.slug}')
