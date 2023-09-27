from decimal import Decimal
from unittest.mock import Mock, patch

import pytest
from django.http import Http404

from accounts.models import State, City, Address, User, Activation
from tests.constants import (
    COMMON_CUSTOMER1,
    CUSTOMER1_EMAIL,
    COMMON_CUSTOMER2,
    CUSTOMER2_EMAIL,
    AGENT3_EMAIL,
    THREE_ORDERS_DELIVERED_AND_ONE_PICKED
)


def get_ids_list_from_queryset(queryset):
    """Returns list of id's of objects in queryset param."""
    return list(queryset.values_list('id', flat=True))


class TestState:
    def test_str_method(self):
        obj = State.objects.get(name='Gujarat')
        assert str(obj) == 'Gujarat'

    def test_fields(self):
        obj = State.objects.get(name='Gujarat')
        assert obj.name == 'Gujarat'


class TestCity:
    def test_str_method(self):
        obj = City.objects.get(name='Ahmedabad')
        assert str(obj) == 'Ahmedabad'

    def test_fields(self):
        obj = City.objects.get(name='Ahmedabad')
        assert obj.name == 'Ahmedabad'


class TestAddress:
    def test_str_method(self, load_data):
        load_data(
            COMMON_CUSTOMER1
        )
        obj = Address.objects.get(id=1)
        assert str(obj) == 'Address1-customer1,Address2-customer1, Street-customer1,' \
                           ' Landmark-customer1, Ahmedabad, 123456, Gujarat'

    def test_fields(self, load_data):
        load_data(
            COMMON_CUSTOMER1
        )
        obj = Address.objects.get(id=1)
        assert obj.address_title == 'Customers Address'
        assert obj.address_line1 == 'Address1-customer1'
        assert obj.address_line2 == 'Address2-customer1'
        assert obj.street == 'Street-customer1'
        assert obj.landmark == 'Landmark-customer1'
        assert obj.pincode == 123456
        assert obj.state.name == 'Gujarat'
        assert obj.city.name == 'Ahmedabad'
        assert obj.lat == Decimal('23.022195')
        assert obj.long == Decimal('72.506745')

    def test_method_get_near_by_restaurants(self, load_admin_panel_data):
        request = Mock()
        request.user = User.objects.get(email=CUSTOMER1_EMAIL)

        assert get_ids_list_from_queryset(Address.get_near_by_restaurants(request)) == [9, 10, 11, 12, 13, 14]

    def test_method_get_near_by_restaurants_by_coordinates(self, load_admin_panel_data):
        customer_address = Address.objects.get(id=1)

        assert get_ids_list_from_queryset(
            Address.get_near_by_restaurants_by_coordinates(customer_address.long, customer_address.lat)
        ) == [9, 10, 11, 12, 13, 14]

    def test_method_get_all(self, load_admin_panel_data):
        assert get_ids_list_from_queryset(Address.get_all()) == [9, 10, 11, 12, 13, 14]


