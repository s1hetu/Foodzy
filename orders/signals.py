from datetime import datetime, timedelta
from datetime import timezone

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from orders.models import Order
from orders.tasks import reject_order_if_not_accepted


# @receiver(pre_save, sender=Order)
# def restaurant_accept_order(sender, instance, **kwargs):
#     if instance_previous_state := Order.objects.filter(id=instance.id).first():
#         if instance_previous_state.status == "waiting" and instance.status == "accepted":
#             layer = get_channel_layer()
#             room = "agent"
#             if profile := instance.user.profile_pic:
#                 profile = profile.url
#             else:
#                 profile = "/media/user_images/default.jpg"
# async_to_sync(layer.group_send)(room, {
#     'type': 'order.received',
#     'date': str(instance.order_date.strftime('%b. %d, %Y, %-I:%M %p')),
#     'total': str(instance.total),
#     'name': instance.user.username,
#     'order': instance.id,
#     'profile': profile,
# })


@receiver(post_save, sender=Order)
def restaurant_accept_order(sender, instance, created, **kwargs):
    if created:
        waiting_time = datetime.now(timezone.utc) + timedelta(
            seconds=int(settings.REJECT_ORDER_WAITING_TIME))
        reject_order_if_not_accepted.apply_async(eta=waiting_time, kwargs={'id': instance.id})
