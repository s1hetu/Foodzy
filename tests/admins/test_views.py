import contextlib
from decimal import Decimal
from unittest.mock import patch

import pytest
import requests
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed, assertRedirects

from accounts.models import User
from orders.models import Order
from tests.constants import (
    CUSTOMER1_EMAIL, AGENT2_EMAIL, RES2_EMAIL, ADMIN_EMAIL,
    ADMIN_PANEL_TEMPLATE_NAME, DRIVERS_LIST_TEMPLATE_NAME, DRIVERS_APPLICATION_DETAIL_TEMPLATE_NAME,
    USERS_LIST_TEMPLATE_NAME, RESTAURANT_LIST_TEMPLATE_NAME, USERS_DETAIL_TEMPLATE_NAME,
    RESTAURANT_APPLICATION_LIST_TEMPLATE_NAME, RES1_EMAIL, RES3_EMAIL,
    RES4_EMAIL, RESTAURANT_DETAIL_TEMPLATE_NAME, RESTAURANT_APPLICATION_DETAIL_TEMPLATE_NAME,
    THREE_ORDERS_DELIVERED_AND_ONE_PICKED, ORDERS_LIST_TEMPLATE_NAME, ORDERS_DETAIL_TEMPLATE_NAME,
    COD_AGENT_LIST_TEMPLATE_NAME, COD_AGENT_DETAIL_TEMPLATE_NAME, ORDER_FOR_SAME_RESTAURANTS,
    DRIVERS_APPLICATION_LIST_TEMPLATE_NAME, FORBIDDEN_403_TEMPLATE
)


class TestAdminHome:
    url = reverse('admin-home')

    @pytest.mark.parametrize(
        'user_email',
        [
            CUSTOMER1_EMAIL,
            AGENT2_EMAIL,
            RES2_EMAIL
        ]
    )
    def test_admin_panel_login_forbidden(self, user_email, login_user, test_password, load_admin_panel_data):
        client, _ = login_user(email=user_email, password=test_password)

        response = client.get(self.url)

        assert response.status_code == 403
        assertTemplateUsed(response, FORBIDDEN_403_TEMPLATE)

    def test_admin_panel_login_success(self, login_user, test_admin_password, load_admin_panel_data):
        client, _ = login_user(email=ADMIN_EMAIL, password=test_admin_password)

        response = client.get(self.url)

        assert response.status_code == 200
        assertTemplateUsed(response, ADMIN_PANEL_TEMPLATE_NAME)


class TestDriversListView:
    def test_drivers_list_view(self, load_admin_panel_data, login_user, test_admin_password):
        client, _ = login_user(email=ADMIN_EMAIL, password=test_admin_password)
        response = client.get(reverse('drivers-list'))

        assert response.status_code == 200
        assertTemplateUsed(response, DRIVERS_LIST_TEMPLATE_NAME)
        assert response.context['drivers'].count() == 3

    def test_drivers_list_view_status_filter(self, load_admin_panel_data, login_user, test_admin_password):
        client, _ = login_user(email=ADMIN_EMAIL, password=test_admin_password)
        response = client.get(f"{reverse('drivers-list')}?user_status[]=verified")
        assert response.status_code == 200
        assertTemplateUsed(response, DRIVERS_LIST_TEMPLATE_NAME)
        assert response.context['drivers'].count() == 1

    def test_drivers_list_view_params(self, load_admin_panel_data, login_user, test_admin_password):
        client, _ = login_user(email=ADMIN_EMAIL, password=test_admin_password)
        response = client.get(f"{reverse('drivers-list')}?agent=agent2")
        assert response.status_code == 200
        assertTemplateUsed(response, DRIVERS_LIST_TEMPLATE_NAME)
        assert response.context['drivers'].count() == 1


