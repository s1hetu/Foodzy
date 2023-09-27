import pytest
from django.urls import reverse

from carts.models import CartItems
from tests.constants import (
    CUSTOMER1_EMAIL, CART_ITEMS_OF_VALID_RESTAURANT
)


class TestCartAPIView:

    def test_create_cart_item(self, load_cart_prerequisite_data, test_password, login_user,
                              ):
        user_client, user = login_user(email=CUSTOMER1_EMAIL, password=test_password)
        url = reverse('create-cart-item')
        response = user_client.post(url, data={"item": 1})
        assert response.status_code == 201

    def test_create_cart_item_duplicate(self, load_cart_prerequisite_data, load_data, test_password, login_user,
                                        ):
        user_client, user = login_user(email=CUSTOMER1_EMAIL, password=test_password)
        url = reverse('create-cart-item')
        user_client.post(url, data={"item": 1})
        response = user_client.post(url, data={"item": 1})
        assert response.status_code == 400

    def test_increase_quantity_of_cart_item(self, load_cart_prerequisite_data, load_data, test_password, login_user,
                                            ):
        load_data(CART_ITEMS_OF_VALID_RESTAURANT)
        user_client, user = login_user(email=CUSTOMER1_EMAIL, password=test_password)
        url = reverse('increase-cart-item-quantity', kwargs={"pk": 1})
        response = user_client.post(url)
        cart_item = CartItems.objects.get(item__id=1)
        assert response.status_code == 200
        assert cart_item.quantity == 3

    def test_decrease_quantity_of_cart_item(self, load_cart_prerequisite_data, load_data, test_password, login_user,
                                            ):
        load_data(CART_ITEMS_OF_VALID_RESTAURANT)
        user_client, user = login_user(email=CUSTOMER1_EMAIL, password=test_password)
        url = reverse('decrease-cart-item-quantity', kwargs={"pk": 1})
        response = user_client.post(url)
        cart_item = CartItems.objects.get(item__id=1)
        assert response.status_code == 200
        assert cart_item.quantity == 1

    @pytest.mark.xfail(raises=CartItems.DoesNotExist)
    def test_delete_item_from_cart(self, load_cart_prerequisite_data, load_data, test_password, login_user,
                                   ):
        load_data(CART_ITEMS_OF_VALID_RESTAURANT)
        user_client, user = login_user(email=CUSTOMER1_EMAIL, password=test_password)
        url = reverse('delete-cart-item', kwargs={"pk": 1})
        response = user_client.post(url)
        assert response.status_code == 200
        # get deleted item from the cart
        CartItems.objects.get(item__id=1)
