from rest_framework.serializers import ModelSerializer
from .models import Product,Category,ProductImage
from rest_framework import serializers

        # =============================product category=============================

class Productcategoryserializer(ModelSerializer):
    class Meta:
        model=Category
        fields="__all__"
        
        # ===================================product image==========================
        
class Productimageserializer(ModelSerializer):
    class Meta:
        model=ProductImage
        fields = ["id","product", "image"]
    
    def to_representation(self, instance):
        data = super().to_representation(instance)

        if instance.image:
            data["image"] = instance.image.url
        return data
    
        # ====================================product serializer======================
        
class Productserializer(ModelSerializer):
    images=Productimageserializer(many=True,required=False)
    class Meta:
        model=Product
        fields="__all__"
        
    def create(self, validated_data):
        images_data = validated_data.pop("images", [])
        product = Product.objects.create(**validated_data)

        for image in images_data:
            ProductImage.objects.create(
                product=product,
                image=image["image"]
            )
        return product