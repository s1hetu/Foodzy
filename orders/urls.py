from django.urls import path

from orders.views import (
    PlaceOrder, DetailOrderView, DownloadInvoice,
    OrdersView, PaymentHandler, PaymentSuccess, OrderPaymentMethod, CODPayment
)

urlpatterns = [
    path("place_order/", PlaceOrder.as_view(), name="place-order"),
    path("order_payment_method/", OrderPaymentMethod.as_view(), name="order-payment-method"),
    path('paymenthandler/', PaymentHandler.as_view(), name='paymenthandler'),
    path("orders/", OrdersView.as_view(), name="orders"),
    path("view_detail_order/<int:pk>/", DetailOrderView.as_view(), name="view-detail-order"),
    path("download_invoice/<int:pk>/", DownloadInvoice.as_view(), name="download-invoice"),
    path("order_paid/", PaymentSuccess, name="order-paid"),
    path("cod_payment/", CODPayment.as_view(), name="cod-payment"),
]
