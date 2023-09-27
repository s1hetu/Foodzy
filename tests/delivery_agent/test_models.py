import datetime
from decimal import Decimal

from accounts.models import User
from delivery_agent.models import AdditionalDetail, ActivationTime, Document, AcceptedOrder, AgentCashEntry
from orders.models import Order
from tests.constants import (
    COMMON_AGENT1, COMMON_AGENT6, AGENT4_EMAIL, AGENT6_EMAIL, COMMON_RESTAURANT6,
    COMMON_CUSTOMER1, ORDER_FOR_SAME_RESTAURANTS, COMMON_AGENT4,
    THREE_ORDERS_DELIVERED_AND_ONE_PICKED,
    TWO_DELIVERED_ORDER_FOR_SAME_RESTAURANTS, AGENT1_EMAIL
)

filename = "./media/default.jpg"


def get_ids_list_from_queryset(queryset):
    return list(queryset.values_list('id', flat=True))


class TestDocumentModel(object):

    def test_str_method(self, load_data):
        load_data(COMMON_AGENT1)
        agent = User.objects.get(email=AGENT1_EMAIL)
        document_obj = Document.objects.get(agent=agent)
        assert str(document_obj) == '1 | agent1@test.com | False'

    def test_fields(self, load_data):
        load_data(COMMON_AGENT1)
        agent = User.objects.get(email=AGENT1_EMAIL)
        document_obj = Document.objects.get(agent=agent)
        assert document_obj.agent.email == 'agent1@test.com'
        assert document_obj.is_verified is False
        assert document_obj.account_no == '5555555555555'
        assert document_obj.ifsc_code == 'ABCD0123456'
        assert document_obj.pancard_number == 'BNZAA2318J'
        assert document_obj.pancard_document is not None
        assert document_obj.ifsc_code == 'ABCD0123456'
        assert document_obj.license_number == 'HR-0619850034761'
        assert document_obj.license_document is not None
        assert document_obj.razorpay_contact_id is None
        assert document_obj.razorpay_fund_account_id is None


class TestAdditionalDetailModel(object):

    def test_str_method(self, load_data):
        load_data(
            COMMON_AGENT6
        )
        agent = User.objects.get(email=AGENT6_EMAIL)
        additional_detail_obj = AdditionalDetail.objects.get(agent=agent)
        assert str(additional_detail_obj) == '6 | agent6@test.com'

    def test_fields(self, load_data):
        load_data(
            COMMON_AGENT6
        )
        agent = User.objects.get(email=AGENT6_EMAIL)
        additional_detail_obj = AdditionalDetail.objects.get(agent=agent)
        assert additional_detail_obj.agent.email == 'agent6@test.com'
        assert additional_detail_obj.status == 'Not Available'
        assert additional_detail_obj.rating is None

    def test_get_agent_additional_details(self, load_data):
        load_data(
            COMMON_AGENT6
        )
        agent = User.objects.get(email=AGENT6_EMAIL)
        assert isinstance(AdditionalDetail.get_agent_additional_details(agent), AdditionalDetail)
        assert AdditionalDetail.get_agent_additional_details(agent).id == 6

    def test_get_agent_status(self, load_data):
        load_data(
            COMMON_AGENT6
        )
        agent = User.objects.get(email=AGENT6_EMAIL)
        assert AdditionalDetail.get_agent_status(agent) == 'Not Available'


