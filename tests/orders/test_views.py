import pytest
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from tests.constants import (
    COMMON_RESTAURANT7, ORDER_FOR_DIFFERENT_RESTAURANTS, CUSTOMER1_EMAIL, CART_ITEMS_OF_VALID_RESTAURANT,
    COMMON_RESTAURANT6, CART_ITEMS_NOT_AVAILABLE_QUANTITY_WISE, CART_ITEMS_OF_NOT_AVAILABLE_LOCATION_WISE,
    CART_ITEMS_FOR_RESTAURANT_NOT_ACCEPTING_ORDER, COMMON_RESTAURANT8, COMMON_CUSTOMER1
)


class TestOrderView:
    DETAIL_ORDER_VIEW_TEMPLATE = 'orders/detail_order.html'
    ORDERS_VIEW_TEMPLATE = 'orders/orders.html'
    DOWNLOAD_INVOICE_VIEW = 'customers/invoice.html'
    PLACE_ORDER_TEMPLATE = 'orders/pay_now.html'

    def test_detail_order_view(self, load_order_prerequisite_data, load_data, test_password, login_user, ):
        load_data(COMMON_RESTAURANT7, ORDER_FOR_DIFFERENT_RESTAURANTS)
        user_client, user = login_user(email=CUSTOMER1_EMAIL, password=test_password)
        url = reverse('view-detail-order', kwargs={"pk": 1})
        response = user_client.get(url)
        assert response.status_code == 200
        assertTemplateUsed(response, self.DETAIL_ORDER_VIEW_TEMPLATE)

    def test_orders_view(self, load_order_prerequisite_data, load_data, test_password, login_user, ):
        load_data(COMMON_RESTAURANT7, ORDER_FOR_DIFFERENT_RESTAURANTS)
        user_client, user = login_user(email=CUSTOMER1_EMAIL, password=test_password)
        url = reverse('orders')
        response = user_client.get(url)
        assert response.status_code == 200
        assertTemplateUsed(response, self.ORDERS_VIEW_TEMPLATE)

    def test_download_invoice_view(self, load_order_prerequisite_data, load_data, test_password, login_user, ):
        load_data(COMMON_RESTAURANT7, ORDER_FOR_DIFFERENT_RESTAURANTS)
        user_client, user = login_user(email=CUSTOMER1_EMAIL, password=test_password)
        url = reverse('download-invoice', kwargs={"pk": 1})
        response = user_client.get(url)
        assert response.status_code == 200
        assertTemplateUsed(response, self.DOWNLOAD_INVOICE_VIEW)

    def test_place_order(self, load_cart_prerequisite_data, load_data, test_password, login_user, ):
        load_data(CART_ITEMS_OF_VALID_RESTAURANT)
        user_client, user = login_user(email=CUSTOMER1_EMAIL, password=test_password)
        url = reverse('place-order')
        response = user_client.get(url)
        assert response.status_code == 200
        assertTemplateUsed(response, self.PLACE_ORDER_TEMPLATE)

    @pytest.mark.parametrize('data_fixture_path', [
        (COMMON_RESTAURANT6,),
        (COMMON_RESTAURANT7, CART_ITEMS_OF_NOT_AVAILABLE_LOCATION_WISE),
        (COMMON_RESTAURANT6, CART_ITEMS_NOT_AVAILABLE_QUANTITY_WISE),
        (COMMON_RESTAURANT8, CART_ITEMS_FOR_RESTAURANT_NOT_ACCEPTING_ORDER)
    ])
    def test_place_order_with_failure(self, load_data, test_password, login_user,
                                      data_fixture_path):
        """
        1. place order with empty cart\
        2. place order with item in cart and user both located in different city or not in range to deliver order
        3. place order from cart with restaurant item ,required quantity of order is not available in restaurant
        4. place order from cart with restaurant item, when restaurant is not accepting order
        """
        load_data(COMMON_CUSTOMER1, *data_fixture_path)
        user_client, user = login_user(email=CUSTOMER1_EMAIL, password=test_password)
        url = reverse('place-order')
        response = user_client.get(url)
        assert response.status_code == 302

    def test_order_payment_method(self, load_cart_prerequisite_data, load_data, test_password, login_user, ):
        load_data(CART_ITEMS_OF_VALID_RESTAURANT)
        user_client, user = login_user(email=CUSTOMER1_EMAIL, password=test_password)
        url = reverse('order-payment-method')
        response = user_client.get(url)
        assert response.status_code == 200

    def test_cod(self, load_cart_prerequisite_data, load_data, test_password, login_user, ):
        load_data(CART_ITEMS_OF_VALID_RESTAURANT)
        user_client, user = login_user(email=CUSTOMER1_EMAIL, password=test_password)
        url = reverse('cod-payment')
        response = user_client.get(url)
        assert response.status_code == 200
        assertTemplateUsed(response, self.ORDERS_VIEW_TEMPLATE)
