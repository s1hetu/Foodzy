from django.contrib import admin

from .models import Restaurant, Categories, Items, Documents, RatingsAndReviews, RestaurantGallery

admin.site.register(Restaurant)
admin.site.register(Categories)
admin.site.register(Items)
admin.site.register(Documents)
admin.site.register(RatingsAndReviews)
admin.site.register(RestaurantGallery)
