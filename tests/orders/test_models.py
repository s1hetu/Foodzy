import pytest

from accounts.models import User
from orders.models import Order, OrderItems, OrderConfirmOtp
from tests.constants import (
    TWO_DELIVERED_ORDER_FOR_SAME_RESTAURANTS, ORDER_FOR_DIFFERENT_RESTAURANTS,
    THREE_ORDERS_DELIVERED_AND_ONE_PICKED,
    COMMON_RESTAURANT7, ONE_ACCEPTED_ORDER_BY_AGENT
)


class TestOrderMethods:
    @pytest.mark.parametrize('param, result',
                             [('1', [1, 2]), ('res6 Name', [1, 2]), ('res7 Name', []), ('customer1', [1, 2]),
                              ('customer145', [])])
    def test_get_order_with_search_params(self, load_order_prerequisite_data, param, result, load_data):
        load_data(TWO_DELIVERED_ORDER_FOR_SAME_RESTAURANTS)
        assert list(Order.get_order_with_search_params(params=param, queryset=Order.objects.all()). \
                    values_list('id', flat=True)) == result

    def test_get_orders(self, load_order_prerequisite_data, load_data):
        load_data(TWO_DELIVERED_ORDER_FOR_SAME_RESTAURANTS)
        assert list(Order.get_orders().values_list('id', flat=True)) == [1, 2]

    @pytest.mark.parametrize('data_to_load, result_order_list, status',
                             [(ORDER_FOR_DIFFERENT_RESTAURANTS, [1, 2], "waiting"),
                              (THREE_ORDERS_DELIVERED_AND_ONE_PICKED, [4],
                               "ready to pick"),
                              (THREE_ORDERS_DELIVERED_AND_ONE_PICKED, [1, 2, 3],
                               "delivered")])
    def test_get_order_from_status(self, load_order_prerequisite_data, load_data, data_to_load, result_order_list,
                                   status):
        load_data(COMMON_RESTAURANT7)
        load_data(data_to_load)
        assert list(Order.get_order_from_status(params=status, queryset=Order.objects.all()). \
                    values_list('id', flat=True)) == result_order_list

    @pytest.mark.parametrize('data_to_load, result_order_list, status',
                             [(ORDER_FOR_DIFFERENT_RESTAURANTS, [1, 2], "waiting"),
                              (THREE_ORDERS_DELIVERED_AND_ONE_PICKED, [4],
                               "ready to pick"),
                              (THREE_ORDERS_DELIVERED_AND_ONE_PICKED, [1, 2, 3],
                               "delivered")])
    def test_get_order_from_status_without_queryset(self, load_order_prerequisite_data, load_data, data_to_load,
                                                    result_order_list,
                                                    status):
        load_data(COMMON_RESTAURANT7)
        load_data(data_to_load)
        assert list(Order.get_order_from_status(params=status). \
                    values_list('id', flat=True)) == result_order_list

    def test_get_order_from_restaurant_id(self, load_order_prerequisite_data, load_data):
        load_data(TWO_DELIVERED_ORDER_FOR_SAME_RESTAURANTS)
        assert list(Order.get_order_from_restaurant_id(params=6). \
                    values_list('id', flat=True)) == [1, 2]

    def test_get_object_from_pk(self, load_order_prerequisite_data, load_data):
        load_data(TWO_DELIVERED_ORDER_FOR_SAME_RESTAURANTS)
        order_object = Order.get_object_from_pk(1)
        assert order_object.user.id == 2
        assert order_object.restaurant.id == 6
        assert order_object.total == 150.00

    def test_get_total_of_all_orders(self, load_order_prerequisite_data, load_data):
        load_data(TWO_DELIVERED_ORDER_FOR_SAME_RESTAURANTS)
        assert Order.get_total_of_all_orders() == 390.00

    def test_get_user_orders(self, load_order_prerequisite_data, load_data):
        load_data(TWO_DELIVERED_ORDER_FOR_SAME_RESTAURANTS)
        assert list(Order.get_user_orders(user=User.objects.get(id=2)). \
                    values_list('id', flat=True)) == [1, 2]

    @pytest.mark.parametrize('order_id, is_paid', [(1, True), (2, True), (4, False)])
    def test_is_order_paid(self, load_order_prerequisite_data, load_data, order_id, is_paid):
        load_data(THREE_ORDERS_DELIVERED_AND_ONE_PICKED)
        assert Order.is_order_paid(order_id=order_id) == is_paid

    @pytest.mark.parametrize('order_id, status', [(1, 'delivered'), (2, 'delivered'), (4, 'ready to pick')])
    def test_get_order_status(self, load_order_prerequisite_data, load_data, order_id, status):
        load_data(THREE_ORDERS_DELIVERED_AND_ONE_PICKED)
        assert Order.get_order_status(order_id=order_id) == status

    def test_get_orders_count(self, load_order_prerequisite_data, load_data):
        load_data(TWO_DELIVERED_ORDER_FOR_SAME_RESTAURANTS)
        assert Order.get_orders_count() == 2

    def test_get_delivered_orders(self, load_order_prerequisite_data, load_data):
        load_data(TWO_DELIVERED_ORDER_FOR_SAME_RESTAURANTS)
        assert list(Order.get_delivered_orders().values_list('id',
                                                             flat=True)) == [1, 2]

    def test_get_delivered_orders_with_queryset(self, load_order_prerequisite_data, load_data):
        load_data(TWO_DELIVERED_ORDER_FOR_SAME_RESTAURANTS)
        assert list(Order.get_delivered_orders(queryset=Order.objects.all()).values_list('id',
                                                                                         flat=True)) == [1, 2]

    def test_get_delivered_orders_count(self, load_order_prerequisite_data, load_data):
        load_data(TWO_DELIVERED_ORDER_FOR_SAME_RESTAURANTS)
        assert Order.get_delivered_orders_count() == 2

    def test_get_orders_from_payment_id(self, load_order_prerequisite_data, load_data):
        load_data(TWO_DELIVERED_ORDER_FOR_SAME_RESTAURANTS)
        assert Order.get_orders_from_payment_id(payment_id="ssssss").count() == 0

    def test_get_restaurant_orders(self, load_order_prerequisite_data, load_data):
        load_data(TWO_DELIVERED_ORDER_FOR_SAME_RESTAURANTS)
        assert list(Order.get_restaurant_orders(restaurant=6).values_list('id', flat=True)) == [2, 1]

    def test_get_current_orders(self, load_order_prerequisite_data, load_data):
        load_data(THREE_ORDERS_DELIVERED_AND_ONE_PICKED)
        available_order = [4]
        assert list(Order.get_current_orders(restaurant=6).values_list('id',
                                                                       flat=True)) == available_order

    def test_get_restaurant_orders_count(self, load_order_prerequisite_data, load_data):
        load_data(TWO_DELIVERED_ORDER_FOR_SAME_RESTAURANTS)
        assert Order.get_restaurant_orders_count(restaurant=6) == 2

    def test_get_restaurant_orders_revenue(self, load_order_prerequisite_data, load_data):
        load_data(TWO_DELIVERED_ORDER_FOR_SAME_RESTAURANTS)
        assert Order.get_restaurant_orders_revenue(restaurant=6)['total__sum'] == 390.00

    def test_get_pending_restaurant_orders(self, load_order_prerequisite_data, load_data):
        load_data(ONE_ACCEPTED_ORDER_BY_AGENT)
        assert not list(Order.get_pending_restaurant_orders(restaurant=6).values_list('id', flat=True))


