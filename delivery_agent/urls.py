from django.urls import path

from delivery_agent.views import (
    UpdateAgentStatusAPIView, RegisterDeliveryAgent, AgentPanelView,
    AllDeliveriesListView, SeeAvailableDeliveriesListView, AcceptDeliveryAPIView,
    SeeAllRatingAndReviewsView, CurrentDeliveriesListView, DetailOrderTemplateView,
    UpdateDeliveryStatusAPIView, AgentApplicationStatusView, AllTimeEntriesListView,
    NotAvailableTemplateView, AcceptPaymentAPIView, ValidateOtpAPIView, ResendOtpAPIView,
    AgentEarningListView, GetCoordinates
)

urlpatterns = [
    path("register/", RegisterDeliveryAgent.as_view(), name="register-delivery-agent"),
    path("panel/", AgentPanelView.as_view(), name="delivery-agent-panel"),
    path("update-status/", UpdateAgentStatusAPIView.as_view(), name="update_agent_status"),
    path("see_available_deliveries/", SeeAvailableDeliveriesListView.as_view(), name="see-available-deliveries"),
    path("accept_delivery/", AcceptDeliveryAPIView.as_view(), name="accept_delivery"),
    path("agent_review/<int:pk>/", SeeAllRatingAndReviewsView.as_view(), name="agent_review"),
    path("all_delivery/", AllDeliveriesListView.as_view(), name="all-accepted-delivery"),
    path("current_delivery", CurrentDeliveriesListView.as_view(), name="current_delivery"),
    path("detail_delivery/<int:pk>/", DetailOrderTemplateView.as_view(), name="detail_delivery"),
    path("update_delivery_status/", UpdateDeliveryStatusAPIView.as_view(), name="update_delivery_status"),
    path("all_time_entries/", AllTimeEntriesListView.as_view(), name="all_time_entries"),
    path("application_status/", AgentApplicationStatusView.as_view(), name="agent-application-status"),
    path("not_available/", NotAvailableTemplateView.as_view(), name="not-available"),
    path("accept_payment/", AcceptPaymentAPIView.as_view(), name="accept_payment"),
    path("validate_otp/", ValidateOtpAPIView.as_view(), name="validate_otp"),
    path("resend_otp/", ResendOtpAPIView.as_view(), name="resend_otp"),
    path("earning/", AgentEarningListView.as_view(), name="agent_earning"),
    path("get_coordinates/", GetCoordinates.as_view(), name="get-coordinates"),
]
