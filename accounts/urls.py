from django.urls import path, include

from .views import (
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

urlpatterns = [
    path('password-reset/', PasswordResetView.as_view(), name='password-reset-api'),

    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('restore-password/<uidb64>/<token>/', RestorePasswordConfirmView.as_view(), name='restore-password'),

    path('activate/<code>/', ActivateView.as_view(), name='activate-api'),
    path('resent-activation-code/', ResendActivationCodeView.as_view(), name='resend-activation-code-api'),

    path('deactivate/', DeactivateAccountView.as_view(), name='deactivate-api'),

    path('settings/', SocialAuthManageSetting.as_view(), name='settings'),
    path('settings/password/', SocialAuthSetPassword.as_view(), name='password'),

    path('login-view/', LoginView.as_view(), name='login'),
    path('register-view/', RegisterView.as_view(), name='register'),
    path('logout-view/', LogoutView.as_view(), name='logout'),
    path('user-profile/', UserProfileView.as_view(), name='profile'),
    path('address/edit/', UserAddressUpdateView.as_view(), name='edit-address'),

    path('oauth/', include('social_django.urls', namespace='social')),
]
