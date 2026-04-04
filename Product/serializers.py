from rest_framework.serializers import ModelSerializer
from .models import Product,Category,ProductImage
from rest_framework import serializers
import cloudinary.uploader





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
        
        
        
def upload_image_if_needed(img_url):
    if not img_url or not isinstance(img_url, str):
        return img_url
    if 'res.cloudinary.com' in img_url:
        return img_url
    if img_url.startswith('http://') or img_url.startswith('https://') or img_url.startswith('data:image'):
        try:
            upload_data = cloudinary.uploader.upload(img_url)
            return upload_data.get('public_id')
        except Exception:
            return img_url
    return img_url

        

        
class Productserializer(ModelSerializer):
    images=Productimageserializer(many=True,required=False)
    class Meta:
        model=Product
        fields=["id","name","price","images","category","description","is_active","stock"]
        
        
        
    def to_internal_value(self, data):
        mutable_data = data.copy() if hasattr(data, 'copy') else dict(data)
        
        if 'images' in mutable_data:
            del mutable_data['images']

        if 'category' in mutable_data:
            cat_val = mutable_data['category']
            if isinstance(cat_val, str) and not cat_val.isdigit():
                if cat_val.strip() == "":
                    cat_obj, _ = Category.objects.get_or_create(name="Uncategorized")
                else:
                    cat_obj, _ = Category.objects.get_or_create(name=cat_val)
                mutable_data['category'] = cat_obj.id

        if 'stock' in mutable_data and mutable_data['stock'] == '':
            mutable_data['stock'] = 0

        if 'price' in mutable_data and mutable_data['price'] == '':
            mutable_data['price'] = 0
        return super().to_internal_value(mutable_data)



    def create(self, validated_data):
        validated_data.pop("images", None)
        product = Product.objects.create(**validated_data)
        images_data = self.initial_data.get("images", [])
        if isinstance(images_data, str):
            if images_data.strip():
                images_data = [images_data]
            else:
                images_data = []
        for image in images_data:
            if isinstance(image, dict):
                img_url = image.get("image")
            else:
                img_url = image 
            if img_url:
                processed_url = upload_image_if_needed(img_url)
                ProductImage.objects.create(product=product,image=processed_url)
        return product



    def update(self, instance, validated_data):
        images_data = self.initial_data.get("images", None)
        validated_data.pop("images", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if images_data is not None:
            for image in images_data:
                if isinstance(image, dict):
                    img_id = image.get("id")
                    img_url = image.get("image")
                else:
                    img_id = None
                    img_url = image
                if img_url:
                    processed_url = upload_image_if_needed(img_url)
                    if img_id:
                        try:
                            img_obj = ProductImage.objects.get(id=img_id, product=instance)                 
                            current_url = img_obj.image.url if hasattr(img_obj.image, 'url') else str(img_obj.image)
                            if str(img_url) != str(current_url):
                                img_obj.image = processed_url
                                img_obj.save()
                        except ProductImage.DoesNotExist:
                            pass
                    else:
                        ProductImage.objects.create(product=instance, image=processed_url)
        return instance