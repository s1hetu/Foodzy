from django.contrib import admin

from .models import Order, OrderItems, OrderConfirmOtp, OrderPayoutDetail

# Register your models here.
admin.site.register(Order)
admin.site.register(OrderConfirmOtp)
admin.site.register(OrderItems)
admin.site.register(OrderPayoutDetail)
