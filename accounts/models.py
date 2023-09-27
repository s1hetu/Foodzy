import contextlib
import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator

from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator

from django.db import models
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from social_django.models import UserSocialAuth

from FDA.constants import ACCOUNT_MIN_2_LENGTH_ERROR
from .managers import UserManager, AddressManager
import datetime

from phonenumber_field.modelfields import PhoneNumberField


class State(models.Model):
    name = models.CharField(max_length=30)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name


class City(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name


class Address(models.Model):
    address_title = models.CharField(max_length=50, null=True)
    address_line1 = models.CharField(max_length=100, validators=[MinLengthValidator(2, ACCOUNT_MIN_2_LENGTH_ERROR)])
    address_line2 = models.CharField(max_length=100, validators=[MinLengthValidator(2, ACCOUNT_MIN_2_LENGTH_ERROR)])
    street = models.CharField(max_length=100, validators=[MinLengthValidator(2, ACCOUNT_MIN_2_LENGTH_ERROR)])
    landmark = models.CharField(max_length=50, validators=[MinLengthValidator(2, ACCOUNT_MIN_2_LENGTH_ERROR)])
    pincode = models.IntegerField(validators=[MinValueValidator(100000), MaxValueValidator(999999)])
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    long = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    objects = AddressManager()

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'{self.address_line1},{self.address_line2}, {self.street}, {self.landmark}, {self.city}, {self.pincode}, {self.state}'

    @classmethod
    def get_near_by_restaurants(cls, request, km=10):
        return cls.objects.filter(address_title="Restaurant Address").locations_near_give_coordinates(
            request.user.addresses.first().lat,
            request.user.addresses.first().long, km).select_related('restaurant',)

    @classmethod
    def get_near_by_restaurants_by_coordinates(cls, long, lat, km=10):
        return cls.objects.filter(address_title="Restaurant Address"
                                  ).locations_near_give_coordinates(lat, long, km).select_related('restaurant')

    @classmethod
    def get_all(cls):
        return cls.objects.filter(address_title="Restaurant Address")


class User(AbstractUser):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _("User Name"),
        max_length=150,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
    )
    email = models.EmailField(unique=True, null=False)
    mobile_number = PhoneNumberField(unique=True, help_text='Example: +919090909090')
    is_admin = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    profile_pic = models.ImageField(upload_to='user_images/', null=True)
    addresses = models.ManyToManyField(Address, related_name='user', through='UserAddress')
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'mobile_number']

    objects = UserManager()

    class Meta:
        ordering = ['id']

    @classmethod
    def get_user_emails(cls):
        return cls.objects.values_list('email', flat=True)

    @classmethod
    def is_active_user(cls, email):
        return cls.objects.filter(email=email, is_active=True).exists()

    @classmethod
    def is_blocked_user(cls, email):
        return cls.objects.filter(email=email, is_blocked=True).exists()

    @classmethod
    def is_inactive_user(cls, email):
        return cls.objects.filter(email=email, is_active=False).exists()

    @classmethod
    def get_total_customers(cls, queryset=None):
        if not queryset:
            queryset = cls.objects.all()
        return queryset.filter(is_admin=False, groups__name='customer')

    @classmethod
    def get_total_customers_count(cls, queryset=None):
        return cls.get_total_customers(queryset).count()

    @classmethod
    def get_blocked_customers(cls, queryset=None):
        if not queryset:
            queryset = cls.objects.all()
        return queryset.filter(is_admin=False, is_blocked=True, groups__name='customer')

    @classmethod
    def get_blocked_customers_count(cls, queryset=None):
        return cls.get_blocked_customers(queryset).count()

    @classmethod
    def get_active_customers(cls, queryset=None):
        if not queryset:
            queryset = cls.objects.all()
        return queryset.filter(
            is_admin=False,
            is_blocked=False,
            is_active=True,
            groups__name='customer'
        )

    @classmethod
    def get_active_customers_count(cls, queryset=None):
        return cls.get_active_customers(queryset).count()

    @classmethod
    def get_inactive_customers(cls, queryset=None):
        if not queryset:
            queryset = cls.objects.all()
        return queryset.filter(
            is_admin=False,
            is_blocked=False,
            is_active=False,
            groups__name='customer'
        )

    @classmethod
    def get_inactive_customers_count(cls, queryset=None):
        return cls.get_inactive_customers(queryset).count()

    @classmethod
    def get_total_agents(cls, queryset=None):
        if not queryset:
            queryset = cls.objects.all()
        return queryset.filter(
            is_admin=False,
            groups__name='delivery_agent'
        ).exclude(document__application_status='rejected')

    @classmethod
    def get_total_agents_having_cash(cls, queryset=None):
        if not queryset:
            queryset = cls.objects.all()
        return cls.get_total_agents(queryset=queryset).filter(
            agent_cash__deposit=False
        )

    @classmethod
    def get_unique_users(cls, queryset=None):
        if not queryset:
            queryset = cls.objects.all()
        return queryset.distinct('id')

    @classmethod
    def get_total_agents_having_cash_count(cls, queryset=None):
        return cls.get_unique_users(queryset=cls.get_total_agents_having_cash(queryset)).count()

    @classmethod
    def get_total_agents_count(cls, queryset=None):
        return cls.get_total_agents(queryset).count()

    @classmethod
    def get_unverified_agents(cls, queryset=None):
        if not queryset:
            queryset = cls.objects.all()
        return queryset.filter(
            is_admin=False,
            document__is_verified=False,
            groups__name='delivery_agent',
            is_blocked=False,
            document__application_status='pending',
        )

    @classmethod
    def is_unverified_agent(cls, pk, queryset=None):
        return cls.get_unverified_agents(queryset).filter(id=pk).first()

    @classmethod
    def get_unverified_agents_count(cls, queryset=None):
        return cls.get_unverified_agents(queryset).count()

    @classmethod
    def get_blocked_agents(cls, queryset=None):
        if not queryset:
            queryset = cls.objects.all()
        return queryset.filter(
            is_admin=False,
            is_blocked=True,
            groups__name='delivery_agent'
        )

    @classmethod
    def get_blocked_agents_count(cls, queryset=None):
        return cls.get_blocked_agents(queryset).count()

    @classmethod
    def get_active_agents(cls, queryset=None):
        if not queryset:
            queryset = cls.objects.all()
        return queryset.filter(
            is_admin=False,
            is_blocked=False,
            is_active=True,
            document__is_verified=True,
            groups__name='delivery_agent'
        )

    @classmethod
    def get_active_agents_count(cls, queryset=None):
        return cls.get_active_agents(queryset).count()

    @classmethod
    def get_agent_with_user_status(cls, user_status, queryset=None):
        is_verified = [False, True, True] if 'verified' in user_status else [None, None, None]
        is_unverified = [False, True, False] if 'unverified' in user_status else [None, None, None]
        is_blocked = True if 'blocked' in user_status else None

        if not queryset:
            queryset = cls.get_total_agents()

        return queryset.filter(
            (Q(is_blocked=is_verified[0]) & Q(is_active=is_verified[1]) & Q(document__is_verified=is_verified[2])) |
            (
                    Q(is_blocked=is_unverified[0]) &
                    Q(is_active=is_unverified[1]) &
                    Q(document__is_verified=is_unverified[2]) &
                    Q(document__application_status='pending')
            ) |
            (Q(is_blocked=is_blocked))
        )

    @classmethod
    def get_agent_with_search_params(cls, params, queryset=None):
        agent_id = None
        with contextlib.suppress(ValueError):
            agent_id = int(params)

        if not queryset:
            queryset = cls.get_total_agents()

        return queryset.filter(
            Q(email__icontains=params) | Q(username__icontains=params) | Q(id=agent_id)
        )

    @classmethod
    def get_users_with_user_status(cls, user_status, queryset=None):
        is_active = [False, True] if 'active' in user_status else [None, None]
        is_inactive = [False, False] if 'inactive' in user_status else [None, None]
        is_blocked = True if 'blocked' in user_status else None

        if not queryset:
            queryset = cls.get_total_customers()

        return queryset.filter(
            (Q(is_blocked=is_active[0]) & Q(is_active=is_active[1])) |
            (Q(is_blocked=is_inactive[0]) & Q(is_active=is_inactive[1])) |
            (Q(is_blocked=is_blocked))
        )

    @classmethod
    def get_user_from_id(cls, pk, queryset=None):
        if queryset:
            if user := queryset.filter(id=pk).first():
                return user
            raise Http404(f"No {queryset.model._meta.object_name} matches the given query.")

        return get_object_or_404(cls, id=pk)

    @classmethod
    def get_object_from_pk(cls, pk):
        return cls.objects.filter(id=pk).first()

    @classmethod
    def get_user_from_email(cls, email):
        return cls.objects.get(email=email)

    @classmethod
    def get_orders_from_user_id(cls, pk, queryset=None):
        return cls.get_user_from_id(pk=pk, queryset=queryset).agent_cash.filter(deposit=False)

    def get_social_auth_from_provider(self, provider):
        with contextlib.suppress(UserSocialAuth.DoesNotExist):
            return self.social_auth.get(provider=provider)

    def can_disconnect(self):
        return self.social_auth.count() > 1 or self.has_usable_password()

    def get_profile_pic(self):
        if self.profile_pic:
            return self.profile_pic.url

    def delete_user(self):
        self.is_active = False
        self.save()

    def get_activation_code(self):
        code = uuid.uuid4()

        act = Activation()
        act.code = code
        act.user = self
        act.save()

        return code
    @classmethod
    def get_user_address(cls,user_id=None, user=None):
        """
        :params user_id: user's id
        :params user: user object
        :returns: user_object , user's address. user's address lat, user's address long
        """
        if not user:
            user = cls.objects.filter(pk=user_id).first()
        user_address_obj = user.addresses.first()
        user_address = str(user_address_obj)
        user_address_long = user_address_obj.long
        user_address_lat = user_address_obj.lat
        return user, user_address_obj,user_address, user_address_lat, user_address_long

    def __str__(self):
        return self.email


class Activation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=36, unique=True)
    email = models.EmailField(blank=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'{self.user} - {self.code}'

    def is_valid(self):
        buffer = int(settings.BUFFER_TIME)
        return self.created_at + datetime.timedelta(seconds=buffer) >= timezone.now()

    def activate(self):
        user = self.user
        user.is_active = True
        user.save()

        Activation.objects.filter(user=self.user).delete()


class UserAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)

    class Meta:
        ordering = ['id']
