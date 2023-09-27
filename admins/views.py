from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import View
from django.views.generic import ListView, TemplateView

from FDA.constants import (
    ADMINS_HOME_PAGE, ADMINS_DRIVERS_LIST_PAGE, ADMINS_DRIVERS_APPLICATION_LIST_PAGE, ADMINS_DRIVERS_DETAIL_PAGE,
    ADMINS_DRIVERS_APPLICATION_DETAIL_PAGE, ADMINS_USERS_LIST_PAGE, ADMINS_USERS_DETAIL_PAGE,
    ADMINS_RESTAURANT_LIST_PAGE, ADMINS_RESTAURANT_DETAIL_PAGE, ADMINS_RESTAURANT_APPLICATION_LIST_PAGE,
    ADMINS_RESTAURANT_APPLICATION_DETAIL_PAGE, ADMINS_ORDERS_LIST_PAGE, ADMINS_ORDERS_DETAIL_PAGE,
    ADMINS_COD_AGENTS_LIST_PAGE, ADMINS_COD_AGENTS_DETAIL_PAGE
)
from accounts.models import User
from admins.mixins import AdminRequiredMixin, PaginationMixin, PkValidationMixin, DriverApplicationValidationMixin, \
    RestaurantApplicationValidationMixin
from admins.services import (
    HomeService,
    DriversListService,
    DriversApplicationListService,
    DriversDetailService, UsersListService, UsersDetailService, RestaurantListService, RestaurantsDetailService,
    RestaurantApplicationListService, UserActionService, OrdersListService, OrdersDetailService, CodAgentListService,
    CodAgentDetailService,
)
from admins.utils import CustomPaginator
from orders.models import Order
from restaurant.models import Restaurant


