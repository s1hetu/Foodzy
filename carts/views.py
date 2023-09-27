from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView

from .models import CartItems
from .serializers import (
    CreateCartItemSerializer
)
from .services import IncreaseQuantityOfCartItemServices, DecreaseQuantityOfCartItemService, DeleteCartItemService


class CreateCartItemAPIView(LoginRequiredMixin, PermissionRequiredMixin, CreateAPIView):
    """Creates new :model:`carts.CartItems`.
    """
    permission_required = ['carts.add_cart']
    queryset = CartItems.objects.all()
    """The queryset that should be used for returning objects from this view.
    """

    serializer_class = CreateCartItemSerializer
    """The serializer class that should be used for validating and deserializing input,
    and for serializing output.
    """


class IncreaseQuantityOfCartItemAPIView(LoginRequiredMixin, PermissionRequiredMixin, APIView):
    """Increase Quantity for :model:`carts.CartItems`.
    """
    permission_required = ['carts.change_cartitems']

    def post(self, request, pk, *args, **kwargs):
        return IncreaseQuantityOfCartItemServices.increase_quantity_of_cart_items(request=request, pk=pk)


class DecreaseQuantityOfCartItemAPIView(LoginRequiredMixin, PermissionRequiredMixin, APIView):
    """Decrease Quantity for :model:`carts.CartItems`.
    """
    permission_required = ['carts.change_cartitems']

    def post(self, request, pk, *args, **kwargs):
        return DecreaseQuantityOfCartItemService.decrease_quantity_of_cart_item(request=request, pk=pk)


class DeleteCartItemAPIView(LoginRequiredMixin, PermissionRequiredMixin, APIView):
    """Delete method for :model:`carts.CartItems`.
    """
    permission_required = ['carts.delete_cartitems']

    def post(self, request, pk, *args, **kwargs):
        return DeleteCartItemService.delete_cart_item(request=request, pk=pk)
