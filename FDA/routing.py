from django.urls import re_path

from restaurant.consumers import RecentOrders
from delivery_agent.consumers import AvailableDeliveries

websocket_urlpatterns = [
    re_path(r'ws/(?P<res_id>\w+)/$', RecentOrders.as_asgi()),
    re_path(r'ws/', AvailableDeliveries.as_asgi()),
]
