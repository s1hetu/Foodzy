from django.core.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError

from FDA.constants import (
    REQUIRED_FIELD, ALREADY_AN_ACCEPTED_ORDER,
    CAN_NOT_ACCEPT_WAITING_CANCELLED_OR_REJECTED_ORDER, DELIVERY_ALREADY_ACCEPTED,
    ALREADY_UPDATED, ORDER_NOT_DELIVERED, OTP_NOT_FOUND, WRONG_OTP
)
from delivery_agent.models import AcceptedOrder
from orders.models import Order
from orders.utils import get_delivery_charge_from_distance


def validate_delivery_status_data(data, user):
    delivery_status = {
        0: 'ready to pick',
        1: 'picked',
        2: 'out for delivery',
    }
    try:
        order_id = data['id']
        status = int(data['status'])
        data['status'] = delivery_status[status]
    except Exception as e:
        raise ValidationError('Bad Request') from e
    order_agent = AcceptedOrder.get_agent_from_order_id(order_id)
    if not order_agent or order_agent != user:
        raise PermissionDenied
    return data


def validate_accept_delivery_data(data, agent):
    order_id = data.get('order_id')
    if not order_id:
        raise ValidationError({'order_id': REQUIRED_FIELD})
    order = Order.get_object_from_pk(pk=order_id)
    if AcceptedOrder.current_active_delivery_count(agent) != 0:
        raise ValidationError({'Error': ALREADY_AN_ACCEPTED_ORDER})
    if order.status in ['waiting', 'rejected'] or order.cancelled:
        raise ValidationError({'Error': CAN_NOT_ACCEPT_WAITING_CANCELLED_OR_REJECTED_ORDER})
    if hasattr(order, "accepted_order"):
        raise ValidationError(DELIVERY_ALREADY_ACCEPTED)
    AcceptedOrder.accept_deliveries(agent=agent, order_id=order_id)
    return data


def validate_accept_payment_data(data, user):
    order_id = data.get('order_id')
    if not order_id:
        raise ValidationError({'order_id': REQUIRED_FIELD})
    order_agent = AcceptedOrder.get_agent_from_order_id(order_id)
    data['paid'] = True
    if order_agent != user:
        raise PermissionDenied
    if Order.is_order_paid(data['order_id']):
        raise ValidationError({'paid': ALREADY_UPDATED})
    if Order.get_order_status(data['order_id']) != 'delivered':
        raise ValidationError({'Error': ORDER_NOT_DELIVERED})
    return data


def validate_otp_validation_api_data(user, data):
    otp = data.get('otp')
    order_id = data.get('order_id')
    if not otp and not order_id:
        raise ValidationError({'otp': REQUIRED_FIELD, 'order_id': REQUIRED_FIELD})
    if not otp:
        raise ValidationError({'otp': REQUIRED_FIELD})
    if not order_id:
        raise ValidationError({'order_id': REQUIRED_FIELD})

    order_agent = AcceptedOrder.get_agent_from_order_id(order_id)
    if order_agent != user:
        raise PermissionDenied

    order = Order.get_object_from_pk(order_id)
    if not hasattr(order, 'confirm_otp'):
        raise ValidationError(OTP_NOT_FOUND)

    if order.confirm_otp.otp != otp:
        raise ValidationError(WRONG_OTP)
    agent_amount = get_delivery_charge_from_distance(order.user_address_lat, order.user_address_long,
                                                     order.restaurant_address_lat,
                                                     order.restaurant_address_long)
    total = order.total - agent_amount
    rest_amount = round(float(total) * 0.85, 2)
    commission = float(total) - rest_amount
    data = {
        "order": order, "agent": order_agent, "agent_amount": agent_amount,
        "rest_amount": rest_amount, "commission": commission
    }
    return data
