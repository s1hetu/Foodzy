from decimal import Decimal
from unittest.mock import Mock

from accounts.models import User
from orders.models import Order
from restaurant.models import Categories, RestaurantGallery, RatingsAndReviews, Items, Restaurant, Documents
from tests.constants import (
    COMMON_RESTAURANT4, COMMON_RESTAURANT3, COMMON_RESTAURANT5,
    COMMON_RESTAURANT6, COMMON_RESTAURANT9, COMMON_AGENT4,
    COMMON_CUSTOMER1
)


class TestCategoriesModel:

    def test_categories_data(self):
        category = Categories.objects.get(id=1)
        assert category.id == 1
        assert category.name == "Rice"
        assert str(category) == "Rice"

    def test_get_categories(self):
        assert list(Categories.get_categories().values_list('id', flat=True)) == [1, 2, 3, 4, 5, 6]


class TestRestaurantModel:
    restaurant4 = COMMON_RESTAURANT4
    total_restaurant = COMMON_RESTAURANT3, restaurant4, COMMON_RESTAURANT5, COMMON_RESTAURANT6, COMMON_RESTAURANT9

    def test_restaurant_data(self, load_data):
        load_data(self.restaurant4)
        restaurant = Restaurant.objects.get(id=4)
        assert restaurant.id == 4
        assert restaurant.name == "res4 Name"
        assert not restaurant.is_blocked
        assert restaurant.is_verified
        assert restaurant.application_status == "approved"
        assert not restaurant.is_accepting_orders
        assert restaurant.owner.email == "res4@test.com"
        assert restaurant.address.landmark == "Landmark-res4"
        assert str(restaurant) == f"Restaurant-{restaurant.name} | Owner-{restaurant.owner}"

    def test_get_total_restaurants(self, load_data):
        load_data(self.total_restaurant)
        assert list(Restaurant.get_total_restaurants().values_list('id', flat=True)) == [3, 4, 5, 6, 9]

    def test_get_total_restaurants_count(self, load_data):
        load_data(self.total_restaurant)
        assert Restaurant.get_total_restaurants_count() == 5

    def test_get_blocked_restaurants(self, load_data):
        load_data(self.total_restaurant)
        assert list(Restaurant.get_blocked_restaurants().values_list('id', flat=True)) == [5, 9]

    def test_get_blocked_restaurants_count(self, load_data):
        load_data(self.total_restaurant)
        assert Restaurant.get_blocked_restaurants_count() == 2

    def test_get_active_restaurants(self, load_data):
        load_data(self.total_restaurant)
        assert list(Restaurant.get_active_restaurants().values_list('id', flat=True)) == [4, 6]

    def test_get_active_restaurants_count(self, load_data):
        load_data(self.total_restaurant)
        assert Restaurant.get_active_restaurants_count() == 2

    def test_get_restaurant_applications(self, load_data):
        load_data(self.total_restaurant)
        assert list(Restaurant.get_restaurant_applications().values_list('id', flat=True)) == [3]

    def test_get_restaurant_applications_count(self, load_data):
        load_data(self.total_restaurant)
        assert Restaurant.get_restaurant_applications_count() == 1

    def test_get_all_restaurants(self, load_data):
        load_data(self.total_restaurant)
        assert list(Restaurant.get_all_restaurants().values_list('id', flat=True)) == [3, 4, 5, 6, 9]

    def test_get_restaurant_with_search_params_val(self, load_data):
        load_data(self.total_restaurant)
        assert list(Restaurant.get_restaurant_with_search_params(params="res",
                                                                 queryset=Restaurant.get_all_restaurants().values_list(
                                                                     'id', flat=True))) == [3, 4, 5, 6, 9]

    def test_get_restaurant_with_search_params_int(self, load_data):
        load_data(self.total_restaurant)
        assert list(Restaurant.get_restaurant_with_search_params(params=3,
                                                                 queryset=Restaurant.get_all_restaurants().values_list(
                                                                     'id', flat=True))) == [3]

    def test_get_restaurant_with_restaurant_status_ver(self, load_data):
        load_data(self.total_restaurant)
        assert list(Restaurant.get_restaurant_with_restaurant_status(restaurant_status='verified',
                                                                     queryset=Restaurant.get_all_restaurants().values_list(
                                                                         'id', flat=True))) == [4, 6]

    def test_get_restaurant_with_restaurant_status_unver(self, load_data):
        load_data(self.total_restaurant)
        assert list(Restaurant.get_restaurant_with_restaurant_status(restaurant_status='unverified',
                                                                     queryset=Restaurant.get_all_restaurants().values_list(
                                                                         'id', flat=True))) == [3, 4, 6]

    def test_get_restaurant_from_id(self, load_data):
        load_data(self.restaurant4)
        assert Restaurant.get_restaurant_from_id(pk=4).id == 4
        assert Restaurant.get_restaurant_from_id(pk=4, queryset=Restaurant.objects.all()).id == 4

    def test_get_object_from_pk(self, load_data):
        load_data(self.restaurant4)
        assert Restaurant.get_object_from_pk(pk=4).id == 4

    def test_get_restaurants_from_user(self, load_data):
        load_data(self.restaurant4)
        assert (list(
            Restaurant.get_restaurants_from_user(user=User.objects.get(id=13)).values_list('id', flat=True))) == [4]

    def test_get_restaurant_address(self, load_data):
        load_data(self.restaurant4)
        result = Restaurant.get_restaurant_address(restaurant_id=Restaurant.objects.get(id=4).id)
        assert result[0].id == 4
        assert result[1] == 'Address1-res4,Address2-res4, Street-res4, Landmark-res4, Ahmedabad, 123456, Gujarat'
        assert str(result[2]) == '23.021981'
        assert result[3] == Decimal('72.593775')

    def test_is_valid_restaurant_application_user(self, load_data):
        load_data(COMMON_RESTAURANT3)
        assert Restaurant.is_valid_restaurant_application_user(pk=Restaurant.objects.get(id=3).id).id == 3


