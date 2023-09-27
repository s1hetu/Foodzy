from decimal import Decimal

import pytest
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed, assertRedirects, assertQuerysetEqual

from accounts.models import User, State, City
from delivery_agent.models import AcceptedOrder, ActivationTime, AdditionalDetail
from orders.models import Order, OrderConfirmOtp, OrderPayoutDetail, OrderItems
from tests.constants import (
    COMMON_RESTAURANT7, COMMON_CUSTOMER1, COMMON_FIXTURE0, COMMON_AGENT2,
    COMMON_AGENT4, COMMON_RESTAURANT6, THREE_ORDERS_DELIVERED_AND_ONE_PICKED,
    COMMON_AGENT6, ORDER_FOR_SAME_RESTAURANTS, TWO_ORDER_FOR_SAME_RESTAURANTS,
    PAYMENT_OF_TWO_ORDER_FOR_SAME_RESTAURANTS, AGENT2_EMAIL, AGENT4_EMAIL,
    AGENT6_EMAIL, TWO_DELIVERED_ORDER_FOR_SAME_RESTAURANTS
)

file = "./media/default.jpg"


class TestRegisterDeliveryAgent:
    url = reverse('register-delivery-agent')

    def test_get_register_restaurant_form(self, client):
        response = client.get(self.url)
        assert response.status_code == 200
        assertTemplateUsed(response, 'delivery_agent/registration.html')

    @pytest.mark.parametrize(
        'invalid_data',
        [
            {'password1': 'test@123', 'password2': 'test@123'},
            {'password1': 'Test123', 'password2': 'Test123'},
            {'password1': 'Test@test', 'password2': 'Test@test'},
            {'password1': 'test@123', 'password2': 'test@23'},
            {'mobile_number': '7894561230'},
            {'email': 'testgmail.com'},
            {'pancard_number': 'HShs'},
            {'pancard_number': 'HShs'},
            {'license_number': 982345566},
            {'license_number': '9d90d0d'},
        ]
    )
    def test_agent_registration_invalid_data(self, client, invalid_data, get_delivery_agent_registration_data):
        state = State.objects.get(id=1)
        city = City.objects.get(id=1)
        data = get_delivery_agent_registration_data(state=state, city=city, **invalid_data)
        response = client.post(self.url,
                               data=data)
        assert response.status_code == 200
        assertTemplateUsed(response, 'delivery_agent/registration.html')

    def test_agent_registration_user_exists(self, client, get_delivery_agent_registration_data, load_data):
        load_data(COMMON_AGENT4)
        state = State.objects.get(id=1)
        city = City.objects.get(id=1)
        url = reverse('register-delivery-agent')
        new_registration = get_delivery_agent_registration_data(email=AGENT4_EMAIL, state=state, city=city)
        response = client.post(url, data=new_registration)
        assert response.status_code == 200
        assertTemplateUsed(response, 'delivery_agent/registration.html')

    def test_user_registration_blank_form_submission(self, client):
        url = reverse('register-delivery-agent')
        response = client.post(url, data={})
        assert response.status_code == 200
        assertTemplateUsed(response, 'delivery_agent/registration.html')

    def test_user_registration_missing_parameter(self, client, get_delivery_agent_registration_data):
        url = reverse('register-delivery-agent')
        state = State.objects.get(id=1)
        city = City.objects.get(id=1)
        data = get_delivery_agent_registration_data(state=state, city=city)
        del data['username']
        response = client.post(url, data=data)
        assert response.status_code == 200
        assertTemplateUsed(response, 'delivery_agent/registration.html')

    def test_user_registration_success(self, client, get_delivery_agent_registration_data):
        state = State.objects.get(id=1)
        city = City.objects.get(id=1)
        data = get_delivery_agent_registration_data(username='agent1', state=state, city=city)
        response = client.post(self.url, data=data)
        assert response.status_code == 302


class TestAgentPanel:
    url = reverse('delivery-agent-panel')

    @pytest.mark.parametrize(
        'user_email',
        [
            "customer1@test.com",
            "res7@test.com"
        ]
    )
    def test_agent_panel_forbidden1(self, load_data, user_email, login_user, test_password,
                                    ):
        """
        test customer user and restaurant user can't access this view
        """
        load_data(COMMON_CUSTOMER1)
        load_data(COMMON_RESTAURANT7)

        client, user = login_user(email=user_email, password=test_password)

        response = client.get(self.url)
        assert response.status_code == 403
        assertTemplateUsed(response, 'delivery_agent/403_forbidden.html')

    def test_agent_panel_forbidden3(self, load_data, login_user, test_admin_password):
        """
        test admin can't access this view
        """
        load_data(
            COMMON_FIXTURE0
        )
        client, user = login_user(email="admin@admin.com", password=test_admin_password)

        response = client.get(self.url)
        assert response.status_code == 403
        assertTemplateUsed(response, 'delivery_agent/403_forbidden.html')

    def test_agent_panel_failed_scenario1(self, load_data, login_user, test_password):
        """
        test unverified agent will be redirected to AgentApplicationStatusView
        """
        load_data(
            COMMON_AGENT2
        )
        client, agent = login_user(email=AGENT2_EMAIL, password=test_password)
        response = client.get(self.url)
        assert response.status_code == 302

        assertRedirects(response, reverse('agent-application-status'))

    def test_agent_panel_success(self, load_data, login_user, test_password):
        """
        test verified agent can access AgentPanelView
        """
        load_data(
            COMMON_AGENT4,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            THREE_ORDERS_DELIVERED_AND_ONE_PICKED,
        )

        client, agent = login_user(email=AGENT4_EMAIL, password=test_password)

        response = client.get(self.url)
        assert response.status_code == 200
        assert response.context['delivery_agent_status'] == 'on'
        assert response.context['number_of_orders'] == 4
        assert response.context['total_order_price'] == Decimal('870.00')
        assert response.context['cod_collection'] == Decimal('630.00')
        assert response.context['orders_delivered'] == 3
        assertTemplateUsed(response, 'delivery_agent/panel.html')


