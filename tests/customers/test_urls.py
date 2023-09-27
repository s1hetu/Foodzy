from django.urls import reverse, resolve

from customers.views import HomeView, CartView, ItemDetailView, DeliveryAgentRatings, RestaurantRatings


class TestCustomerUrls:
    def test_home_url(self):
        home_url = reverse('home')
        assert resolve(home_url).func.view_class == HomeView

    def test_cart_url(self):
        cart_url = reverse('cart')
        assert resolve(cart_url).func.view_class == CartView

    def test_cart_item_url(self):
        cart_item_url = reverse('cart-item', kwargs={'pk': 1})
        assert resolve(cart_item_url).func.view_class == ItemDetailView

    def test_delivery_agent_rating_url(self):
        delivery_agent_rating_url = reverse('delivery-agent-rating', kwargs={'pk': 1})
        assert resolve(delivery_agent_rating_url).func.view_class == DeliveryAgentRatings

    def test_restaurant_rating_url(self):
        restaurant_rating_url = reverse('restaurant-rating', kwargs={'pk': 1})
        assert resolve(restaurant_rating_url).func.view_class == RestaurantRatings
