from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import redirect

from orders.models import Order
from restaurant.models import Items, Restaurant


class RestaurantItemMixin:

    def dispatch(self, request, *args, **kwargs):
        if item := Items.get_item(kwargs['pk']):
            if not item.restaurant or item.restaurant.owner != request.user or item.restaurant.is_blocked:
                raise PermissionDenied
            return super(RestaurantItemMixin, self).dispatch(request, *args, **kwargs)
        else:
            raise Http404


class RestaurantOwnerMixin:
    def dispatch(self, request, *args, **kwargs):
        if not (restaurant := Restaurant.get_restaurant_from_id(kwargs['pk'])):
            raise Http404
        if restaurant.owner != request.user:
            raise PermissionDenied
        return super(RestaurantOwnerMixin, self).dispatch(request, *args,
                                                          **kwargs) if restaurant.is_verified else redirect(
            'restaurant-verification-status', restaurant_id=restaurant.id)


class RestaurantNotBlockedMixin:
    def dispatch(self, request, *args, **kwargs):
        restaurant = Restaurant.get_restaurant_from_id(kwargs['pk'])
        if restaurant.is_blocked:
            messages.error(request, "The restaurant is blocked.")
            raise PermissionDenied
        return super(RestaurantNotBlockedMixin, self).dispatch(request, *args, **kwargs)


class CheckOrderRestaurantMixin:
    def dispatch(self, request, *args, **kwargs):
        order = Order.get_object_from_pk(pk=kwargs['pk'])
        if order.restaurant.owner != request.user or order.restaurant.is_blocked:
            raise PermissionDenied
        return super(CheckOrderRestaurantMixin, self).dispatch(request, *args,
                                                               **kwargs) if order.restaurant.is_verified else redirect(
            'restaurant-verification-status', restaurant_id=order.restaurant.id)


class CheckRestaurantMixin:
    def dispatch(self, request, *args, **kwargs):
        if hasattr(request.user, 'restaurants'):
            return super(CheckRestaurantMixin, self).dispatch(request, *args, **kwargs)
        raise PermissionDenied


class RedirectToRestaurant:  # pragma:no cover
    def dispatch(self, request, *args, **kwargs):
        if restaurant_id := request.session.get('restaurant_id'):
            if request.GET.get('view_all_restaurants') == '1':
                request.session.pop('restaurant_id')
                return super().dispatch(request, *args, **kwargs)
            return redirect('owner-admin', int(restaurant_id))
        return super().dispatch(request, *args, **kwargs)


class AddRestaurantInSession:
    def dispatch(self, request, *args, **kwargs):
        if Restaurant.get_restaurant_from_id(kwargs['pk']).is_verified:
            request.session['restaurant_id'] = kwargs['pk']

        return super().dispatch(request, *args, **kwargs)