class TestAgentStatusView:
    url = reverse('update_agent_status')

    @pytest.mark.parametrize(
        'user_email',
        [
            "customer1@test.com",
            "res7@test.com"
        ]
    )
    def test_agent_status_forbidden(self, load_data, user_email, login_user, test_password):
        """
        test customer user and restaurant user can't access this view
        """
        load_data(
            COMMON_CUSTOMER1,
            COMMON_RESTAURANT7
        )

        client, user = login_user(email=user_email, password=test_password)
        data = {
            "status": 'Available'
        }
        response = client.post(self.url, data)

        assert response.status_code == 403
        assertTemplateUsed(response, 'delivery_agent/403_forbidden.html')

    def test_agent_status_failed(self, load_data, login_user, test_password):
        """
        test unverified agent will be redirected to AgentApplicationStatusView
        """
        load_data(
            COMMON_AGENT2
        )
        client, agent = login_user(email=AGENT2_EMAIL, password=test_password)
        data = {
            "status": 'Available'
        }
        response = client.post(self.url, data)
        assert response.status_code == 302
        assertRedirects(response, reverse('agent-application-status'))

    def test_agent_status_success_scenario(self, load_data, login_user, test_password):
        """
        test verified agent can access UpdateAgentStatusAPIView and update status
        """
        load_data(
            COMMON_AGENT6
        )
        client, agent = login_user(email=AGENT6_EMAIL, password=test_password)
        data = {
            "status": 'Available'
        }
        response = client.post(self.url, data)
        assert response.status_code == 200


class TestSeeAllRatingAndReviewsView:

    @pytest.mark.parametrize(
        'user_email',
        [
            "customer1@test.com",
            "res7@test.com"
        ]
    )
    def test_display_agent_reviews_forbidden1(self, load_data, user_email, login_user, test_password):
        """
        test customer user and restaurant user can't access this view
        """
        load_data(
            COMMON_CUSTOMER1,
            COMMON_RESTAURANT7
        )
        client, user = login_user(email=user_email, password=test_password)

        url = reverse('agent_review', kwargs={'pk': user.id})
        response = client.get(url)

        assert response.status_code == 403
        assertTemplateUsed(response, 'delivery_agent/403_forbidden.html')

    def test_display_agent_reviews_forbidden2(self, load_data, login_user, test_password):
        """
        test agent try to see another agent's View
        """
        load_data(
            COMMON_AGENT6,
            COMMON_AGENT4
        )
        agent1 = User.objects.get(email=AGENT4_EMAIL)
        client, agent2 = login_user(email=AGENT6_EMAIL, password=test_password)

        url = reverse('agent_review', kwargs={'pk': agent1.id})
        response = client.get(url)

        assert response.status_code == 403
        assertTemplateUsed(response, 'delivery_agent/403_forbidden.html')

    def test_see_all_rating_and_reviews_view_fail_scenario1(self, get_client, load_data,
                                                            test_password):
        """
        test logged-in user is required to access this view
        """
        load_data(
            COMMON_AGENT4
        )
        agent = User.objects.get(email=AGENT4_EMAIL)
        client = get_client()
        url = reverse('agent_review', kwargs={'pk': agent.id})
        response = client.get(url)
        assert response.status_code == 302

    def test_see_all_rating_and_reviews_view_fail_scenario2(self, load_data, login_user, test_password):
        """
        test Invalid pk returns 404 not found error
        """
        load_data(
            COMMON_AGENT4
        )
        client, agent = login_user(email=AGENT4_EMAIL, password=test_password)
        url = reverse('agent_review', kwargs={'pk': 8000})

        response = client.get(url)
        assert response.status_code == 404
        assertTemplateUsed(response, 'delivery_agent/404_not_found.html')

    def test_see_all_rating_and_reviews_view_fail_scenario3(self, load_data, login_user,
                                                            test_password):
        """
        test unverified agent redirects AgentApplicationStatusView
        """

        load_data(
            COMMON_AGENT2
        )
        client, agent = login_user(email=AGENT2_EMAIL, password=test_password)
        url = reverse('agent_review', kwargs={'pk': agent.id})
        response = client.get(url)
        assert response.status_code == 302
        assertRedirects(response, reverse('agent-application-status'))

    def test_see_all_rating_and_reviews_view_success(self, load_data, login_user, test_password):
        load_data(
            COMMON_AGENT4,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            THREE_ORDERS_DELIVERED_AND_ONE_PICKED
        )
        client, agent = login_user(email=AGENT4_EMAIL, password=test_password)
        url = reverse('agent_review', kwargs={'pk': agent.id})
        response = client.get(url)
        assert response.status_code == 200
        assertTemplateUsed(response, 'delivery_agent/reviews.html')


