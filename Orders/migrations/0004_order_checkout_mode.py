from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Orders", "0003_order_payment_id_order_razorpay_order_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="checkout_mode",
            field=models.CharField(
                choices=[("cart", "Cart"), ("buy_now", "Buy Now")],
                default="cart",
                max_length=20,
            ),
        ),
    ]
