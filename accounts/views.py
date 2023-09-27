from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView, FormView

from FDA.constants import (
    ACCOUNT_LOGIN_PAGE, ACCOUNT_REGISTER_PAGE,
    ACCOUNT_SOCIAL_AUTH_MANAGE_PAGE, ACCOUNT_SOCIAL_AUTH_SET_PASSWORD_PAGE, ACCOUNT_FORGOT_PASSWORD_PAGE,
    ACCOUNT_RESTORE_PASSWORD_PAGE, ACCOUNT_RESET_PASSWORD_PAGE, ACCOUNT_RESEND_ACTIVATION_CODE_PAGE,
    ACCOUNT_USER_PROFILE_PAGE, ACCOUNT_USER_ACTIVATED_PAGE, ACCOUNT_USER_EDIT_ADDRESS_PAGE
)
from .forms import (
    LoginForm, ResendActivationCodeForm, PasswordResetForm, ForgotPasswordForm,
    PasswordChangeForm, PasswordRestoreForm, UserProfileForm, CustomerAddressUpdateForm
)
from .mixins import (
    AnonymousRequiredMixin, ActivationValidationMixin, ValidUserRequiredInTokenMixin,
    CustomerUserRequired
)
from .services import (
    ActivateService, ResendActivationCodeService, PasswordResetService, ForgotPasswordService,
    RestorePasswordConfirmService, DeactivateAccountService, LoginService, RegisterService, LogoutService,
    SocialAuthManageSettingService, SocialAuthSetPasswordService, UserProfileService, UserAddressUpdateService
)


class ActivateView(ActivationValidationMixin, TemplateView):
    """
    description: This is user's email activation View.
    """
    template_name = ACCOUNT_USER_ACTIVATED_PAGE

    def get_context_data(self, **kwargs):
        context = super(ActivateView, self).get_context_data(**kwargs)
        return ActivateService.get_context_data(context=context, **kwargs)


class ResendActivationCodeView(AnonymousRequiredMixin, FormView):
    """
    description: This is View for resending activation email.
    """
    template_name = ACCOUNT_RESEND_ACTIVATION_CODE_PAGE
    form_class = ResendActivationCodeForm

    def form_valid(self, form):
        return ResendActivationCodeService(request=self.request).form_valid(form=form)


class PasswordResetView(LoginRequiredMixin, FormView):
    """
    description: This is View is for resetting password.
    """

    template_name = ACCOUNT_RESET_PASSWORD_PAGE
    form_class = PasswordResetForm

    def form_valid(self, form):
        return PasswordResetService(request=self.request).form_valid(form=form)

    def get_form_kwargs(self):
        kwargs = super(PasswordResetView, self).get_form_kwargs()
        return PasswordResetService(request=self.request).get_form_kwargs(**kwargs)


class ForgotPasswordView(AnonymousRequiredMixin, FormView):
    """
    description: This is View for sending mail for forgot password.
    """

    template_name = ACCOUNT_FORGOT_PASSWORD_PAGE
    form_class = ForgotPasswordForm

    def form_valid(self, form):
        return ForgotPasswordService(request=self.request).form_valid(form=form)


class RestorePasswordConfirmView(AnonymousRequiredMixin, ValidUserRequiredInTokenMixin, FormView):
    """
    description: This is View is for restoring password after sending link via forgot password.
    """

    template_name = ACCOUNT_RESTORE_PASSWORD_PAGE
    form_class = PasswordRestoreForm

    def form_valid(self, form):
        return RestorePasswordConfirmService(request=self.request).form_valid(form=form, **self.kwargs)


class DeactivateAccountView(LoginRequiredMixin, View):
    """
    description: This is View for deactivating/removing user account.
    """

    def get(self, request):
        return DeactivateAccountService.delete_user(request=request)


# Views
class LoginView(AnonymousRequiredMixin, FormView):
    """
    description: This is user login view.
    GET request will display Login Form in login.html page.
    POST request will make user login if details is valid else login form with error is displayed.
    """
    template_name = ACCOUNT_LOGIN_PAGE
    form_class = LoginForm

    def form_valid(self, form):
        return LoginService(request=self.request).form_valid(form=form)


class RegisterView(AnonymousRequiredMixin, View):
    """
    description: This is user register view.
    GET request will display Register Form in register.html page.
    POST request will make user registered if details is valid else register
    form with error is displayed.
    """
    template_name = ACCOUNT_REGISTER_PAGE

    def get(self, request):
        context = RegisterService.get_context_data()
        return render(request, RegisterView.template_name, context=context)

    def post(self, request):
        return RegisterService.is_forms_valid(request=request, template_name=RegisterView.template_name)


class LogoutView(LoginRequiredMixin, View):
    """
    description: This is user logout view.
    GET request will log out user and redirects to home page.
    """

    def get(self, request):
        return LogoutService.logout_user(request=request)


class SocialAuthManageSetting(LoginRequiredMixin, TemplateView):
    """
    description: This is managing users social auths.
    GET request will allow user to add/remove social auth accounts.
    """
    template_name = ACCOUNT_SOCIAL_AUTH_MANAGE_PAGE

    def get_context_data(self, **kwargs):
        context = super(SocialAuthManageSetting, self).get_context_data(**kwargs)
        return SocialAuthManageSettingService.get_context_data(context=context, request=self.request)


class SocialAuthSetPassword(LoginRequiredMixin, FormView):
    """
    description: This is setting password for removing all social auths and setup default user account.
    GET request will Password Change form.
    POST request will set new password to user account if form is valid, else form with error is displayed.
    """
    template_name = ACCOUNT_SOCIAL_AUTH_SET_PASSWORD_PAGE
    form_class = PasswordChangeForm

    def form_valid(self, form):
        return SocialAuthSetPasswordService(request=self.request).form_valid(form=form)

    def get_form_kwargs(self):
        kwargs = super(SocialAuthSetPassword, self).get_form_kwargs()
        return SocialAuthSetPasswordService(request=self.request).get_form_kwargs(**kwargs)


class UserProfileView(LoginRequiredMixin, FormView):
    """
    description: This is View and Update for user profile.
    """
    template_name = ACCOUNT_USER_PROFILE_PAGE
    form_class = UserProfileForm

    def get_form_kwargs(self):
        kwargs = super(UserProfileView, self).get_form_kwargs()
        return UserProfileService(request=self.request).get_form_kwargs(**kwargs)

    def get_context_data(self, **kwargs):
        context = super(UserProfileView, self).get_context_data(**kwargs)
        return UserProfileService.get_context_data(context=context, request=self.request)

    def form_valid(self, form):
        return UserProfileService(request=self.request).form_valid(form=form)


class UserAddressUpdateView(LoginRequiredMixin, CustomerUserRequired, FormView):
    """
    description: This is View and Update for user address.
    """
    template_name = ACCOUNT_USER_EDIT_ADDRESS_PAGE
    form_class = CustomerAddressUpdateForm

    def get_form_kwargs(self):
        kwargs = super(UserAddressUpdateView, self).get_form_kwargs()
        return UserAddressUpdateService(request=self.request).get_form_kwargs(**kwargs)

    def get_context_data(self, **kwargs):
        context = super(UserAddressUpdateView, self).get_context_data(**kwargs)
        return UserAddressUpdateService.get_context_data(context=context, request=self.request)

    def form_valid(self, form):
        return UserAddressUpdateService(request=self.request).form_valid(form=form)