class TestSeeAvailableDeliveryView:

    @pytest.mark.parametrize(
        'user_email',
        [
            "customer1@test.com",
            "res7@test.com"
        ]
    )
    def test_see_available_delivery_forbidden(self, load_data, user_email, login_user, test_password):
        """
        test customer can't access this view
        """
        load_data(
            COMMON_CUSTOMER1,
            COMMON_RESTAURANT7
        )
        client, user = login_user(email=user_email, password=test_password)
        url = reverse('see-available-deliveries')
        response = client.get(url)
        assert response.status_code == 403
        assertTemplateUsed(response, 'delivery_agent/403_forbidden.html')

    def test_see_available_delivery_failed_scenario1(self, load_data, login_user, test_password):
        """
        test unverified agent will be redirected to AgentApplicationStatusView
        """
        load_data(
            COMMON_AGENT2
        )
        client, agent = login_user(email=AGENT2_EMAIL, password=test_password)
        url = reverse('see-available-deliveries')
        response = client.get(url)
        assert response.status_code == 302
        assertRedirects(response, reverse('agent-application-status'))

    def test_see_available_delivery_failed_scenario2(self, load_data, login_user,
                                                     test_password):
        """
        test agent will be redirected to get_coordination view if location is not accessible by app
        """
        load_data(
            COMMON_AGENT6
        )
        client, agent = login_user(email=AGENT6_EMAIL, password=test_password)
        AdditionalDetail.objects.filter(agent=agent).update(status='Available')
        url = reverse('see-available-deliveries')
        response = client.get(url)
        assert response.status_code == 200
        assertTemplateUsed(response, 'delivery_agent/get_coordinates.html')

    def test_see_available_delivery_failed_scenario3(self, load_data, login_user, test_password):
        """
        test Agent will be redirected to NotAvailableTemplateView if coordinates are given but agent status is
         'Not Available'
        """
        load_data(
            COMMON_AGENT6
        )
        client, agent = login_user(email=AGENT6_EMAIL, password=test_password)
        url = reverse('see-available-deliveries')
        data = {
            "lat": 25.40,
            "long": 75.50
        }
        response = client.get(url, data=data)
        assert response.status_code == 302
        assertRedirects(response, reverse('not-available'))

    def test_see_available_delivery_success(self, load_data, login_user, test_password):
        """
        Verified Agent can access Nearby orders in SeeAvailableDeliveriesListView
        """
        load_data(
            COMMON_AGENT6,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            ORDER_FOR_SAME_RESTAURANTS
        )
        client, agent = login_user(email=AGENT6_EMAIL, password=test_password)

        # Update order status from waiting to ready to pick to make order available for delivery
        Order.objects.filter(id=1).update(status='ready to pick')

        # Update agent status  to available
        AdditionalDetail.objects.filter(agent=agent).update(status='Available')
        url = reverse('see-available-deliveries')
        data = {
            "lat": 23.022195,
            "long": 72.50
        }
        response = client.get(url, data=data)
        assert response.status_code == 200
        assert response.context['orders'].first() == Order.objects.get(pk=1)
        assertTemplateUsed(response, 'delivery_agent/see_available_deliveries.html')

    def test_see_available_delivery_success2(self, load_data, login_user, test_password):
        """
        Verified Agent can access SeeAvailableDeliveriesListView but get empty queryset
        """
        load_data(
            COMMON_AGENT6,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            ORDER_FOR_SAME_RESTAURANTS
        )
        client, agent = login_user(email=AGENT6_EMAIL, password=test_password)

        # Update order status from waiting to ready to pick to make order available for delivery
        Order.objects.filter(id=1).update(status='ready to pick')

        AdditionalDetail.objects.filter(agent=agent).update(status='Available')
        url = reverse('see-available-deliveries')
        data = {
            "lat": 25.022195,
            "long": 75.50
        }
        response = client.get(url, data=data)
        assert response.status_code == 200
        assert response.context['orders'].first() is None
        assertTemplateUsed(response, 'delivery_agent/see_available_deliveries.html')


class TestCurrentDeliveryView:
    url = reverse('current_delivery')

    @pytest.mark.parametrize(
        'user_email',
        [
            "customer1@test.com",
            "res7@test.com"
        ]
    )
    def test_current_delivery_list_view_forbidden1(self, load_data, user_email, login_user, test_password):
        """
        test customer user and restaurant user can not access CurrentDeliveriesListView
        """
        load_data(
            COMMON_RESTAURANT7,
            COMMON_CUSTOMER1
        )
        client, user = login_user(email=user_email, password=test_password)
        response = client.get(self.url)
        assert response.status_code == 403
        assertTemplateUsed(response, 'delivery_agent/403_forbidden.html')

    def test_current_delivery_list_view_failed(self, load_data, login_user, test_password):
        """
        Unverified agent will be redirected to AgentApplicationStatusView
        """
        load_data(
            COMMON_AGENT2
        )
        client, agent = login_user(email=AGENT2_EMAIL, password=test_password)
        response = client.get(self.url)
        assert response.status_code == 302
        assertRedirects(response, reverse('agent-application-status'))

    def test_current_delivery_list_view_success(self, load_data, login_user, test_password, ):
        """
        Verified agent can access CurrentDeliveriesListView
        """
        load_data(
            COMMON_AGENT4,
            COMMON_CUSTOMER1,
            COMMON_RESTAURANT6,
            THREE_ORDERS_DELIVERED_AND_ONE_PICKED

        )
        client, agent = login_user(email=AGENT4_EMAIL, password=test_password)
        response = client.get(self.url)
        assert response.status_code == 200
        assertQuerysetEqual(response.context['orders'], AcceptedOrder.get_current_active_deliveries(agent),
                            ordered=False)
        assert AcceptedOrder.current_active_delivery_count(agent) == 1
        assertTemplateUsed(response, 'delivery_agent/current_deliveries.html')


class TestAgentEarningView:
    url = reverse('agent_earning')

    @pytest.mark.parametrize(
        'user_email',
        [
            "customer1@test.com",
            "res7@test.com"
        ]
    )
    def test_agent_earning_list_view_forbidden1(self, load_data, user_email, login_user, test_password):
        """
        test customer user  and restaurant owner can not access AgentEarningListView
        """

        load_data(
            COMMON_CUSTOMER1,
            COMMON_RESTAURANT7
        )
        client, user = login_user(email=user_email, password=test_password)
        response = client.get(self.url)
        assert response.status_code == 403
        assertTemplateUsed(response, 'delivery_agent/403_forbidden.html')

    def test_agent_earning_failed(self, load_data, login_user, test_password):
        """
        Unverified agent will be redirected to AgentApplicationStatusView
        """
        load_data(
            COMMON_AGENT2
        )
        client, agent = login_user(email=AGENT2_EMAIL, password=test_password)
        response = client.get(self.url)
        assert response.status_code == 302
        assertRedirects(response, reverse('agent-application-status'))

    def test_agent_earning_list_view_success(self, load_data, login_user, test_password):
        """
        Verified agent can access AgentEarningListView
        """
        load_data(
            COMMON_AGENT4,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            PAYMENT_OF_TWO_ORDER_FOR_SAME_RESTAURANTS

        )
        client, agent = login_user(email=AGENT4_EMAIL, password=test_password)
        response = client.get(self.url)
        assert response.status_code == 200
        assert response.context['total_earning'] == Decimal('120.00')
        assert response.context['last_month_earning'] == Decimal('120.00')
        assertQuerysetEqual(response.context['orders'],
                            OrderPayoutDetail.get_payout_detail_for_agent(agent_id=8).order_by('id'))
        assertTemplateUsed(response, 'delivery_agent/agent_earning.html')


