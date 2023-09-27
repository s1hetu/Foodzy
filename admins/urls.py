from django.urls import path

from .views import (
    AdminPanel, DriversListView, DriversDetailView, DriversApplicationDetailView,
    DriversApplicationListView, UsersListView, UsersDetailView,
    RestaurantListView, RestaurantsDetailView, RestaurantApplicationListView, RestaurantsApplicationDetailView,
    OrdersListView, OrdersDetailView, ActionForRestaurantView, ApplicationActionForDeliveryAgentView,
    ActionForCustomerView, ApplicationActionForRestaurantView, ActionForDeliveryAgentView, CodAgentListView,
    CodAgentDetailView, ActionForCodDeliveryAgentView
)

urlpatterns = [
    path('', AdminPanel.as_view(), name="admin-home"),
    path('drivers/', DriversListView.as_view(), name="drivers-list"),
    path('cod-agents/', CodAgentListView.as_view(), name="cod-agents-list"),
    path('drivers/application/', DriversApplicationListView.as_view(), name="drivers-list-application"),

    path('drivers/<int:pk>/', DriversDetailView.as_view(), name="drivers-detail"),
    path('cod-agents/<int:pk>/', CodAgentDetailView.as_view(), name="cod-agent-detail"),
    path('drivers/application/<int:pk>/', DriversApplicationDetailView.as_view(), name="drivers-detail-application"),

    path('users/', UsersListView.as_view(), name="users-list"),
    path('users/<int:pk>/', UsersDetailView.as_view(), name="users-detail"),

    path('restaurants/', RestaurantListView.as_view(), name="restaurant-list"),
    path('restaurants/application/', RestaurantApplicationListView.as_view(), name="restaurant-list-application"),

    path('restaurants/<int:pk>/', RestaurantsDetailView.as_view(), name="restaurant-detail"),
    path('restaurants/application/<int:pk>/', RestaurantsApplicationDetailView.as_view(),
         name="restaurant-detail-application"),

    path('orders/', OrdersListView.as_view(), name="orders-list"),
    path('orders/<int:pk>/', OrdersDetailView.as_view(), name="orders-detail"),

    path('action-for-restaurant/<int:pk>/', ActionForRestaurantView.as_view(), name="action-for-restaurant"),
    path('action-for-delivery-agent/<int:pk>/', ActionForDeliveryAgentView.as_view(), name="action-for-delivery-agent"),
    path('action-for-customer/<int:pk>/', ActionForCustomerView.as_view(), name="action-for-customer"),
    path('action-for-cod-delivery-agent/<int:pk>/', ActionForCodDeliveryAgentView.as_view(),
         name="action-for-cod-delivery-agent"),

    path('application-action-for-delivery-agent/<int:pk>/', ApplicationActionForDeliveryAgentView.as_view(),
         name="application-action-for-delivery-agent"),
    path('application-action-for-restaurant/<int:pk>/', ApplicationActionForRestaurantView.as_view(),
         name="application-action-for-restaurant"),
]
