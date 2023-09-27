import razorpay
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from FDA.constants import (
    ORDER_DETAIL_ORDER_PAGE, ORDER_ORDER_PAGE, ORDER_PAY_NOW_PAGE, ORDER_CALLBACK_URL,
    ORDER_PLACED_MESSAGE
)
from accounts.mixins import CustomerUserRequired
from accounts.models import User
from carts.models import CartItems
from customers.mixins import OrderOwnerRequiredMixin
from orders.models import Order
from restaurant.models import Restaurant
from .services import DownloadPDF, OrderService, check_webhook, CODPaymentService, PlaceOrderService
from .utils import get_delivery_charge_from_distance

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_ID, settings.RAZORPAY_SECRET_KEY))


class DetailOrderView(LoginRequiredMixin, PermissionRequiredMixin, OrderOwnerRequiredMixin, TemplateView):
    """
    Description : View Detailed order
    Parameters : Order ID
    """
    permission_required = ['orders.view_order']
    template_name = ORDER_DETAIL_ORDER_PAGE

    # model = Order

    def get_context_data(self, **kwargs):
        context = super(DetailOrderView, self).get_context_data(**kwargs)
        return OrderService().get_detail_order_context_data(pk=kwargs['pk'], context=context)


class OrdersView(LoginRequiredMixin, PermissionRequiredMixin, CustomerUserRequired, TemplateView):
    """
    Description : View all orders of a user
    """
    permission_required = ['orders.view_order']
    template_name = ORDER_ORDER_PAGE
    model = Order

    def get_context_data(self, **kwargs):
        context = super(OrdersView, self).get_context_data(**kwargs)
        return OrderService().get_order_context_data(context=context, user=self.request.user)


class DownloadInvoice(LoginRequiredMixin, OrderOwnerRequiredMixin, CustomerUserRequired, View):
    """For downloading invoice"""

    def get(self, request, pk):
        return DownloadPDF.get(self, pk)


class PlaceOrder(LoginRequiredMixin, PermissionRequiredMixin, CustomerUserRequired, View):
    """
    Description : Payment Page
    """
    permission_required = ['orders.add_order']
    template_name = ORDER_PAY_NOW_PAGE

    def get(self, request):
        return PlaceOrderService.get_request(user=self.request.user, request=request)


class OrderPaymentMethod(CustomerUserRequired, View):
    def get(self, request):
        if CartItems.get_unavailable_items():
            return redirect('cart')

        currency = 'INR'

        user, user_address_obj, user_address, user_address_lat, user_address_long = User.get_user_address(
            user=request.user)
        cart_items = CartItems.get_all_user_items(user.id)
        amount_final = 0
        data = CartItems.get_cart_item_restaurant_wise(cart_items)
        for restaurant_id, details in data.items():
            restaurant_obj, restaurant_address, restaurant_address_lat, restaurant_address_long = Restaurant.get_restaurant_address(
                restaurant_id=restaurant_id)
            charge = get_delivery_charge_from_distance(user_address_lat, user_address_long, restaurant_address_lat,
                                                       restaurant_address_long)

            total = CartItems.get_item_total_cartitems(cart_items, restaurant_id)

            amount_final += float(total)
            amount_final += charge

        razorpay_order = razorpay_client.order.create(
            dict(amount=amount_final * 100, currency=currency, payment_capture='1'))

        razorpay_order_id = razorpay_order['id']
        callback_url = ORDER_CALLBACK_URL

        context = {'razorpay_order_id': razorpay_order_id, 'razorpay_key': settings.RAZORPAY_ID,
                   'razorpay_amount': amount_final, 'currency': currency, 'callback_url': callback_url,
                   'amount': amount_final}

        return JsonResponse({"context": context})


@method_decorator(csrf_exempt, name='dispatch')
class PaymentHandler(View):  # pragma: no cover

    def post(self, request):
        return check_webhook(request)


@csrf_exempt
def PaymentSuccess(request):  # pragma: no cover
    orders = Order.get_orders_from_payment_id(request.POST.get('razorpay_payment_id'))
    messages.success(request, ORDER_PLACED_MESSAGE % len(orders))
    return render(request, ORDER_ORDER_PAGE, context={'orders': orders})


class CODPayment(LoginRequiredMixin, CustomerUserRequired, TemplateView):
    template_name = ORDER_ORDER_PAGE
    model = Order

    def get_context_data(self, **kwargs):
        context = super(CODPayment, self).get_context_data(**kwargs)
        return CODPaymentService.get_context_data(context=context, user=self.request.user, request=self.request)