class TestAllDeliveriesListView:
    url = reverse('all-accepted-delivery')

    @pytest.mark.parametrize(
        'user_email',
        [
            "customer1@test.com",
            "res7@test.com"
        ]
    )
    def test_all_delivery_list_view_forbidden(self, load_data, user_email, login_user, test_password):
        """
        test customer user and restaurant owner can not access AllDeliveriesListView
        """
        load_data(
            COMMON_CUSTOMER1,
            COMMON_RESTAURANT7
        )

        client, user = login_user(email=user_email, password=test_password)
        response = client.get(self.url)
        assert response.status_code == 403
        assertTemplateUsed(response, 'delivery_agent/403_forbidden.html')

    def test_all_delivery_list_view_failed(self, load_data, login_user, test_password):
        """
        Unverified agent will be redirected to AgentApplicationStatusView
        """
        load_data(
            COMMON_AGENT2
        )

        client, agent = login_user(email=AGENT2_EMAIL, password=test_password)
        response = client.get(self.url)
        assert response.status_code == 302
        assertRedirects(response, reverse('agent-application-status'))

    def test_all_delivery_list_view_success(self, load_data, login_user, test_password):
        """
        Verified agent can access AllDeliveriesListView
        """

        load_data(
            COMMON_AGENT4,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            PAYMENT_OF_TWO_ORDER_FOR_SAME_RESTAURANTS
        )
        client, agent = login_user(email=AGENT4_EMAIL, password=test_password)
        response = client.get(self.url)
        assert response.status_code == 200

        assertQuerysetEqual(response.context['orders'], AcceptedOrder.accepted_order_deliveries(agent).filter(
            order__status='delivered'), ordered=False)
        assert response.context['orders'].count() == 2
        assertTemplateUsed(response, 'delivery_agent/list_accepted_orders.html')


class TestAllTimeEntriesListView:
    url = reverse('all_time_entries')

    @pytest.mark.parametrize(
        'user_email',
        [
            "customer1@test.com",
            "res7@test.com"
        ]
    )
    def test_all_time_entries_list_view_forbidden(self, load_data, user_email, login_user, test_password):
        """
        Customer user and restaurant owner can not access AllTimeEntriesListView
        """
        load_data(
            COMMON_RESTAURANT7,
            COMMON_CUSTOMER1
        )
        client, user = login_user(email=user_email, password=test_password)
        response = client.get(self.url)
        assert response.status_code == 403
        assertTemplateUsed(response, 'delivery_agent/403_forbidden.html')

    def test_all_time_entries_list_view_failed(self, load_data, login_user, test_password):
        """
        Unverified agent will be redirected to AgentApplicationStatusView
        """
        load_data(
            COMMON_AGENT2
        )
        client, agent = login_user(email=AGENT2_EMAIL, password=test_password)
        response = client.get(self.url)
        assert response.status_code == 302
        assertRedirects(response, reverse('agent-application-status'))

    def test_all_time_entries_list_view_success(self, load_data, login_user, test_password):
        """
        Verified agent can access AllTimeEntriesListView
        """
        load_data(
            COMMON_AGENT4

        )
        client, agent = login_user(email=AGENT4_EMAIL, password=test_password)
        response = client.get(self.url)
        assert response.status_code == 200
        assertTemplateUsed(response, 'delivery_agent/time_entries.html')
        assert response.context['active_time_obj'].count() == 4
        assertQuerysetEqual(response.context['active_time_obj'], ActivationTime.get_active_time_entries(agent))


class TestAgentApplicationStatusView:
    url = reverse('agent-application-status')

    @pytest.mark.parametrize(
        'user_email',
        [
            "customer1@test.com",
            "res7@test.com",
        ]
    )
    def test_agent_application_status_view_forbidden1(self, load_data, user_email, login_user, test_password):
        """
        test customer user and restaurant owner can not access AgentApplicationStatusView
        """
        load_data(
            COMMON_CUSTOMER1,
            COMMON_RESTAURANT7
        )
        client, user = login_user(email=user_email, password=test_password)
        response = client.get(self.url)
        assert response.status_code == 403
        assertTemplateUsed(response, 'delivery_agent/403_forbidden.html')

    def test_agent_application_status_view_forbidden2(self, load_data, login_user, test_admin_password):
        """
        test admin client can not access AgentApplicationStatusView
        """
        load_data(
            COMMON_FIXTURE0
        )
        admin_client, user = login_user(email="admin@admin.com", password=test_admin_password)
        response = admin_client.get(self.url)
        assert response.status_code == 403
        assertTemplateUsed(response, 'delivery_agent/403_forbidden.html')

    def test_agent_application_status_view_success_scenario1(self, load_data, login_user, test_password):
        """
        Unverified agent can access AgentApplicationStatusView
        """
        load_data(
            COMMON_AGENT2
        )
        client, agent = login_user(email=AGENT2_EMAIL, password=test_password)
        response = client.get(self.url)
        assert response.status_code == 200
        assertTemplateUsed(response, 'delivery_agent/agent_application_status.html')

    def test_agent_application_status_view_success_scenario2(self, load_data, login_user, test_password):
        """
        Verified agent can access AgentApplicationStatusView
        """
        load_data(
            COMMON_AGENT6
        )
        client, agent = login_user(email=AGENT6_EMAIL, password=test_password)
        response = client.get(self.url)
        assert response.status_code == 200
        assertTemplateUsed(response, 'delivery_agent/agent_application_status.html')


