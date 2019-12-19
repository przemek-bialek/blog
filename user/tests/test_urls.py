from django.test import SimpleTestCase
from django.urls import reverse, resolve
from django.contrib.auth.views import (LoginView, LogoutView, PasswordResetView, PasswordResetDoneView,
                                       PasswordResetConfirmView, PasswordResetCompleteView)

from user.views import register, profile

class TestUrls(SimpleTestCase):
    def test_user_register_url_resolves(self):
        url = reverse('user-register')
        self.assertEqual(resolve(url).func, register)

    def test_user_login_url_resolves(self):
        url = reverse('user-login')
        self.assertEqual(resolve(url).func.view_class, LoginView)

    def test_user_logout_url_resolves(self):
        url = reverse('user-logout')
        self.assertEqual(resolve(url).func.view_class, LogoutView)

    def test_password_reset_url_resolves(self):
        url = reverse('password_reset')
        self.assertEqual(resolve(url).func.view_class, PasswordResetView)

    def test_password_reset_done_url_resolves(self):
        url = reverse('password_reset_done')
        self.assertEqual(resolve(url).func.view_class, PasswordResetDoneView)

    def test_password_reset_confirm_url_resolves(self):
        url = reverse('password_reset_confirm', args=['MTJ', '5cf-25f3e93df8ad7ea97eef'])
        self.assertEqual(resolve(url).func.view_class, PasswordResetConfirmView)

    def test_password_reset_complete_url_resolves(self):
        url = reverse('password_reset_complete')
        self.assertEqual(resolve(url).func.view_class, PasswordResetCompleteView)

    def test_user_profile_url_resolves(self):
        url = reverse('user-profile')
        self.assertEqual(resolve(url).func, profile)
