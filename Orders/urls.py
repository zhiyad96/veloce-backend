from django.urls import path
from .views import OrderView,CancelOrder,AddressView

urlpatterns = [
    path("orders/", OrderView.as_view()),
    path("orders/<int:id>/cancel/", CancelOrder.as_view()),
    path("address/", AddressView.as_view()),

]