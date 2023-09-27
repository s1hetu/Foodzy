from django.urls import reverse, resolve

from carts.views import (
    IncreaseQuantityOfCartItemAPIView, CreateCartItemAPIView, DecreaseQuantityOfCartItemAPIView,
    DeleteCartItemAPIView
)


class TestCartUrls:
    def test_create_cart_item_url(self):
        create_cart_item_url = reverse('create-cart-item')
        assert resolve(create_cart_item_url).func.view_class == CreateCartItemAPIView

    def test_increase_cart_item_quantity_url(self):
        increase_cart_item_quantity_url = reverse('increase-cart-item-quantity', kwargs={'pk': 1})
        assert resolve(increase_cart_item_quantity_url).func.view_class == IncreaseQuantityOfCartItemAPIView

    def test_decrease_cart_item_quantity_url(self):
        decrease_cart_item_quantity_url = reverse('decrease-cart-item-quantity', kwargs={'pk': 1})
        assert resolve(decrease_cart_item_quantity_url).func.view_class == DecreaseQuantityOfCartItemAPIView

    def test_delete_cart_item_url(self):
        delete_cart_item_url = reverse('delete-cart-item', kwargs={'pk': 1})
        assert resolve(delete_cart_item_url).func.view_class == DeleteCartItemAPIView
