import contextlib
import datetime
import uuid

from django.conf import settings
from django.db import models
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404

from orders.utils import send_otp_email
from restaurant.models import Items
from restaurant.models import Restaurant

User = settings.AUTH_USER_MODEL
choice_status = [
    ('waiting', 'waiting'),
    ('accepted', 'accepted'),
    ('rejected', 'rejected'),
    ('preparing', 'preparing'),
    ('prepared', 'prepared'),
    ('ready to pick', 'ready to pick'),
    ('picked', 'picked'),
    ('out for delivery', 'out for delivery'),
    ('delivered', 'delivered'),
    ('failed', 'failed')
]

choice_mode = [
    ('COD', 'COD'),
    ('Online', 'Online')
]


class Order(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    order_date = models.DateTimeField(auto_now_add=True)
    cancelled = models.BooleanField(default=False)
    items = models.ManyToManyField(Items, through='OrderItems')
    status = models.CharField(max_length=30, choices=choice_status, default='waiting')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.SET_NULL, related_name='orders', null=True)
    razorpay_payment_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_order_id = models.CharField(max_length=100, null=True, blank=True)
    mode = models.CharField(max_length=10, choices=choice_mode, default='COD', null=True, blank=True)
    paid = models.BooleanField(default=False, null=True, blank=True)
    delivery_charges = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    user_address = models.TextField(max_length=500)
    user_address_lat = models.DecimalField(max_digits=9, decimal_places=6)
    user_address_long = models.DecimalField(max_digits=9, decimal_places=6)
    restaurant_address = models.TextField(max_length=500)
    restaurant_address_lat = models.DecimalField(max_digits=9, decimal_places=6)
    restaurant_address_long = models.DecimalField(max_digits=9, decimal_places=6)

    class Meta:
        ordering = ['id']

    @classmethod
    def get_order_with_search_params(cls, params, queryset):
        search_order_id = None
        with contextlib.suppress(ValueError):
            search_order_id = int(params)

        return queryset.filter(
            Q(user__username__icontains=params) |
            Q(restaurant__name__icontains=params) |
            Q(id=search_order_id)
        )

    @classmethod
    def get_orders(cls):
        return cls.objects.all()

    @classmethod
    def get_order_from_status(cls, params, queryset=None):
        if not queryset:
            queryset = cls.objects.all()
        return queryset.filter(Q(status=params.lower()))

    @classmethod
    def get_order_from_restaurant_id(cls, params, queryset=None):
        if not queryset:
            queryset = cls.get_orders()
        with contextlib.suppress(ValueError):
            restaurant_id = int(params)
        return queryset.filter(Q(restaurant_id=restaurant_id))

    @classmethod
    def get_object_from_pk(cls, pk):
        return get_object_or_404(cls, pk=pk)

    @classmethod
    def get_total_of_all_orders(cls, queryset=None):
        if not queryset:
            queryset = cls.get_orders()
        return queryset.filter(status='delivered').aggregate(total_sum=Sum('total'))['total_sum']

    @classmethod
    def get_user_orders(cls, user):
        return cls.objects.filter(user=user)

    @classmethod
    def is_order_paid(cls, order_id):
        return cls.objects.get(id=order_id).paid

    @classmethod
    def get_order_status(cls, order_id):
        return cls.objects.get(id=order_id).status

    @classmethod
    def get_orders_count(cls, queryset=None):
        return queryset.count() if queryset else cls.get_orders().count()

    @classmethod
    def get_delivered_orders(cls, queryset=None):
        if not queryset:
            queryset = cls.get_orders()
        return queryset.filter(status='delivered')

    @classmethod
    def get_delivered_orders_count(cls, queryset=None):
        return cls.get_delivered_orders(queryset).count()

    @classmethod
    def get_orders_from_payment_id(cls, payment_id):
        return cls.objects.filter(razorpay_payment_id=payment_id)

    @classmethod
    def get_restaurant_orders(cls, restaurant):
        return cls.objects.filter(restaurant=restaurant).order_by('-id').select_related('user')

    @classmethod
    def get_current_orders(cls, restaurant):
        return cls.objects.filter(restaurant=restaurant, cancelled=False,
                                  status__in=['accepted', 'preparing', 'ready to pick', 'prepared',
                                              ]).order_by('-order_date')

    @classmethod
    def get_restaurant_orders_count(cls, restaurant):
        return cls.get_restaurant_orders(restaurant).count()

    @classmethod
    def get_restaurant_orders_revenue(cls, restaurant):
        return cls.get_restaurant_orders(restaurant).values_list('total', flat=True).aggregate(Sum('total'))

    @classmethod
    def get_pending_restaurant_orders(cls, restaurant):
        return cls.objects.filter(
            Q(restaurant=restaurant), Q(status='waiting') | Q(
                status='accepted') | Q(status='preparing'))

    def __str__(self):
        return f"Order-{self.id} User-{self.user_id}"


