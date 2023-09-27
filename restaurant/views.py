from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import UpdateView, ListView, TemplateView, FormView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from FDA.constants import (
    RESTAURANT_OWNER_PANEL_PAGE, RESTAURANT_PANEL_PAGE, RESTAURANT_UPDATE_ITEM_PAGE,
    RESTAURANT_REGISTRATION_PAGE, RESTAURANT_ADD_RESTAURANT_PAGE, RESTAURANT_MENU_PAGE,
    RESTAURANT_ORDERS_PAGE, RESTAURANT_DETAIL_ORDER_PAGE, RESTAURANT_STATUS_PAGE,
    RESTAURANT_REVIEWS_PAGE, RESTAURANT_ADD_GALLERY_IMAGE_PAGE,
    RESTAURANT_VIEW_GALLERY_IMAGE_PAGE, RESTAURANT_EARNING_PAGE, RESTAURANT_ADD_ITEM_PAGE,
    RESTAURANT_VIEW_RESTAURANT_PERMISSION, RESTAURANT_VIEW_DOCUMENTS_PERMISSION,
    RESTAURANT_UPDATE_RESTAURANT_ACCEPTING_ORDER_PERMISSION, RESTAURANT_ADD_ITEM_PERMISSION,
    RESTAURANT_UPDATE_IEM_PERMISSION, RESTAURANT_ADD_RESTAURANT_PERMISSION,
    RESTAURANT_VIEW_ITEMS_PERMISSION, ORDERS_CHANGE_ORDER_PERMISSION,
    ORDERS_VIEW_ORDER_PERMISSION, RESTAURANT_VIEW_RATINGSANDREVIEWS_PERMISSION,
    RESTAURANT_ADD_RESTAURANTGALLERY_PERMISSION, RESTAURANT_VIEW_RESTAURANTGALLERY_PERMISSION
)
from accounts.mixins import AnonymousRequiredMixin, ViewRestaurantGalleryMixin
from admins.mixins import PaginationMixin
from admins.utils import CustomPaginator
from orders.models import Order, OrderPayoutDetail
from .forms import ItemForm, GalleryImageForm
from .mixins import (
    RestaurantItemMixin, RestaurantOwnerMixin, RestaurantNotBlockedMixin, CheckOrderRestaurantMixin,
    CheckRestaurantMixin, RedirectToRestaurant, AddRestaurantInSession
)
from .models import Restaurant, Items, RatingsAndReviews, RestaurantGallery
from .services import (
    RestaurantOwnerService, RestaurantMenuService, RestaurantStatus, DetailOrderService,
    ReviewsRestaurantService, ViewOrderService, RegisterRestaurantFormService, AddItemFormService,
    AddRestaurantService, UpdateRestaurantOrderStatusService, RestaurantPanelService,
    AddGalleryImageService, RestaurantGalleryService, RestaurantEarningService
)


class RestaurantPanel(LoginRequiredMixin, PermissionRequiredMixin, RedirectToRestaurant, ListView):
    """
    Description : Get all restaurants of the logged-in user
    """
    model = Restaurant
    permission_required = [RESTAURANT_VIEW_RESTAURANT_PERMISSION, RESTAURANT_VIEW_DOCUMENTS_PERMISSION]
    template_name = RESTAURANT_OWNER_PANEL_PAGE
    context_object_name = 'restaurants'

    def get_queryset(self):
        super(RestaurantPanel, self).get_queryset()
        return RestaurantOwnerService(request=self.request, model=self.model).get_owner_restaurants()


class OwnerPanel(LoginRequiredMixin, PermissionRequiredMixin, RestaurantOwnerMixin, AddRestaurantInSession,
                 TemplateView):
    """
    Description : Get the Restaurant related details like orders, reviews, ratings, customers, etc. if restaurant is
    verified
    Parameters : Restaurant pk
    """
    permission_required = [RESTAURANT_VIEW_RESTAURANT_PERMISSION, RESTAURANT_VIEW_DOCUMENTS_PERMISSION]
    template_name = RESTAURANT_PANEL_PAGE

    def get_context_data(self, *args, **kwargs):
        context = super(OwnerPanel, self).get_context_data(**kwargs)
        return RestaurantPanelService.get_data(context=context, pk=kwargs['pk'], request=self.request)


