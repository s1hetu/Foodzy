import datetime

from dateutil.utils import today
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from FDA.constants import (
    ACCOUNT_REGISTER_SUCCESS, PAYMENT_RECEIVED_SUCCESSFULLY, REQUIRED_FIELD, DELIVERY_ACCEPTED,
    STATUS_UPDATED, ORDER_DELIVERED, OTP_RESEND, AGENT_REGISTRATION_FORM_PAGE
)
from accounts.models import User, Address
from accounts.utils import send_activation_email
from delivery_agent.forms import UserForm, AddressForm, DocumentForm
from delivery_agent.models import (
    ActivationTime, AcceptedOrder, AdditionalDetail, AgentCashEntry
)
from delivery_agent.serializers import (
    UpdateDeliveryStatusSerializer, UpdateAgentStatusSerializer,
    UpdateDeliveryPaidFieldSerializer
)
from delivery_agent.utils import convert_into_star_rating, get_rating_degrees
from delivery_agent.validations import (
    validate_delivery_status_data, validate_accept_delivery_data,
    validate_accept_payment_data, validate_otp_validation_api_data
)
from orders.models import Order, OrderItems, OrderPayoutDetail
from orders.utils import send_otp_email, get_delivery_charge_from_distance
from restaurant.models import Items


class RegisterDeliveryAgentFormService:
    @staticmethod
    def get_form():
        return {'user': UserForm(), 'address': AddressForm(), 'documents': DocumentForm()}

    @staticmethod
    def save_form(request):
        user = UserForm(request.POST)
        address = AddressForm(request.POST)
        documents = DocumentForm(request.POST, request.FILES)

        if user.is_valid() and address.is_valid() and documents.is_valid():
            user = user.save()
            address.save(agent=user)
            documents.save(agent=user)
            code = user.get_activation_code()
            send_activation_email(request, user.email, code)
            messages.success(request, ACCOUNT_REGISTER_SUCCESS)
            return redirect('login')

        return render(request, template_name=AGENT_REGISTRATION_FORM_PAGE,
                      context={'user': user, 'address': address, 'documents': documents})


class AgentPanel:
    @staticmethod
    def get_context_data(context, agent):
        agent_object = AdditionalDetail.get_agent_additional_details(agent)
        delivery_agent_status = 'on' if agent_object.status == 'Available' else 'off'
        avg_rating = agent_object.rating
        avg_rating, first_half_rating_degrees, second_half_rating_degrees = get_rating_degrees(avg_rating)
        activated_today = ActivationTime.today_active_time(agent)
        number_of_orders = AcceptedOrder.accepted_order_deliveries_count(agent)
        orders_delivered = AcceptedOrder.total_orders_delivered_count(agent)
        today_delivery = AcceptedOrder.orders_delivered_today_count(agent)
        active_delivery_count = AcceptedOrder.current_active_delivery_count(agent)
        active_delivery = active_delivery_count != 0
        total_order_price = AcceptedOrder.get_total_value_of_orders_delivered_by_agent(agent)
        cod_collection = AgentCashEntry.cash_collection_of_agent(agent)
        my_profit = AcceptedOrder.get_delivery_charge(agent)

        context.update(
            {'delivery_agent_status': delivery_agent_status, 'ratings': avg_rating, 'activated_today': activated_today,
             'rating_first_half': first_half_rating_degrees, 'rating_second_half': second_half_rating_degrees,
             'number_of_orders': number_of_orders, 'orders_delivered': orders_delivered,
             'delivered_today': today_delivery, 'active_delivery': active_delivery,
             'total_order_price': total_order_price, 'cod_collection': cod_collection,
             'my_profit': my_profit
             })
        return context


