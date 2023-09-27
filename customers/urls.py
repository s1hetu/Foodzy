from django.urls import path

from .views import HomeView, CartView, ItemDetailView, DeliveryAgentRatings, RestaurantRatings

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("cart/", CartView.as_view(), name="cart"),
    path("item/<int:pk>/", ItemDetailView.as_view(), name="cart-item"),

    path("rate/delivery-agent/<int:pk>/", DeliveryAgentRatings.as_view(), name="delivery-agent-rating"),
    path("rate/restaurant/<int:pk>/", RestaurantRatings.as_view(), name="restaurant-rating"),
]
