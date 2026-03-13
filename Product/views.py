from rest_framework.views import APIView
from .serializers import Productserializer,Productcategoryserializer,Productimageserializer
from rest_framework.response import Response
from rest_framework import status
from .models import Product,Category,ProductImage
from rest_framework.parsers import MultiPartParser,FormParser
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from django.http import Http404



        # ==========================paginatioclass==================

class paginationclass(PageNumberPagination):
    page_size=2



        # =================== product section ===================

class Productlist(APIView):
    
    parser_classes = [MultiPartParser, FormParser]
    
    def get(self,request):
        products=Product.objects.all()
        
        
        search=request.GET.get("search")
        if search :
            products=products.filter(Q(name__icontains=search)|Q(description__icontains=search))
        
        
        category=request.GET.get("category")
        if category and category !="all" :
            products=products.filter(category_id=category)
            
            
        sort = request.GET.get("sort")
        if sort == "price-low-high":
            products = products.order_by("price")

        elif sort == "price-high-low":
            products = products.order_by("-price")

        elif sort == "name-a-z":
            products = products.order_by("name")

        elif sort == "name-z-a":
            products = products.order_by("-name")
            
            
        paginator=paginationclass()
        product=paginator.paginate_queryset(products,request)
        serializer=Productserializer(product,many=True)
        return paginator.get_paginated_response(serializer.data)
    
    
    def post(self, request):
        serializer = Productserializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # ==============================productdetails========================
        
class ProductDetailView(APIView):

    def get_object(self, id):
        try:
            return Product.objects.prefetch_related("images").get(id=id)
        except Product.DoesNotExist:
            raise Http404

    def get(self, request, id):
        product = self.get_object(id)
        serializer = Productserializer(product)
        return Response(serializer.data)
        
            # ================category section================ 

        
class Categorylist(APIView):
    def get(self,request):
        item=Category.objects.all()
        serializer=Productcategoryserializer(item,many=True)
        return Response (serializer.data,status=status.HTTP_200_OK)
    
    
    def post(self,request):
        serializer=Productcategoryserializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    
class categories(APIView):
    
    def get_object(self,id):
            try:
                item=Category.objects.get(id=id)
                return item
            except Category.DoesNotExist:
                return Response({"category":"category not found in categorydeletee"},status=status.HTTP_404_NOT_FOUND)
    def get(self,request,id):
        item=self.get_object(id)
        serializer=Productcategoryserializer(item)
        return Response(serializer.data,status=status.HTTP_200_OK)        
            
    def patch(self,request,id):
        item=self.get_object(id)
        serializer=Productcategoryserializer(item,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def put(self,request,id):
        item=self.get_object(id)
        serializer=Productcategoryserializer(item,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_204_NO_CONTENT)
    
    def delete(self,request,id):
        item=self.get_object(id)
        item.delete()
        return Response({"messege":"item deleted"},status=status.HTTP_200_OK)
    
    # ===============================imagesection==========================

class productimageview(APIView):
    
    parser_classes = [MultiPartParser, FormParser]
    
    def get(self, request):
        images = ProductImage.objects.all()
        serializer = Productimageserializer(images, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        if "image" not in request.data:
            return Response({"error": "Image file required"}, status=400)
        serializer = Productimageserializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # ===============================productimageupdate============
    
class productimageupdate(APIView):
    
    def get(self, request, id):
        images = ProductImage.objects.filter(product_id=id)
        serializer = Productimageserializer(images, many=True)
        return Response(serializer.data)
       
    def put(self, request, id):
        try:
            image = ProductImage.objects.get(id=id)
        except ProductImage.DoesNotExist:
            return Response({"error": "Image not found in image section "}, status=status.HTTP_404_NOT_FOUND)

        serializer = Productimageserializer(image, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, id):
        try:
            image = ProductImage.objects.get(id=id)
        except ProductImage.DoesNotExist:
            return Response({"error": "Image not found in image section"}, status=status.HTTP_404_NOT_FOUND)

        image.delete()
        return Response({"message": "Image deleted"}, status=status.HTTP_204_NO_CONTENT)

    