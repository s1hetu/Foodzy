import json
import logging

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

logger = logging.getLogger('info_log')


class RecentOrders(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.res_id = None
        self.room_name = None

    def connect(self):
        self.res_id = self.scope['url_route']['kwargs']['res_id']
        self.room_name = f"res_{self.res_id}"

        self.accept()

        async_to_sync(self.channel_layer.group_add)(
            self.room_name,
            self.channel_name,
        )
        logger.info("connected with connect method")

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_name,
            self.channel_name,
        )
        logger.info("disconnected with disconnect method")

    def receive(self, text_data=None, bytes_data=None):
        logger.info("received with receive method")

    def order_received(self, event):
        logger.info("order_received call")
        self.send(text_data=json.dumps(event))
