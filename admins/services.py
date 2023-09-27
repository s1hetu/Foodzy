import razorpay
from django.contrib import messages

from FDA.constants import CANNOT_BLOCK_RESTAURANT_ERROR, CONTACT_NOT_CREATED_ERROR, FUND_NOT_CREATED_ERROR
from accounts.models import User
from admins.utils import create_razorpay_contact, create_fund_account
from delivery_agent.models import AgentCashEntry
from orders.models import Order, choice_status, OrderItems
from orders.services import client
from restaurant.models import Restaurant
import logging

logger = logging.getLogger('info_log')


class HomeService:
    @staticmethod
    def get_context_data(context):
        context.update(
            {
                'total_orders': Order.get_orders_count(),
                'total_delivered_orders': Order.get_delivered_orders_count(),
                'total_price': Order.get_total_of_all_orders(),

                'total_customers': User.get_total_customers_count(),
                'deactive_customers': User.get_blocked_customers_count(),
                'active_customers': User.get_active_customers_count(),
                'unverified_customers': User.get_inactive_customers_count(),

                'total_restaurants': Restaurant.get_total_restaurants_count(),
                'deactive_restaurants': Restaurant.get_blocked_restaurants_count(),
                'active_restaurants': Restaurant.get_active_restaurants_count(),
                'unverified_restaurants': Restaurant.get_restaurant_applications_count(),

                'total_agents': User.get_total_agents_count(),
                'unverified_agents': User.get_unverified_agents_count(),
                'deactive_agents': User.get_blocked_agents_count(),
                'active_agents': User.get_active_agents_count(),
                'agent_with_cash': User.get_total_agents_having_cash_count(),
            }
        )
        return context


class DriversListService:
    def __init__(self, request, model):
        self.request = request
        self.model = model

    def get_queryset(self, queryset):
        queryset = self.model.get_total_agents(queryset=queryset)

        if user_status := self.request.GET.getlist('user_status[]'):
            queryset = self.model.get_agent_with_user_status(user_status, queryset)

        if params := self.request.GET.get('agent'):
            queryset = self.model.get_agent_with_search_params(params, queryset)

        return queryset


class DriversApplicationListService:
    def __init__(self, request, model):
        self.request = request
        self.model = model

    def get_queryset(self, queryset):
        queryset = self.model.get_unverified_agents(queryset=queryset)

        if params := self.request.GET.get('agent'):
            queryset = self.model.get_agent_with_search_params(params, queryset)

        return queryset


class DriversDetailService:
    @staticmethod
    def get_context_data(context, pk):
        context.update({'agent_user': User.get_user_from_id(pk=pk, queryset=User.get_total_agents())})
        return context


class UsersListService:
    def __init__(self, request, model):
        self.request = request
        self.model = model

    def get_queryset(self, queryset):
        queryset = self.model.get_total_customers(queryset=queryset)

        if params := self.request.GET.get('search_user'):
            queryset = self.model.get_agent_with_search_params(params, queryset)

        if user_status := self.request.GET.getlist('user_status[]'):
            queryset = self.model.get_users_with_user_status(user_status, queryset)

        return queryset


class UsersDetailService:
    @staticmethod
    def get_context_data(context, pk):
        context.update({'user_obj': User.get_user_from_id(pk=pk, queryset=User.get_total_customers())})
        return context


class RestaurantListService:
    def __init__(self, request, model):
        self.request = request
        self.model = model

    def get_queryset(self, queryset):
        queryset = self.model.get_total_restaurants(queryset=queryset)

        if params := self.request.GET.get('restaurant_search'):
            queryset = self.model.get_restaurant_with_search_params(params, queryset)

        if restaurant_status := self.request.GET.getlist('restaurant_status[]'):
            queryset = self.model.get_restaurant_with_restaurant_status(restaurant_status, queryset)

        return queryset


class RestaurantsDetailService:
    @staticmethod
    def get_context_data(context, pk):
        context.update({'restaurant': Restaurant.get_restaurant_from_id(pk=pk, queryset=Restaurant.get_total_restaurants())})
        return context


class RestaurantApplicationListService:
    def __init__(self, request, model):
        self.request = request
        self.model = model

    def get_queryset(self, queryset):
        queryset = self.model.get_restaurant_applications(queryset=queryset)

        if params := self.request.GET.get('restaurant_search'):
            queryset = self.model.get_restaurant_with_search_params(params, queryset)

        return queryset


class OrdersListService:
    def __init__(self, request, model):
        self.request = request
        self.model = model

    def get_queryset(self, queryset):
        queryset = self.model.get_orders()

        if params := self.request.GET.get('order'):
            queryset = self.model.get_order_with_search_params(params, queryset)

        if params := self.request.GET.get('order_status'):
            queryset = self.model.get_order_from_status(params, queryset)

        if params := self.request.GET.get('restaurant'):
            queryset = self.model.get_order_from_restaurant_id(params, queryset)

        return queryset

    @staticmethod
    def get_context_data(context):
        context.update({'order_status': choice_status})
        context.update({'restaurants': Restaurant.get_active_restaurants()})
        return context


class OrdersDetailService:
    @staticmethod
    def get_context_data(context, pk):
        context.update({'order': Order.get_object_from_pk(pk=pk)})
        context.update({'items': OrderItems.get_items_from_order_id(pk=pk)})
        return context