class TestDriversApplicationListView:
    def test_drivers_application_list_view(self, login_user, test_admin_password, load_admin_panel_data):
        client, _ = login_user(email=ADMIN_EMAIL, password=test_admin_password)

        response = client.get(reverse('drivers-list-application'))

        assert response.status_code == 200
        assertTemplateUsed(response, DRIVERS_APPLICATION_LIST_TEMPLATE_NAME)
        assert response.context['drivers'].count() == 2

    def test_drivers_list_view_params(self, load_admin_panel_data, login_user, test_admin_password):
        client, _ = login_user(email=ADMIN_EMAIL, password=test_admin_password)
        response = client.get(f"{reverse('drivers-list-application')}?agent=agent2")
        assert response.status_code == 200
        assertTemplateUsed(response, DRIVERS_APPLICATION_LIST_TEMPLATE_NAME)
        assert response.context['drivers'].count() == 1


class TestDriversApplicationDetailView:
    @pytest.mark.parametrize(
        'agent_email',
        [
            'agent1@test.com',
            'agent2@test.com',
        ]
    )
    def test_drivers_application_detail_view(
            self, agent_email, login_user, test_admin_password, load_admin_panel_data
    ):
        agent = User.objects.get(email=agent_email)

        client, _ = login_user(email=ADMIN_EMAIL, password=test_admin_password)

        response = client.get(reverse('drivers-detail-application', kwargs={'pk': agent.id}))
        assert response.status_code == 200
        assertTemplateUsed(response, DRIVERS_APPLICATION_DETAIL_TEMPLATE_NAME)
        assert response.context['agent_user'] == agent


class TestDriversDetailView:
    @pytest.mark.parametrize(
        'agent_email',
        [
            'agent1@test.com',
            'agent2@test.com',
        ]
    )
    def test_drivers_detail_view(self, agent_email, login_user, test_admin_password, load_admin_panel_data):
        agent = User.objects.get(email=agent_email)

        client, _ = login_user(email=ADMIN_EMAIL, password=test_admin_password)

        response = client.get(reverse('drivers-detail-application', kwargs={'pk': agent.id}))
        assert response.status_code == 200
        assertTemplateUsed(response, DRIVERS_APPLICATION_DETAIL_TEMPLATE_NAME)
        assert response.context['agent_user'] == agent


class TestUsersListView:
    def test_users_list_view(self, login_user, test_admin_password, load_admin_panel_data):
        client, _ = login_user(email=ADMIN_EMAIL, password=test_admin_password)
        response = client.get(reverse('users-list'))

        assert response.status_code == 200
        assertTemplateUsed(response, USERS_LIST_TEMPLATE_NAME)
        assert response.context['users'].count() == 3

    def test_users_list_view_status_filter(self, load_admin_panel_data, login_user, test_admin_password):
        client, _ = login_user(email=ADMIN_EMAIL, password=test_admin_password)
        response = client.get(f"{reverse('users-list')}?user_status[]=active")
        assert response.status_code == 200
        assertTemplateUsed(response, USERS_LIST_TEMPLATE_NAME)
        assert response.context['users'].count() == 1

    def test_users_list_view_params(self, load_admin_panel_data, login_user, test_admin_password):
        client, _ = login_user(email=ADMIN_EMAIL, password=test_admin_password)
        response = client.get(f"{reverse('users-list')}?search_user=customer1")
        assert response.status_code == 200
        assertTemplateUsed(response, USERS_LIST_TEMPLATE_NAME)
        assert response.context['users'].count() == 1


class TestUsersDetailView:
    def test_users_detail_view(self, login_user, test_admin_password, load_admin_panel_data):
        user = User.objects.get(id=2)

        client, _ = login_user(email=ADMIN_EMAIL, password=test_admin_password)

        response = client.get(reverse('users-detail', kwargs={'pk': 2}))
        assert response.status_code == 200
        assertTemplateUsed(response, USERS_DETAIL_TEMPLATE_NAME)
        assert response.context['user_obj'] == user