class TestAcceptDeliveryAPIView:
    url = reverse('accept_delivery')

    @pytest.mark.parametrize(
        'user_email',
        [
            "customer1@test.com",
            "res7@test.com",
        ]
    )
    def test_accept_delivery_api_view_forbidden(self, load_data, user_email, login_user, test_password):
        """
        Customer user and restaurant owner can not access AcceptDeliveryAPIView
        """
        load_data(
            COMMON_RESTAURANT7,
            COMMON_CUSTOMER1
        )
        client, user = login_user(email=user_email, password=test_password)
        response = client.post(self.url)
        assert response.status_code == 403
        assertTemplateUsed(response, 'delivery_agent/403_forbidden.html')

    def test_accept_delivery_api_view_failed_scenario1(self, load_data, login_user, test_password):
        """
        Unverified agent will be redirected to AgentApplicationStatusView
        """
        load_data(
            COMMON_AGENT2
        )
        client, agent = login_user(email=AGENT2_EMAIL, password=test_password)
        response = client.post(self.url)
        assert response.status_code == 302
        assertRedirects(response, reverse('agent-application-status'))

    def test_accept_delivery_api_view_fail_scenario2(self, load_data, login_user, test_password):
        """
        Verified agent will be redirected to NotAvailableTemplateView if status of agent is not avaialble
        """
        load_data(
            COMMON_AGENT6
        )
        client, agent = login_user(email=AGENT6_EMAIL, password=test_password)
        response = client.post(self.url)
        assert response.status_code == 302
        assert agent.additional_detail.status == 'Not Available'
        assertRedirects(response, reverse('not-available'))

    def test_accept_delivery_api_view_fail_scenario3(self, load_data, login_user, test_password):
        """
        test id not passed in data, raise validationError
        """
        load_data(
            COMMON_AGENT4
        )
        client, agent = login_user(email=AGENT4_EMAIL, password=test_password)
        AdditionalDetail.objects.filter(agent=agent).update(status='Available')
        response = client.post(self.url)
        assert response.status_code == 400
        assert str(response.data['order_id']) == 'This Field is required!'
        assert agent.additional_detail.status == 'Available'

    def test_accept_delivery_api_view_fail_scenario4(self, load_data, login_user, test_password):
        """
        Here invalid pk will raise 404 not found
        """
        load_data(
            COMMON_AGENT4
        )
        client, agent = login_user(email=AGENT4_EMAIL, password=test_password)
        AdditionalDetail.objects.filter(agent=agent).update(status='Available')
        data = {
            'order_id': 10000
        }
        response = client.post(self.url, data=data)
        assert response.status_code == 404
        assertTemplateUsed(response, 'delivery_agent/404_not_found.html')

    def test_accept_delivery_api_view_fail_scenario5(self, load_data, login_user, test_password):
        """
        Agent can't accept order if order is already accepted
        """
        load_data(
            COMMON_AGENT4,
            COMMON_AGENT6,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            THREE_ORDERS_DELIVERED_AND_ONE_PICKED
        )
        agent_client1, agent1 = login_user(email=AGENT4_EMAIL, password=test_password)
        agent_client2, agent2 = login_user(email=AGENT6_EMAIL, password=test_password)
        AdditionalDetail.objects.filter(agent=agent2).update(status='Available')

        data = {
            'order_id': 4
        }
        agent_client1.post(self.url, data=data)
        response = agent_client2.post(self.url, data=data)
        assert response.status_code == 400
        assert str(response.data[0]) == 'Oops! Delivery is already accepted !!'

    def test_accept_delivery_api_view_fail_scenario6(self, load_data, login_user, test_password):
        """
        Agent can't accept order if order status is waiting or cancelled.
        """
        load_data(
            COMMON_AGENT6,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            TWO_ORDER_FOR_SAME_RESTAURANTS
        )

        agent_client2, agent2 = login_user(email=AGENT6_EMAIL, password=test_password)
        AdditionalDetail.objects.filter(agent=agent2).update(status='Available')
        data = {
            'order_id': 1
        }
        agent_client2.post(self.url, data=data)
        response = agent_client2.post(self.url, data=data)
        assert response.status_code == 400
        assert response.data['Error'] == 'Can not accept cancelled order or order contains rejected or ' \
                                         'waiting status ! '

    def test_accept_delivery_api_view_fail_scenario7(self, load_data, login_user, test_password):
        """
        Agent can't accept order if agent has any current delivery.
        """
        load_data(
            COMMON_AGENT6,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            TWO_ORDER_FOR_SAME_RESTAURANTS
        )
        Order.objects.filter(pk=1).update(status='accepted')
        Order.objects.filter(pk=2).update(status='accepted')
        client, agent = login_user(email=AGENT6_EMAIL, password=test_password)
        AdditionalDetail.objects.filter(agent=agent).update(status='Available')
        data = {
            'order_id': 1
        }
        response1 = client.post(self.url, data=data)
        assert response1.status_code == 201

        data = {
            'order_id': 2
        }
        response = client.post(self.url, data=data)
        # breakpoint()
        assert response.status_code == 400
        assert response.data['Error'] == 'You have some Orders to deliver first'

    def test_accept_delivery_api_view_success(self, load_data, login_user, test_password, ):
        """
        Verified agent can accept delivery after updating status to Available
        """
        load_data(
            COMMON_AGENT6,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            TWO_ORDER_FOR_SAME_RESTAURANTS
        )
        Order.objects.filter(pk=1).update(status='accepted')
        client, agent = login_user(email=AGENT6_EMAIL, password=test_password)
        AdditionalDetail.objects.filter(agent=agent).update(status='Available')
        data = {
            'order_id': 1
        }
        response = client.post(self.url, data=data)
        assert response.status_code == 201
        assert str(response.data['message']) == "Delivery Accepted Successfully!"


