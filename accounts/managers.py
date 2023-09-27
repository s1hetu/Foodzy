from decimal import Decimal

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import Group
from django.db import models
from django.db.models import F
from django.db.models.functions import Power, Sin, Cos, ATan2, Sqrt, Radians
from django.utils.translation import gettext_lazy as _

from FDA.constants import USER_TYPES
from accounts.utils import add_permissions_to_group


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, user_type='customer', **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        if user_type not in USER_TYPES:
            raise ValueError(_(f'{user_type} is not valid.'))

        user_type_group, created = Group.objects.get_or_create(name=user_type)

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()

        user_type_group.user_set.add(user)
        # uncomment below to add permissions only on create user
        # if created:
        add_permissions_to_group(group=user_type_group)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_admin') is not True:
            raise ValueError(_('Superuser must have is_admin=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, user_type='admin', **extra_fields)

    def create_restaurant_owner(self, email, password, **extra_fields):
        return self.create_user(email, password, user_type='restaurant_owner', **extra_fields)

    def create_delivery_agent(self, email, password, **extra_fields):
        return self.create_user(email, password, user_type='delivery_agent', **extra_fields)


class AddressQuerySet(models.QuerySet):

    def locations_near_give_coordinates(self, current_lat, current_long, km=10):
        current_lat = Decimal(current_lat)
        current_long = Decimal(current_long)

        # Using the Haversine formula (Great Circle Formula)
        dlat = Radians(F('lat') - current_lat)
        dlong = Radians(F('long') - current_long)
        a = (Power(Sin(dlat / 2), 2) + Cos(Radians(current_lat))
             * Cos(Radians(F('lat'))) * Power(Sin(dlong / 2), 2)
             )
        c = 2 * ATan2(Sqrt(a), Sqrt(1 - a))
        d = 6371 * c  # 6371 is radius of the earth

        return self.annotate(distance=d).order_by('distance').filter(distance__lt=km)


class AddressManager(models.Manager):
    def get_queryset(self):
        return AddressQuerySet(self.model, using=self._db)
