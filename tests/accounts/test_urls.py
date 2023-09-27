from django.urls import reverse, resolve

from accounts.views import (
    ActivateView,
    ResendActivationCodeView,
    PasswordResetView,
    RestorePasswordConfirmView,
    ForgotPasswordView,
    LoginView,
    RegisterView,
    LogoutView,
    SocialAuthManageSetting,
    SocialAuthSetPassword,
    DeactivateAccountView,
    UserProfileView, UserAddressUpdateView
)


class TestAccountsUrls(object):
    """Test for accounts app's urls.
    Below test functions tests for all urls defined in accounts/urls.py
    """

    def test_password_reset_url(self):
        url = reverse('password-reset-api')
        assert resolve(url).func.view_class == PasswordResetView

    def test_forgot_password_url(self):
        url = reverse('forgot-password')
        assert resolve(url).func.view_class == ForgotPasswordView

    def test_restore_password_url(self):
        url = reverse('restore-password', kwargs={'uidb64': 'Mg', 'token': 'bevicu-e302749a776d508fc1c6b2f0e7eb194f'})
        assert resolve(url).func.view_class == RestorePasswordConfirmView

    def test_activate_api_url(self):
        url = reverse('activate-api', kwargs={'code': '645569e3-4651-4079-9177-d1096e964614'})
        assert resolve(url).func.view_class == ActivateView

    def test_resend_activation_code_api_url(self):
        url = reverse('resend-activation-code-api')
        assert resolve(url).func.view_class == ResendActivationCodeView

    def test_deactivate_api_url(self):
        url = reverse('deactivate-api')
        assert resolve(url).func.view_class == DeactivateAccountView

    def test_settings_url(self):
        url = reverse('settings')
        assert resolve(url).func.view_class == SocialAuthManageSetting

    def test_password_url(self):
        url = reverse('password')
        assert resolve(url).func.view_class == SocialAuthSetPassword

    def test_login_url(self):
        url = reverse('login')
        assert resolve(url).func.view_class == LoginView

    def test_register_url(self):
        url = reverse('register')
        assert resolve(url).func.view_class == RegisterView

    def test_logout_url(self):
        url = reverse('logout')
        assert resolve(url).func.view_class == LogoutView

    def test_profile_url(self):
        url = reverse('profile')
        assert resolve(url).func.view_class == UserProfileView

    def test_edit_address_url(self):
        url = reverse('edit-address')
        assert resolve(url).func.view_class == UserAddressUpdateView
