from django.urls import reverse, resolve

from restaurant.views import (
    RestaurantPanel, ViewGalleryImage, RestaurantEarningListView, AddGalleryImage,
    RestaurantStatusView, UpdateRestaurantAcceptingOrderStatus, ViewReviews, ViewOrders,
    DetailOrder, RestaurantMenu, AddRestaurant, RegisterRestaurant, UpdateItem, OwnerPanel, AddItem
)


class TestRestaurantUrls:

    def test_home_url(self):
        restaurant_admin_url = reverse('restaurant-admin')
        assert resolve(restaurant_admin_url).func.view_class == RestaurantPanel

    def test_owner_admin_url(self):
        owner_admin_url = reverse('owner-admin', kwargs={'pk': 1})
        assert resolve(owner_admin_url).func.view_class == OwnerPanel

    def test_add_item_url(self):
        add_item_url = reverse('add-item', kwargs={'pk': 1})
        assert resolve(add_item_url).func.view_class == AddItem

    def test_update_item_url(self):
        update_item_url = reverse('update-item', kwargs={'pk': 1})
        assert resolve(update_item_url).func.view_class == UpdateItem

    def test_register_restaurant_url(self):
        register_restaurant_url = reverse('register-restaurant')
        assert resolve(register_restaurant_url).func.view_class == RegisterRestaurant

    def test_add_restaurant_url(self):
        add_restaurant_url = reverse('add-restaurant')
        assert resolve(add_restaurant_url).func.view_class == AddRestaurant

    def test_restaurant_menu_url(self):
        restaurant_menu_url = reverse('restaurant-menu', kwargs={'pk': 1})
        assert resolve(restaurant_menu_url).func.view_class == RestaurantMenu

    def test_detail_order_url(self):
        detail_order_url = reverse('detail-order', kwargs={'pk': 1})
        assert resolve(detail_order_url).func.view_class == DetailOrder

    def test_view_orders_url(self):
        view_orders_url = reverse('view-orders', kwargs={'pk': 1})
        assert resolve(view_orders_url).func.view_class == ViewOrders

    def test_view_reviews_url(self):
        view_reviews_url = reverse('view-reviews', kwargs={'pk': 1})
        assert resolve(view_reviews_url).func.view_class == ViewReviews

    def test_restaurant_status_url(self):
        update_restaurant_status = reverse('restaurant-status', kwargs={'pk': 1})
        assert resolve(update_restaurant_status).func.view_class == UpdateRestaurantAcceptingOrderStatus

    def test_restaurant_verification_status_url(self):
        restaurant_verification_status_url = reverse('restaurant-verification-status', kwargs={'restaurant_id': 1})
        assert resolve(restaurant_verification_status_url).func.view_class == RestaurantStatusView

    def test_add_gallery_image_url(self):
        add_gallery_image = reverse('add-gallery-image', kwargs={'pk': 1})
        assert resolve(add_gallery_image).func.view_class == AddGalleryImage

    def test_view_gallery_url(self):
        view_gallery_url = reverse('view_gallery')
        assert resolve(view_gallery_url).func.view_class == ViewGalleryImage

    def test_view_restaurant_gallery_url(self):
        view_restaurant_gallery_url = reverse('view_restaurant_gallery', kwargs={'pk': 1})
        assert resolve(view_restaurant_gallery_url).func.view_class == ViewGalleryImage

    def test_restaurant_earning_url(self):
        restaurant_earning_url = reverse('restaurant-earning', kwargs={'pk': 1})
        assert resolve(restaurant_earning_url).func.view_class == RestaurantEarningListView
