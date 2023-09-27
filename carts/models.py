from collections import defaultdict

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q, F, Sum

from restaurant.models import Items

User = settings.AUTH_USER_MODEL


class Cart(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    items = models.ManyToManyField(Items, through='CartItems')

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"Cart-{self.id} User-{self.user_id}"

    @classmethod
    def get_total(cls, user):
        return cls.objects.get(user=user).total


class CartItems(models.Model):
    cart = models.ForeignKey(Cart, null=False, on_delete=models.CASCADE)
    item = models.ForeignKey(Items, null=False, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        verbose_name_plural = "CartItems"
        ordering = ['id']

    @classmethod
    def get_all_user_items(cls, user_id):
        return cls.objects.filter(cart__user_id=user_id).select_related('item__restaurant')

    @classmethod
    def check_unavailability_of_item(cls, user_id):
        return cls.objects.filter(Q(cart__user_id=user_id) & Q(item__restaurant__is_accepting_orders=False) | Q(
            item__restaurant__is_blocked=True)).exists()

    @classmethod
    def get_cart_item(cls, pk, user_id):
        return cls.objects.filter(item_id=pk, cart__user_id=user_id).first()

    @classmethod
    def get_unavailable_items(cls):
        return cls.objects.filter(
            Q(item__restaurant__is_accepting_orders=False) | Q(quantity__gt=F('item__available_quantity'))).exists()

    @staticmethod
    def get_cart_item_restaurant_wise(cart_items):
        data = defaultdict(list)
        for item in cart_items:
            data[item.item.restaurant.id].append({"item": item.item, "quantity": item.quantity, "total": item.total})
        return data

    @staticmethod
    def get_item_total_cartitems(cart_items, restaurant_id):
        """
        :params restaurant_id: restaurant's id
        :params cart_items: restaurant's id
        :returns: restaurant_object , restaurant's address. restaurant's address lat, restaurant's address long
        """
        return cart_items.filter(item__restaurant__id=restaurant_id).aggregate(total=Sum('total'))['total'] or 0
