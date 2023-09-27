from rest_framework import serializers
from carts.models import CartItems, Cart


class CreateCartItemSerializer(serializers.ModelSerializer):
    """Used for saving new cart items into the :model:`carts.CartItems`.
    """

    class Meta:
        model = CartItems
        fields = ['cart', 'item', 'total']
        read_only_fields = ('total',)

    def validate(self, data):
        """Check validation on data.
        """
        if CartItems.objects.filter(item=data['item'], cart__user_id=self.context['request'].user.id).exists():
            raise serializers.ValidationError("Item already added to cart")
        return data

    def to_internal_value(self, data):
        """Overridden for saving cart_id in the data.
        """
        cart, _ = Cart.objects.get_or_create(user=self.context['request'].user)
        data = data.copy()
        data['cart'] = cart.id
        return super(CreateCartItemSerializer, self).to_internal_value(data)


class IncreaseQuantityOfCartItemSerializer(serializers.ModelSerializer):
    """Used for increasing cart items quantity for the :model:`carts.CartItems`.
    """
    cart_total = serializers.SerializerMethodField()

    class Meta:
        model = CartItems
        fields = ['quantity', 'total', 'cart_total']
        read_only_fields = ('total', 'cart_total')

    def get_cart_total(self, obj):
        return str(obj.cart.total)

    def to_internal_value(self, data):
        """Overridden for saving quantity in the data.
        """
        cart_item = CartItems.objects.filter(item_id=self.context['pk'],
                                             cart__user_id=self.context['request'].user.id).first()
        data = data.copy()
        data['quantity'] = cart_item.quantity + 1
        return super(IncreaseQuantityOfCartItemSerializer, self).to_internal_value(data)


class DecreaseQuantityOfCartItemSerializer(serializers.ModelSerializer):
    """Used for decreasing cart items quantity for the :model:`carts.CartItems`.
    """
    cart_total = serializers.SerializerMethodField()

    class Meta:
        model = CartItems
        fields = ['quantity', 'total', 'cart_total']
        read_only_fields = ('total', 'cart_total')

    def get_cart_total(self, obj):
        return str(obj.cart.total)

    def to_internal_value(self, data):
        """Overridden for saving quantity in the data.
        """
        cart_item = CartItems.objects.filter(item_id=self.context['pk'],
                                             cart__user_id=self.context['request'].user.id).first()
        data = data.copy()
        data['quantity'] = cart_item.quantity - 1
        return super(DecreaseQuantityOfCartItemSerializer, self).to_internal_value(data)