class TestDetailOrderTemplateView:

    @pytest.mark.parametrize(
        'user_email',
        [
            "customer1@test.com",
            "res7@test.com",
        ]
    )
    def test_detail_order_template_view_forbidden(self, load_data, user_email, login_user, test_password):
        """
        Customer user and restaurant owner can not access DetailOrderTemplateView
        """
        load_data(
            COMMON_CUSTOMER1,
            COMMON_RESTAURANT7
        )
        client, user = login_user(email=user_email, password=test_password)
        url = reverse('detail_delivery', kwargs={'pk': 1})
        response = client.get(url)
        assert response.status_code == 403
        assertTemplateUsed(response, 'delivery_agent/403_forbidden.html')

    def test_detail_order_template_view_failed_scenario1(self, load_data, login_user, test_password):
        """
        test Unverified agent will be redirected to AgentApplicationStatusView
        """
        load_data(
            COMMON_AGENT2
        )
        client, agent1 = login_user(email=AGENT2_EMAIL, password=test_password)
        url = reverse('detail_deli'
                      'very', kwargs={'pk': 1})
        response = client.get(url)
        assert response.status_code == 302
        assertRedirects(response, reverse('agent-application-status'))

    def test_detail_order_template_view_fail_scenario2(self, load_data, login_user, test_password):
        """
        test order_details when order is in waiting state
        """

        load_data(
            COMMON_AGENT6,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            TWO_ORDER_FOR_SAME_RESTAURANTS
        )
        client, agent1 = login_user(email=AGENT6_EMAIL, password=test_password)
        url = reverse('detail_delivery', kwargs={'pk': 1})
        response = client.get(url)
        assert response.status_code == 403
        assertTemplateUsed(response, 'delivery_agent/403_forbidden.html')

    def test_detail_order_template_view_fail_scenario3(self, load_data, login_user, test_password):
        """
        test order_details when order is rejected by restaurant
        """

        load_data(
            COMMON_AGENT6,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,

            TWO_ORDER_FOR_SAME_RESTAURANTS
        )
        Order.objects.filter(id=1).update(status='rejected')
        client, agent1 = login_user(email=AGENT6_EMAIL, password=test_password)
        url = reverse('detail_delivery', kwargs={'pk': 1})
        response = client.get(url)
        assert response.status_code == 403
        assertTemplateUsed(response, 'delivery_agent/403_forbidden.html')

    def test_detail_order_template_view_fail_scenario4(self, load_data, login_user, test_password):
        """
        Here invalid pk will raise 404 not found
        """

        load_data(
            COMMON_AGENT4,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            TWO_DELIVERED_ORDER_FOR_SAME_RESTAURANTS
        )
        Order.objects.filter(id=1).update(status='accepted')
        client, agent1 = login_user(email=AGENT4_EMAIL, password=test_password)
        url = reverse('detail_delivery', kwargs={'pk': 30000})
        response = client.get(url)
        assert response.status_code == 404
        assertTemplateUsed(response, 'delivery_agent/404_not_found.html')

    def test_detail_order_template_view_fail_scenario5(self, load_data, login_user, test_password):
        """
        test other agents can't see details of deliveries of an agent
        """
        load_data(
            COMMON_AGENT4,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            TWO_DELIVERED_ORDER_FOR_SAME_RESTAURANTS,
            COMMON_AGENT6
        )
        order = Order.objects.get(pk=1)

        client1, agent1 = login_user(email=AGENT4_EMAIL, password=test_password)
        url = reverse('detail_delivery', kwargs={'pk': order.id})
        response1 = client1.get(url)

        client2, agent2 = login_user(email=AGENT6_EMAIL, password=test_password)
        url = reverse('detail_delivery', kwargs={'pk': order.id})
        response2 = client2.get(url)
        assert response1.status_code == 200
        assert response2.status_code == 403
        assertTemplateUsed(response2, 'delivery_agent/403_forbidden.html')

    def test_detail_order_template_success(self, load_data, login_user, test_password, ):
        """
        Verified agent will see order details
        """
        load_data(
            COMMON_AGENT4,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            TWO_DELIVERED_ORDER_FOR_SAME_RESTAURANTS,
        )
        order = Order.objects.get(pk=1)
        client, agent = login_user(email=AGENT4_EMAIL, password=test_password)
        url = reverse('detail_delivery', kwargs={'pk': 1})
        response = client.get(url)
        assert response.status_code == 200
        assert response.context['order'] == order
        assertQuerysetEqual(response.context['details'], OrderItems.get_order_items_from_order(order=order))
        assertTemplateUsed(response, 'delivery_agent/detail_order.html')


class TestUpdateDeliveryStatusAPIView:
    url = reverse('update_delivery_status')

    @pytest.mark.parametrize(
        'user_email',
        [
            "customer1@test.com",
            "res7@test.com",
        ]
    )
    def test_update_delivery_status_api_view_forbidden(self, load_data, user_email, login_user, test_password):
        """
        Customer user and restaurant owner can not access AllTimeEntriesListView
        """
        load_data(
            COMMON_CUSTOMER1,
            COMMON_RESTAURANT7
        )
        client, user = login_user(email=user_email, password=test_password)
        response = client.post(self.url)
        assert response.status_code == 403
        assertTemplateUsed(response, 'delivery_agent/403_forbidden.html')

    def test_update_delivery_status_api_view_failed_scenario1(self, load_data, login_user, test_password):
        """
        Unverified agent will be redirected to AgentApplicationStatusView
        """
        load_data(
            COMMON_AGENT2
        )
        client, agent1 = login_user(email=AGENT2_EMAIL, password=test_password)
        response = client.post(self.url)
        assert response.status_code == 302
        assertRedirects(response, reverse('agent-application-status'))

    def test_update_delivery_status_api_view_fail_scenario2(self, load_data, login_user, test_password):
        """
        test agent2 can't update status of deliveries of agent1
        """
        load_data(
            COMMON_AGENT6,
            COMMON_AGENT4,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            THREE_ORDERS_DELIVERED_AND_ONE_PICKED,
        )
        order = Order.objects.get(id=4)
        client1, agent1 = login_user(email=AGENT4_EMAIL, password=test_password)
        data = {
            'id': order.id,
            'status': 1
        }
        response1 = client1.post(self.url, data=data)

        client2, agent2 = login_user(email=AGENT6_EMAIL, password=test_password)
        AdditionalDetail.objects.filter(agent=agent2).update(status='Available')
        data = {
            'id': order.id,
            'status': 1
        }
        response2 = client2.post(self.url, data=data)
        assert response1.status_code == 200
        assert response2.status_code == 403

    def test_update_delivery_status_api_view_fail_scenario3(self, load_data, login_user, test_password):
        """
        test invalid pk will raise 404 not found
        """
        load_data(
            COMMON_AGENT4,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            THREE_ORDERS_DELIVERED_AND_ONE_PICKED,
        )
        client1, agent1 = login_user(email=AGENT4_EMAIL, password=test_password)
        data = {
            'id': 10000,
            'status': 1
        }
        response = client1.post(self.url, data=data)
        assert response.status_code == 404
        assertTemplateUsed(response, 'delivery_agent/404_not_found.html')

    def test_update_delivery_status_api_view_fail_scenario5(self, load_data, login_user, test_password):
        """
        test update delivery status on data not passed into body
        """
        load_data(
            COMMON_AGENT4,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            THREE_ORDERS_DELIVERED_AND_ONE_PICKED,
        )
        client, agent1 = login_user(email=AGENT4_EMAIL, password=test_password)
        response = client.post(self.url)
        assert response.status_code == 400
        assert str(response.data[0]) == 'Bad Request'

    def test_update_delivery_status_api_view_success(self, load_data, login_user, test_password):
        """
        test agent successfully update order status
        """
        load_data(
            COMMON_AGENT4,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            THREE_ORDERS_DELIVERED_AND_ONE_PICKED,
        )
        client1, agent1 = login_user(email=AGENT4_EMAIL, password=test_password)
        data = {
            'id': 4,
            'status': 1
        }
        response = client1.post(self.url, data=data)
        assert response.status_code == 200