class UpdateRestaurantAcceptingOrderStatus(LoginRequiredMixin, PermissionRequiredMixin, RestaurantOwnerMixin,
                                           RestaurantNotBlockedMixin, SuccessMessageMixin, APIView):
    """
    Description : Restaurant Owner updates the order status
    Parameters : Restaurant pk
    """
    permission_classes = [IsAuthenticated]
    permission_required = [RESTAURANT_UPDATE_RESTAURANT_ACCEPTING_ORDER_PERMISSION]

    queryset = Restaurant.get_all_restaurants()

    def post(self, request, pk):
        return UpdateRestaurantOrderStatusService.get_response(request, pk)


class AddItem(LoginRequiredMixin, PermissionRequiredMixin, RestaurantOwnerMixin, RestaurantNotBlockedMixin, FormView):
    """
    Description : Add Item to the Restaurant Menu
    Parameters : Restaurant pk
    """
    permission_required = [RESTAURANT_ADD_ITEM_PERMISSION]
    form_class = ItemForm
    template_name = RESTAURANT_ADD_ITEM_PAGE

    def get_success_url(self, pk=None):
        return reverse_lazy('restaurant-menu', pk=self.kwargs.get('pk'))

    def form_valid(self, form):
        return AddItemFormService(request=self.request).form_valid(form=form, **self.kwargs)


class UpdateItem(LoginRequiredMixin, PermissionRequiredMixin, RestaurantItemMixin, UpdateView):
    """
    Description : Update the Restaurant Item
    """
    model = Items
    permission_required = [RESTAURANT_UPDATE_IEM_PERMISSION]
    fields = ['category', 'name', 'available_quantity', 'quantity', 'unit', 'price', 'description', 'image', 'discount']
    template_name = RESTAURANT_UPDATE_ITEM_PAGE

    def get_success_url(self):
        pk = self.kwargs["pk"]
        return reverse("restaurant-menu", kwargs={"pk": Items.get_item(pk).restaurant.id})


class RegisterRestaurant(AnonymousRequiredMixin, View):
    """
        description: Restaurant register view.
        GET request will display Register Form in restaurant_registration.html page.
        POST request will make user registered if provided details are valid else register
        form with error is displayed.
        permission: Must Be Anonymous user
        """

    def get(self, request):
        context = RegisterRestaurantFormService.get_form()
        return render(request, template_name=RESTAURANT_REGISTRATION_PAGE, context=context)

    def post(self, request):
        return RegisterRestaurantFormService.save_form(request)


class AddRestaurant(LoginRequiredMixin, PermissionRequiredMixin, CheckRestaurantMixin, View):
    """
    Description : Add the Restaurants
    """
    permission_required = [RESTAURANT_ADD_RESTAURANT_PERMISSION]

    def get(self, request):
        context = AddRestaurantService.get_form()
        return render(request, template_name=RESTAURANT_ADD_RESTAURANT_PAGE, context=context)

    def post(self, request):
        return AddRestaurantService.save_form(request)


class RestaurantMenu(LoginRequiredMixin, PermissionRequiredMixin, RestaurantOwnerMixin, ListView):
    """
    Description : View the Restaurant Menu
    Parameters : Restaurant ID
    """
    permission_required = [RESTAURANT_VIEW_ITEMS_PERMISSION]
    model = Items
    template_name = RESTAURANT_MENU_PAGE
    context_object_name = 'products'

    def get_queryset(self):
        super(RestaurantMenu, self).get_queryset()
        return RestaurantMenuService.get_restaurant_menu(self.kwargs['pk'])


class ViewOrders(LoginRequiredMixin, PermissionRequiredMixin, RestaurantOwnerMixin, PaginationMixin, ListView):
    """
    Description : Get all the order of a Restaurant
    Parameters : Restaurant ID

    """
    permission_required = [ORDERS_VIEW_ORDER_PERMISSION]
    model = Order
    template_name = RESTAURANT_ORDERS_PAGE
    context_object_name = 'orders'
    ordering = ['-id']
    paginator_class = CustomPaginator
    paginate_by = 10

    def get_queryset(self):
        queryset = super(ViewOrders, self).get_queryset()
        return ViewOrderService.get_queryset(queryset=queryset, pk=self.kwargs['pk'])