class UserActionService:
    @staticmethod
    def perform_restaurant_action(request, pk):
        restaurant_action = request.POST.get('restaurant_action')
        restaurant_obj = Restaurant.get_object_from_pk(pk=pk)
        if restaurant_action and restaurant_action == 'block' and not restaurant_obj.is_blocked:
            for order in restaurant_obj.orders.all():
                if order.status in ["waiting", "accepted", "preparing", "prepared"]:
                    messages.error(request, CANNOT_BLOCK_RESTAURANT_ERROR)
                    restaurant_obj.is_blocked = False
                    break
            else:
                restaurant_obj.is_blocked = True
        elif restaurant_obj and restaurant_action == 'unblock' and restaurant_obj.is_blocked:
            restaurant_obj.is_blocked = False

        restaurant_obj.save()

    @staticmethod
    def perform_agent_action(request, pk):
        agent_action = request.POST.get('agent_action')
        agent_obj = User.get_object_from_pk(pk=pk)
        if agent_action and agent_action == 'block' and not agent_obj.is_blocked:
            agent_obj.is_blocked = True
        elif agent_obj and agent_action == 'unblock' and agent_obj.is_blocked:
            agent_obj.is_blocked = False

        agent_obj.save()

    @staticmethod
    def perform_customer_action(request, pk):
        user_action = request.POST.get('user_action')
        user_obj = User.get_object_from_pk(pk=pk)
        if user_action and user_action == 'block' and not user_obj.is_blocked:
            user_obj.is_blocked = True
        elif user_obj and user_action == 'unblock' and user_obj.is_blocked:
            user_obj.is_blocked = False

        user_obj.save()

    @staticmethod
    def perform_cod_agent_action(request, pk):
        User.get_orders_from_user_id(pk=pk).update(deposit=True)
        logger.info(f'Payment is collected from agent with User(id={pk})')

    @staticmethod
    def perform_agent_application_action(request, pk):
        is_agent_valid = request.POST.get('is_agent_valid')

        user = User.get_object_from_pk(pk=pk)
        document = user.document

        if is_agent_valid in ['0', '1'] and document.application_status == 'pending':
            if is_agent_valid == '1':
                document.is_verified = True
                document.application_status = 'approved'

                contact = create_razorpay_contact(
                    client=client,
                    name=f"agent{user.id}",
                    email=user.email,
                    contact=str(user.mobile_number),
                    contact_type='vendor',
                    reference_id=f"{user.id} - delivery agent"
                )

                contact_id = contact.get('id')
                if not contact_id:
                    messages.error(request, CONTACT_NOT_CREATED_ERROR)
                    return

                document.razorpay_contact_id = contact_id

                fund_account = create_fund_account(
                    client=client,
                    contact_id=contact['id'],
                    user_name=f"user{user.id}",
                    ifsc='RAZR0000001',
                    account_number=document.account_no
                )

                fund_account_id = fund_account.get('id')

                if not fund_account_id:
                    messages.error(request, FUND_NOT_CREATED_ERROR)
                    return

                document.razorpay_fund_account_id = fund_account_id
            elif is_agent_valid == '0':
                document.application_status = 'rejected'

            document.save()

    @staticmethod
    def perform_restaurant_application_action(request, pk):
        is_restaurant_valid = request.POST.get('is_restaurant_valid')

        restaurant = Restaurant.get_object_from_pk(pk=pk)

        if is_restaurant_valid in ['0', '1'] and restaurant.application_status == 'pending':
            if is_restaurant_valid == '1':
                restaurant.is_verified = True
                restaurant.application_status = 'approved'

                contact = create_razorpay_contact(
                    client=client,
                    name=f"restaurant{restaurant.owner.id}",
                    email=restaurant.owner.email,
                    contact=str(restaurant.owner.mobile_number),
                    contact_type='vendor',
                    reference_id=f"{restaurant.owner.id} - restaurant owner"
                )

                contact_id = contact.get('id')

                if not contact_id:
                    messages.error(request, CONTACT_NOT_CREATED_ERROR)
                    return

                restaurant.documents.razorpay_contact_id = contact_id

                fund_account = create_fund_account(
                    client=client,
                    contact_id=contact['id'],
                    user_name=f"restaurant{restaurant.owner.id}",
                    ifsc='RAZR0000001',
                    account_number=restaurant.documents.account_no
                )

                fund_account_id = fund_account.get('id')

                if not fund_account_id:
                    messages.error(request, FUND_NOT_CREATED_ERROR)
                    return

                restaurant.documents.razorpay_fund_account_id = fund_account_id
                restaurant.documents.save()

            elif is_restaurant_valid == '0':
                restaurant.application_status = 'rejected'
            restaurant.save()


class CodAgentListService:
    def __init__(self, request, model):
        self.request = request
        self.model = model

    def get_queryset(self, queryset):
        queryset = self.model.get_unique_users(queryset=self.model.get_total_agents_having_cash(queryset=queryset))

        if params := self.request.GET.get('agent'):
            queryset = self.model.get_agent_with_search_params(params, queryset)

        return queryset


class CodAgentDetailService:
    @staticmethod
    def get_context_data(context, pk):
        context['agent_cash_orders'] = User.get_orders_from_user_id(
            pk=pk,
            queryset=User.get_unique_users(
                queryset=User.get_total_agents_having_cash()
            )
        )
        context['agent_user'] = User.get_user_from_id(pk=pk)
        context['total_cash'] = AgentCashEntry.get_total_cash(queryset=context['agent_cash_orders']) or 0
        return context