class TestRestaurantListView:
    def test_restaurants_list_view(self, login_user, test_admin_password, load_admin_panel_data):
        client, _ = login_user(email=ADMIN_EMAIL, password=test_admin_password)
        response = client.get(reverse('restaurant-list'))

        assert response.status_code == 200
        assertTemplateUsed(response, RESTAURANT_LIST_TEMPLATE_NAME)
        assert response.context['restaurants'].count() == 3

    def test_restaurants_list_view_status_filter(self, load_admin_panel_data, login_user, test_admin_password):
        client, _ = login_user(email=ADMIN_EMAIL, password=test_admin_password)
        response = client.get(f"{reverse('restaurant-list')}?restaurant_status[]=verified")
        assert response.status_code == 200
        assertTemplateUsed(response, RESTAURANT_LIST_TEMPLATE_NAME)
        assert response.context['restaurants'].count() == 2

    def test_restaurants_list_view_params(self, load_admin_panel_data, login_user, test_admin_password):
        client, _ = login_user(email=ADMIN_EMAIL, password=test_admin_password)
        response = client.get(f"{reverse('restaurant-list')}?restaurant_search=res")
        assert response.status_code == 200
        assertTemplateUsed(response, RESTAURANT_LIST_TEMPLATE_NAME)
        assert response.context['restaurants'].count() == 3


class TestRestaurantApplicationListView:
    def test_restaurants_application_list_view(self, login_user, test_admin_password, load_admin_panel_data):
        client, _ = login_user(email=ADMIN_EMAIL, password=test_admin_password)
        response = client.get(reverse('restaurant-list-application'))

        assert response.status_code == 200
        assertTemplateUsed(response, RESTAURANT_APPLICATION_LIST_TEMPLATE_NAME)
        assert response.context['restaurants'].count() == 3

    def test_restaurants_application_list_view_params(self, load_admin_panel_data, login_user, test_admin_password):
        client, _ = login_user(email=ADMIN_EMAIL, password=test_admin_password)
        response = client.get(f"{reverse('restaurant-list-application')}?restaurant_search=res")
        assert response.status_code == 200
        assertTemplateUsed(response, RESTAURANT_APPLICATION_LIST_TEMPLATE_NAME)
        assert response.context['restaurants'].count() == 3


class TestRestaurantsDetailView:
    @pytest.mark.parametrize(
        'restaurant_owner_email',
        [
            RES1_EMAIL,
            RES2_EMAIL,
            RES3_EMAIL,
            RES4_EMAIL,
        ]
    )
    def test_restaurant_detail_view(
            self, restaurant_owner_email, login_user, test_admin_password, load_admin_panel_data
    ):
        restaurant_owner = User.objects.get(email=restaurant_owner_email)
        restaurant = restaurant_owner.restaurants.first()

        client, _ = login_user(email=ADMIN_EMAIL, password=test_admin_password)

        response = client.get(reverse('restaurant-detail', kwargs={'pk': restaurant.id}))
        assert response.status_code == 200
        assertTemplateUsed(response, RESTAURANT_DETAIL_TEMPLATE_NAME)
        assert response.context['restaurant'] == restaurant


class TestRestaurantApplicationDetailView:
    @pytest.mark.parametrize(
        'restaurant_owner_email',
        [
            RES1_EMAIL,
            RES2_EMAIL,
            RES3_EMAIL,
        ]
    )
    def test_restaurant_application_detail_view(
            self, restaurant_owner_email, login_user, test_admin_password, load_admin_panel_data
    ):
        restaurant_owner = User.objects.get(email=restaurant_owner_email)
        restaurant = restaurant_owner.restaurants.first()

        client, _ = login_user(email=ADMIN_EMAIL, password=test_admin_password)

        response = client.get(reverse('restaurant-detail-application', kwargs={'pk': restaurant.id}))
        assert response.status_code == 200
        assertTemplateUsed(response, RESTAURANT_APPLICATION_DETAIL_TEMPLATE_NAME)
        assert response.context['restaurant'] == restaurant


