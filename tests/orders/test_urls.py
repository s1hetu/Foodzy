from django.urls import reverse, resolve

from orders.views import (
    PlaceOrder, DetailOrderView, DownloadInvoice,
    OrdersView, PaymentHandler, PaymentSuccess,
    OrderPaymentMethod, CODPayment
)


class TestOrdersUrls(object):
    """Test for Orders app's urls.
    Below test functions tests for all urls defined in orders/urls.py
    """

    # PK for post-detail and follow urls
    pk = 1

    def test_place_order_url(self):
        url = reverse('place-order')
        assert resolve(url).func.view_class == PlaceOrder

    def test_order_payment_method_url(self):
        url = reverse('order-payment-method')
        assert resolve(url).func.view_class == OrderPaymentMethod

    def test_payment_handler_url(self):
        url = reverse('paymenthandler')
        assert resolve(url).func.view_class == PaymentHandler

    def test_orders_url(self):
        url = reverse('orders')
        assert resolve(url).func.view_class == OrdersView

    def test_view_detail_order_url(self):
        url = reverse('view-detail-order', kwargs={'pk': self.pk})
        assert resolve(url).func.view_class == DetailOrderView

    def test_download_invoice_url(self):
        url = reverse('download-invoice', kwargs={'pk': self.pk})
        assert resolve(url).func.view_class == DownloadInvoice

    def test_order_paid_url(self):
        url = reverse('order-paid')
        assert resolve(url).func == PaymentSuccess

    def test_cod_payment_url(self):
        url = reverse('cod-payment')
        assert resolve(url).func.view_class == CODPayment
