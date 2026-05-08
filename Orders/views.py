
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny
from Cart.models import Cart
from .models import Order, OrderItem,Address
from .serializers import AddressSerializer,OrderSerializer
from service.revenue import current_month_revenue,avg_order_value
from .websocket import send_order_status




# ==========================================order view==========================

class Adminorderview(APIView):
    
    permission_classes = [AllowAny]

    
    def get(self,request):
        orders=Order.objects.all()
        serialiser=OrderSerializer(orders,many=True)
        return Response(serialiser.data)



class OrderView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).prefetch_related("items__product")
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


    def post(self, request):
        address_id = request.data.get("address_id")
        if not address_id:
            return Response({"error": "Address is required"}, status=400)
        try:
            address = Address.objects.get(id=address_id, user=request.user)
        except Address.DoesNotExist:
            return Response({"error": "Invalid address"}, status=404)
        try:
            cart = Cart.objects.prefetch_related("items__product").get(user=request.user)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=404)
        if not cart.items.exists():
            return Response({"error": "Cart is empty"}, status=400)
        total = 0
        order = Order.objects.create(
            user=request.user,
            address=address,
            total_price=0
        )

        for item in cart.items.all():

            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

            total += item.product.price * item.quantity
        order.total_price = total
        order.save()
        cart.items.all().delete()
        return Response({
            "message": "Order created successfully",
            "order_id": order.id,
            "total_price": total
        })
        
        # ==================================address view====================
        
class AddressView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        addresses = Address.objects.filter(user=request.user)
        serializer = AddressSerializer(addresses, many=True)
        return Response(serializer.data)


    def post(self, request):
        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)
        return Response(serializer.errors)
    
    # ========================================cancelorder view=====================
    
class UpdateOrderStatus(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, id):
        try:
            order = Order.objects.get(id=id)
            if request.user.role == "user":
                if order.user != request.user:
                    return Response({"error": "Not allowed"}, status=403)
                if order.status in ["shipped", "delivered"]:
                    return Response(  {"error": "Order cannot be cancelled"}, status=400)
                order.status = "cancelled"  
                order.save()
                return Response({"message": "Order cancelled successfully"})
            elif request.user.role == "admin":
                new_status = request.data.get("status")
                order.status = new_status
                order.save()
                send_order_status(order.user.id,order.id,order.status)
                return Response({"message": "Order status updated"})
            else:
                return Response({"error": "Invalid role"}, status=403)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)
        
        
        # ==============================================monthly revenue =====================================
        
class Monthlyrevenuea(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        data = current_month_revenue()
        return Response(data)
    
            # ================================ Avg order value==================================
    
class AvgView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({ "avg_order_value": avg_order_value()})