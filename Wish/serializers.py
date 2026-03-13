from rest_framework.serializers import ModelSerializer
from .models import Wishlist, WishlistItem
from rest_framework import serializers


class WishlistItemSerializer(ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    price = serializers.DecimalField(source="product.price", max_digits=10, decimal_places=2, read_only=True)

    image = serializers.SerializerMethodField()

    class Meta:
        model = WishlistItem
        fields = ["id", "product", "product_name", "price", "image"]

    def get_image(self, obj):
        img = obj.product.images.first()
        if img:
            return img.image.url
        return None