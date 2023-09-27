import contextlib

from django.core.validators import MaxValueValidator, MinValueValidator, MaxLengthValidator, MinLengthValidator
from django.db import models
from django.db.models import Q, Case, When, OuterRef, BooleanField
from django.http import Http404

from FDA.constants import (
    RESTAURANT_ITEM_MODEL_UNIT_CHOICE, RESTAURANT_RESTAURANT_MODEL_STATUS_CHOICES,
    RESTAURANT_RESTAURANT_MODEL_DEFAULT_IMAGE, RESTAURANT_RESTAURANT_MODEL_IMAGE_UPLOAD_TO_PATH,
    RESTAURANT_DOCUMENTS_MODEL_PAN_CARD_UPLOAD_TO_PATH, RESTAURANT_DOCUMENTS_MODEL_GST_CERTIFICATES_UPLOAD_TO_PATH,
    RESTAURANT_DOCUMENTS_MODEL_FSSAI_CERTIFICATES_UPLOAD_TO_PATH, RESTAURANT_ITEMS_MODEL_DEFAULT_IMAGE,
    RESTAURANT_ITEMS_MODEL_IMAGE_UPLOAD_TO_PATH, RESTAURANT_GALLERY_MODEL_DEFAULT_IMAGE,
    RESTAURANT_GALLERY_MODEL_IMAGE_UPLOAD_TO_PATH
)
from accounts.models import User, Address
from restaurant.validators import validate_ifsc_code


class Restaurant(models.Model):
    """
        Stores a single restaurant, related to :model:`accounts.User`, :model:`accounts.Address`.
    """

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="restaurants")
    name = models.CharField(max_length=50)
    address = models.OneToOneField(Address, on_delete=models.SET_NULL, related_name="restaurant", null=True)
    is_verified = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    application_status = models.CharField(max_length=20, choices=RESTAURANT_RESTAURANT_MODEL_STATUS_CHOICES,
                                          default="pending")
    is_accepting_orders = models.BooleanField(default=False)
    ratings = models.FloatField(null=True, validators=[MinValueValidator(0.5), MaxValueValidator(5)], default=0)
    image = models.ImageField(default=RESTAURANT_RESTAURANT_MODEL_DEFAULT_IMAGE,
                              upload_to=RESTAURANT_RESTAURANT_MODEL_IMAGE_UPLOAD_TO_PATH)

    class Meta:
        permissions = [('change_is_accepting_orders_on_restaurant', 'Can change is accepting orders in restaurant'), ]
        ordering = ['id']

    @classmethod
    def get_total_restaurants(cls, queryset=None):
        if not queryset:
            queryset = cls.objects.all()
        return queryset.filter(owner__groups__name='restaurant_owner').exclude(application_status='rejected')

    @classmethod
    def get_total_restaurants_count(cls, queryset=None):
        return cls.get_total_restaurants(queryset).count()

    @classmethod
    def get_blocked_restaurants(cls, queryset=None):
        if not queryset:
            queryset = cls.objects.all()
        return queryset.filter(is_verified=True, is_blocked=True)

    @classmethod
    def get_blocked_restaurants_count(cls, queryset=None):
        return cls.get_blocked_restaurants(queryset).count()

    @classmethod
    def get_active_restaurants(cls, queryset=None):
        if not queryset:
            queryset = cls.objects.all()
        return queryset.filter(is_verified=True, is_blocked=False)

    @classmethod
    def get_active_restaurants_count(cls, queryset=None):
        return cls.get_active_restaurants(queryset).count()

    @classmethod
    def get_restaurant_applications(cls, queryset=None):
        if not queryset:
            queryset = cls.objects.all()
        return queryset.filter(owner__groups__name='restaurant_owner', is_verified=False, is_blocked=False,
                               application_status='pending')

    @classmethod
    def is_valid_restaurant_application_user(cls, pk, queryset=None):
        return cls.get_restaurant_applications(queryset).filter(id=pk).first()

    @classmethod
    def get_restaurant_applications_count(cls, queryset=None):
        return cls.get_restaurant_applications(queryset).count()

    @classmethod
    def get_restaurant_with_search_params(cls, params, queryset=None):
        search_restaurant_id = None
        with contextlib.suppress(ValueError):
            search_restaurant_id = int(params)

        return queryset.filter(
            Q(name__icontains=params) | Q(owner__username__icontains=params) | Q(id=search_restaurant_id))

    @classmethod
    def get_restaurant_with_restaurant_status(cls, restaurant_status, queryset=None):
        is_verified = [False, True] if 'verified' in restaurant_status else [None, None]
        is_unverified = [False, False] if 'unverified' in restaurant_status else [None, None]
        is_blocked = True if 'blocked' in restaurant_status else None

        return queryset.filter((Q(is_blocked=is_verified[0]) & Q(is_verified=is_verified[1])) | (
                Q(is_blocked=is_unverified[0]) & Q(is_verified=is_unverified[1]) & Q(application_status='pending')) | (
                                   Q(is_blocked=is_blocked)))

    @classmethod
    def get_restaurant_from_id(cls, pk, queryset=None):
        if queryset:
            if restaurant := queryset.filter(id=pk).first():
                return restaurant
            raise Http404
        return cls.objects.select_related('owner', 'address__city', 'address__state').filter(pk=pk).first()

    @classmethod
    def get_object_from_pk(cls, pk, queryset=None):
        return queryset.filter(pk=pk).first() if queryset else cls.objects.filter(pk=pk).first()

    @classmethod
    def get_restaurants_from_user(cls, user, queryset=None):
        if not queryset:
            queryset = cls.objects.all()
        return queryset.filter(owner=user)

    @classmethod
    def get_all_restaurants(cls):
        return cls.objects.all()

    @classmethod
    def get_restaurant_address(cls, restaurant_id):
        """
        :params restaurant_id: restaurant's id
        :returns: restaurant_object , restaurant's address. restaurant's address lat, restaurant's address long
        """

        restaurant_obj = cls.get_restaurant_from_id(pk=restaurant_id)
        restaurant_address_obj = restaurant_obj.address
        restaurant_address = str(restaurant_address_obj)
        restaurant_address_lat = restaurant_address_obj.lat
        restaurant_address_long = restaurant_address_obj.long
        return restaurant_obj, restaurant_address, restaurant_address_lat, restaurant_address_long

    def __str__(self):
        return f"Restaurant-{self.name} | Owner-{self.owner}"