class TestActivationTimeModel(object):

    def test_str_method(self, load_data):
        load_data(
            COMMON_AGENT4
        )
        activation_time_obj = ActivationTime.objects.get(id=1)
        assert str(
            activation_time_obj) == f'agent4@test.com | {datetime.datetime(2022, 12, 22, 9, 25, 35, 98000, tzinfo=datetime.timezone.utc)}'

    def test_fields(self, load_data):
        load_data(
            COMMON_AGENT4
        )
        activation_time_obj = ActivationTime.objects.get(id=2)
        # breakpoint()
        assert activation_time_obj.agent.email == 'agent4@test.com'
        assert activation_time_obj.started_at == datetime.datetime(2022, 12, 22, 9, 25, 36, 202000,
                                                                   tzinfo=datetime.timezone.utc)

        assert activation_time_obj.ended_at == datetime.datetime(2022, 12, 22, 9, 42, 21, 102000,
                                                                 tzinfo=datetime.timezone.utc)
        assert activation_time_obj.session_duration == datetime.timedelta(seconds=1004, microseconds=900000)

    def test_add_time_entry(self, load_data):
        load_data(
            COMMON_AGENT4
        )
        prev_total_time_entries = ActivationTime.objects.count()
        agent = User.objects.get(email=AGENT4_EMAIL)
        ActivationTime.add_time_entry(agent=agent)
        assert ActivationTime.objects.count() == prev_total_time_entries + 1

    def test_last_time_entry_of_agent(self, load_data):
        load_data(
            COMMON_AGENT4
        )
        agent = User.objects.get(email=AGENT4_EMAIL)
        assert ActivationTime.last_time_entry_of_agent(agent).started_at == datetime.datetime(2022, 12, 22, 9, 44, 25,
                                                                                              307000,
                                                                                              tzinfo=datetime.timezone.utc)

    def test_get_active_time_entries(self, load_data):
        load_data(
            COMMON_AGENT4
        )
        agent = User.objects.get(email=AGENT4_EMAIL)
        assert get_ids_list_from_queryset(ActivationTime.get_active_time_entries(agent)) == [4, 3, 2, 1]

    def test_get_session(self, load_data):
        load_data(
            COMMON_AGENT4
        )
        activation_time_obj = ActivationTime.objects.get(id=2)
        assert activation_time_obj.session_duration == datetime.timedelta(seconds=1004, microseconds=900000)

    def test_today_active_time(self, load_data):
        load_data(
            COMMON_AGENT4
        )
        agent = User.objects.get(email=AGENT4_EMAIL)
        assert ActivationTime.today_active_time(agent) == '0:00:00'