class TestAcceptPaymentAPIView:
    url = reverse('accept_payment')

    @pytest.mark.parametrize(
        'user_email',
        [
            "customer1@test.com",
            "res7@test.com",
        ]
    )
    def test_accept_payment_api_view_forbidden(self, load_data, user_email, login_user, test_password):
        """
        test customer user and restaurant owner can not access AcceptPaymentAPIView
        """
        load_data(
            COMMON_CUSTOMER1,
            COMMON_RESTAURANT7
        )
        client, user = login_user(email=user_email, password=test_password)
        response = client.post(self.url)
        assert response.status_code == 403
        assertTemplateUsed(response, 'delivery_agent/403_forbidden.html')

    def test_accept_payment_api_view_forbidden2(self, load_data, login_user, test_password):
        """
        test different agent  can not accept payment
        """
        load_data(
            COMMON_AGENT6,
            COMMON_AGENT4,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            THREE_ORDERS_DELIVERED_AND_ONE_PICKED,
        )
        Order.objects.filter(id=4).update(status='delivered')

        client1, agent1 = login_user(email=AGENT4_EMAIL, password=test_password)
        client2, agent2 = login_user(email=AGENT6_EMAIL, password=test_password)
        AdditionalDetail.objects.filter(agent=agent2).update(status='Available')

        data = {
            "order_id": 4,
        }
        response = client2.post(self.url, data=data)
        assert response.status_code == 403

    def test_accept_payment_api_view_failed_scenario1(self, load_data, login_user,
                                                      test_password):
        """
        test unverified agent will be redirected to AgentApplicationStatusView
        """
        load_data(COMMON_AGENT2)
        client, agent1 = login_user(email=AGENT2_EMAIL, password=test_password)
        response = client.post(self.url)
        assert response.status_code == 302
        assertRedirects(response, reverse('agent-application-status'))

    def test_accept_payment_api_view_fail_scenario2(self, load_data, login_user, test_password):
        """
        test invalid pk will raise 404 not found
        """
        load_data(
            COMMON_AGENT4,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            THREE_ORDERS_DELIVERED_AND_ONE_PICKED,
        )
        Order.objects.filter(id=4).update(status='delivered')
        client, agent = login_user(email=AGENT4_EMAIL, password=test_password)
        data = {
            'order_id': 10000
        }
        response = client.post(self.url, data=data)
        assert response.status_code == 404
        assertTemplateUsed(response, 'delivery_agent/404_not_found.html')

    def test_accept_payment_api_view_fail_scenario4(self, load_data, login_user, test_password):
        """
        test accept payment on data not passed
        """
        load_data(
            COMMON_AGENT4,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            THREE_ORDERS_DELIVERED_AND_ONE_PICKED,
        )
        Order.objects.filter(id=4).update(status='delivered')
        client, agent = login_user(email=AGENT4_EMAIL, password=test_password)
        response = client.post(self.url)
        assert response.status_code == 400

    def test_accept_payment_api_view_failed_scenario5(self, load_data, login_user, test_password):
        """
        test agent can't accept payment if order is paid
        """

        load_data(
            COMMON_AGENT4,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            THREE_ORDERS_DELIVERED_AND_ONE_PICKED,
        )
        client, agent = login_user(email=AGENT4_EMAIL, password=test_password)
        Order.objects.filter(id=4).update(status='delivered')
        Order.objects.filter(id=4).update(paid=True)
        data = {
            "order_id": 4,
        }
        client.post(self.url, data=data)
        response = client.post(self.url, data=data)
        assert response.status_code == 400
        assert response.data['paid'] == 'This field is already updated'

    def test_accept_payment_api_view_failed_scenario6(self, load_data, login_user, test_password):
        """
        test agent can't accept payment if order is not delivered
        """

        load_data(
            COMMON_AGENT4,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            THREE_ORDERS_DELIVERED_AND_ONE_PICKED,
        )
        client, agent = login_user(email=AGENT4_EMAIL, password=test_password)
        data = {
            "order_id": 4,
        }
        response = client.post(self.url, data=data)
        assert response.status_code == 400
        assert response.data['Error'] == 'Order is not delivered yet!'

    def test_accept_payment_api_view_success(self, load_data, login_user, test_password):
        """
        test agent successfully accept payment
        """

        load_data(
            COMMON_AGENT4,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            THREE_ORDERS_DELIVERED_AND_ONE_PICKED,
        )
        client, agent = login_user(email=AGENT4_EMAIL, password=test_password)
        Order.objects.filter(id=4).update(status='delivered')

        data = {
            "order_id": 4,
        }
        response = client.post(self.url, data=data)
        assert response.status_code == 200


