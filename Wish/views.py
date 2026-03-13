from django.shortcuts import render
from rest_framework.views import APIView
from .models import Wishlist,WishlistItem
from .serializers import WishlistItemSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated






class WishlistView(APIView):
    
    permission_classes=[IsAuthenticated]

    def get(self, request):
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        items = wishlist.items.select_related("product").all()
        serializer = WishlistItemSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        product_id = request.data.get("product")

        wishlist, created = Wishlist.objects.get_or_create(user=request.user)

        item, created = WishlistItem.objects.get_or_create(
            wishlist=wishlist,
            product_id=product_id
        )

        serializer = WishlistItemSerializer(item)
        return Response(serializer.data)
    
    
    
class WishlistitemDelete(APIView):

    def delete(self, request, id):
        item = WishlistItem.objects.get(id=id)
        item.delete()
        return Response({"message": "removed"})