class TestUser:
    def test_str_method(self, load_data):
        load_data(
            COMMON_CUSTOMER1
        )
        obj = User.objects.get(email=CUSTOMER1_EMAIL)
        assert str(obj) == 'customer1@test.com'

    def test_fields(self, load_data):
        load_data(
            COMMON_CUSTOMER1
        )
        obj = User.objects.get(email=CUSTOMER1_EMAIL)
        assert not obj.is_superuser
        assert obj.first_name == ''
        assert obj.last_name == ''
        assert not obj.is_staff
        assert obj.is_active
        assert obj.username == 'customer1'
        assert obj.email == 'customer1@test.com'
        assert obj.mobile_number == '+919911111111'
        assert not obj.is_admin
        assert not obj.is_blocked
        assert not obj.is_admin
        assert obj.addresses.count() == 1

    def test_method_get_user_emails(self, load_admin_panel_data):
        assert get_ids_list_from_queryset(User.get_user_emails()) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]

    def test_method_is_active_user(self, load_admin_panel_data):
        assert User.is_active_user(email=CUSTOMER1_EMAIL)
        assert not User.is_active_user(email=CUSTOMER2_EMAIL)

    def test_method_is_blocked_user(self, load_admin_panel_data):
        assert User.is_blocked_user(email=AGENT3_EMAIL)
        assert not User.is_blocked_user(email=CUSTOMER1_EMAIL)

    def test_method_is_inactive_user(self, load_admin_panel_data):
        assert User.is_inactive_user(email=CUSTOMER2_EMAIL)
        assert not User.is_inactive_user(email=CUSTOMER1_EMAIL)

    def test_method_get_total_customers(self, load_admin_panel_data):
        assert get_ids_list_from_queryset(User.get_total_customers()) == [2, 3, 4]

    def test_method_get_total_customers_count(self, load_admin_panel_data):
        assert User.get_total_customers_count() == 3

    def test_method_get_blocked_customers(self, load_admin_panel_data):
        assert get_ids_list_from_queryset(User.get_blocked_customers()) == [4]

    def test_method_get_blocked_customers_count(self, load_admin_panel_data):
        assert User.get_blocked_customers_count() == 1

    def test_method_get_active_customers(self, load_admin_panel_data):
        assert get_ids_list_from_queryset(User.get_active_customers()) == [2]

    def test_method_get_active_customers_count(self, load_admin_panel_data):
        assert User.get_active_customers_count() == 1

    def test_method_get_inactive_customers(self, load_admin_panel_data):
        assert get_ids_list_from_queryset(User.get_inactive_customers()) == [3]

    def test_method_get_inactive_customers_count(self, load_admin_panel_data):
        assert User.get_inactive_customers_count() == 1

    def test_method_get_total_agents(self, load_admin_panel_data):
        assert get_ids_list_from_queryset(User.get_total_agents()) == [5, 6, 7, 8, 9]

    def test_method_get_total_agents_count(self, load_admin_panel_data):
        assert User.get_total_agents_count() == 5

    def test_method_get_total_agents_having_cash(self, load_data, load_admin_panel_data):
        load_data(
            THREE_ORDERS_DELIVERED_AND_ONE_PICKED
        )
        assert get_ids_list_from_queryset(User.get_total_agents_having_cash()) == [8, 8, 8]

    def test_method_get_unique_users(self, load_admin_panel_data):
        assert get_ids_list_from_queryset(User.get_unique_users()) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
                                                                       15]

    def test_method_get_total_agents_having_cash_count(self, load_data, load_admin_panel_data):
        load_data(
            THREE_ORDERS_DELIVERED_AND_ONE_PICKED
        )
        assert User.get_total_agents_having_cash_count() == 1

    def test_method_get_unverified_agents(self, load_admin_panel_data):
        assert get_ids_list_from_queryset(User.get_unverified_agents()) == [5, 6]

    def test_method_get_unverified_agents_count(self, load_admin_panel_data):
        assert User.get_unverified_agents_count() == 2

    def test_method_get_blocked_agents(self, load_admin_panel_data):
        assert get_ids_list_from_queryset(User.get_blocked_agents()) == [7, 9]

    def test_method_get_blocked_agents_count(self, load_admin_panel_data):
        assert User.get_blocked_agents_count() == 2

    def test_method_get_active_agents(self, load_admin_panel_data):
        assert get_ids_list_from_queryset(User.get_active_agents()) == [8]

    def test_method_get_active_agents_count(self, load_admin_panel_data):
        assert User.get_active_agents_count() == 1

    def test_method_get_agent_with_user_status(self, load_admin_panel_data):
        assert get_ids_list_from_queryset(User.get_agent_with_user_status(user_status='verified')) == [8]
        assert get_ids_list_from_queryset(User.get_agent_with_user_status(user_status='unverified')) == [6, 8]
        assert get_ids_list_from_queryset(User.get_agent_with_user_status(user_status='blocked')) == [7, 9]

    def test_method_get_agent_with_search_params(self, load_admin_panel_data):
        assert get_ids_list_from_queryset(User.get_agent_with_search_params(params='agent1')) == [5]
        assert get_ids_list_from_queryset(User.get_agent_with_search_params(params='4')) == [8]
        assert get_ids_list_from_queryset(User.get_agent_with_search_params(params='1')) == [5]
        assert get_ids_list_from_queryset(User.get_agent_with_search_params(params='@test.com')) == [5, 6, 7, 8, 9]
        assert get_ids_list_from_queryset(User.get_agent_with_search_params(params='agent')) == [5, 6, 7, 8, 9]

    def test_method_get_users_with_user_status(self, load_admin_panel_data):
        assert get_ids_list_from_queryset(User.get_users_with_user_status(user_status='active')) == [2]
        assert get_ids_list_from_queryset(User.get_users_with_user_status(user_status='inactive')) == [2, 3]
        assert get_ids_list_from_queryset(User.get_users_with_user_status(user_status='blocked')) == [4]

    def test_method_get_user_from_id(self, load_admin_panel_data):
        assert User.get_user_from_id(pk=2) == User.objects.get(id=2)
        assert User.get_user_from_id(pk=2, queryset=User.objects.filter(id__in=[2, 3, 4, 5, 6])) == User.objects.get(
            id=2)

        with pytest.raises(Http404) as e_info:
            User.get_user_from_id(pk=0)
            assert e_info == 'No User matches the given query.'
            User.get_user_from_id(pk=1, queryset=User.objects.filter(id__in=[2, 3, 4, 5, 6]))
            assert e_info == 'No User matches the given query.'

    def test_method_get_object_from_pk(self, load_admin_panel_data):
        assert User.get_object_from_pk(pk=2) == User.objects.get(id=2)
        assert User.get_object_from_pk(pk=0) is None

    def test_method_get_user_from_email(self, load_admin_panel_data):
        assert User.get_user_from_email(email=CUSTOMER1_EMAIL) == User.objects.get(id=2)

    def test_method_get_orders_from_user_id(self, load_admin_panel_data):
        assert get_ids_list_from_queryset(User.get_orders_from_user_id(pk=2)) == []

    def test_method_get_social_auth_from_provider(self, load_admin_panel_data):
        customer_user = User.objects.get(email=CUSTOMER1_EMAIL)
        assert customer_user.get_social_auth_from_provider(provider='github') is None

    def test_method_can_disconnect(self, load_admin_panel_data):
        customer_user = User.objects.get(email=CUSTOMER1_EMAIL)
        assert customer_user.can_disconnect()

    def test_method_get_profile_pic(self, load_admin_panel_data):
        customer_user = User.objects.get(email=CUSTOMER1_EMAIL)
        assert customer_user.get_profile_pic() is None

    def test_method_delete_user(self, load_admin_panel_data):
        customer_user = User.objects.get(email=CUSTOMER1_EMAIL)
        assert customer_user.delete_user() is None
        assert not customer_user.is_active

    def test_method_get_activation_code(self, load_admin_panel_data):
        customer_user = User.objects.get(email=CUSTOMER1_EMAIL)
        previous_activation_count = Activation.objects.count()
        with patch('accounts.models.uuid') as mock_uuid:
            mock_uuid.uuid4.return_value = 'fake-code'
            assert customer_user.get_activation_code() == 'fake-code'
            assert Activation.objects.count() == previous_activation_count + 1
            activation_obj = Activation.objects.order_by('-id').first()
            assert activation_obj
            assert activation_obj.code == 'fake-code'
            assert activation_obj.user == customer_user


