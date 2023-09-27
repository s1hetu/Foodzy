from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from carts.models import CartItems
from carts.serializers import IncreaseQuantityOfCartItemSerializer, DecreaseQuantityOfCartItemSerializer


class IncreaseQuantityOfCartItemServices:

    @staticmethod
    def increase_quantity_of_cart_items(request, pk):
        instance = get_object_or_404(CartItems, item_id=pk, cart__user_id=request.user.id)

        serializer = IncreaseQuantityOfCartItemSerializer(
            instance,
            data=request.data,
            context={'request': request, 'pk': pk}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class DecreaseQuantityOfCartItemService:

    @staticmethod
    def decrease_quantity_of_cart_item(request, pk):
        instance = get_object_or_404(CartItems, item_id=pk, cart__user_id=request.user.id)

        serializer = DecreaseQuantityOfCartItemSerializer(
            instance,
            data=request.data,
            context={'request': request, 'pk': pk}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class DeleteCartItemService:

    @staticmethod
    def delete_cart_item(request, pk):
        instance = get_object_or_404(CartItems, item_id=pk, cart__user_id=request.user.id)
        instance.delete()

        cart_total = request.user.cart_set.first().total
        not_available = CartItems.objects.filter(
            Q(cart__user_id=request.user.id) &
            Q(item__restaurant__is_accepting_orders=False) |
            Q(item__restaurant__is_blocked=True)
        ).exists()

        if not not_available:
            not_available = not CartItems.objects.filter(Q(cart__user_id=request.user.id)).exists()
        return Response({'cart_total': cart_total, 'not_available': not_available}, status=status.HTTP_200_OK)
