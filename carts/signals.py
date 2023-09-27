from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from .models import CartItems


@receiver(post_save, sender=CartItems)
def calculate_total_for_new_cart_item(sender, instance, created, **kwargs):
    if created:

        instance.cart.total += instance.item.calculate_discount()
        instance.cart.save()
        instance.total = instance.item.calculate_discount()
        instance.save()


@receiver(pre_save, sender=CartItems)
def recalculate_total_for_update_cart_item(sender, instance, **kwargs):
    if instance_previous_state := CartItems.objects.filter(id=instance.id).first():
        instance.cart.total += (instance.quantity - instance_previous_state.quantity) * instance.item.calculate_discount()
        instance.cart.save()
        instance.total = instance.item.calculate_discount() * instance.quantity


@receiver(post_delete, sender=CartItems)
def recalculate_total_for_delete_cart_item(sender, instance, **kwargs):
    instance.cart.total -= instance.item.calculate_discount() * instance.quantity
    instance.cart.save()
