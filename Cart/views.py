from django.shortcuts import render
from rest_framework.views import APIView
from .models import Cart,CartItems
from .serializers import CartItemSerializer,CartSerializer
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from rest_framework.permissions import IsAuthenticated




        # ======================================cart section ===================================

class Cartlist(APIView):
    
    permission_classes=[IsAuthenticated]
    
    def get(self,request):
        items = Cart.objects.prefetch_related("items__product").filter(user=request.user).first()
        serializer=CartSerializer(items)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    def post(self,request):
        product_id=request.data.get('product')
        quantity=int(request.data.get('quantity',1))
        
        if not product_id:
            return Response(
            {"error": "not have product"},
            status=status.HTTP_400_BAD_REQUEST)
            
        cart = Cart.objects.filter(user=request.user).first()

        if not cart:
            cart = Cart.objects.create(user=request.user)
       
        item = CartItems.objects.filter(cart=cart, product_id=product_id).first()
        if item:
            item.quantity += quantity
            item.save()
        else:
            item = CartItems.objects.create(
            cart=cart,
            product_id=product_id,
            quantity=quantity
            )
        serializer = CartItemSerializer(item)
        return Response(serializer.data)
    
    # ==========================cartitems=================
    
class Cartitems(APIView):
    
    def get_object(self,id):
        try:
            items=CartItems.objects.get(id=id)
            return items
        except CartItems.DoesNotExist :
            raise Http404
        
    def get(self, request, id):
        item = self.get_object(id)
        serializer = CartItemSerializer(item)
        return Response(serializer.data)
    
    def put(self,request,id):
        item=self.get_object(id)
        serializer=CartItemSerializer(item,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request,id):
        item=self.get_object(id)
        
        item.delete()
        return Response({"success":"item deleted"})