class TestAcceptedOrderModel(object):

    def test_str_method(self, load_data):
        load_data(
            COMMON_AGENT4,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            TWO_DELIVERED_ORDER_FOR_SAME_RESTAURANTS
        )
        accepted_order_obj = AcceptedOrder.objects.get(id=1)
        assert str(
            accepted_order_obj) == '1 | agent4| 8'

    def test_fields(self, load_data):
        load_data(
            COMMON_AGENT4,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            TWO_DELIVERED_ORDER_FOR_SAME_RESTAURANTS
        )
        accepted_order_obj = AcceptedOrder.objects.get(id=1)
        assert accepted_order_obj.agent.email == 'agent4@test.com'
        assert accepted_order_obj.order.id == 1
        assert accepted_order_obj.rating == 3
        assert accepted_order_obj.review == 'Good Agent Review 1'

    def test_get_agent_from_order_id(self, load_data):
        load_data(
            COMMON_AGENT4,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            TWO_DELIVERED_ORDER_FOR_SAME_RESTAURANTS
        )
        assert AcceptedOrder.get_agent_from_order_id(pk=1).email == 'agent4@test.com'

    def test_get_total_value_of_orders_delivered_by_agent(self, load_data):
        load_data(
            COMMON_AGENT4,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            TWO_DELIVERED_ORDER_FOR_SAME_RESTAURANTS
        )
        agent = User.objects.get(email=AGENT4_EMAIL)
        assert AcceptedOrder.get_total_value_of_orders_delivered_by_agent(agent) == Decimal('390.00')

    def test_get_delivery_charge(self, load_data):
        load_data(
            COMMON_AGENT4,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            TWO_DELIVERED_ORDER_FOR_SAME_RESTAURANTS
        )
        agent = User.objects.get(email=AGENT4_EMAIL)
        assert AcceptedOrder.get_delivery_charge(agent) == Decimal('100.00')

    def test_get_object_by_id(self, load_data):
        load_data(
            COMMON_AGENT4,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            TWO_DELIVERED_ORDER_FOR_SAME_RESTAURANTS
        )
        assert AcceptedOrder.get_object_by_id(pk=1).order.id == 1

    def test_average_rating(self, load_data):
        load_data(
            COMMON_AGENT4,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            TWO_DELIVERED_ORDER_FOR_SAME_RESTAURANTS
        )
        accepted_order_obj = AcceptedOrder.objects.get(id=1)
        assert accepted_order_obj.average_rating() == 3.0

    def test_accept_deliveries(self, load_data, ):
        load_data(
            COMMON_AGENT6,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            ORDER_FOR_SAME_RESTAURANTS
        )
        agent = User.objects.get(email=AGENT6_EMAIL)
        # Update order status from waiting to ready to pick to make order available for delivery
        Order.objects.filter(id=1).update(status='ready to pick')

        # Update agent status  to available
        AdditionalDetail.objects.filter(agent=agent).update(status='Available')

        prev_total_accepted_order = AcceptedOrder.objects.count()
        AcceptedOrder.accept_deliveries(agent=agent, order_id=1)
        assert AcceptedOrder.objects.count() == prev_total_accepted_order + 1

    def test_get_agent_reviews_and_ratings(self, load_data):
        load_data(
            COMMON_AGENT4,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            THREE_ORDERS_DELIVERED_AND_ONE_PICKED
        )
        agent = User.objects.get(email=AGENT4_EMAIL)
        assert get_ids_list_from_queryset(AcceptedOrder.get_agent_reviews_and_ratings(agent_id=agent.id)) == [1, 2, 3]

    def test_get_current_active_deliveries(self, load_data):
        load_data(
            COMMON_AGENT4,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            THREE_ORDERS_DELIVERED_AND_ONE_PICKED
        )
        agent = User.objects.get(email=AGENT4_EMAIL)
        assert get_ids_list_from_queryset(AcceptedOrder.get_current_active_deliveries(agent=agent)) == [4]

    def test_current_active_delivery_count(self, load_data):
        load_data(
            COMMON_AGENT4,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            THREE_ORDERS_DELIVERED_AND_ONE_PICKED
        )
        agent = User.objects.get(email=AGENT4_EMAIL)
        assert AcceptedOrder.current_active_delivery_count(agent=agent) == 1

    def test_accepted_order_deliveries(self, load_data):
        load_data(
            COMMON_AGENT4,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            THREE_ORDERS_DELIVERED_AND_ONE_PICKED
        )
        agent = User.objects.get(email=AGENT4_EMAIL)
        assert get_ids_list_from_queryset(AcceptedOrder.accepted_order_deliveries(agent=agent)) == [4, 1, 2, 3]

    def test_accepted_order_deliveries_count(self, load_data):
        load_data(
            COMMON_AGENT4,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            THREE_ORDERS_DELIVERED_AND_ONE_PICKED
        )
        agent = User.objects.get(email=AGENT4_EMAIL)
        assert AcceptedOrder.accepted_order_deliveries_count(agent=agent) == 4

    def test_accepted_order_deliveries_on_range(self, load_data):
        load_data(
            COMMON_AGENT4,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            THREE_ORDERS_DELIVERED_AND_ONE_PICKED
        )
        agent = User.objects.get(email=AGENT4_EMAIL)
        today_date = datetime.date.today()
        first_date_of_month = today_date.replace(day=1)
        AcceptedOrder.accepted_order_deliveries_on_range(agent, first_date_of_month, today_date)
        assert get_ids_list_from_queryset(
            AcceptedOrder.accepted_order_deliveries_on_range(agent, first_date_of_month, today_date)) == []

    def test_total_orders_delivered(self, load_data):
        load_data(
            COMMON_AGENT4,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            THREE_ORDERS_DELIVERED_AND_ONE_PICKED
        )
        agent = User.objects.get(email=AGENT4_EMAIL)
        assert get_ids_list_from_queryset(AcceptedOrder.total_orders_delivered(agent=agent)) == [1, 2, 3]

    def test_total_orders_delivered_count(self, load_data):
        load_data(
            COMMON_AGENT4,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            THREE_ORDERS_DELIVERED_AND_ONE_PICKED
        )
        agent = User.objects.get(email=AGENT4_EMAIL)
        assert AcceptedOrder.total_orders_delivered_count(agent=agent) == 3

    def test_orders_delivered_today(self, load_data):
        load_data(
            COMMON_AGENT4,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            THREE_ORDERS_DELIVERED_AND_ONE_PICKED
        )
        agent = User.objects.get(email=AGENT4_EMAIL)
        assert get_ids_list_from_queryset(AcceptedOrder.orders_delivered_today(agent=agent)) == []

    def test_orders_delivered_today_count(self, load_data):
        load_data(
            COMMON_AGENT4,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            THREE_ORDERS_DELIVERED_AND_ONE_PICKED
        )
        agent = User.objects.get(email=AGENT4_EMAIL)
        assert AcceptedOrder.orders_delivered_today_count(agent=agent) == 0

    def test_save(self, load_data):
        load_data(
            COMMON_AGENT4,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            THREE_ORDERS_DELIVERED_AND_ONE_PICKED
        )
        agent = User.objects.get(email=AGENT4_EMAIL)
        prev_agent_rating = AdditionalDetail.objects.get(agent=agent).rating
        accepted_order_obj = AcceptedOrder.objects.get(id=4)
        accepted_order_obj.rating = 5.0
        accepted_order_obj.save()
        new_agent_rating = AdditionalDetail.objects.get(agent=agent).rating
        assert new_agent_rating == round(((prev_agent_rating * 3) + 5) / 4, 2)