class OrderItems(models.Model):
    order = models.ForeignKey(Order, null=False, on_delete=models.CASCADE)
    item = models.ForeignKey(Items, null=False, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    item_price = models.FloatField()
    item_discount = models.FloatField(default=0)

    class Meta:
        verbose_name_plural = "OrderItems"
        ordering = ['id']

    def get_discounted_price(self):
        return self.item_price - (self.item_price * self.item_discount / 100)

    def get_items_total(self):
        return self.quantity * (self.get_discounted_price())

    @classmethod
    def get_order_items_from_order(cls, order):
        return cls.objects.filter(order=order)

    @classmethod
    def get_items_from_order_id(cls, pk):
        return cls.objects.select_related('item').filter(order=pk)


    @classmethod
    def create_order_items(cls, item_details, order, decrease_item=False):
        for item_detail in item_details:
            item = Items.get_item(item_detail['item'].id)
            cls.objects.create(order=order, quantity=item_detail['quantity'], total=item_detail['total'], item=item,
                               item_price=item.price,
                               item_discount=item.discount)
            if decrease_item:
                item.decrease_item_quantity(item_detail)
        return None


class OrderConfirmOtp(models.Model):
    otp = models.CharField(max_length=6)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='confirm_otp')

    class Meta:
        ordering = ['id']

    @staticmethod
    def generate_otp_code():
        return str(uuid.uuid4())[:6]

    @classmethod
    def get_otp(cls, order):
        obj = cls()
        obj.otp = cls.generate_otp_code()
        obj.order = order
        obj.save()
        return obj.otp

    @classmethod
    def send_otp(cls, order):
        otp = cls.get_otp(order=order)
        send_otp_email(order.user.email, otp, order.id)

    def __str__(self):
        return f'{self.order}'


class OrderPayoutDetail(models.Model):  # pragma: no cover
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='order_payout')
    agent = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='agent_payment')
    agent_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    restaurant = models.ForeignKey(Restaurant, null=True, on_delete=models.SET_NULL, related_name='restaurant_payment')
    rest_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payout_date = models.DateTimeField(auto_now_add=True)
    commission = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    razorpay_payout_restaurant_id = models.CharField(max_length=40, null=True, blank=True)
    razorpay_payout_agent_id = models.CharField(max_length=40, null=True, blank=True)

    class Meta:
        ordering = ['id']

    @classmethod
    def create_payout_detail(cls, order, agent, agent_amount, rest_amount, commission):
        OrderPayoutDetail.objects.get_or_create(order=order, agent=agent, agent_amount=agent_amount,
                                                restaurant=order.restaurant, rest_amount=rest_amount,
                                                commission=commission)

    @classmethod
    def get_payout_detail_for_agent(cls, agent_id, order_id=None):
        return cls.objects.filter(agent=agent_id, order_id=order_id,
                                  razorpay_payout_agent_id__isnull=False) if order_id else cls.objects.filter(
            agent=agent_id, razorpay_payout_agent_id__isnull=False).select_related('order', 'order__user')

    @classmethod
    def get_agent_total_earning(cls, agent):
        return cls.objects.filter(agent=agent, razorpay_payout_agent_id__isnull=False).select_related('order',
                                                                                                      'order__user').aggregate(
            earning_total=Sum('agent_amount'))['earning_total'] or 0

    @classmethod
    def get_agent_last_month_earning(cls, agent):
        prev = datetime.date.today().replace(day=1) - datetime.timedelta(days=1)
        last_month = prev.month
        return cls.objects.filter(agent=agent,
                                  order__order_date__month=last_month,
                                  razorpay_payout_agent_id__isnull=False).aggregate(earning_total=Sum('agent_amount'))[
            'earning_total'] or 0

    @classmethod
    def get_payout_detail_for_restaurant(cls, restaurant_id, queryset=None):
        if not queryset:
            queryset = cls.objects.all()
        return queryset.filter(
            restaurant_id=restaurant_id, razorpay_payout_restaurant_id__isnull=False).select_related('order',
                                                                                                     'order__user')

    @classmethod
    def get_restaurant_last_month_earning(cls, restaurant_id):
        last_month = (datetime.date.today().replace(day=1) - datetime.timedelta(days=1)).month
        return cls.objects.filter(restaurant_id=restaurant_id,
                                  order__order_date__month=last_month,
                                  razorpay_payout_restaurant_id__isnull=False).aggregate(
            earning_total=Sum('rest_amount'))['earning_total'] or 0

    @classmethod
    def get_restaurant_pending_money(cls, restaurant_id):
        return cls.objects.filter(restaurant_id=restaurant_id, razorpay_payout_restaurant_id__isnull=True).aggregate(
            earning_total=Sum('rest_amount'))['earning_total'] or 0

    @classmethod
    def get_total_payment_paid_to_restaurant(cls, restaurant_id):
        return cls.objects.filter(restaurant_id=restaurant_id, razorpay_payout_restaurant_id__isnull=False).aggregate(
            earning_total=Sum('rest_amount'))['earning_total'] or 0

    @classmethod
    def get_total_restaurant_profit(cls, restaurant_id):
        return cls.objects.filter(restaurant_id=restaurant_id).aggregate(
            earning_total=Sum('rest_amount'))['earning_total'] or 0

    def __str__(self):
        return f'order {self.order.id} details'
