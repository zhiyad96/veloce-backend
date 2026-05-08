from rest_framework.serializers import ModelSerializer
from .models import Order, OrderItem
from rest_framework import serializers
from accounts. models import Address



class AddressSerializer(ModelSerializer):

    class Meta:
        model = Address
        fields = "__all__"
        read_only_fields = ["user"]


class OrderItemSerializer(ModelSerializer):

    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_name", "quantity", "price"]


class OrderSerializer(ModelSerializer):

    items = OrderItemSerializer(many=True, read_only=True)
    address = AddressSerializer(read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "status",
            "checkout_mode",
            "total_price",
            "payment_id",
            "razorpay_order_id",
            "created_at",
            "items",
            "address",
            "username",
        ]
