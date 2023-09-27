import json
import logging
from collections import defaultdict

import razorpay
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import BadRequest
from django.http import HttpResponse
from django.shortcuts import redirect, render

from FDA.constants import (
    NOT_AVAILABLE, NOT_AVAILABLE_QUANTITY, CART_EMPTY, ORDER_INVOICE_PAGE,
    ORDER_PAYMENT_SUCCESSFUL, ORDER_PAYMENT_FAILED, ORDER_PLACED_MESSAGE, ORDER_PAY_NOW_PAGE, BAD_REQUEST,
    ITEM_NOT_AVAILABLE_LOCATION_WISE, VALID_ORDER_DISTANCE, ERR_PAYMENT_EVENT_NOT_DEFINE
)
from accounts.models import User
from carts.models import CartItems, Cart
from orders.models import Order, OrderItems, OrderConfirmOtp
from orders.utils import (
    get_delivery_charge_from_distance, render_to_pdf, get_razorpay_payment_id,
    get_user_order_data_from_razorpay_payload, get_distance_between_two_locations
)
from restaurant.models import Restaurant

client = razorpay.Client(auth=(settings.RAZORPAY_ID, settings.RAZORPAY_SECRET_KEY))

logger = logging.getLogger(__name__)


class DownloadPDF:
    def get(self, pk):
        """
        Use to Download the pdf
        """
        order = Order.get_object_from_pk(pk)
        context = {'order': order, }
        if pdf := render_to_pdf(ORDER_INVOICE_PAGE, context):
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = f"Invoice_{context['order']}.pdf"
            content = f"file; filename={filename}"
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")  # pragma: no cover


class OrderService:

    def get_order_context_data(self, user, context):
        context['orders'] = Order.get_user_orders(user).order_by('-order_date').select_related('user',
                                                                                               'accepted_order',
                                                                                               'restaurant')
        return context

    def get_detail_order_context_data(self, pk, context):
        context['order'] = Order.objects.filter(pk=pk).select_related('user', 'accepted_order', 'restaurant',
                                                                      'ratingsandreviews').first()
        return context


def check_webhook(request):  # pragma: no cover
    captured_data = json.loads(request.body)
    razorpay_payment_id = get_razorpay_payment_id(captured_data)
    razorpay_order_id, user_id = get_user_order_data_from_razorpay_payload(captured_data)
    user, user_address_obj, user_address, user_address_lat, user_address_long = User.get_user_address(user_id)
    cart_items = CartItems.get_all_user_items(user.id)

    if not client.utility.verify_webhook_signature(str(request.body, 'utf-8'), request.headers['X-Razorpay-Signature'],
                                                   settings.RAZORPAY_SECRET_KEY):
        return redirect('home')

    if captured_data['event'] in ['payment.captured', 'payment.failed']:
        data = CartItems.get_cart_item_restaurant_wise(cart_items)

        for restaurant_id, details in data.items():
            restaurant_obj, restaurant_address, restaurant_address_lat, restaurant_address_long = Restaurant.get_restaurant_address(
                restaurant_id=restaurant_id)
            charge = get_delivery_charge_from_distance(user_address_lat, user_address_long, restaurant_address_lat,
                                                       restaurant_address_long)

            total = CartItems.get_item_total_cartitems(cart_items, restaurant_id)

            if captured_data['event'] == 'payment.captured':
                order = Order.objects.create(user=user, user_address=user_address, user_address_long=user_address_long,
                                             user_address_lat=user_address_lat, restaurant=restaurant_obj,
                                             restaurant_address=restaurant_address,
                                             restaurant_address_lat=restaurant_address_lat,
                                             restaurant_address_long=restaurant_address_long,
                                             total=total + charge,
                                             razorpay_payment_id=razorpay_payment_id,
                                             razorpay_order_id=razorpay_order_id,
                                             mode="Online", paid=True,
                                             delivery_charges=charge)

                OrderConfirmOtp.send_otp(order)

                OrderItems.create_order_items(details, order, decrease_item=True)

            elif captured_data['event'] == 'payment.failed':
                order = Order.objects.create(user=user, user_address=user_address, user_address_long=user_address_long,
                                             user_address_lat=user_address_lat, restaurant_address=restaurant_address,
                                             restaurant_address_lat=restaurant_address_lat,
                                             restaurant_address_long=restaurant_address_long,
                                             restaurant=restaurant_obj, total=total + charge,
                                             status="failed", razorpay_order_id=razorpay_order_id, mode="Online",
                                             paid=False,
                                             delivery_charges=charge)

                OrderItems.create_order_items(details, order, decrease_item=True)

        if captured_data['event'] == 'payment.captured':
            Cart.objects.filter(user=user).delete()
            messages.success(request, ORDER_PAYMENT_SUCCESSFUL)
            logger.info(ORDER_PAYMENT_SUCCESSFUL)
            return HttpResponse(status=200)
        elif captured_data['event'] == 'payment.failed':
            messages.error(request, ORDER_PAYMENT_FAILED)
            logger.error(ORDER_PAYMENT_FAILED)
            return HttpResponse(status=200)
    else:
        logger.error(ERR_PAYMENT_EVENT_NOT_DEFINE)
        raise BadRequest(BAD_REQUEST)


