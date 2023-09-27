import datetime

from dateutil.utils import today
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.db import models
from django.db.models import Sum, Q
from django.http import Http404
from django.shortcuts import get_object_or_404

from accounts.models import User
from delivery_agent.utils import convert_timedelta
from delivery_agent.validators import validate_rating, validate_license_no, validate_pancard_no
from orders.models import Order
from restaurant.validators import validate_ifsc_code

agent_status = (
    ('Available', 'Available'),
    ('Not Available', 'Not Available'),
)

status_choices = (
    ('pending', 'pending'),
    ('approved', 'approved'),
    ('rejected', 'rejected'),
    # ('under_process', 'under_process')
)


class Document(models.Model):
    agent = models.OneToOneField(User, on_delete=models.CASCADE, related_name='document')
    license_number = models.CharField(max_length=16, validators=[validate_license_no])
    license_document = models.ImageField(upload_to='delivery_agent_licenses/')
    pancard_number = models.CharField(max_length=10, validators=[validate_pancard_no])
    pancard_document = models.ImageField(upload_to='delivery_agent_pancard/')
    is_verified = models.BooleanField(default=False)
    application_status = models.CharField(max_length=20, choices=status_choices, default='pending')
    account_no = models.CharField(validators=[MinLengthValidator(8), MaxLengthValidator(18)], max_length=18,
                                  default="1234567890")
    ifsc_code = models.CharField(validators=[validate_ifsc_code], max_length=11)
    razorpay_contact_id = models.CharField(max_length=40, null=True, blank=True)
    razorpay_fund_account_id = models.CharField(max_length=40, null=True, blank=True)

    # razorpay_account_id = models.CharField(max_length=30, null=True, blank=True)

    class Meta:
        permissions = [
            ('verify_document', 'can varify document'),
        ]

        ordering = ['id']

    def __str__(self):
        return f'{self.id} | {self.agent} | {self.is_verified}'


class AdditionalDetail(models.Model):
    agent = models.OneToOneField(User, on_delete=models.CASCADE, related_name='additional_detail')
    rating = models.FloatField(null=True, validators=[validate_rating])
    status = models.CharField(max_length=30, choices=agent_status, default='Not Available')

    class Meta:
        permissions = [
            ('update_status', 'can update status'),
        ]
        ordering = ['id']

    @classmethod
    def get_agent_additional_details(cls, agent):
        return cls.objects.filter(agent=agent).first()

    @classmethod
    def get_agent_status(cls, agent):
        if agent_obj := cls.get_agent_additional_details(agent):
            return agent_obj.status
        else:
            return None

    def __str__(self):
        return f'{self.id} | {self.agent}'