class AdminPanel(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    """View for admins panel."""
    template_name = ADMINS_HOME_PAGE

    def get_context_data(self, **kwargs):
        context = super(AdminPanel, self).get_context_data(**kwargs)
        return HomeService.get_context_data(context=context)


class DriversListView(LoginRequiredMixin, AdminRequiredMixin, PaginationMixin, ListView):
    model = User
    template_name = ADMINS_DRIVERS_LIST_PAGE
    context_object_name = 'drivers'
    ordering = ['-id']
    paginator_class = CustomPaginator

    def get_queryset(self):
        queryset = super().get_queryset()
        return DriversListService(request=self.request, model=self.model).get_queryset(queryset=queryset)


class DriversApplicationListView(LoginRequiredMixin, AdminRequiredMixin, PaginationMixin, ListView):
    """Description: List of all drivers whose application status is pending."""

    model = User
    template_name = ADMINS_DRIVERS_APPLICATION_LIST_PAGE
    context_object_name = 'drivers'
    ordering = ['-id']
    paginator_class = CustomPaginator

    def get_queryset(self):
        queryset = super().get_queryset()
        return DriversApplicationListService(
            request=self.request, model=self.model
        ).get_queryset(queryset=queryset)


class DriversApplicationDetailView(
    LoginRequiredMixin, AdminRequiredMixin, PkValidationMixin,
    DriverApplicationValidationMixin, TemplateView
):
    """Description: Shows detail of particular applicant for given ID(pk)
    """
    template_name = ADMINS_DRIVERS_APPLICATION_DETAIL_PAGE
    class_name = User

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return DriversDetailService.get_context_data(context=context, pk=kwargs['pk'])


class DriversDetailView(LoginRequiredMixin, AdminRequiredMixin, PkValidationMixin, TemplateView):
    """Description: Shows detail of particular driver for given ID(pk)"""

    template_name = ADMINS_DRIVERS_DETAIL_PAGE
    class_name = User

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return DriversDetailService.get_context_data(context=context, pk=kwargs['pk'])


class UsersListView(LoginRequiredMixin, AdminRequiredMixin, PaginationMixin, ListView):
    """Description: List of all Users with group customers"""

    model = User
    template_name = ADMINS_USERS_LIST_PAGE
    context_object_name = 'users'
    ordering = ['-id']
    paginator_class = CustomPaginator

    def get_queryset(self):
        queryset = super().get_queryset()
        return UsersListService(
            request=self.request, model=self.model
        ).get_queryset(queryset=queryset)


class UsersDetailView(LoginRequiredMixin, AdminRequiredMixin, PkValidationMixin, TemplateView):
    """Description: Shows detail of particular customer for given ID(pk)
    """
    template_name = ADMINS_USERS_DETAIL_PAGE
    class_name = User

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return UsersDetailService.get_context_data(context=context, pk=kwargs['pk'])


class RestaurantListView(LoginRequiredMixin, AdminRequiredMixin, PaginationMixin, ListView):
    """Description: List of restaurants
    """

    model = Restaurant
    template_name = ADMINS_RESTAURANT_LIST_PAGE
    context_object_name = 'restaurants'
    ordering = ['-id']
    paginator_class = CustomPaginator

    def get_queryset(self):
        queryset = super().get_queryset()
        return RestaurantListService(
            request=self.request, model=self.model
        ).get_queryset(queryset=queryset)


class RestaurantsDetailView(LoginRequiredMixin, AdminRequiredMixin, PkValidationMixin, TemplateView):
    """Description: Shows detail of particular restaurant for given ID(pk)
    """
    template_name = ADMINS_RESTAURANT_DETAIL_PAGE
    class_name = Restaurant

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return RestaurantsDetailService.get_context_data(context=context, pk=kwargs['pk'])


class RestaurantApplicationListView(LoginRequiredMixin, AdminRequiredMixin, PaginationMixin, ListView):
    """Description: List of new applications for restaurants
    """

    model = Restaurant
    template_name = ADMINS_RESTAURANT_APPLICATION_LIST_PAGE
    context_object_name = 'restaurants'
    ordering = ['-id']
    paginator_class = CustomPaginator

    def get_queryset(self):
        queryset = super().get_queryset()
        return RestaurantApplicationListService(
            request=self.request, model=self.model
        ).get_queryset(queryset=queryset)


class RestaurantsApplicationDetailView(
    LoginRequiredMixin, AdminRequiredMixin, PkValidationMixin,
    RestaurantApplicationValidationMixin, TemplateView
):
    """Description: Detail view for new restaurants applications"""

    template_name = ADMINS_RESTAURANT_APPLICATION_DETAIL_PAGE
    class_name = Restaurant

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return RestaurantsDetailService.get_context_data(context=context, pk=kwargs['pk'])


class OrdersListView(LoginRequiredMixin, AdminRequiredMixin, PaginationMixin, ListView):
    """Description: List of orders made by customers"""

    model = Order
    template_name = ADMINS_ORDERS_LIST_PAGE
    context_object_name = 'orders'
    ordering = ['-id']
    paginator_class = CustomPaginator

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return OrdersListService.get_context_data(context=context)

    def get_queryset(self):
        queryset = super().get_queryset()
        return OrdersListService(
            request=self.request, model=self.model
        ).get_queryset(queryset=queryset)


class OrdersDetailView(LoginRequiredMixin, AdminRequiredMixin, PkValidationMixin, TemplateView):
    """Description: Detail of order for given order ID"""
    template_name = ADMINS_ORDERS_DETAIL_PAGE
    class_name = Order

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return OrdersDetailService.get_context_data(context=context, pk=kwargs['pk'])


class ActionForRestaurantView(LoginRequiredMixin, AdminRequiredMixin, PkValidationMixin, View):
    class_name = Restaurant

    def post(self, request, pk):
        UserActionService.perform_restaurant_action(request, pk)
        return redirect('restaurant-detail', pk=pk)


class ActionForDeliveryAgentView(LoginRequiredMixin, AdminRequiredMixin, PkValidationMixin, View):
    class_name = User

    def post(self, request, pk):
        UserActionService.perform_agent_action(request, pk)
        return redirect('drivers-detail', pk=pk)


class ActionForCustomerView(LoginRequiredMixin, AdminRequiredMixin, PkValidationMixin, View):
    class_name = User

    def post(self, request, pk):
        UserActionService.perform_customer_action(request, pk)
        return redirect('users-detail', pk=pk)


class ApplicationActionForRestaurantView(LoginRequiredMixin, AdminRequiredMixin, PkValidationMixin, View):
    class_name = Restaurant

    def post(self, request, pk):
        UserActionService.perform_restaurant_application_action(request, pk)
        return redirect('restaurant-list-application')


class ApplicationActionForDeliveryAgentView(LoginRequiredMixin, AdminRequiredMixin, PkValidationMixin, View):
    class_name = User

    def post(self, request, pk):
        UserActionService.perform_agent_application_action(request, pk)
        return redirect('drivers-list-application')


class CodAgentListView(LoginRequiredMixin, AdminRequiredMixin, PaginationMixin, ListView):
    model = User
    template_name = ADMINS_COD_AGENTS_LIST_PAGE
    context_object_name = 'agents'
    ordering = ['-id']
    paginator_class = CustomPaginator

    def get_queryset(self):
        queryset = super().get_queryset()
        return CodAgentListService(request=self.request, model=self.model).get_queryset(queryset=queryset)


class CodAgentDetailView(LoginRequiredMixin, AdminRequiredMixin, PkValidationMixin, TemplateView):
    """Description: Shows detail of particular cod driver for given ID(pk)"""

    template_name = ADMINS_COD_AGENTS_DETAIL_PAGE
    class_name = User

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return CodAgentDetailService.get_context_data(context=context, pk=kwargs['pk'])


class ActionForCodDeliveryAgentView(LoginRequiredMixin, AdminRequiredMixin, PkValidationMixin, View):
    class_name = User

    def post(self, request, pk):
        UserActionService.perform_cod_agent_action(request, pk)
        return redirect('cod-agents-list')
