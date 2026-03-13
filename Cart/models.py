from django.db import models
from django.conf import settings
from Product.models import Product





class Cart(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    

class CartItems(models.Model):
    cart=models.ForeignKey(Cart,on_delete=models.CASCADE,related_name="items")
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity=models.PositiveIntegerField(default=1)
    
    class Meta:
        unique_together=["cart","product"]