class TestAgentCashEntryModel(object):

    def test_str_method(self, load_data):
        load_data(
            COMMON_AGENT4,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            THREE_ORDERS_DELIVERED_AND_ONE_PICKED
        )
        accepted_cash_obj = AgentCashEntry.objects.get(id=1)
        assert str(accepted_cash_obj) == 'agent 8 | order 1'

    def test_agent_cash_entry_data(self, load_data):
        load_data(
            COMMON_AGENT4,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            THREE_ORDERS_DELIVERED_AND_ONE_PICKED
        )
        accepted_cash_obj = AgentCashEntry.objects.get(id=1)
        assert accepted_cash_obj.agent.email == 'agent4@test.com'
        assert accepted_cash_obj.order.id == 1
        assert accepted_cash_obj.deposit is False
        assert accepted_cash_obj.amount == Decimal('150.00')

    def test_create_agent_cash_entry(self, load_data):
        load_data(
            COMMON_AGENT4,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            THREE_ORDERS_DELIVERED_AND_ONE_PICKED
        )
        prev_agent_cash_entries_total = AgentCashEntry.objects.count()
        AgentCashEntry.create_agent_cash_entry(agent=User.objects.get(email=AGENT4_EMAIL),
                                               order=Order.objects.get(id=4), amount=240)
        assert AgentCashEntry.objects.count() == prev_agent_cash_entries_total + 1

    def test_cash_collection_of_agent(self, load_data):
        load_data(
            COMMON_AGENT4,
            COMMON_RESTAURANT6,
            COMMON_CUSTOMER1,
            THREE_ORDERS_DELIVERED_AND_ONE_PICKED
        )
        agent = User.objects.get(email=AGENT4_EMAIL)
        assert AgentCashEntry.cash_collection_of_agent(agent) == Decimal('630.00')
