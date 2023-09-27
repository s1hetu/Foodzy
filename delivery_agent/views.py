from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import render
from django.views import View
from django.views.generic import ListView, TemplateView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from FDA.constants import (
    AGENT_REGISTRATION_FORM_PAGE, AGENT_LIST_ACCEPTED_ORDERS_PAGE, AGENT_CURRENT_DELIVERIES_PAGE,
    AGENT_SEE_AVAILABLE_DELIVERIES_PAGE, AGENT_REVIEWS_PAGE, AGENT_DETAIL_ORDER_PAGE,
    AGENT_TIME_ENTRY_PAGE, AGENT_APPLICATION_STATUS_PAGE, AGENT_NOT_AVAILABLE_PAGE,
    AGENT_EARNING_PAGE, AGENT_GET_COORDINATES_PAGE, AGENT_PANEL_PAGE
)
from accounts.mixins import AnonymousRequiredMixin
from admins.mixins import PaginationMixin
from admins.utils import CustomPaginator
from delivery_agent.mixins import (
    VerifiedAgentRequiredMixin, CheckOrderAgentMixin,
    AvailableAgentRequiredMixin, LatLongRequiredMixin
)
from delivery_agent.models import AdditionalDetail, ActivationTime, AcceptedOrder
from delivery_agent.services import (
    AllDeliveryListService, CurrentDeliveryListService,
    SeeAvailableDeliveryListService,
    AgentApplicationStatusService, AllTimeEntriesService, DetailOrderService,
    AgentPanel, UpdateDeliveryStatusService,
    AcceptDeliveryService, UpdateAgentStatusService, AcceptPaymentService,
    RegisterDeliveryAgentFormService, AgentReviewService, AgentEarningService,
    ValidateOtpAPIViewService, ResendOtpAPIViewService
)
from orders.models import Order, OrderConfirmOtp, OrderPayoutDetail


class RegisterDeliveryAgent(AnonymousRequiredMixin, View):
    """
    description: This is Delivery Agent register view.
    GET request will display Register Form in registration.html page.
    POST request will make user registered if details is valid else register
    form with error is displayed.
    permission: Must Be Anonymous user
    """

    def get(self, request):
        context = RegisterDeliveryAgentFormService.get_form()
        return render(request, template_name=AGENT_REGISTRATION_FORM_PAGE,
                      context=context)

    def post(self, request):
        return RegisterDeliveryAgentFormService.save_form(request)


class UpdateAgentStatusAPIView(LoginRequiredMixin, PermissionRequiredMixin, VerifiedAgentRequiredMixin, APIView):
    """
    description: APIView to Update AgentStatus
    perms: status
    """
    permission_required = ['delivery_agent.update_status']
    model = AdditionalDetail

    def post(self, request):
        response = UpdateAgentStatusService(
            request=request, model=self.model
        ).update_data()
        return Response(response, status=status.HTTP_200_OK)


class AgentPanelView(LoginRequiredMixin, VerifiedAgentRequiredMixin, TemplateView):
    """
    description: View for agent panel
    """
    template_name = AGENT_PANEL_PAGE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return AgentPanel.get_context_data(context=context, agent=self.request.user)


