from accounts.models import User
from carts.models import Cart, CartItems
from tests.constants import (
    CART_ITEMS_OF_VALID_RESTAURANT, COMMON_CUSTOMER1, CART_ITEMS_FOR_BLOCKED_RESTAURANTS, COMMON_RESTAURANT9,
    COMMON_RESTAURANT8, CART_ITEMS_FOR_RESTAURANT_NOT_ACCEPTING_ORDER, CART_ITEMS_NOT_AVAILABLE_QUANTITY_WISE,
    COMMON_RESTAURANT6, COMMON_RESTAURANT7, CART_ITEMS_OF_DIFFERENT_RESTAURANTS
)


class TestCartMethods:

    def test_get_total(self, load_cart_prerequisite_data, load_data):
        load_data(CART_ITEMS_OF_VALID_RESTAURANT)
        assert Cart.get_total(user=User.objects.get(id=2)) == 335.00

    def test_str(self, load_cart_prerequisite_data, load_data):
        load_data(CART_ITEMS_OF_VALID_RESTAURANT)
        assert str(Cart.objects.get(id=1)) == "Cart-1 User-2"


class TestCartItemsMethods:

    def test_get_all_user_items(self, load_cart_prerequisite_data, load_data):
        assert not list(CartItems.get_all_user_items(user_id=2).values_list('id', flat=True))
        load_data(CART_ITEMS_OF_VALID_RESTAURANT)
        assert list(
            CartItems.get_all_user_items(user_id=2).values_list('id', flat=True)) == [5, 6]

    def test_check_unavailability_of_item_scenario1(self, load_cart_prerequisite_data, load_data):
        """
        For This case All item is available
        """
        load_data(CART_ITEMS_OF_VALID_RESTAURANT)
        assert CartItems.check_unavailability_of_item(user_id=2) == False

    def test_check_unavailability_of_item_scenario2(self, load_data):
        """
        For This user's cart contain restaurant item , which is blocked
        """
        load_data(COMMON_CUSTOMER1,
                  COMMON_RESTAURANT9,
                  CART_ITEMS_FOR_BLOCKED_RESTAURANTS)
        assert CartItems.check_unavailability_of_item(user_id=2) == True

    def test_check_unavailability_of_item_scenario3(self, load_data):
        """
        For This user's cart contain restaurant item , which is not accepting order currently
        """
        load_data(COMMON_CUSTOMER1,
                  COMMON_RESTAURANT8,
                  CART_ITEMS_FOR_RESTAURANT_NOT_ACCEPTING_ORDER)
        assert CartItems.check_unavailability_of_item(user_id=2) == True

    def test_get_cart_item(self, load_cart_prerequisite_data, load_data):
        load_data(CART_ITEMS_OF_VALID_RESTAURANT)
        cart_item = CartItems.get_cart_item(pk=1, user_id=2)
        assert cart_item.cart.id == 1
        assert cart_item.item.id == 1
        assert cart_item.quantity == 2
        assert cart_item.total == 90.00

    def test_get_unavailable_items(self, load_cart_prerequisite_data, load_data):
        """
        For This user's cart contain item quantity which is not available in restaurant ,
        """
        load_data(CART_ITEMS_NOT_AVAILABLE_QUANTITY_WISE)
        assert CartItems.get_unavailable_items() != False

    def test_get_cart_item_restaurant_wise(self, load_data):
        load_data(COMMON_CUSTOMER1,
                  COMMON_RESTAURANT6,
                  COMMON_RESTAURANT7)
        load_data(CART_ITEMS_OF_DIFFERENT_RESTAURANTS)

        cart_items = CartItems.get_all_user_items(user_id=2)
        data = CartItems.get_cart_item_restaurant_wise(cart_items)
        result_data_keys = [6, 7]
        result_item_values = [1, 5]
        for restaurant_id, details, result_restaurant_id, result_item_id in zip(data.keys(), data.values(),
                                                                                result_data_keys,
                                                                                result_item_values):
            assert restaurant_id == result_restaurant_id
            assert details[0]['item'].id == result_item_id

    def test_get_item_total_cartitems(self, load_cart_prerequisite_data, load_data):
        """
        For This user's cart contain item quantity which is not available in restaurant ,
        """
        load_data(CART_ITEMS_OF_VALID_RESTAURANT)
        cart_items = CartItems.get_all_user_items(user_id=2)
        assert CartItems.get_item_total_cartitems(cart_items=cart_items, restaurant_id=6) == 190.00
