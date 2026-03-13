from django.urls import path
from . views import Cartlist,Cartitems


urlpatterns = [
    path("carts/", Cartlist.as_view()),
    path("cartitem/<int:id>/", Cartitems.as_view()),
]