class ActivationTime(models.Model):
    agent = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='agent_time_log')
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True)
    session_duration = models.DurationField(null=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'{self.agent} | {self.started_at}'

    @classmethod
    def add_time_entry(cls, agent):
        cls.objects.create(agent=agent)

    @classmethod
    def last_time_entry_of_agent(cls, agent):
        return cls.objects.filter(agent=agent).order_by('-id').first()

    @classmethod
    def get_active_time_entries(cls, user):
        return cls.objects.filter(agent=user).order_by('-started_at')

    def get_session(self):
        return convert_timedelta(self.session_duration) if self.session_duration else "Active"

    @classmethod
    def today_active_time(cls, agent):
        today_act_time = (
            cls.objects.filter(agent=agent, started_at__date=today(),
                               session_duration__isnull=False).values_list(
                'session_duration', flat=True))
        today_act_time = map(lambda x: x - datetime.timedelta(microseconds=x.microseconds), today_act_time)
        active_time = sum(today_act_time, datetime.timedelta(0))
        return convert_timedelta(active_time)


class AcceptedOrder(models.Model):
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accepted_orders')
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='accepted_order')
    rating = models.FloatField(null=True, validators=[validate_rating])
    review = models.TextField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'{self.id} | {self.agent.username}| {self.agent.id}'

    @classmethod
    def get_agent_from_order_id(cls, pk):
        if order_obj := cls.objects.filter(order_id=pk).select_related('order', 'order__user').first():
            return order_obj.agent
        else:
            raise Http404

    @classmethod
    def get_total_value_of_orders_delivered_by_agent(cls, agent):
        total_price = cls.objects.filter(agent=agent).aggregate(order_total_sum=Sum('order__total')).get(
            'order_total_sum')
        return total_price or 0

    @classmethod
    def get_delivery_charge(cls, agent):
        delivery_charge = cls.objects.filter(agent=agent).aggregate(
            total_delivery_charge=Sum('order__delivery_charges')).get(
            'total_delivery_charge')
        return delivery_charge or 0

    @classmethod
    def get_object_by_id(cls, pk):
        return get_object_or_404(cls, id=pk)

    def average_rating(self):
        average_rating = AcceptedOrder.objects.filter(agent=self.agent, rating__isnull=False).aggregate(
            avg_rating=models.Avg('rating'))
        if average_rating['avg_rating']:
            average_rating['avg_rating'] = round(average_rating['avg_rating'], 2)
        return average_rating['avg_rating']

    @classmethod
    def accept_deliveries(cls, agent, order_id):
        return cls.objects.create(agent=agent, order_id=order_id)

    @classmethod
    def get_agent_reviews_and_ratings(cls, agent_id):
        return cls.objects.filter(agent_id=agent_id, order__status='delivered',
                                  rating__isnull=False).select_related('agent', 'order__user')

    @classmethod
    def get_current_active_deliveries(cls, agent, queryset=None):
        if not agent:
            cls.objects.filter(Q(order__cancelled=False,
                                 order__status__in=['accepted', 'preparing', 'ready to pick', 'picked', 'prepared',
                                                    'out for delivery']) | Q(order__cancelled=False,
                                                                             order__status__in=['delivered'],
                                                                             order__paid=False, order__mode='COD'))
        return cls.objects.filter(Q(agent=agent, order__cancelled=False,
                                    order__status__in=['accepted', 'preparing', 'ready to pick', 'picked', 'prepared',
                                                       'out for delivery']) | Q(agent=agent, order__cancelled=False,
                                                                                order__status__in=['delivered'],
                                                                                order__paid=False,
                                                                                order__mode='COD')).select_related(
            'order').order_by('created_at')

    @classmethod
    def current_active_delivery_count(cls, agent):
        return cls.get_current_active_deliveries(agent=agent).count()

    @classmethod
    def accepted_order_deliveries(cls, agent, queryset=None):
        if not queryset:
            queryset = cls.objects.all()
        return queryset.filter(agent=agent).select_related('order', 'order__order_payout', 'order__user').order_by(
            '-created_at')

    @classmethod
    def accepted_order_deliveries_count(cls, agent, queryset=None):
        return cls.accepted_order_deliveries(agent=agent, queryset=queryset).count()

    @classmethod
    def accepted_order_deliveries_on_range(cls, agent, first_date, second_date):
        return cls.objects.filter(agent=agent, order__status='delivered',
                                  order__order_date__date__range=[first_date, second_date])

    @classmethod
    def total_orders_delivered(cls, agent):
        return cls.objects.filter(agent=agent, order__status='delivered')

    @classmethod
    def total_orders_delivered_count(cls, agent):
        return cls.total_orders_delivered(agent=agent).count()

    @classmethod
    def orders_delivered_today(cls, agent):
        return cls.objects.filter(agent_id=agent, order__status='delivered',
                                  order__order_date__date=today())

    @classmethod
    def orders_delivered_today_count(cls, agent):
        return cls.orders_delivered_today(agent=agent).count()

    def save(self, **kwargs):
        obj = super(AcceptedOrder, self).save(**kwargs)
        agent_detail = AdditionalDetail.objects.get(agent=self.agent)
        agent_detail.rating = self.average_rating()
        agent_detail.save()
        return obj


class AgentCashEntry(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='cod_order')
    agent = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='agent_cash')
    date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    deposit = models.BooleanField(default=False)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'agent {self.agent_id} | order {self.order_id}'

    @classmethod
    def create_agent_cash_entry(cls, agent, order, amount):
        cls.objects.get_or_create(agent=agent, order=order, amount=amount)

    # @classmethod
    # def get_pending_deposit_cash_entry_of_agent(cls, agent_id, order_id):
    #     return cls.objects.filter(agent=agent_id, order_id=order_id) if order_id else cls.objects.filter(agent=agent_id)

    @classmethod
    def cash_collection_of_agent(cls, agent):
        cash_collection = cls.objects.filter(agent=agent, deposit=False).aggregate(Sum('amount'))['amount__sum']
        return cash_collection or 0

    @classmethod
    def get_total_cash(cls, queryset):
        return queryset.aggregate(total=Sum('amount'))['total']

    @classmethod
    def get_unique_agents(cls, queryset):
        return queryset.distinct('id', 'agent')