class Documents(models.Model):
    restaurant = models.OneToOneField(Restaurant, on_delete=models.SET_NULL, related_name="documents", null=True)
    pan_card = models.ImageField(upload_to=RESTAURANT_DOCUMENTS_MODEL_PAN_CARD_UPLOAD_TO_PATH)
    gst_certificate = models.ImageField(upload_to=RESTAURANT_DOCUMENTS_MODEL_GST_CERTIFICATES_UPLOAD_TO_PATH)
    fssai_certificate = models.ImageField(upload_to=RESTAURANT_DOCUMENTS_MODEL_FSSAI_CERTIFICATES_UPLOAD_TO_PATH)
    account_no = models.CharField(validators=[MinLengthValidator(8), MaxLengthValidator(18)], max_length=18)
    ifsc_code = models.CharField(max_length=11, validators=[validate_ifsc_code])
    razorpay_contact_id = models.CharField(max_length=40, null=True, blank=True)
    razorpay_fund_account_id = models.CharField(max_length=40, null=True, blank=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.restaurant}-Restaurant Documents"


class RatingsAndReviews(models.Model):
    ratings = models.FloatField(null=True, validators=[MinValueValidator(0.5), MaxValueValidator(5)])
    reviews = models.CharField(max_length=200, null=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="ratings_and_reviews")
    order = models.OneToOneField('orders.order', on_delete=models.CASCADE)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"Restaurant-{self.restaurant.name} User-{self.order.user}"

    def average_rating(self):
        if self.ratings:
            average_rating = RatingsAndReviews.objects.filter(restaurant=self.restaurant,
                                                              ratings__isnull=False).aggregate(
                avg_rating=models.Avg('ratings'))
            return round(average_rating['avg_rating'], 1)
        return None

    def save(self, **kwargs):
        super(RatingsAndReviews, self).save(kwargs)

        restaurant = self.restaurant
        restaurant.ratings = self.average_rating()
        restaurant.save()

    @classmethod
    def get_restaurant_ratings_reviews(cls, restaurant, queryset=None):
        if not queryset:
            queryset = cls.objects.all()
        return queryset.filter(restaurant=restaurant)

    @classmethod
    def get_restaurant_ratings_reviews_count(cls, restaurant):
        return cls.get_restaurant_ratings_reviews(restaurant).count()

    @classmethod
    def get_or_create_rating_reviews_by_order_and_restaurant(cls, order):
        return cls.objects.get_or_create(order=order, restaurant=order.restaurant)


