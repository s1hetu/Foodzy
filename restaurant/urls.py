from django.urls import path


from .views import (RestaurantPanel, AddItem, UpdateItem, RegisterRestaurant, AddRestaurant, RestaurantMenu,
                    DetailOrder, ViewOrders, ViewReviews, OwnerPanel,
                    UpdateRestaurantAcceptingOrderStatus, RestaurantStatusView, RestaurantEarningListView, AddGalleryImage, ViewGalleryImage)


urlpatterns = [
    path("restaurant_admin/", RestaurantPanel.as_view(), name="restaurant-admin"),
    path("owner_admin/<int:pk>/", OwnerPanel.as_view(), name="owner-admin"),
    path("add_item/<int:pk>/", AddItem.as_view(), name="add-item"),
    path("update_item/<int:pk>/", UpdateItem.as_view(), name="update-item"),
    path("register/", RegisterRestaurant.as_view(), name="register-restaurant"),
    path("add_restaurant/", AddRestaurant.as_view(), name="add-restaurant"),
    path("restaurant_menu/<int:pk>/", RestaurantMenu.as_view(), name="restaurant-menu"),
    path("detail_order/<int:pk>/", DetailOrder.as_view(), name="detail-order"),
    path("view_orders/<int:pk>/", ViewOrders.as_view(), name="view-orders"),
    path("view_reviews/<int:pk>/", ViewReviews.as_view(), name="view-reviews"),
    path("restaurant_status/<int:pk>/", UpdateRestaurantAcceptingOrderStatus.as_view(), name="restaurant-status"),
    path("<int:restaurant_id>/status/", RestaurantStatusView.as_view(), name="restaurant-verification-status"),
    path("add_gallery_image/<int:pk>/", AddGalleryImage.as_view(), name="add-gallery-image"),
    path("view_gallery/<int:pk>/", ViewGalleryImage.as_view(), name="view_restaurant_gallery"),
    path("view_gallery/", ViewGalleryImage.as_view(), name="view_gallery"),
    path("earning/<int:pk>/", RestaurantEarningListView.as_view(), name="restaurant-earning"),

]
