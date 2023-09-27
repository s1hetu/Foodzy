import pytest
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed, assertRedirects

from accounts.models import User
from orders.models import Order
from restaurant.models import Items
from tests.constants import (
    COMMON_CUSTOMER1, COMMON_RESTAURANT6, COMMON_FIXTURE0, COMMON_AGENT4, ONE_ACCEPTED_ORDER_BY_AGENT,
    THREE_ORDERS_DELIVERED_AND_ONE_PICKED, PAGE_NOT_FOUND_404_TEMPLATE, COMMON_AGENT1, FORBIDDEN_403_TEMPLATE
)


class TestHomeView:
    url = reverse('home')
    template_name = 'customers/item_list.html'

    def test_get_request(self, client):
        response = client.get(self.url)
        assert response.status_code == 200
        assertTemplateUsed(response, self.template_name)

    def test_get_request_customer_login(self, load_data, test_password, login_user):
        load_data(COMMON_CUSTOMER1)
        user = User.objects.get(id=2)
        user_client, user = login_user(email=user.email, password=test_password)
        response = user_client.get(self.url)
        assert response.status_code == 200
        assertTemplateUsed(response, self.template_name)

    def test_get_request_customer_login_with_search_filter(self, load_data, test_password, login_user):
        load_data(COMMON_CUSTOMER1, COMMON_RESTAURANT6)
        user = User.objects.get(id=2)
        user_client, user = login_user(email=user.email, password=test_password)
        response = user_client.get(self.url, data={'searched': "res", "price_filter": "low_to_high"})
        assert response.status_code == 200
        assertTemplateUsed(response, self.template_name)

    def test_get_request_restaurant_login(self, load_data, test_password, login_user):
        load_data(COMMON_RESTAURANT6)
        owner = User.objects.get(id=15)
        owner_client, owner = login_user(email=owner.email, password=test_password)
        response = owner_client.get(self.url)
        assert response.status_code == 302
        assertRedirects(response, reverse('restaurant-admin'))

    def test_get_request_admin_login(self, load_data, login_user):
        load_data(COMMON_FIXTURE0)
        admin = User.objects.get(id=1)
        admin_client, user = login_user(email=admin.email, password="123")
        response = admin_client.get(self.url)
        assert response.status_code == 302
        assertRedirects(response, reverse('admin-home'))

    def test_get_request_agent_login(self, load_data, test_password, login_user):
        load_data(COMMON_AGENT4)
        agent = User.objects.get(id=8)
        agent_client, agent = login_user(email=agent.email, password=test_password)
        response = agent_client.get(self.url)
        assert response.status_code == 302
        assertRedirects(response, reverse('delivery-agent-panel'))


class TestCartView:
    url = reverse('cart')
    template_name = 'customers/cart.html'

    def test_get_request(self, client):
        response = client.get(self.url)
        assert response.status_code == 302
        assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_get_request_user_login(self, load_data, login_user, test_password):
        load_data(COMMON_CUSTOMER1, COMMON_RESTAURANT6)
        user = User.objects.get(id=2)
        user_client, user = login_user(email=user.email, password=test_password)
        response = user_client.get(self.url)
        assert response.status_code == 200
        assertTemplateUsed(response, self.template_name)


class TestItemDetailView:
    template_name = 'customers/item_detail.html'

    def test_get_request(self, load_data, client):
        load_data(COMMON_RESTAURANT6)
        item = Items.objects.get(id=1)
        url = reverse('cart-item', kwargs={'pk': item.id})
        response = client.get(url)
        assert response.status_code == 200
        assertTemplateUsed(response, self.template_name)

    def test_get_request_user_login(self, load_data, login_user, test_password):
        load_data(COMMON_CUSTOMER1, COMMON_RESTAURANT6)
        item = Items.objects.get(id=1)
        url = reverse('cart-item', kwargs={'pk': item.id})
        user = User.objects.get(id=2)
        user_client, user = login_user(email=user.email, password=test_password)
        response = user_client.get(url)
        assert response.status_code == 200
        assertTemplateUsed(response, self.template_name)


