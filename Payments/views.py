import razorpay
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from Cart.models import Cart,CartItems
from Orders.models import OrderItem,Order



    # ==========================payment view===========

class CreatePayment(APIView):

    def post(self, request):
        amount = request.data.get("amount")
        if not amount:
            return Response({"error": "Amount is required"},status=status.HTTP_400_BAD_REQUEST)
        try:
            amount = int(float(amount) * 100)
        except:
            return Response({"error": "Invalid amount"}, status=status.HTTP_400_BAD_REQUEST)
        if amount < 100:
            return Response({"error": "Amount must be at least ₹1"},status=status.HTTP_400_BAD_REQUEST)
        client = razorpay.Client( auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET) )
        order = client.order.create({ "amount": amount, "currency": "INR", "payment_capture": 1 })
        return Response({ "order": order,  "razorpay_key": settings.RAZORPAY_KEY_ID })
    
            # ==================================verifypayment===================

class VerifyPayment(APIView):
    def post(self, request):
        client = razorpay.Client( auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET) )
        params_dict = {
            "razorpay_order_id": request.data.get("razorpay_order_id"),
            "razorpay_payment_id": request.data.get("razorpay_payment_id"),
            "razorpay_signature": request.data.get("razorpay_signature"),
        }
        try:
            client.utility.verify_payment_signature(params_dict)
            cart = Cart.objects.get(user=request.user)
            cart_items = CartItems.objects.filter(cart=cart)
            total = sum(item.product.price * item.quantity for item in cart_items)

            order = Order.objects.create(
                user=request.user,
                address_id=request.data.get("address_id"),
                total_price=total,
                payment_id=request.data.get("razorpay_payment_id"),
                razorpay_order_id=request.data.get("razorpay_order_id"),
                status="paid"
            )

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )

            cart_items.delete()

            return Response({
                "message": "Order placed successfully",
                "order_id": order.id
            })

        except Exception as e:
            return Response(
                {"message": "Payment verification failed"},
                status=status.HTTP_400_BAD_REQUEST
            )