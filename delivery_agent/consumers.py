import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class AvailableDeliveries(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_name = None

    # client to server
    def connect(self):
        self.room_name = "agent"

        self.accept()

        async_to_sync(self.channel_layer.group_add)(
            self.room_name,
            self.channel_name,
        )

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_name,
            self.channel_name,
        )

    # server to client
    def receive(self, text_data=None, bytes_data=None):
        pass

    def order_received(self, event):
        self.send(text_data=json.dumps(event))

    def delivery_accepted(self, event):
        self.send(text_data=json.dumps(event))
