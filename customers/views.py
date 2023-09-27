from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views import View
from django.views.generic import ListView

from FDA.constants import CUSTOMER_ITEM_LIST_PAGE
from admins.mixins import PaginationMixin
from admins.utils import CustomPaginator
from customers.mixins import CustomerOrAnonymousUserRequiredMixin, OrderOwnerRequiredMixin, HomeRedirectionMixin
from customers.services import CustomerServices, HomeService
from restaurant.models import Items


class HomeView(HomeRedirectionMixin, PaginationMixin, ListView):
    """Description: Renders home page for customers,
    redirects other roles user to respected views.
    """
    model = Items
    template_name = CUSTOMER_ITEM_LIST_PAGE
    context_object_name = 'products'
    ordering = ['-id']
    paginator_class = CustomPaginator
    paginate_by = 9

    def get_queryset(self):
        queryset = super().get_queryset()
        return HomeService(
            request=self.request, model=self.model
        ).get_queryset(queryset=queryset)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(HomeView, self).get_context_data(object_list=None, **kwargs)
        return HomeService(
            request=self.request, model=self.model
        ).get_context_data(context=context)


class CartView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """Description: Renders cart page for customers
    """
    permission_required = ['carts.view_cart']

    def get(self, request):
        return CustomerServices.cart_view(request)


class ItemDetailView(CustomerOrAnonymousUserRequiredMixin, View):
    """Description: Renders an item detail page for customers.
    """

    def get(self, request, pk):
        return CustomerServices.item_detail_view(request, pk)


class DeliveryAgentRatings(LoginRequiredMixin, PermissionRequiredMixin, OrderOwnerRequiredMixin, View):
    """
    description: This is Delivery Agent rating view.
    GET request will display rating form page.
    POST request will save the rating
    """
    permission_required = ['delivery_agent.change_acceptedorder', 'delivery_agent.view_acceptedorder', ]

    def get(self, request, pk):
        return CustomerServices.delivery_agent_rating_get(request, order_id=pk)

    def post(self, request, pk):
        return CustomerServices.delivery_agent_rating_post(request, order_id=pk)


class RestaurantRatings(LoginRequiredMixin, PermissionRequiredMixin, OrderOwnerRequiredMixin, View):
    """
    description: This is Restaurant rating view.
    GET request will display rating form page.
    POST request will save the rating
    """
    permission_required = ['restaurant.add_ratingsandreviews', 'restaurant.view_ratingsandreviews']

    def get(self, request, pk):
        return CustomerServices.restaurant_rating_get(request, order_id=pk)

    def post(self, request, pk):
        return CustomerServices.restaurant_rating_post(request, order_id=pk)