class TestOrdersListView:
    def test_orders_list_view(
            self,
            login_user, test_admin_password, load_admin_panel_data, load_data
    ):
        client, _ = login_user(email=ADMIN_EMAIL, password=test_admin_password)
        load_data(THREE_ORDERS_DELIVERED_AND_ONE_PICKED)
        client, _ = login_user(email=ADMIN_EMAIL, password=test_admin_password)
        response = client.get(reverse('orders-list'))
        assert response.status_code == 200
        assertTemplateUsed(response, ORDERS_LIST_TEMPLATE_NAME)
        assert len(response.context['orders']) == 3

    @pytest.mark.parametrize(
        ['params_key', 'params_value', 'result'],
        [
            ['order', '1', 3],
            ['order', 'customer', 3],
            ['order_status', 'ready to pick', 1],
            ['order_status', 'delivered', 3],
            ['restaurant', '1', 0],
        ]
    )
    def test_orders_list_view_params(self, load_admin_panel_data, login_user, test_admin_password, params_key,
                                     params_value,
                                     result, load_data):
        load_data(THREE_ORDERS_DELIVERED_AND_ONE_PICKED)
        client, _ = login_user(email=ADMIN_EMAIL, password=test_admin_password)
        response = client.get(f"{reverse('orders-list')}?{params_key}={params_value}")
        assert response.status_code == 200
        assertTemplateUsed(response, ORDERS_LIST_TEMPLATE_NAME)
        assert response.context['orders'].count() == result


class TestOrdersDetailView:
    def test_order_detail_view(self, login_user, test_admin_password, load_admin_panel_data, load_data):
        load_data(THREE_ORDERS_DELIVERED_AND_ONE_PICKED)

        client, _ = login_user(email=ADMIN_EMAIL, password=test_admin_password)
        response = client.get(reverse('orders-detail', kwargs={'pk': 1}))

        assert response.status_code == 200
        assertTemplateUsed(response, ORDERS_DETAIL_TEMPLATE_NAME)
        assert response.context['order'] == Order.objects.get(id=1)


class TestCodAgentListView:

    def test_cod_agent_list_view(self, login_user, test_admin_password, load_admin_panel_data):
        client, _ = login_user(email=ADMIN_EMAIL, password=test_admin_password)
        response = client.get(reverse('cod-agents-list'))

        assert response.status_code == 200
        assertTemplateUsed(response, COD_AGENT_LIST_TEMPLATE_NAME)
        assert response.context['agents'].count() == 3

    def test_cod_agent_list_view_params(self, load_admin_panel_data, login_user, test_admin_password):
        client, _ = login_user(email=ADMIN_EMAIL, password=test_admin_password)
        response = client.get(f"{reverse('cod-agents-list')}?agent=agent")
        assert response.status_code == 200
        assertTemplateUsed(response, COD_AGENT_LIST_TEMPLATE_NAME)
        assert response.context['agents'].count() == 3


class TestCodAgentDetailView:
    def test_cod_agent_detail_view(self, login_user, test_admin_password, load_admin_panel_data, load_data):
        agent_user = User.objects.get(id=8)
        load_data(THREE_ORDERS_DELIVERED_AND_ONE_PICKED)

        client, _ = login_user(email=ADMIN_EMAIL, password=test_admin_password)
        response = client.get(reverse('cod-agent-detail', kwargs={'pk': 8}))

        assert response.status_code == 200
        assertTemplateUsed(response, COD_AGENT_DETAIL_TEMPLATE_NAME)
        assert response.context['agent_user'] == agent_user

        assert response.context['total_cash'] == Decimal('630.00')


