import json

from django.contrib import messages
from django.http import HttpResponse, Http404
from django.shortcuts import redirect, render
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from FDA.constants import (
    RESTAURANT_ACCOUNT_REGISTER_SUCCESS, RESTAURANT_STATUS_UPDATED, USER_TYPES,
    RESTAURANT_REGISTRATION_PAGE, RESTAURANT_ADDED_SUCCESSFULLY,
    RESTAURANT_ADD_RESTAURANT_PAGE, RESTAURANT_IMAGE_ADDED_SUCCESSFULLY,
    RESTAURANT_ITEM_ADDED_SUCCESSFULLY
)
from accounts.utils import send_activation_email
from delivery_agent.utils import convert_into_star_rating, get_rating_degrees
from orders.models import Order, OrderItems, OrderPayoutDetail
from orders.services import client
from restaurant.models import Items, Restaurant, RatingsAndReviews
from .forms import RestaurantForm, AddressForm, DocumentsForm, RestaurantUserForm, GalleryImageForm
from .serializers import RestaurantSerializer


class RestaurantOwnerService:
    def __init__(self, request, model):
        self.request = request
        self.model = model
        self.user = request.user

    def get_owner_restaurants(self):
        return self.model.get_restaurants_from_user(self.user).select_related('owner', 'address', 'address__city',
                                                                              'address__state')


class RestaurantStatus:
    @staticmethod
    def get_context_data(context, pk, request):
        context.update({'restaurants': Restaurant.get_restaurants_from_user(request.user)})
        context.update({"restaurant": Restaurant.get_restaurant_from_id(pk)})
        return context


class RestaurantMenuService:
    @staticmethod
    def get_restaurant_menu(pk):
        items = Items.get_items_from_restaurant(pk).select_related('category')
        products = {}
        for item in items:
            products[item.category.name] = products.get(item.category.name, []) + [
                (item.name, float(item.price), item.description, item.id)]
        return products


class DetailOrderService:

    @staticmethod
    def get_order_details(pk):
        context = {}
        order = Order.get_object_from_pk(pk)
        details = OrderItems.get_order_items_from_order(order)
        context['order'] = order
        context['details'] = details
        return context

    @staticmethod
    def update_order_status(request, pk):
        data = json.loads(request.body)
        status = data['status']
        order = Order.get_object_from_pk(pk=pk)

        order.status = status
        if order.status == "rejected" and order.mode == "Online" and order.paid:  # pragma: no cover
            payment_id = order.razorpay_payment_id
            client.payment.refund(payment_id, {"amount": int(order.total) * 100, "speed": "normal", "notes": {
                "notes_key_1": f"Refund for {order.id} as the order got cancelled.", }, })
        for item in order.orderitems_set.all():
            item.item.available_quantity += item.quantity
            item.item.save()
        order.save()
        return HttpResponse({'status': 'good'})


class ReviewsRestaurantService:

    def __init__(self, model):
        self.model = model

    def get_queryset(self, queryset, pk):
        queryset = self.model.get_restaurant_ratings_reviews(pk)
        convert_into_star_rating(queryset, restaurant=True)
        return queryset


class ViewOrderService:

    @staticmethod
    def get_queryset(queryset, pk):
        restaurant = Restaurant.get_restaurant_from_id(pk=pk)
        queryset = Order.get_restaurant_orders(restaurant).select_related('restaurant', 'user')
        return queryset


class RegisterRestaurantFormService:

    @staticmethod
    def get_form():
        return {'user': RestaurantUserForm(), 'address': AddressForm(), 'restaurant': RestaurantForm(),
                'documents': DocumentsForm()}

    @staticmethod
    def save_form(request):
        user = RestaurantUserForm(request.POST)
        address = AddressForm(request.POST)
        restaurant = RestaurantForm(request.POST, request.FILES)
        documents = DocumentsForm(request.POST, request.FILES)
        if user.is_valid() and address.is_valid() and restaurant.is_valid() and documents.is_valid():
            user = user.save()
            address = address.save(user=user)
            restaurant = restaurant.save(owner=user, address=address)
            documents = documents.save(restaurant=restaurant)
            code = user.get_activation_code()
            send_activation_email(request, user.email, code)
            messages.success(request, RESTAURANT_ACCOUNT_REGISTER_SUCCESS)
            return redirect('login')

        return render(request, template_name=RESTAURANT_REGISTRATION_PAGE,
                      context={'user': user, 'address': address, 'restaurant': restaurant, 'documents': documents})


class AddItemFormService:

    def __init__(self, request):
        self.request = request

    def form_valid(self, form, **kwargs):
        form.save(pk=kwargs.get('pk'))
        messages.success(self.request, RESTAURANT_ITEM_ADDED_SUCCESSFULLY)
        return redirect('restaurant-menu', kwargs.get('pk'))