class TestDocumentsModel:
    restaurant4 = COMMON_RESTAURANT4

    def test_documents_data(self, load_data):
        load_data(self.restaurant4)
        documents = Documents.objects.get(id=1)
        assert documents.id == 1
        assert documents.restaurant.name == "res4 Name"
        assert documents.restaurant.id == 4
        assert documents.account_no == "5555555555555"
        assert documents.ifsc_code == "ABCD0123456"
        assert documents.razorpay_contact_id == "cont_Ku8XFtFW4TzfOz"
        assert documents.razorpay_fund_account_id == "fa_Ku8XGIEcWjkJAt"
        assert documents.pan_card == "pan_cards/Screenshot_from_2022-12-15_11-43-54_3C6tW3O.png"
        assert documents.gst_certificate == "gst_certificates/Screenshot_from_2022-12-09_10-17-03.png"
        assert documents.fssai_certificate == "fssai_certificates/Screenshot_from_2022-12-12_12-52-50_Y06WKTg.png"
        assert str(documents) == f"{documents.restaurant}-Restaurant Documents"


class TestItemsModel:
    restaurant6 = COMMON_RESTAURANT6

    def test_items_data(self, load_data):
        load_data(self.restaurant6)
        item = Items.objects.get(id=1)
        assert item.id == 1
        assert item.restaurant.name == "res6 Name"
        assert item.restaurant.id == 6
        assert item.category.id == 1
        assert item.category.name == "Rice"
        assert item.name == "RiceName"
        assert item.price == 50.00
        assert item.discount == 10.00
        assert item.number_of_purchases == 0
        assert item.available_quantity == 30
        assert item.quantity == 1
        assert item.unit == "plate"
        assert item.description == "This is rice."
        assert item.image == "item_images/Screenshot_from_2022-12-12_12-52-50_3RXZ4YQ.png"
        assert str(item) == f"{item.name} | {item.restaurant}"

    def test_decrease_item_quantity(self, load_data):
        load_data(self.restaurant6)
        item = Items.objects.get(id=2)
        order_item = {'quantity': 2}
        assert item.decrease_item_quantity(order_item) == item

    def test_calculate_discount(self, load_data):
        load_data(self.restaurant6)
        item = Items.objects.get(id=1)
        assert item.calculate_discount() == 45

    def test_get_item(self, load_data):
        load_data(self.restaurant6)
        assert Items.get_item(pk=1).id == 1

    def test_filter_by_near_by_valid_restaurant(self, load_data):
        load_data(self.restaurant6)
        mock_request = Mock()
        restaurant = Restaurant.objects.get(id=6)
        owner = restaurant.owner
        mock_request.user = owner
        mock_request.user.addresses.add(restaurant.address)
        assert list(
            Items.filter_by_near_by_valid_restaurant(queryset=Items.objects.all(), request=mock_request).values_list(
                'id', flat=True)) == [1, 2, 3]

    def test_get_all_trending_items(self, load_data):
        load_data(self.restaurant6)
        mock_request = Mock()
        restaurant = Restaurant.objects.get(id=6)
        owner = restaurant.owner
        mock_request.user = owner
        mock_request.user.addresses.add(restaurant.address)
        assert list(Items.get_all_trending_items(request=mock_request).values_list('id', flat=True)) == [1, 2, 3]

    def test_get_all_items(self, load_data):
        load_data(self.restaurant6)
        mock_request = Mock()
        restaurant = Restaurant.objects.get(id=6)
        owner = restaurant.owner
        mock_request.user = owner
        mock_request.user.addresses.add(restaurant.address)
        assert list(Items.get_all_items(request=mock_request).values_list('id', flat=True)) == [1, 2, 3]

    def test_get_searched_items(self, load_data):
        load_data(self.restaurant6)
        assert list(Items.get_searched_items(searched_param="a").values_list('id', flat=True)) == [1, 2, 3]

    def test_get_items_from_restaurant(self, load_data):
        load_data(self.restaurant6)
        assert list(
            Items.get_items_from_restaurant(restaurant=Restaurant.objects.get(id=6)).values_list('id', flat=True)) == [
                   1, 2, 3]

    def test_get_restaurant_items_count(self, load_data):
        load_data(self.restaurant6)
        assert Items.get_restaurant_items_count(restaurant=Restaurant.objects.get(id=6)) == 3

    def test_get_restaurant_category_serving_count(self, load_data):
        load_data(self.restaurant6)
        assert Items.get_restaurant_category_serving_count(restaurant=Restaurant.objects.get(id=6)) == 3