class TestActivation:
    def test_str_method(self, load_data):
        load_data(
            COMMON_CUSTOMER2
        )
        obj = Activation.objects.get(id=1)
        assert str(obj) == 'customer2@test.com - 36c54215-296f-4fba-a7f7-c4e96004c231'

    def test_fields(self, load_data):
        load_data(
            COMMON_CUSTOMER2
        )
        obj = Activation.objects.get(id=1)

        assert obj.user.email == 'customer2@test.com'
        assert obj.code == '36c54215-296f-4fba-a7f7-c4e96004c231'
        assert obj.email == ''

    def test_method_is_valid(self, load_data):
        load_data(
            COMMON_CUSTOMER2
        )
        with patch('accounts.models.Activation.is_valid') as mock_is_valid:
            mock_is_valid.return_value = True
            activation_obj = Activation.objects.get(id=1)
            assert activation_obj.is_valid()
            mock_is_valid.return_value = False
            assert not activation_obj.is_valid()

    def test_method_activate(self, load_data):
        load_data(
            COMMON_CUSTOMER2
        )
        activation_obj = Activation.objects.get(id=1)
        previous_activation_count = Activation.objects.count()
        user = activation_obj.user

        assert not user.is_active
        assert activation_obj.activate() is None
        assert Activation.objects.count() == previous_activation_count - 1

        user.refresh_from_db()
        assert user.is_active