class TestValidateOtpAPIView:
    url = reverse('validate_otp')

    @pytest.mark.parametrize(
        'user_email',
        [
            "customer1@test.com",
            "res7@test.com",
        ]
    )
    def test_validate_otp_api_view_forbidden(self, load_data, user_email, login_user, test_password):
        """
        test customer user and restaurant owner can not access TestValidateOtpAPIView
        """
        load_data(COMMON_CUSTOMER1, COMMON_RESTAURANT7)
        client, user = login_user(email=user_email, password=test_password)
        response = client.post(self.url)
        assert response.status_code == 403
        assertTemplateUsed(response, 'delivery_agent/403_forbidden.html')

    def test_validate_otp_api_view_failed_scenario1(self, load_data, login_user,
                                                    test_password):
        """
        test unverified agent will be redirected to AgentApplicationStatusView
        """
        load_data(COMMON_AGENT2)
        client, agent = login_user(email=AGENT2_EMAIL, password=test_password)
        response = client.post(self.url)
        assert response.status_code == 302
        assertRedirects(response, reverse('agent-application-status'))

    def test_validate_otp_api_view_failed_scenario2(self, load_data, login_user, test_password):
        """
        test verified agent will be redirected to NotAvailableTemplateView if status of agent is not available
        """
        load_data(
            COMMON_AGENT4,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            THREE_ORDERS_DELIVERED_AND_ONE_PICKED,
        )
        order = Order.objects.get(id=4)
        client, agent = login_user(email=AGENT4_EMAIL, password=test_password)
        AdditionalDetail.objects.filter(agent=agent).update(status='Not Available')
        response = client.post(self.url)
        assert response.status_code == 302
        assert agent.additional_detail.status == 'Not Available'
        assertRedirects(response, reverse('not-available'))

    @pytest.mark.parametrize(
        ['data', 'error_field'],
        [
            [{'otp': '24f53'}, 'order_id'],
            [{'order_id': '12'}, 'otp']
        ]
    )
    def test_validate_otp_api_view_fail_scenario3(self, load_data, data, error_field, login_user, test_password):
        """
        test otp or order_id not provided
        """
        load_data(
            COMMON_AGENT4,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            THREE_ORDERS_DELIVERED_AND_ONE_PICKED,
        )
        client, agent = login_user(email=AGENT4_EMAIL, password=test_password)
        response = client.post(self.url, data=data)
        assert response.status_code == 400
        assert response.data[error_field] == 'This Field is required!'

    def test_validate_otp_api_view_fail_scenario4(self, load_data, login_user, test_password):
        """
        test data not provided
        """
        load_data(
            COMMON_AGENT4,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            THREE_ORDERS_DELIVERED_AND_ONE_PICKED,
        )
        client, agent = login_user(email=AGENT4_EMAIL, password=test_password)
        response = client.post(self.url)
        assert response.status_code == 400
        assert response.data['otp'] == 'This Field is required!'
        assert response.data['order_id'] == 'This Field is required!'

    def test_validate_otp_api_view_fail_scenario5(self, load_data, login_user, test_password):
        """
        test invalid pk will raise 404 not found
        """
        load_data(
            COMMON_AGENT4,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            THREE_ORDERS_DELIVERED_AND_ONE_PICKED,
        )
        client, agent = login_user(email=AGENT4_EMAIL, password=test_password)
        data = {
            'order_id': 10000,
            'otp': '8js35'
        }
        response = client.post(self.url, data=data)
        assert response.status_code == 404
        assertTemplateUsed(response, 'delivery_agent/404_not_found.html')

    def test_validate_otp_api_view_fail_scenario6(self, load_data, login_user, test_password):
        """
        test  invalid otp fail
        """
        load_data(
            COMMON_AGENT4,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            THREE_ORDERS_DELIVERED_AND_ONE_PICKED,
        )
        client, agent = login_user(email=AGENT4_EMAIL, password=test_password)
        data = {
            'order_id': 4,
            'otp': 'jsjs2'
        }
        response = client.post(self.url, data=data)
        assert response.status_code == 400
        assert str(response.data[0]) == 'OTP is incorrect'

    def test_validate_otp_api_view_success(self, load_data, login_user, test_password):
        """
        test otp validate success
        """
        load_data(
            COMMON_AGENT4,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            THREE_ORDERS_DELIVERED_AND_ONE_PICKED,
        )
        client, agent = login_user(email=AGENT4_EMAIL, password=test_password)
        otp = OrderConfirmOtp.objects.get(order_id=4).otp
        data = {
            'order_id': 4,
            'otp': 'd06740'
        }
        response = client.post(self.url, data=data)
        assert response.status_code == 200


class TestResendOtpAPIView:
    url = reverse('resend_otp')

    @pytest.mark.parametrize(
        'user_email',
        [
            "customer1@test.com",
            "res7@test.com",
        ]
    )
    def test_resend_otp_api_view_forbidden(self, load_data, user_email, login_user, test_password):
        """
        test customer user and restaurant owner can not access TestValidateOtpAPIView
        """
        load_data(COMMON_CUSTOMER1, COMMON_RESTAURANT7)
        client, user = login_user(email=user_email, password=test_password)
        response = client.post(self.url)
        assert response.status_code == 403
        assertTemplateUsed(response, 'delivery_agent/403_forbidden.html')

    def test_resend_otp_api_view_failed_scenario1(self, load_data, login_user, test_password):
        """
        test unverified agent will be redirected to AgentApplicationStatusView
        """
        load_data(COMMON_AGENT2)
        client, agent = login_user(email=AGENT2_EMAIL, password=test_password)
        response = client.post(self.url)
        assert response.status_code == 302
        assertRedirects(response, reverse('agent-application-status'))

    def test_resend_otp_api_view_failed_scenario2(self, load_data, login_user, test_password):
        """
        test verified agent will be redirected to NotAvailableTemplateView if status of agent is not avaialble
        """
        load_data(
            COMMON_AGENT4,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            THREE_ORDERS_DELIVERED_AND_ONE_PICKED,
        )
        client, agent = login_user(email=AGENT4_EMAIL, password=test_password)
        AdditionalDetail.objects.filter(agent=agent).update(status='Not Available')
        response = client.post(self.url)
        assert response.status_code == 302
        assert agent.additional_detail.status == 'Not Available'
        assertRedirects(response, reverse('not-available'))

    def test_resend_otp_api_view_fail_scenario3(self, load_data, login_user, test_password):
        """
        test data not provided
        """
        load_data(
            COMMON_AGENT4,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            THREE_ORDERS_DELIVERED_AND_ONE_PICKED,
        )
        client, agent = login_user(email=AGENT4_EMAIL, password=test_password)
        response = client.post(self.url)
        assert response.status_code == 400
        assert response.data['order_id'] == 'This Field is required!'

    def test_resend_otp_api_view_fail_scenario4(self, load_data, login_user, test_password, ):
        """
        test invalid pk will raise 404 not found
        """
        load_data(
            COMMON_AGENT4,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            THREE_ORDERS_DELIVERED_AND_ONE_PICKED,
        )
        client, agent = login_user(email=AGENT4_EMAIL, password=test_password)
        data = {
            'order_id': 10000,
        }
        response = client.post(self.url, data=data)
        assert response.status_code == 404
        assertTemplateUsed(response, 'delivery_agent/404_not_found.html')

    def test_resend_otp_api_view_success(self, load_data, login_user, test_password):
        """
        test otp validate success
        """
        load_data(
            COMMON_AGENT4,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            THREE_ORDERS_DELIVERED_AND_ONE_PICKED,
        )
        client, agent = login_user(email=AGENT4_EMAIL, password=test_password)
        data = {
            'order_id': 4,
        }
        response = client.post(self.url, data=data)
        assert response.status_code == 200