class UpdateAgentStatusService:
    def __init__(self, request, model):
        self.request = request
        self.model = model

    def update_data(self):
        agent = self.request.user
        data = self.request.data.copy()
        serializer = UpdateAgentStatusSerializer(AdditionalDetail.get_agent_additional_details(agent), data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if AcceptedOrder.current_active_delivery_count(agent=agent) == 0:
            if data['status'] == 'Available':
                ActivationTime.add_time_entry(agent=agent)
            elif obj := ActivationTime.last_time_entry_of_agent(agent=agent):
                obj.ended_at = timezone.now()
                obj.save()
        return {'message': STATUS_UPDATED, 'data': data}


class AllDeliveryListService:
    def __init__(self, request, model):
        self.request = request
        self.model = model

    def get_queryset(self, queryset):
        queryset = self.model.accepted_order_deliveries(self.request.user, queryset).filter(
            order__status='delivered')
        return queryset

    def get_context_data(self, context):
        week_day = today().weekday()
        first_date = (datetime.date.today() - datetime.timedelta(days=week_day))
        second_date = datetime.date.today()
        first_date_of_month = second_date.replace(day=1)
        month_deliveries = self.model.accepted_order_deliveries_on_range(self.request.user, first_date_of_month,
                                                                         second_date)
        context['month_count'] = month_deliveries.count()
        context['week_count'] = month_deliveries.filter(
            order__order_date__date__range=[first_date, second_date]).count()
        context['today_count'] = self.model.orders_delivered_today_count(agent=self.request.user)

        return context


class CurrentDeliveryListService:
    def __init__(self, request, model):
        self.request = request
        self.model = model

    def get_queryset(self, queryset):
        queryset = self.model.get_current_active_deliveries(self.request.user, queryset).select_related('order',
                                                                                                        'order__order_payout',
                                                                                                        'order__user')
        return queryset


class SeeAvailableDeliveryListService:
    def __init__(self, request, model):
        self.request = request
        self.model = model

    def get_queryset(self, queryset):
        lat = self.request.GET.get('lat')
        long = self.request.GET.get('long')
        restaurant_addresses = Address.get_near_by_restaurants_by_coordinates(long, lat).values_list('id', flat=True)
        queryset = queryset.filter(status__in=['accepted', 'preparing', 'ready to pick', 'prepared'],
                                   accepted_order__isnull=True, restaurant__address_id__in=restaurant_addresses)
        return queryset


class AgentApplicationStatusService:
    @staticmethod
    def get_context_data(context, user):
        if not hasattr(user, 'document'):
            raise PermissionDenied
        context.update({'document': user.document})
        return context


class AllTimeEntriesService:
    def __init__(self, request, model):
        self.request = request
        self.model = model

    def get_queryset(self, queryset):
        queryset = self.model.get_active_time_entries(user=self.request.user)
        return queryset


class UpdateDeliveryStatusService:
    def __init__(self, request, model):
        self.request = request
        self.model = model

    def update_data(self):
        data = self.request.data.copy()
        user = self.request.user
        validated_data = validate_delivery_status_data(data, user)
        order_object = self.model.get_object_from_pk(pk=validated_data['id'])
        serializer = UpdateDeliveryStatusSerializer(order_object, data=validated_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return {'message': STATUS_UPDATED, 'data': data}


class DetailOrderService:
    @staticmethod
    def get_context_data(context, agent, pk):
        order_obj = Order.get_object_from_pk(pk)
        delivery_charge = get_delivery_charge_from_distance(order_obj.restaurant_address_lat,
                                                            order_obj.restaurant_address_long,
                                                            order_obj.user_address_lat, order_obj.user_address_long)
        details = OrderItems.get_order_items_from_order(order=order_obj)
        current_status = order_obj.status
        delivery_status = {'ready to pick': 0, 'picked': 1, 'out for delivery': 2, 'delivered': 3, }

        # get value from delivery_status  if order is ready for delivery else status remains
        current_delivery_status = delivery_status.get(current_status, current_status)

        # get boolean value for update_order_status if order is accepted by agent
        update_order_status = bool(hasattr(order_obj, 'accepted_order') and order_obj.accepted_order.agent == agent
                                   and current_status in delivery_status)

        context.update({'order': order_obj, 'details': details, 'current_status': current_delivery_status,
                        'update_order_status': update_order_status, 'delivery_charge': delivery_charge}, )
        return context


class AcceptDeliveryService:
    def __init__(self, request, model):
        self.request = request
        self.model = model

    def create_data(self):
        data = self.request.data.copy()
        agent = self.request.user
        validated_data = validate_accept_delivery_data(data=data, agent=agent)
        return {'message': DELIVERY_ACCEPTED, 'data': validated_data}


class AcceptPaymentService:
    def __init__(self, request, model):
        self.request = request
        self.model = model

    def update_data(self):
        data = self.request.data.copy()
        user = self.request.user
        validated_data = validate_accept_payment_data(data=data, user=user)
        order_object = self.model.get_object_from_pk(pk=validated_data['order_id'])
        serializer = UpdateDeliveryPaidFieldSerializer(order_object, data=validated_data)
        serializer.is_valid(raise_exception=True)

        AgentCashEntry.create_agent_cash_entry(agent=self.request.user, order=order_object,
                                               amount=order_object.total)
        serializer.save()
        return {'message': PAYMENT_RECEIVED_SUCCESSFULLY, 'data': validated_data}


class AgentReviewService:
    def __init__(self, request, model):
        self.request = request
        self.model = model

    def get_context_data(self, context, pk):
        user = User.get_user_from_id(pk)
        if self.request.user != user:
            raise PermissionDenied
        delivery_rating_and_review = AcceptedOrder.get_agent_reviews_and_ratings(pk)
        convert_into_star_rating(delivery_rating_and_review)
        context.update({'reviews': delivery_rating_and_review})
        return context


class AgentEarningService:
    def __init__(self, request, model):
        self.request = request
        self.model = model

    def get_queryset(self, queryset):
        queryset = OrderPayoutDetail.get_payout_detail_for_agent(agent_id=self.request.user.id).order_by('id')
        return queryset

    def get_context_data(self, context):
        last_month_earning = OrderPayoutDetail.get_agent_last_month_earning(self.request.user)
        total_earning = OrderPayoutDetail.get_agent_total_earning(self.request.user)
        context['last_month_earning'] = last_month_earning
        context['total_earning'] = total_earning
        return context


class ValidateOtpAPIViewService:
    def __init__(self, request, model):
        self.request = request
        self.model = model

    def update_data(self):
        data = self.request.data.copy()
        user = self.request.user
        validated_data = validate_otp_validation_api_data(user, data)
        order = validated_data['order']
        order.status = 'delivered'
        items = []
        for item in order.items.all():
            item.number_of_purchases += 1
            items.append(item)
        Items.objects.bulk_update(items, fields=['number_of_purchases'])
        OrderPayoutDetail.create_payout_detail(order=order, agent=validated_data['agent'],
                                               agent_amount=validated_data['agent_amount'],
                                               rest_amount=validated_data['rest_amount'],
                                               commission=validated_data['commission'])

        order.save()
        order.confirm_otp.delete()
        return {'message': ORDER_DELIVERED}


class ResendOtpAPIViewService:
    def __init__(self, request, model):
        self.request = request
        self.model = model

    def update_data(self):
        order_id = self.request.data.get('order_id')
        if not order_id:
            raise ValidationError({'order_id': REQUIRED_FIELD})
        order = Order.get_object_from_pk(pk=int(order_id))

        if not hasattr(order, 'confirm_otp'):
            otp = self.model.get_otp(order=order)
        else:
            otp = self.model.generate_otp_code()
            order.confirm_otp.otp = otp
            order.confirm_otp.save()
        send_otp_email(order.user.email, otp, order.id)
        return {'message': OTP_RESEND}
