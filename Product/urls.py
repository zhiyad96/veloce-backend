from django.urls import path
from .views import Productlist,Categorylist,categories,productimageview,productimageupdate,ProductDetailView
from django.conf import settings 
from django.conf.urls.static import static



urlpatterns=[
    path("products/",Productlist.as_view()),
    
    path("products/<int:id>/", ProductDetailView.as_view()),
    
    path("category/",Categorylist.as_view()),
    
    path("productimg/", productimageview.as_view()),
    
    path("category/<int:id>/",categories.as_view()),
    
    path("productimg/<int:id>/",productimageupdate.as_view())
    
    
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)