class TestActionForRestaurantView:
    @pytest.mark.parametrize("order_data", [ORDER_FOR_SAME_RESTAURANTS, THREE_ORDERS_DELIVERED_AND_ONE_PICKED])
    def test_action_for_restaurant_view_block(self, login_user, test_admin_password, load_admin_panel_data, load_data,
                                              order_data):
        client, _ = login_user(email=ADMIN_EMAIL, password=test_admin_password)
        load_data(order_data)
        data = {'restaurant_action': 'block'}
        response = client.post(reverse('action-for-restaurant', kwargs={'pk': 6}), data=data)

        assertRedirects(response, reverse('restaurant-detail', kwargs={'pk': 6}))

    def test_action_for_restaurant_view_unblock(self, login_user, test_admin_password, load_admin_panel_data):
        client, _ = login_user(email=ADMIN_EMAIL, password=test_admin_password)
        data = {'restaurant_action': 'unblock'}
        response = client.post(reverse('action-for-restaurant', kwargs={'pk': 5}), data=data)

        assertRedirects(response, reverse('restaurant-detail', kwargs={'pk': 5}))


class TestActionForDeliveryAgentView:
    def test_action_for_delivery_agent_view_block(self, login_user, test_admin_password, load_admin_panel_data):
        client, _ = login_user(email=ADMIN_EMAIL, password=test_admin_password)
        data = {'agent_action': 'block'}
        response = client.post(reverse('action-for-delivery-agent', kwargs={'pk': 8}), data=data)

        assertRedirects(response, reverse('drivers-detail', kwargs={'pk': 8}))

    def test_action_for_restaurant_view_unblock(self, login_user, test_admin_password, load_admin_panel_data):
        client, _ = login_user(email=ADMIN_EMAIL, password=test_admin_password)
        data = {'agent_action': 'unblock'}
        response = client.post(reverse('action-for-delivery-agent', kwargs={'pk': 9}), data=data)

        assertRedirects(response, reverse('drivers-detail', kwargs={'pk': 9}))


class TestActionForCustomerView:
    def test_action_for_customer_view_block(self, login_user, test_admin_password, load_admin_panel_data):
        client, _ = login_user(email=ADMIN_EMAIL, password=test_admin_password)
        data = {'user_action': 'block'}
        response = client.post(reverse('action-for-customer', kwargs={'pk': 2}), data=data)

        assertRedirects(response, reverse('users-detail', kwargs={'pk': 2}))

    def test_action_for_customer_view_unblock(self, login_user, test_admin_password, load_admin_panel_data):
        client, _ = login_user(email=ADMIN_EMAIL, password=test_admin_password)
        data = {'user_action': 'unblock'}
        response = client.post(reverse('action-for-customer', kwargs={'pk': 4}), data=data)

        assertRedirects(response, reverse('users-detail', kwargs={'pk': 4}))


class TestActionForCodDeliveryAgentView:
    def test_action_for_cod_delibery_agent_view(self, login_user, test_admin_password, load_admin_panel_data):
        client, _ = login_user(email=ADMIN_EMAIL, password=test_admin_password)
        response = client.post(reverse('action-for-cod-delivery-agent', kwargs={'pk': 4}))

        assertRedirects(response, reverse('cod-agents-list'))


