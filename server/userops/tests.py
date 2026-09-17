from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse


class RegistrationTests(TestCase):
	def setUp(self):
		self.register_url = reverse('register')
		self.login_url = reverse('login')
		self.valid_data = {
			'username': 'new_student',
			'email': 'new.student@example.com',
			'institution': 'Campus University',
			'phone': '+919876543210',
			'password': 'strong-test-password',
			'password_confirm': 'strong-test-password',
		}

	def test_valid_registration_creates_and_logs_in_user(self):
		response = self.client.post(self.register_url, self.valid_data)

		self.assertRedirects(response, reverse('home'))
		self.assertTrue(
			self.client.session.get('_auth_user_id'),
		)
		self.assertTrue(
			get_user_model().objects.filter(username='new_student').exists(),
		)

	def test_invalid_registration_renders_form_with_errors(self):
		invalid_data = self.valid_data.copy()
		invalid_data['password_confirm'] = 'different-password'

		response = self.client.post(self.register_url, invalid_data)

		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'user/register.html')
		self.assertContains(response, 'Passwords do not match')

	def test_admin_login_redirects_to_admin_dashboard(self):
		admin = get_user_model().objects.create_user(
			username='admin_student',
			email='admin@example.com',
			password='strong-test-password',
			institution='Campus University',
			user_roles='ADMIN',
		)

		response = self.client.post(self.login_url, {
			'username': admin.username,
			'password': 'strong-test-password',
		})

		self.assertRedirects(response, reverse('admin_dashboard'))

	def test_admin_can_create_user_from_custom_admin_page(self):
		admin = get_user_model().objects.create_user(
			username='page_admin',
			email='page-admin@example.com',
			password='strong-test-password',
			institution='Campus University',
			user_roles='ADMIN',
		)
		self.client.force_login(admin)
		data = {
			'username': 'created_from_admin',
			'email': 'created@example.com',
			'institution': 'Campus University',
			'phone': '+919876543221',
			'password': 'strong-test-password',
			'password_confirm': 'strong-test-password',
			'user_roles': 'ADMIN',
		}

		response = self.client.post(reverse('admin_user_add'), data)

		self.assertRedirects(response, reverse('admin_users'))
		created_user = get_user_model().objects.get(username='created_from_admin')
		self.assertEqual(created_user.user_roles, 'ADMIN')
		self.assertTrue(created_user.is_staff)

	def test_login_page_and_password_reset_route_render(self):
		response = self.client.get(self.login_url)

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'password-reset')

		get_user_model().objects.create_user(
			username='reset_student',
			email='reset@example.com',
			password='strong-test-password',
			institution='Campus University',
		)

		reset_response = self.client.post('/password-reset/', {
			'email': 'reset@example.com',
		})

		self.assertRedirects(reset_response, '/password-reset/done/')
		self.assertEqual(len(mail.outbox), 1)