class Categories(models.Model):
    name = models.CharField(max_length=30, unique=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name

    @classmethod
    def get_categories(cls):
        return cls.objects.all()


class Items(models.Model):
    category = models.ForeignKey(Categories, on_delete=models.CASCADE, related_name="category_items")
    name = models.CharField(max_length=150)
    available_quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit = models.CharField(max_length=20, choices=RESTAURANT_ITEM_MODEL_UNIT_CHOICE, default="grams")
    price = models.DecimalField(max_digits=12, decimal_places=2, default=100, validators=[MinValueValidator(1)])
    description = models.CharField(max_length=1500)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.SET_NULL, related_name="restaurant_items", null=True)
    image = models.ImageField(default=RESTAURANT_ITEMS_MODEL_DEFAULT_IMAGE,
                              upload_to=RESTAURANT_ITEMS_MODEL_IMAGE_UPLOAD_TO_PATH)
    number_of_purchases = models.PositiveIntegerField(default=0)
    discount = models.DecimalField(max_digits=4, decimal_places=2, default=0,
                                   validators=[MinValueValidator(0), MaxValueValidator(99)])

    class Meta:
        ordering = ['id']

    def decrease_item_quantity(self, item):
        self.available_quantity -= item['quantity']
        self.save()
        return self

    def calculate_discount(self):
        return round(self.price - self.price * self.discount / 100, 2) if self.discount >= 0 else self.price

    def __str__(self):
        return f"{self.name} | {self.restaurant}"

    @classmethod
    def get_item(cls, pk, queryset=None):
        if not queryset:
            queryset = cls.objects.all()
        return queryset.filter(pk=pk).first()

    @staticmethod
    def filter_by_near_by_valid_restaurant(request, queryset):
        if request.user.is_authenticated:
            restaurant_addresses = Address.get_near_by_restaurants(request).values_list('id', flat=True)
        else:
            restaurant_addresses = Address.get_all().values_list('id', flat=True)

        return queryset.filter(restaurant__address_id__in=restaurant_addresses, restaurant__is_verified=True,
                               restaurant__is_blocked=False)

    @classmethod
    def get_all_trending_items(cls, request, queryset=None):
        if not queryset:
            queryset = cls.objects.all()

        queryset = cls.filter_by_near_by_valid_restaurant(request=request, queryset=queryset)
        return queryset.order_by('-number_of_purchases', 'id')[:5]

    @classmethod
    def get_all_items(cls, request, queryset=None):
        from carts.models import CartItems

        if not queryset:
            queryset = cls.objects.all()

        queryset = cls.filter_by_near_by_valid_restaurant(request=request, queryset=queryset)
        return queryset.filter(available_quantity__gt=0, restaurant__is_accepting_orders=True).annotate(in_cart=Case(
            When(id__in=CartItems.objects.filter(item_id=OuterRef('id'), cart__user_id=request.user.id).values(
                "item_id"), then=True), default=False, output_field=BooleanField()))

    @classmethod
    def get_searched_items(cls, searched_param, queryset=None):
        if not queryset:
            queryset = cls.objects.all()

        return queryset.filter(Q(name__icontains=searched_param) | Q(description__icontains=searched_param) | Q(
            category__name__icontains=searched_param) | Q(restaurant__name__icontains=searched_param)).order_by(
            'id').distinct()

    @classmethod
    def get_items_from_restaurant(cls, restaurant, queryset=None):
        if not queryset:
            queryset = cls.objects.all()
        return queryset.filter(restaurant=restaurant).select_related('restaurant')

    @classmethod
    def get_restaurant_items_count(cls, restaurant):
        return cls.get_items_from_restaurant(restaurant).count()

    @classmethod
    def get_restaurant_category_serving_count(cls, restaurant):
        return cls.get_items_from_restaurant(restaurant).distinct('id', 'category').count()


class RestaurantGallery(models.Model):
    image = models.ImageField(default=RESTAURANT_GALLERY_MODEL_DEFAULT_IMAGE,
                              upload_to=RESTAURANT_GALLERY_MODEL_IMAGE_UPLOAD_TO_PATH)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.SET_NULL, related_name='restaurant_gallery', null=True)

    class Meta:
        ordering = ['id']

    @classmethod
    def get_restaurant_gallery_image_by_id(cls, restaurant_id, queryset=None):
        if not queryset:
            queryset = cls.objects.all()
        return queryset.filter(restaurant__id=restaurant_id)

    @classmethod
    def get_restaurant_gallery_images(cls):
        return cls.objects.all()

    def __str__(self):
        return f"Restaurant-{self.restaurant} | Gallery"
