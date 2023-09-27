from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect

from FDA.constants import USER_TYPES
from orders.models import Order
from restaurant.models import Items


class OrderOwnerRequiredMixin:

    def dispatch(self, request, *args, **kwargs):
        order_obj = Order.get_object_from_pk(pk=kwargs['pk'])
        if not order_obj:
            raise Http404
        if hasattr(order_obj, 'user') and order_obj.user == request.user:
            return super(OrderOwnerRequiredMixin, self).dispatch(request, *args, **kwargs)
        raise PermissionDenied


class CustomerOrAnonymousUserRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            get_object_or_404(Items, id=kwargs['pk'])
            if not request.user.groups.filter(name=USER_TYPES[0]).exists():
                raise PermissionDenied
        return super(CustomerOrAnonymousUserRequiredMixin, self).dispatch(request, *args, **kwargs)


#
# class CartOwnerRequiredMixin:
#     def dispatch(self, request, *args, **kwargs):
#         user = request.user
#         # if
#                 raise PermissionDenied
#         return super(CustomerOrAnonymousUserRequiredMixin, self).dispatch(request, *args, **kwargs)


class HomeRedirectionMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user_role_page = {
                'restaurant_owner': 'restaurant-admin',
                'delivery_agent': 'delivery-agent-panel',
                'admin': 'admin-home',
            }
            if base_name := user_role_page.get(request.user.groups.filter(
                    Q(name='restaurant_owner') | Q(name='delivery_agent') | Q(name='admin')).values_list('name',
                                                                                                         flat=True).first()):
                return redirect(base_name)
        return super().dispatch(request, *args, **kwargs)
