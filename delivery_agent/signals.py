from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Document, AdditionalDetail, AcceptedOrder, ActivationTime


@receiver(pre_save, sender=Document)
def additional_details_on_agent_varify(sender, instance, **kwargs):
    """
    This signal will create an object in AdditionalDetail table when document of agent will approve
    """
    x = Document.objects.filter(id=instance.id).first()
    if x and not x.is_verified and instance.is_verified:
        AdditionalDetail.objects.get_or_create(agent=instance.agent)


@receiver(pre_save, sender=ActivationTime)
def update_session_duration(sender, instance, **kwargs):
    """
    This signal will update session duration when ended_at is updated
    """
    if instance.ended_at:
        instance.session_duration = instance.ended_at - instance.started_at


@receiver(post_save, sender=AcceptedOrder)
def accepted_order_created(sender, created, instance, **kwargs):
    if created:
        order = instance.order.id
        layer = get_channel_layer()
        room = 'agent'
        async_to_sync(layer.group_send)(room, {
            'type': 'delivery.accepted',
            'id': order,
            'date': str(instance.order.order_date.strftime('%b. %d, %Y, %-I:%M %p')),
            'total': str(instance.order.total),

        })
