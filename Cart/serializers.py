from rest_framework.serializers import ModelSerializer
from .models import Cart,CartItems
from rest_framework import serializers




class CartItemSerializer(ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    price = serializers.DecimalField(source="product.price", max_digits=10, decimal_places=2, read_only=True)
    description = serializers.CharField(source="product.description", read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = CartItems
        fields = ["id", "product", "product_name","image", "price", "quantity","description"]
        
    def get_image(self, obj):
        image = obj.product.images.first()
        if image:
            return image.image.url
        return None
          


class CartSerializer(ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "items"]



