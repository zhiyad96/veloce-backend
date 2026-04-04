from django.urls import path
from .views import OrderView,UpdateOrderStatus,AddressView,Monthlyrevenuea,Adminorderview,AvgView

urlpatterns = [
    path("orders/", OrderView.as_view()),
    path("orders/<int:id>/cancel/", UpdateOrderStatus.as_view()),
    path("address/", AddressView.as_view()),
    path("monthly-revenue/", Monthlyrevenuea.as_view()),
    path("adminorderview/", Adminorderview.as_view()),
    path("avg/", AvgView.as_view()),

]