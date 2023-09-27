from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver

from orders.models import Order
from restaurant.models import Items


@receiver(post_save, sender=Order)
def restaurant_order_created(sender, created, instance, **kwargs):
    if created:
        restaurant = instance.restaurant.id
        layer = get_channel_layer()
        room = f"res_{restaurant}"
        profile = instance.user.profile_pic
        if profile:
            profile = profile.url

        else:
            profile = "/media/restaurant_images/snack2_Lpbnu3f.jpeg"
        async_to_sync(layer.group_send)(room, {
            'type': 'order.received',
            'date': str(instance.order_date.strftime('%b. %d, %Y, %-I:%M %p')),
            'total': str(instance.total),
            'name': instance.user.username,
            'order': instance.id,
            'status': instance.status,
            'profile': profile,
        })


@receiver(post_save, sender=Items)
def restaurant_update_item(sender, created, instance, **kwargs):
    if not created:
        for cart_item in instance.cartitems_set.all():
            cart_item.total = cart_item.quantity * instance.price
            cart_item.save()
            cart_item.cart.total = cart_item.cart.cartitems_set.all().aggregate(total=Sum('total'))['total']
            cart_item.cart.save()