class TestOrderItemsMethods:

    def test_get_discounted_price(self, load_order_prerequisite_data, load_data):
        load_data(TWO_DELIVERED_ORDER_FOR_SAME_RESTAURANTS)
        order_item = OrderItems.objects.get(id=1)
        assert order_item.get_discounted_price() == 45.0

    def test_get_items_total(self, load_order_prerequisite_data, load_data):
        load_data(TWO_DELIVERED_ORDER_FOR_SAME_RESTAURANTS)
        order_item = OrderItems.objects.get(id=1)
        assert order_item.get_items_total() == 90.0

    def test_get_order_items_from_order(self, load_order_prerequisite_data, load_data):
        load_data(TWO_DELIVERED_ORDER_FOR_SAME_RESTAURANTS)
        assert list(
            OrderItems.get_order_items_from_order(order=Order.objects.get(id=1)).values_list('id', flat=True)) == [1]

    def test_get_items_from_order_id(self, load_order_prerequisite_data, load_data):
        load_data(TWO_DELIVERED_ORDER_FOR_SAME_RESTAURANTS)
        assert list(
            OrderItems.get_items_from_order_id(pk=1).values_list('id', flat=True)) == [1]


class TestOrderConfirmOtpMethods:
    def test_generate_otp_code(self):
        assert OrderConfirmOtp.generate_otp_code()

    def test_str(self, load_order_prerequisite_data, load_data):
        load_data(ONE_ACCEPTED_ORDER_BY_AGENT)
        assert str(OrderConfirmOtp.objects.get(order=1)) == 'Order-1 User-2'