class TestDeliveryAgentRatingsView:
    template_name = 'customers/rating.html'
    order_data = COMMON_CUSTOMER1, COMMON_RESTAURANT6, COMMON_AGENT4, ONE_ACCEPTED_ORDER_BY_AGENT
    rated_order_data = COMMON_CUSTOMER1, COMMON_RESTAURANT6, COMMON_AGENT4, THREE_ORDERS_DELIVERED_AND_ONE_PICKED

    def test_get_request(self, load_data, client):
        load_data(self.order_data)
        order = Order.objects.get(id=1)
        url = reverse('delivery-agent-rating', kwargs={'pk': order.id})
        response = client.get(url)
        assert response.status_code == 302
        assertRedirects(response, f"{reverse('login')}?next={url}")

    def test_get_request_user_login(self, load_data, login_user, test_password):
        load_data(self.order_data)
        order = Order.objects.get(id=1)
        url = reverse('delivery-agent-rating', kwargs={'pk': order.id})
        user = User.objects.get(id=2)
        user_client, user = login_user(email=user.email, password=test_password)
        response = user_client.get(url)
        assert response.status_code == 200
        assertTemplateUsed(response, self.template_name)

    def test_get_request_user_login_invalid_order_id(self, load_data, login_user, test_password):
        load_data(self.order_data)
        url = reverse('delivery-agent-rating', kwargs={'pk': 100})
        user = User.objects.get(id=2)
        user_client, user = login_user(email=user.email, password=test_password)
        response = user_client.get(url)
        assert response.status_code == 404
        assertTemplateUsed(response, PAGE_NOT_FOUND_404_TEMPLATE)

    def test_get_request_different_user(self, load_data, login_user, test_password):
        load_data(self.order_data, COMMON_AGENT1)
        order = Order.objects.get(id=1)
        url = reverse('delivery-agent-rating', kwargs={'pk': order.id})
        user = User.objects.get(id=15)
        user_client, user = login_user(email=user.email, password=test_password)
        response = user_client.get(url)
        assert response.status_code == 403
        assertTemplateUsed(response, FORBIDDEN_403_TEMPLATE)

    def test_rate_agent_success(self, load_data, login_user, test_password):
        load_data(self.order_data)
        order = Order.objects.get(id=1)
        url = reverse('delivery-agent-rating', kwargs={'pk': order.id})
        user = User.objects.get(id=2)
        user_client, user = login_user(email=user.email, password=test_password)
        response = user_client.post(url, data={'rating': 3, 'review': "Very good"})
        assert response.status_code == 302
        assertRedirects(response, reverse('view-detail-order', kwargs={'pk': order.id}))

    def test_rate_agent_empty_form_submissioon(self, load_data, login_user, test_password):
        load_data(self.order_data)
        order = Order.objects.get(id=1)
        url = reverse('delivery-agent-rating', kwargs={'pk': order.id})
        user = User.objects.get(id=2)
        user_client, user = login_user(email=user.email, password=test_password)
        response = user_client.post(url)
        assert response.status_code == 302
        assertRedirects(response, reverse('delivery-agent-rating', kwargs={'pk': order.id}))

    @pytest.mark.parametrize('invalid_data', [{"rating": 0}, {"rating": 6}])
    def test_rate_agent_invalid_data(self, load_data, login_user, test_password, invalid_data):
        load_data(self.order_data)
        order = Order.objects.get(id=1)
        url = reverse('delivery-agent-rating', kwargs={'pk': order.id})
        user = User.objects.get(id=2)
        user_client, user = login_user(email=user.email, password=test_password)
        response = user_client.post(url, data=invalid_data)
        assert response.status_code == 302
        assertRedirects(response, reverse('delivery-agent-rating', kwargs={'pk': order.id}))

    def test_rate_agent_post_again(self, load_data, login_user, test_password):
        load_data(self.rated_order_data)
        order = Order.objects.get(id=1)
        url = reverse('delivery-agent-rating', kwargs={'pk': order.id})
        user = User.objects.get(id=2)
        user_client, user = login_user(email=user.email, password=test_password)
        response = user_client.post(url, data={'rating': 3, 'review': "Very good"})
        assert response.status_code == 400

    def test_rate_agent_get_again(self, load_data, login_user, test_password):
        load_data(self.rated_order_data)
        order = Order.objects.get(id=1)
        url = reverse('delivery-agent-rating', kwargs={'pk': order.id})
        user = User.objects.get(id=2)
        user_client, user = login_user(email=user.email, password=test_password)
        response = user_client.get(url)
        assert response.status_code == 404
        assertTemplateUsed(response, PAGE_NOT_FOUND_404_TEMPLATE)