#

class TestRestaurantGalleryModel:
    restaurant6 = COMMON_RESTAURANT6

    def test_restaurantgallery_data(self, load_data):
        load_data(self.restaurant6)
        restaurant = Restaurant.objects.get(id=6)
        gallery = RestaurantGallery.objects.get(id=1)
        assert gallery.restaurant.name == "res6 Name"
        assert gallery.image == "restaurant_gallery_images/default.jpg"
        assert str(gallery) == f"Restaurant-{restaurant} | Gallery"

    def test_get_restaurant_gallery_image_by_id(self, load_data):
        load_data(self.restaurant6)
        restaurant_gallery = RestaurantGallery.objects.get(id=1)
        assert list(
            restaurant_gallery.get_restaurant_gallery_image_by_id(restaurant_id=6).values_list('id', flat=True)) == [1]

    def test_get_restaurant_gallery_images(self, load_data):
        load_data(self.restaurant6)
        assert list(RestaurantGallery.get_restaurant_gallery_images().values_list('id', flat=True)) == [1]


class TestRatingsAndReviewsModel:
    order_data = COMMON_RESTAURANT6, COMMON_CUSTOMER1, \
        COMMON_AGENT4, 'orders/three_delivered_and_one_picked_order_for_same_restaurants.json'

    def test_ratings_and_reviews_data(self, load_data):
        load_data(self.order_data)
        ratings_reviews = RatingsAndReviews.objects.get(id=1)
        assert ratings_reviews.id == 1
        assert ratings_reviews.ratings == 2.0
        assert ratings_reviews.restaurant.id == 6
        assert ratings_reviews.order.id == 1
        assert ratings_reviews.reviews == "Good Restaurant Review 1"
        assert str(ratings_reviews) == f"Restaurant-{ratings_reviews.restaurant.name} User-{ratings_reviews.order.user}"

    def test_average_rating(self, load_data):
        load_data(self.order_data)
        ratings_reviews = RatingsAndReviews.objects.get(id=1)
        assert ratings_reviews.average_rating() == 3.7

    def test_get_restaurant_ratings_reviews(self, load_data):
        load_data(self.order_data)
        restaurant6 = Restaurant.objects.get(id=6)
        assert (list(
            RatingsAndReviews.get_restaurant_ratings_reviews(restaurant=Restaurant.objects.get(id=6)).values_list('id',
                                                                                                                  flat=True))) == [
                   1, 2, 3]

    def test_get_restaurant_ratings_reviews_count(self, load_data):
        load_data(self.order_data)
        assert RatingsAndReviews.get_restaurant_ratings_reviews_count(restaurant=Restaurant.objects.get(id=6)) == 3

    def test_get_or_create_rating_reviews_by_order_and_restaurant(self, load_data):
        load_data(self.order_data)

        assert RatingsAndReviews.get_or_create_rating_reviews_by_order_and_restaurant(order=Order.objects.get(id=1))[
                   0].id == 1
