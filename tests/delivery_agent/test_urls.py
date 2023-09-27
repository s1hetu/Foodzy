from django.urls import reverse, resolve

from delivery_agent.views import (
    RegisterDeliveryAgent, AgentPanelView, UpdateAgentStatusAPIView, SeeAvailableDeliveriesListView,
    AcceptDeliveryAPIView, SeeAllRatingAndReviewsView, AllDeliveriesListView, CurrentDeliveriesListView,
    DetailOrderTemplateView, UpdateDeliveryStatusAPIView, AgentApplicationStatusView, AllTimeEntriesListView,
    NotAvailableTemplateView, AcceptPaymentAPIView, ValidateOtpAPIView, ResendOtpAPIView,
    AgentEarningListView, GetCoordinates
)


class TestDeliveryAgentUrls(object):
    """Test for delivery_agent app's urls.
    Below test functions tests for all urls defined in delivery_agent/urls.py
    """

    # PK for post-detail and follow urls
    pk = 1

    def test_register_delivery_agent_url(self):
        url = reverse('register-delivery-agent')
        assert resolve(url).func.view_class == RegisterDeliveryAgent

    def test_delivery_agent_panel_url(self):
        url = reverse('delivery-agent-panel')
        assert resolve(url).func.view_class == AgentPanelView

    def test_update_agent_status_url(self):
        url = reverse('update_agent_status')
        assert resolve(url).func.view_class == UpdateAgentStatusAPIView

    def test_see_available_deliveries_url(self):
        url = reverse('see-available-deliveries')
        assert resolve(url).func.view_class == SeeAvailableDeliveriesListView

    def test_accept_delivery_url(self):
        url = reverse('accept_delivery')
        assert resolve(url).func.view_class == AcceptDeliveryAPIView

    def test_agent_review_url(self):
        url = reverse('agent_review', kwargs={'pk': self.pk})
        assert resolve(url).func.view_class == SeeAllRatingAndReviewsView

    def test_all_delivery_url(self):
        url = reverse('all-accepted-delivery')
        assert resolve(url).func.view_class == AllDeliveriesListView

    def test_current_delivery_url(self):
        url = reverse('current_delivery')
        assert resolve(url).func.view_class == CurrentDeliveriesListView

    def test_detail_delivery_url(self):
        url = reverse('detail_delivery', kwargs={'pk': self.pk})
        assert resolve(url).func.view_class == DetailOrderTemplateView

    def test_update_delivery_status_url(self):
        url = reverse('update_delivery_status')
        assert resolve(url).func.view_class == UpdateDeliveryStatusAPIView

    def test_all_time_entries_url(self):
        url = reverse('all_time_entries')
        assert resolve(url).func.view_class == AllTimeEntriesListView

    def test_agent_application_status_url(self):
        url = reverse('agent-application-status')
        assert resolve(url).func.view_class == AgentApplicationStatusView

    def test_not_available_url(self):
        url = reverse('not-available')
        assert resolve(url).func.view_class == NotAvailableTemplateView

    def test_accept_payment_url(self):
        url = reverse('accept_payment')
        assert resolve(url).func.view_class == AcceptPaymentAPIView

    def test_validate_otp_url(self):
        url = reverse('validate_otp')
        assert resolve(url).func.view_class == ValidateOtpAPIView

    def test_resend_otp_url(self):
        url = reverse('resend_otp')
        assert resolve(url).func.view_class == ResendOtpAPIView

    def test_agent_earning_url(self):
        url = reverse('agent_earning')
        assert resolve(url).func.view_class == AgentEarningListView

    def test_get_coordinates_url(self):
        url = reverse('get-coordinates')
        assert resolve(url).func.view_class == GetCoordinates