class TestRestaurantRatingsView:
    template_name = 'customers/rating.html'
    order_data = COMMON_CUSTOMER1, COMMON_RESTAURANT6, COMMON_AGENT4, ONE_ACCEPTED_ORDER_BY_AGENT
    rated_order_data = COMMON_CUSTOMER1, COMMON_RESTAURANT6, COMMON_AGENT4, THREE_ORDERS_DELIVERED_AND_ONE_PICKED

    def test_get_request(self, load_data, client):
        load_data(self.order_data)
        order = Order.objects.get(id=1)
        url = reverse('restaurant-rating', kwargs={'pk': order.id})
        response = client.get(url)
        assert response.status_code == 302
        assertRedirects(response, f"{reverse('login')}?next={url}")

    def test_get_request_user_login(self, load_data, login_user, test_password):
        load_data(self.order_data)
        order = Order.objects.get(id=1)
        url = reverse('restaurant-rating', kwargs={'pk': order.id})
        user = User.objects.get(id=2)
        user_client, user = login_user(email=user.email, password=test_password)
        response = user_client.get(url)
        assert response.status_code == 200
        assertTemplateUsed(response, self.template_name)

    def test_rate_restaurant_success(self, load_data, login_user, test_password):
        load_data(self.order_data)
        order = Order.objects.get(id=1)
        url = reverse('restaurant-rating', kwargs={'pk': order.id})
        user = User.objects.get(id=2)
        user_client, user = login_user(email=user.email, password=test_password)
        response = user_client.post(url, data={'rating': 3, 'review': "Very good"})
        assert response.status_code == 302
        assertRedirects(response, reverse('view-detail-order', kwargs={'pk': order.id}))

    def test_rate_restaurant_empty_form_submissioon(self, load_data, login_user, test_password):
        load_data(self.order_data)
        order = Order.objects.get(id=1)
        url = reverse('restaurant-rating', kwargs={'pk': order.id})
        user = User.objects.get(id=2)
        user_client, user = login_user(email=user.email, password=test_password)
        response = user_client.post(url)
        assert response.status_code == 302
        assertRedirects(response, reverse('restaurant-rating', kwargs={'pk': order.id}))

    @pytest.mark.parametrize('invalid_data', [{"rating": 0}, {"rating": 6}])
    def test_rate_restaurant_invalid_data(self, load_data, login_user, test_password, invalid_data):
        load_data(self.order_data)
        order = Order.objects.get(id=1)
        url = reverse('restaurant-rating', kwargs={'pk': order.id})
        user = User.objects.get(id=2)
        user_client, user = login_user(email=user.email, password=test_password)
        response = user_client.post(url, data=invalid_data)
        assert response.status_code == 302
        assertRedirects(response, reverse('restaurant-rating', kwargs={'pk': order.id}))

    def test_rate_restaurant_again(self, load_data, login_user, test_password):
        load_data(self.rated_order_data)
        order = Order.objects.get(id=1)
        url = reverse('restaurant-rating', kwargs={'pk': order.id})
        user = User.objects.get(id=2)
        user_client, user = login_user(email=user.email, password=test_password)
        response = user_client.post(url, data={'rating': 3, 'review': "Very good"})
        assert response.status_code == 400

    def test_rate_restaurant_view_again(self, load_data, login_user, test_password):
        load_data(self.rated_order_data)
        order = Order.objects.get(id=1)
        url = reverse('restaurant-rating', kwargs={'pk': order.id})
        user = User.objects.get(id=2)
        user_client, user = login_user(email=user.email, password=test_password)
        response = user_client.get(url)
        assert response.status_code == 404
        assertTemplateUsed(response, PAGE_NOT_FOUND_404_TEMPLATE)