class AllDeliveriesListView(LoginRequiredMixin, VerifiedAgentRequiredMixin, PermissionRequiredMixin, PaginationMixin,
                            ListView):
    """
    View for all accepted deliveries
    """
    permission_required = ['delivery_agent.view_acceptedorder']
    model = AcceptedOrder
    template_name = AGENT_LIST_ACCEPTED_ORDERS_PAGE
    context_object_name = 'orders'
    ordering = ['-id']
    paginator_class = CustomPaginator
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        return AllDeliveryListService(
            request=self.request, model=self.model
        ).get_queryset(queryset=queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return AllDeliveryListService(request=self.request, model=self.model).get_context_data(context)


class CurrentDeliveriesListView(LoginRequiredMixin, PermissionRequiredMixin, VerifiedAgentRequiredMixin,
                                PaginationMixin, ListView):
    """
    description: ListView for number_of_purchasesall accepted deliveries
    """

    permission_required = ['delivery_agent.view_acceptedorder']
    model = AcceptedOrder
    template_name = AGENT_CURRENT_DELIVERIES_PAGE
    context_object_name = 'orders'
    ordering = ['-id']
    paginator_class = CustomPaginator
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        return CurrentDeliveryListService(
            request=self.request, model=self.model
        ).get_queryset(queryset=queryset)


class SeeAvailableDeliveriesListView(LoginRequiredMixin, VerifiedAgentRequiredMixin, PermissionRequiredMixin,
                                     LatLongRequiredMixin, AvailableAgentRequiredMixin, PaginationMixin, ListView):
    """
    description: ListView of all accepted deliveries
    """

    permission_required = ['delivery_agent.view_acceptedorder']
    model = Order
    template_name = AGENT_SEE_AVAILABLE_DELIVERIES_PAGE
    context_object_name = 'orders'
    ordering = ['-id']
    paginator_class = CustomPaginator
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        return SeeAvailableDeliveryListService(
            request=self.request, model=self.model
        ).get_queryset(queryset=queryset)


class AcceptDeliveryAPIView(LoginRequiredMixin, PermissionRequiredMixin, VerifiedAgentRequiredMixin,
                            AvailableAgentRequiredMixin, APIView):
    """
    description: APIView for Accept Available deliveries
    """
    permission_required = ['delivery_agent.add_acceptedorder']
    model = AcceptedOrder

    def post(self, request):
        response = AcceptDeliveryService(
            request=self.request, model=self.model
        ).create_data()
        return Response(response, status=status.HTTP_201_CREATED)


class AcceptPaymentAPIView(LoginRequiredMixin, PermissionRequiredMixin, VerifiedAgentRequiredMixin,
                           AvailableAgentRequiredMixin, APIView):
    """
    Desc: View for Accept Payment from user
    """
    permission_required = ['orders.change_order']
    model = Order

    def post(self, request):
        response = AcceptPaymentService(
            request=self.request, model=self.model
        ).update_data()
        return Response(response, status=status.HTTP_200_OK)


class ValidateOtpAPIView(LoginRequiredMixin, VerifiedAgentRequiredMixin, AvailableAgentRequiredMixin, APIView):
    """
    Desc: Validate OTP for delivery
    """
    model = OrderConfirmOtp

    def post(self, request):
        response = ValidateOtpAPIViewService(
            request=self.request, model=self.model
        ).update_data()
        return Response(response, status=status.HTTP_200_OK)


class ResendOtpAPIView(LoginRequiredMixin, VerifiedAgentRequiredMixin, AvailableAgentRequiredMixin, APIView):
    """
    Desc: Resend OTP for delivery
    """
    model = OrderConfirmOtp

    def post(self, request):
        response = ResendOtpAPIViewService(
            request=self.request, model=self.model
        ).update_data()

        return Response(response, status=status.HTTP_200_OK)


class SeeAllRatingAndReviewsView(LoginRequiredMixin, PermissionRequiredMixin, VerifiedAgentRequiredMixin, TemplateView):
    """
    description: TemplateView for all Reviews And Rating of agent
    perms: pk (user_id)
    res: List of reviews_and_ratings
    """
    permission_required = ['delivery_agent.view_acceptedorder']
    template_name = AGENT_REVIEWS_PAGE
    model = AcceptedOrder

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return AgentReviewService(model=self.model, request=self.request).get_context_data(context=context,
                                                                                           pk=kwargs['pk'])


class DetailOrderTemplateView(LoginRequiredMixin, PermissionRequiredMixin, VerifiedAgentRequiredMixin,
                              CheckOrderAgentMixin, TemplateView):
    """
    desc: Detail View of Order for Agent
    params: pk (order_id)
    """
    permission_required = ['orders.view_order']
    template_name = AGENT_DETAIL_ORDER_PAGE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return DetailOrderService.get_context_data(context=context, agent=self.request.user, pk=kwargs['pk'])


class UpdateDeliveryStatusAPIView(LoginRequiredMixin, PermissionRequiredMixin, VerifiedAgentRequiredMixin,
                                  AvailableAgentRequiredMixin, APIView):
    """
    desc: Update APIView for delivery status by agent
    perms: custom_id of order status
    """
    permission_required = ['orders.change_order']
    model = Order

    def post(self, request):
        response = UpdateDeliveryStatusService(
            request=self.request, model=self.model
        ).update_data()
        return Response(response, status=status.HTTP_200_OK)


class AllTimeEntriesListView(LoginRequiredMixin, VerifiedAgentRequiredMixin, PermissionRequiredMixin, PaginationMixin,
                             ListView):
    """
    description: ListView for time entries of agent
    """
    permission_required = ['delivery_agent.view_activationtime']
    template_name = AGENT_TIME_ENTRY_PAGE
    model = ActivationTime
    context_object_name = 'active_time_obj'
    ordering = ['-id']
    paginator_class = CustomPaginator
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        return AllTimeEntriesService(
            request=self.request, model=self.model
        ).get_queryset(queryset=queryset)


class AgentApplicationStatusView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    """
    description: Delivery Agent Application Status page, when agent is unverified.
    """
    permission_required = ['delivery_agent.view_document']
    template_name = AGENT_APPLICATION_STATUS_PAGE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return AgentApplicationStatusService.get_context_data(context=context, user=self.request.user)


class NotAvailableTemplateView(LoginRequiredMixin, TemplateView):
    """
    description: TemplateView for Delivery Agent Not Available
    """
    template_name = AGENT_NOT_AVAILABLE_PAGE


class AgentEarningListView(LoginRequiredMixin, VerifiedAgentRequiredMixin, PaginationMixin, ListView):
    template_name = AGENT_EARNING_PAGE
    model = OrderPayoutDetail
    context_object_name = 'orders'
    ordering = ['-id']
    paginator_class = CustomPaginator
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        return AgentEarningService(
            request=self.request, model=self.model
        ).get_queryset(queryset=queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return AgentEarningService(request=self.request, model=self.model).get_context_data(context)


class GetCoordinates(LoginRequiredMixin, TemplateView):
    """
    description: TemplateView for Delivery Agent Not Available
    """
    template_name = AGENT_GET_COORDINATES_PAGE
