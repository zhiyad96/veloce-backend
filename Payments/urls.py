from django.urls import path
from .views import CreatePayment,VerifyPayment



urlpatterns=[
    path("payment/", CreatePayment.as_view()),
    path("verify/", VerifyPayment.as_view()),
]