class AddRestaurantService:

    @staticmethod
    def get_form():
        return {'address': AddressForm(), 'restaurant': RestaurantForm(), 'documents': DocumentsForm()}

    @staticmethod
    def save_form(request):
        address = AddressForm(request.POST)
        restaurant = RestaurantForm(request.POST, request.FILES)
        documents = DocumentsForm(request.POST, request.FILES)

        if address.is_valid() and restaurant.is_valid() and documents.is_valid():
            user = request.user
            address = address.save()
            restaurant = restaurant.save(owner=user, address=address)
            documents.save(restaurant=restaurant)
            messages.success(request, RESTAURANT_ADDED_SUCCESSFULLY)
            return redirect('restaurant-admin')

        context = {'address': address, 'restaurant': restaurant, 'documents': documents}
        return render(request, template_name=RESTAURANT_ADD_RESTAURANT_PAGE, context=context)


class UpdateRestaurantOrderStatusService:
    @staticmethod
    def get_response(request, pk):
        data = request.data.copy()
        data['is_accepting_orders'] = data['status']
        restaurant_obj = Restaurant.get_restaurant_from_id(pk)
        serializer = RestaurantSerializer(restaurant_obj, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': RESTAURANT_STATUS_UPDATED, 'data': data, 'status': status.HTTP_200_OK})


class RestaurantPanelService:

    @staticmethod
    def get_data(context, pk, request):
        restaurant = Restaurant.get_restaurant_from_id(pk)
        all_items = Items.get_items_from_restaurant(restaurant)
        number_of_items = Items.get_restaurant_items_count(restaurant)
        number_of_categories = Items.get_restaurant_category_serving_count(restaurant)

        orders = Order.get_restaurant_orders(restaurant)
        pending_orders = Order.get_pending_restaurant_orders(restaurant)
        number_of_customers = orders.values('user__email').distinct('id').count()
        current_orders = Order.get_current_orders(restaurant)
        active_orders = current_orders != 0
        number_of_orders = Order.get_restaurant_orders_count(restaurant)
        revenue = OrderPayoutDetail.get_total_restaurant_profit(restaurant)
        ratings = restaurant.ratings
        my_restaurants = Restaurant.get_restaurants_from_user(request.user).count()
        number_of_ratings = RatingsAndReviews.get_restaurant_ratings_reviews_count(restaurant)
        ratings, first_half_rating_degrees, second_half_rating_degrees = get_rating_degrees(ratings)

        context.update({'restaurants': Restaurant.get_restaurants_from_user(request.user),
                        'first_half_rating_degrees': first_half_rating_degrees,
                        'second_half_rating_degrees': second_half_rating_degrees, 'ratings': ratings,
                        'number_of_orders': number_of_orders, 'number_of_customers': number_of_customers,
                        'number_of_categories': number_of_categories, 'number_of_ratings': number_of_ratings,
                        'restaurant': restaurant, 'orders': orders, 'number_of_items': number_of_items,
                        'revenue': revenue, 'my_restaurants': my_restaurants, 'restaurant_id': restaurant.id,
                        'pending_orders': bool(pending_orders), 'active_orders': active_orders})
        return context


class AddGalleryImageService:
    def __init__(self, request):
        self.request = request

    @staticmethod
    def get_form(pk):
        restaurant = Restaurant.get_restaurant_from_id(pk)
        return {'restaurant': restaurant, 'form': GalleryImageForm}

    def form_valid(self, form, **kwargs):
        form.save(restaurant_id=kwargs['pk'])
        messages.success(self.request, RESTAURANT_IMAGE_ADDED_SUCCESSFULLY)
        return redirect('view_restaurant_gallery', kwargs['pk'])


class RestaurantGalleryService:
    def __init__(self, request, model):
        self.request = request
        self.model = model

    def get_queryset(self, restaurant_id, queryset):
        if self.request.user.groups.filter(name__in=(USER_TYPES[1],)):
            if restaurant_id:
                queryset = self.model.get_restaurant_gallery_image_by_id(restaurant_id=restaurant_id, queryset=queryset)
            else:
                raise Http404
        elif self.request.user.groups.filter(name__in=(USER_TYPES[0],)):
            queryset = self.model.get_restaurant_gallery_images()
        else:
            raise PermissionDenied
        return queryset


class RestaurantEarningService:
    def __init__(self, request, model):
        self.request = request
        self.model = model

    def get_queryset(self, queryset, pk):
        queryset = OrderPayoutDetail.get_payout_detail_for_restaurant(restaurant_id=pk, queryset=queryset).order_by(
            'id')
        return queryset

    def get_context_data(self, context, pk):
        last_month_earning = OrderPayoutDetail.get_restaurant_last_month_earning(pk)
        due_payment = OrderPayoutDetail.get_restaurant_pending_money(pk)
        total_payment_received = OrderPayoutDetail.get_total_payment_paid_to_restaurant(pk)
        context['last_month_earning'] = last_month_earning
        context['due_payment'] = due_payment
        context['total_earning'] = total_payment_received
        return context
