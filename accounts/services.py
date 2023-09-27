import logging

from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from FDA.constants import (
    ACCOUNT_RESENT_ACTIVATION, ACCOUNT_PASSWORD_RESET_SUCCESS, ACCOUNT_PASSWORD_RESET_LINK_SENT,
    ACCOUNT_DEACTIVATION_SUCCESS, ACCOUNT_MODEL_BACKEND, ACCOUNT_LOGIN_SUCCESS, ACCOUNT_LOGIN_FAILED,
    ACCOUNT_LOGIN_PAGE, ACCOUNT_REGISTER_SUCCESS, ACCOUNT_LOGOUT_SUCCESS, ACCOUNT_SOCIAL_AUTH_GITHUB,
    ACCOUNT_SOCIAL_AUTH_TWITTER, ACCOUNT_SOCIAL_AUTH_FACEBOOK, ACCOUNT_SOCIAL_AUTH_GOOGLE, ACCOUNT_USER_PROFILE_SUCCESS,
    ACCOUNT_USER_ADDRESS_SUCCESS
)
from accounts.forms import RegisterForm, CustomerAddressForm
from accounts.models import Activation, User
from accounts.utils import send_activation_email, send_reset_password_email

logger = logging.getLogger('info_log')


class ActivateService:

    @staticmethod
    def get_context_data(context, **kwargs):
        act = Activation.objects.get(code=kwargs['code'])
        if not act.is_valid():
            context.update({'is_link_valid': False})
        else:
            context.update({'is_link_valid': True})
            # Activate profile and Remove the activation record
            act.activate()
        return context


class ResendActivationCodeService:
    def __init__(self, request):
        self.request = request

    def form_valid(self, form):
        user = User.get_user_from_email(email=form.cleaned_data.get('email'))
        code = user.get_activation_code()
        send_activation_email(self.request, user.email, code)
        messages.success(self.request, ACCOUNT_RESENT_ACTIVATION)
        return redirect('home')


class PasswordResetService:
    def __init__(self, request):
        self.request = request

    def form_valid(self, form):
        form.save(user=self.request.user)
        logout(self.request)
        messages.success(self.request, ACCOUNT_PASSWORD_RESET_SUCCESS)
        return redirect('home')

    def get_form_kwargs(self, **kwargs):
        kwargs['user'] = self.request.user
        return kwargs


class ForgotPasswordService:
    def __init__(self, request):
        self.request = request

    def form_valid(self, form):
        user = User.get_user_from_email(email=form.cleaned_data.get('email'))
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        send_reset_password_email(self.request, user.email, token, uid)

        messages.success(self.request, ACCOUNT_PASSWORD_RESET_LINK_SENT)
        return redirect('home')


class RestorePasswordConfirmService:
    def __init__(self, request):
        self.request = request

    def form_valid(self, form, **kwargs):
        user = User.get_user_from_id(pk=urlsafe_base64_decode(kwargs['uidb64']))
        form.save(user=user)
        logout(self.request)
        messages.success(self.request, ACCOUNT_PASSWORD_RESET_SUCCESS)
        return redirect('home')


class DeactivateAccountService:

    @staticmethod
    def delete_user(request):
        request.user.delete_user()
        logout(request)
        messages.success(request, ACCOUNT_DEACTIVATION_SUCCESS)
        return redirect('home')


class LoginService:
    def __init__(self, request):
        self.request = request

    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')

        if user := authenticate(email=email, password=password):
            login(self.request, user, backend=ACCOUNT_MODEL_BACKEND)
            messages.success(self.request, ACCOUNT_LOGIN_SUCCESS)

            if next_page := self.request.GET.get('next'):
                return HttpResponseRedirect(next_page)

            return redirect('home')
        logger.error('Unwanted authentication error in authenticate()')
        messages.error(self.request, ACCOUNT_LOGIN_FAILED)
        return render(self.request, template_name=ACCOUNT_LOGIN_PAGE, context={'form': form})


class RegisterService:

    @staticmethod
    def get_context_data():
        return {
            'user_form': RegisterForm(),
            'address_form': CustomerAddressForm(),
        }

    @staticmethod
    def is_forms_valid(request, template_name):
        user_form = RegisterForm(request.POST, request.FILES)
        address_form = CustomerAddressForm(request.POST, request.FILES)

        if user_form.is_valid() and address_form.is_valid():
            user = user_form.save()
            address_form.save(user=user)
            code = user.get_activation_code()
            send_activation_email(request, user.email, code)
            messages.success(request, ACCOUNT_REGISTER_SUCCESS)
            logger.info(f'Registered new user. email: {user.email}')
            return redirect('home')
        return render(request, template_name, context={
            'user_form': user_form,
            'address_form': address_form,
        })


class LogoutService:

    @staticmethod
    def logout_user(request):
        logout(request)
        messages.success(request, ACCOUNT_LOGOUT_SUCCESS)
        return redirect('home')


class SocialAuthManageSettingService:

    @staticmethod
    def get_context_data(context, request):
        user = request.user

        github_login = user.get_social_auth_from_provider(provider=ACCOUNT_SOCIAL_AUTH_GITHUB)
        twitter_login = user.get_social_auth_from_provider(provider=ACCOUNT_SOCIAL_AUTH_TWITTER)
        facebook_login = user.get_social_auth_from_provider(provider=ACCOUNT_SOCIAL_AUTH_FACEBOOK)
        google_login = user.get_social_auth_from_provider(provider=ACCOUNT_SOCIAL_AUTH_GOOGLE)

        can_disconnect = user.can_disconnect()

        context.update({
            'github_login': github_login,
            'twitter_login': twitter_login,
            'facebook_login': facebook_login,
            'google_login': google_login,
            'can_disconnect': can_disconnect,
            'social_auths_count': user.social_auth.count()
        })
        return context


class SocialAuthSetPasswordService:
    def __init__(self, request):
        self.request = request

    def form_valid(self, form):
        form.save()
        logout(self.request)
        messages.success(self.request, ACCOUNT_PASSWORD_RESET_SUCCESS)
        return redirect('home')

    def get_form_kwargs(self, **kwargs):
        kwargs['user'] = self.request.user
        return kwargs


class UserProfileService:
    def __init__(self, request):
        self.request = request

    def form_valid(self, form):
        form.save()
        messages.success(self.request, ACCOUNT_USER_PROFILE_SUCCESS)
        return redirect('profile')

    def get_form_kwargs(self, **kwargs):
        kwargs['instance'] = self.request.user
        return kwargs

    @staticmethod
    def get_context_data(context, request):
        user_profile_image = request.user.get_profile_pic()
        context.update(
            {'user_profile_image': user_profile_image})
        return context


class UserAddressUpdateService:
    def __init__(self, request):
        self.request = request

    def form_valid(self, form):
        form.save()
        messages.success(self.request, ACCOUNT_USER_ADDRESS_SUCCESS)
        return redirect('edit-address')

    def get_form_kwargs(self, **kwargs):
        kwargs['instance'] = self.request.user.addresses.first()
        return kwargs

    @staticmethod
    def get_context_data(context, request):
        return context