class CODPaymentService:

    @staticmethod
    def get_context_data(context, user, request):
        current_orders = []
        user, user_address_obj, user_address, user_address_lat, user_address_long = User.get_user_address(user=user)
        cart_items = CartItems.get_all_user_items(user.id)
        data = CartItems.get_cart_item_restaurant_wise(cart_items)
        for restaurant_id, details in data.items():
            restaurant_obj, restaurant_address, restaurant_address_lat, restaurant_address_long = Restaurant.get_restaurant_address(
                restaurant_id)
            charge = get_delivery_charge_from_distance(user_address_lat, user_address_long, restaurant_address_lat,
                                                       restaurant_address_long)
            total = CartItems.get_item_total_cartitems(cart_items, restaurant_id)
            order = Order.objects.create(user=user, user_address=user_address, user_address_long=user_address_long,
                                         user_address_lat=user_address_lat, restaurant=restaurant_obj,
                                         restaurant_address=restaurant_address,
                                         restaurant_address_lat=restaurant_address_lat,
                                         restaurant_address_long=restaurant_address_long, delivery_charges=charge,
                                         total=total + charge, mode="COD")
            current_orders.append(order)
            OrderConfirmOtp.send_otp(order)
            OrderItems.create_order_items(details, order, decrease_item=True)

        Cart.objects.filter(user=user).delete()
        context['orders'] = current_orders
        messages.success(request, ORDER_PLACED_MESSAGE % len(current_orders))
        return context


class PlaceOrderService:
    @staticmethod
    def get_request(user, request):
        user, user_address_obj, user_address, user_address_lat, user_address_long = User.get_user_address(user=user)

        if cart_items := CartItems.get_all_user_items(user.id):
            for cart_item in cart_items:
                current_item_restaurant_address = cart_item.item.restaurant.address
                if current_item_restaurant_address.city != user_address_obj.city or get_distance_between_two_locations(
                        current_item_restaurant_address.lat,
                        current_item_restaurant_address.long, user_address_obj.lat,
                        user_address_obj.long) > int(VALID_ORDER_DISTANCE):
                    messages.error(request, ITEM_NOT_AVAILABLE_LOCATION_WISE.format(cart_item.item.name))
                    return redirect('cart')
                if not cart_item.item.restaurant.is_accepting_orders or cart_item.item.restaurant.is_blocked:
                    messages.error(request, NOT_AVAILABLE % cart_item.item.name)
                    return redirect('cart')
                if cart_item.quantity > cart_item.item.available_quantity:
                    messages.error(request, NOT_AVAILABLE_QUANTITY % cart_item.item.name)
                    return redirect('cart')
            restaurants = cart_items.order_by('item__restaurant__id', 'id').distinct(
                'item__restaurant__id').values_list('item__restaurant_id',
                                                    flat=True)

            restaurant_wise_order = defaultdict(list)
            total_order_amount = 0
            for restaurant_id in restaurants:
                restaurant_obj, restaurant_address, restaurant_address_lat, restaurant_address_long = Restaurant.get_restaurant_address(
                    restaurant_id=restaurant_id)
                charge = get_delivery_charge_from_distance(user_address_lat, user_address_long, restaurant_address_lat,
                                                           restaurant_address_long)
                items = CartItems.objects.filter(cart__user_id=user.id, item__restaurant_id=restaurant_id)
                amount = CartItems.get_item_total_cartitems(cart_items, restaurant_id)
                total_order_amount += float(amount)
                total_order_amount += float(charge)

                restaurant_wise_order[restaurant_id] = {
                    "items": items, "charge": float(charge), "order_amount": float(amount), 'sub_total':float(charge)+float(amount)
                }

            context = {
                'amount': total_order_amount,
                "restaurant_orders": dict(restaurant_wise_order)
            }
            print(context)
            return render(request, ORDER_PAY_NOW_PAGE, context=context)
        else:
            messages.error(request, CART_EMPTY)
            return redirect('cart')
