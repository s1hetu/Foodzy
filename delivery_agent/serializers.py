from rest_framework import serializers

from delivery_agent.models import AdditionalDetail
from orders.models import Order


class UpdateAgentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdditionalDetail
        fields = ['status']


class UpdateDeliveryStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']


class UpdateDeliveryPaidFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['paid']