class ViewReviews(LoginRequiredMixin, PermissionRequiredMixin, RestaurantOwnerMixin, PaginationMixin, ListView):
    """
    Description : View the reviews of a Restaurant
    Parameters : Restaurant ID

    """
    permission_required = [RESTAURANT_VIEW_RATINGSANDREVIEWS_PERMISSION]
    model = RatingsAndReviews
    template_name = RESTAURANT_REVIEWS_PAGE
    context_object_name = 'reviews'
    ordering = ['-id']
    paginate_by = 10
    paginator_class = CustomPaginator

    def get_queryset(self):
        queryset = super(ViewReviews, self).get_queryset()
        return ReviewsRestaurantService(model=self.model).get_queryset(queryset=queryset, pk=self.kwargs['pk'])


class DetailOrder(LoginRequiredMixin, PermissionRequiredMixin, CheckOrderRestaurantMixin, View):
    """
    Description : Get all the details of an order
    Parameters : Order ID
    GET : Get the details
    POST : Update the status
    """
    permission_required = [ORDERS_VIEW_ORDER_PERMISSION, ORDERS_CHANGE_ORDER_PERMISSION]

    def get(self, request, pk):
        context = DetailOrderService.get_order_details(pk)
        return render(request, RESTAURANT_DETAIL_ORDER_PAGE, context=context)

    def post(self, request, pk):
        return DetailOrderService.update_order_status(request, pk)


class RestaurantStatusView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    """
    Description : Restaurant Status page, when restaurant is un verified.
    Parameters : Restaurant pk
    """
    permission_required = [RESTAURANT_VIEW_RESTAURANT_PERMISSION, RESTAURANT_VIEW_DOCUMENTS_PERMISSION]

    model = Restaurant
    template_name = RESTAURANT_STATUS_PAGE
    context_object_name = 'restaurant'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return RestaurantStatus.get_context_data(context=context, pk=self.kwargs['restaurant_id'], request=self.request)


class AddGalleryImage(LoginRequiredMixin, PermissionRequiredMixin, RestaurantOwnerMixin, RestaurantNotBlockedMixin,
                      AddRestaurantInSession,
                      FormView):
    template_name = RESTAURANT_ADD_GALLERY_IMAGE_PAGE
    permission_required = [RESTAURANT_ADD_RESTAURANTGALLERY_PERMISSION]
    form_class = GalleryImageForm

    def get_context_data(self, **kwargs):
        return AddGalleryImageService.get_form(pk=self.kwargs.get('pk'))

    def form_valid(self, form):
        return AddGalleryImageService(request=self.request).form_valid(form=form, **self.kwargs)


class ViewGalleryImage(ViewRestaurantGalleryMixin, PermissionRequiredMixin, ListView):
    """
        To display Gallery image to restaurant panel and to customer
    """
    permission_required = [RESTAURANT_VIEW_RESTAURANTGALLERY_PERMISSION]
    template_name = RESTAURANT_VIEW_GALLERY_IMAGE_PAGE
    model = RestaurantGallery
    context_object_name = "gallery_images"

    def get_queryset(self):
        queryset = super().get_queryset()
        return RestaurantGalleryService(request=self.request, model=self.model).get_queryset(queryset=queryset,
                                                                                             restaurant_id=self.kwargs.get(
                                                                                                 'pk'))


class RestaurantEarningListView(LoginRequiredMixin, RestaurantOwnerMixin, PaginationMixin, ListView):
    template_name = RESTAURANT_EARNING_PAGE
    model = OrderPayoutDetail
    context_object_name = 'orders'
    ordering = ['-id']
    paginator_class = CustomPaginator
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        return RestaurantEarningService(request=self.request, model=self.model).get_queryset(queryset=queryset,
                                                                                             pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return RestaurantEarningService(request=self.request, model=self.model).get_context_data(context,
                                                                                                 self.kwargs['pk'])