class TestApplicationActionForDeliveryAgentView:
    def test_application_action_for_delivery_agent_approve(self, login_user, test_admin_password,
                                                           load_admin_panel_data):
        client, _ = login_user(email=ADMIN_EMAIL, password=test_admin_password)
        data = {'is_agent_valid': '1'}
        with contextlib.suppress(requests.exceptions.ConnectionError):
            response = client.post(reverse('application-action-for-delivery-agent', kwargs={'pk': 5}), data=data,
                                   follow=True)
            assert 'Contact was not created due to some errors.' not in [str(i) for i in response.context['messages']]
            assertRedirects(response, reverse('drivers-list-application'))

    def test_application_action_for_delivery_agent_approve_failed1(self, login_user, test_admin_password,
                                                                   load_admin_panel_data):
        client, _ = login_user(email=ADMIN_EMAIL, password=test_admin_password)
        data = {'is_agent_valid': '1'}
        with patch('admins.services.create_razorpay_contact') as mock_create_razorpay_contact:
            mock_create_razorpay_contact.return_value = {}
            response = client.post(reverse('application-action-for-delivery-agent', kwargs={'pk': 5}), data=data,
                                   follow=True)
            assert 'Contact was not created due to some errors.' in [str(i) for i in response.context['messages']]
            assertRedirects(response, reverse('drivers-list-application'))

    def test_application_action_for_delivery_agent_approve_failed2(self, login_user, test_admin_password,
                                                                   load_admin_panel_data):
        client, _ = login_user(email=ADMIN_EMAIL, password=test_admin_password)
        data = {'is_agent_valid': '1'}
        with patch('admins.services.create_fund_account') as mock_create_fund_account:
            mock_create_fund_account.return_value = {}
            response = client.post(reverse('application-action-for-delivery-agent', kwargs={'pk': 5}), data=data,
                                   follow=True)
            assert 'Fund account was not created due to some errors.' in [str(i) for i in response.context['messages']]
            assertRedirects(response, reverse('drivers-list-application'))

    def test_application_action_for_delivery_agent_reject(self, login_user, test_admin_password, load_admin_panel_data):
        client, _ = login_user(email=ADMIN_EMAIL, password=test_admin_password)
        data = {'is_agent_valid': '0'}
        response = client.post(reverse('application-action-for-delivery-agent', kwargs={'pk': 5}), data=data)
        assertRedirects(response, reverse('drivers-list-application'))


class TestApplicationActionForRestaurantView:
    def test_application_action_for_restaurant_approve(self, login_user, test_admin_password, load_admin_panel_data):
        client, _ = login_user(email=ADMIN_EMAIL, password=test_admin_password)
        data = {'is_restaurant_valid': '1'}
        with contextlib.suppress(requests.exceptions.ConnectionError):
            response = client.post(reverse('application-action-for-restaurant', kwargs={'pk': 3}), data=data)
            assertRedirects(response, reverse('restaurant-list-application'))

    def test_application_action_for_restaurant_approve_failed1(self, login_user, test_admin_password,
                                                               load_admin_panel_data):
        client, _ = login_user(email=ADMIN_EMAIL, password=test_admin_password)
        data = {'is_restaurant_valid': '1'}
        with patch('admins.services.create_razorpay_contact') as mock_create_razorpay_contact:
            mock_create_razorpay_contact.return_value = {}
            response = client.post(reverse('application-action-for-restaurant', kwargs={'pk': 3}), data=data,
                                   follow=True)
            assert 'Contact was not created due to some errors.' in [str(i) for i in response.context['messages']]

            assertRedirects(response, reverse('restaurant-list-application'))

    def test_application_action_for_restaurant_approve_failed2(self, login_user, test_admin_password,
                                                               load_admin_panel_data):
        client, _ = login_user(email=ADMIN_EMAIL, password=test_admin_password)
        data = {'is_restaurant_valid': '1'}
        with patch('admins.services.create_fund_account') as mock_create_fund_account:
            mock_create_fund_account.return_value = {}
            response = client.post(reverse('application-action-for-restaurant', kwargs={'pk': 3}), data=data,
                                   follow=True)
            assert 'Fund account was not created due to some errors.' in [str(i) for i in response.context['messages']]

            assertRedirects(response, reverse('restaurant-list-application'))

    def test_application_action_for_restaurant_reject(self, login_user, test_admin_password, load_admin_panel_data):
        client, _ = login_user(email=ADMIN_EMAIL, password=test_admin_password)
        data = {'is_restaurant_valid': '0'}
        response = client.post(reverse('application-action-for-restaurant', kwargs={'pk': 3}), data=data)

        assertRedirects(response, reverse('restaurant-list-application'))
