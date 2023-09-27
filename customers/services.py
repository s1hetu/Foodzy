from django.contrib import messages
from django.core.exceptions import BadRequest
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404

from FDA.constants import (
    BAD_REQUEST, CUSTOMER_CART_PAGE, CUSTOMER_ITEM_DETAIL_PAGE, CUSTOMER_RATING_PAGE,
    EMPTY_RATING_MESSAGE, INVALID_RATING_MESSAGE
)
from carts.models import CartItems
from delivery_agent.models import AcceptedOrder
from orders.models import Order
from restaurant.models import Categories, Items, RatingsAndReviews


class HomeService:
    def __init__(self, request, model):
        self.request = request
        self.model = model

    def get_queryset(self, queryset):
        queryset = self.model.get_all_items(request=self.request, queryset=queryset).select_related('restaurant', )
        if searched := self.request.GET.get('searched'):
            queryset = self.model.get_searched_items(searched_param=searched, queryset=queryset)

        if filter_result := self.request.GET.get('price_filter'):
            queryset = queryset.order_by('price') if filter_result == "low_to_high" else queryset.order_by('-price')

        return queryset

    def get_context_data(self, context):
        context.update(
            {
                'categories': Categories.get_categories(),
                'trending': Items.get_all_trending_items(request=self.request).select_related('restaurant',
                                                                                              'restaurant__address'),
                'searched': self.request.GET.get('searched')
            }
        )
        return context


class CustomerServices:
    @staticmethod
    def cart_view(request):
        all_products = CartItems.get_all_user_items(request.user.id).select_related('cart__user', 'item__restaurant')
        not_available = CartItems.check_unavailability_of_item(request.user.id)
        return render(request, CUSTOMER_CART_PAGE,
                      {'items': all_products, 'not_available': not_available})

    @staticmethod
    def item_detail_view(request, pk):
        context = {'item': get_object_or_404(Items, id=pk)}
        if cart_item := CartItems.get_cart_item(pk, request.user.id):
            context['cart_item'] = cart_item

        return render(request, CUSTOMER_ITEM_DETAIL_PAGE, context)

    @staticmethod
    def delivery_agent_rating_get(request, order_id):
        order = Order.get_object_from_pk(pk=order_id)
        accepted_order = AcceptedOrder.get_object_by_id(pk=order.accepted_order.id)
        if not accepted_order or accepted_order.rating:
            raise Http404
        return render(request, CUSTOMER_RATING_PAGE, {'entity_type': 'Delivery Agent'})

    @staticmethod
    def delivery_agent_rating_post(request, order_id):
        order = Order.get_object_from_pk(pk=order_id)
        accepted_order = AcceptedOrder.get_object_by_id(pk=order.accepted_order.id)
        rating = request.POST.get('rating')
        review = request.POST.get('review')
        try:
            rating = float(rating)
        except (ValueError, TypeError):
            messages.error(request, EMPTY_RATING_MESSAGE)
            return redirect('delivery-agent-rating', order.id)

        if rating <= 0 or rating > 5:
            messages.error(request, INVALID_RATING_MESSAGE)
            return redirect('delivery-agent-rating', order.id)
        if accepted_order.rating:
            raise BadRequest(BAD_REQUEST)
        accepted_order.rating = rating
        accepted_order.review = review
        accepted_order.save()
        return redirect('view-detail-order', order.id)

    @staticmethod
    def restaurant_rating_get(request, order_id):
        order = Order.objects.filter(id=order_id).first()
        if RatingsAndReviews.objects.filter(order=order).exists():
            raise Http404
        return render(request, CUSTOMER_RATING_PAGE, {'entity_type': 'Restaurant'})

    @staticmethod
    def restaurant_rating_post(request, order_id):
        rating = request.POST.get('rating')
        order = Order.objects.filter(id=order_id).first()
        review = request.POST.get('review')

        try:
            rating = float(rating)
        except (ValueError, TypeError):
            messages.error(request, EMPTY_RATING_MESSAGE)
            return redirect('restaurant-rating', order.id)

        if rating <= 0 or rating > 5:
            messages.error(request, INVALID_RATING_MESSAGE)
            return redirect('restaurant-rating', order.id)
        if RatingsAndReviews.objects.filter(order=order).exists():
            raise BadRequest(BAD_REQUEST)
        ratings_and_reviews, _ = RatingsAndReviews.get_or_create_rating_reviews_by_order_and_restaurant(order)
        if ratings_and_reviews.ratings:
            raise BadRequest(BAD_REQUEST)
        ratings_and_reviews.ratings = rating
        ratings_and_reviews.reviews = review
        ratings_and_reviews.save()

        return redirect('view-detail-order', order.id)
