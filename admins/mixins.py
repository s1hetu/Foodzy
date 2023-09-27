from django.conf import settings
from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404

from FDA.constants import USER_TYPES, DEFAULT_PAGINATED_BY
from accounts.models import User
from admins.utils import get_paginated_context
from restaurant.models import Restaurant


class AdminRequiredMixin(AccessMixin):
    """Verify that the current user is admin user."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_admin or not request.user.groups.filter(name=USER_TYPES[3]).exists():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class PkValidationMixin(AccessMixin):
    """Verify that the current pk is valid."""

    def dispatch(self, request, *args, **kwargs):
        if not self.class_name.get_object_from_pk(pk=kwargs['pk']):
            raise Http404
        return super().dispatch(request, *args, **kwargs)


class DriverApplicationValidationMixin(AccessMixin):
    """Verify that current driver is having application."""

    def dispatch(self, request, *args, **kwargs):
        if not User.is_unverified_agent(pk=kwargs['pk']):
            raise Http404
        return super().dispatch(request, *args, **kwargs)


class RestaurantApplicationValidationMixin(AccessMixin):
    """Verify that current restaurant is having application."""

    def dispatch(self, request, *args, **kwargs):
        if not Restaurant.is_valid_restaurant_application_user(pk=kwargs['pk']):
            raise Http404
        return super().dispatch(request, *args, **kwargs)


class PaginationMixin:
    def get_paginate_by(self, queryset):
        paginate_by = self.paginate_by
        try:
            if not paginate_by:
                paginate_by = int(settings.PAGINATION_CONFIGURATIONS.get('PAGINATE_BY', DEFAULT_PAGINATED_BY))
        except AttributeError:
            paginate_by = DEFAULT_PAGINATED_BY

        return paginate_by

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = get_paginated_context(
            context=context,
            request=self.request,
            queryset=self.get_queryset(),
            paginator_class=self.paginator_class,
            paginate_by=self.paginate_by,
        )
        return context
