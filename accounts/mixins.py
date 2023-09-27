from django.contrib import messages
from django.contrib.auth.mixins import AccessMixin
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import redirect, get_object_or_404
from django.utils.http import urlsafe_base64_decode

from FDA.constants import ACCOUNT_MUST_BE_ANONYMOUS_USER, ACCOUNT_PASSWORD_RESET_INVALID_LINK, USER_TYPES
from accounts.models import Activation, User
from restaurant.models import Restaurant


class AnonymousRequiredMixin(AccessMixin):
    """Verify that the current user is not authenticated."""

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.error(request, ACCOUNT_MUST_BE_ANONYMOUS_USER)
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)


class ActivationValidationMixin(AccessMixin):
    """Verify that the current user is not authenticated."""

    def dispatch(self, request, *args, **kwargs):
        code = kwargs['code']
        get_object_or_404(Activation, code=code)
        return super().dispatch(request, *args, **kwargs)


class ValidUserRequiredInTokenMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        uid = urlsafe_base64_decode(kwargs['uidb64'])
        user = User.get_user_from_id(pk=uid)
        is_token_valid = default_token_generator.check_token(user, kwargs['token'])
        if not is_token_valid:
            messages.error(request, ACCOUNT_PASSWORD_RESET_INVALID_LINK)
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)


class CustomerUserRequired(AccessMixin):
    """Verify that the current user is customer user."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name=USER_TYPES[0]).exists():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class ViewRestaurantGalleryMixin(AccessMixin):
    """Verify that the current user is customer user."""

    def dispatch(self, request, *args, **kwargs):
        if pk := kwargs.get('pk'):
            if not (restaurant := Restaurant.get_restaurant_from_id(pk)):
                raise Http404
            if restaurant.owner != request.user:
                raise PermissionDenied
            if restaurant.is_blocked:
                raise PermissionDenied
            return super(ViewRestaurantGalleryMixin, self).dispatch(request, *args,
                                                                    **kwargs) if restaurant.is_verified else redirect(
                'restaurant-verification-status', restaurant_id=restaurant.id)
        return super(ViewRestaurantGalleryMixin, self).dispatch(request, *args, **kwargs)
