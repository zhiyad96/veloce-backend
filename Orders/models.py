from django.db import models
from django.conf import settings
from Product.models import Product
from accounts.models import Address

class Order(models.Model):
    CHECKOUT_MODE_CHOICES = (
        ("cart", "Cart"),
        ("buy_now", "Buy Now"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        null=True,
        related_name="orders"
    )

    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    checkout_mode = models.CharField(
        max_length=20,
        choices=CHECKOUT_MODE_CHOICES,
        default="cart"
    )

    payment_id = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    razorpay_order_id = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.user}"



class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
