from django.urls import path

from .views import CreateCartItemAPIView, IncreaseQuantityOfCartItemAPIView, DeleteCartItemAPIView, \
    DecreaseQuantityOfCartItemAPIView

urlpatterns = [
    path('create-item/', CreateCartItemAPIView.as_view(), name="create-cart-item"),
    path('increase-item-quantity/<int:pk>/', IncreaseQuantityOfCartItemAPIView.as_view(),
         name="increase-cart-item-quantity"),
    path('decrease-item-quantity/<int:pk>/', DecreaseQuantityOfCartItemAPIView.as_view(),
         name="decrease-cart-item-quantity"),
    path('delete-item/<int:pk>/', DeleteCartItemAPIView.as_view(), name="delete-cart-item"),
]
