from django.db import models
import cloudinary.models


# Create your models here.
class Category(models.Model):
    name=models.CharField(max_length=200)


class Product(models.Model):
    name=models.CharField(max_length=200)
    price=models.DecimalField(max_digits=10,decimal_places=2)
    category=models.ForeignKey(Category,on_delete= models.CASCADE)
    description=models.TextField()
    stock=models.IntegerField()
    is_active=models.BooleanField(default= False)
    
    
class ProductImage(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name="images")
    image = cloudinary.models.CloudinaryField('image')    
    