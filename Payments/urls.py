from django.urls import path
from .views import (
    CheckoutPreview,
    CreatePayment,
    LegacyCreatePayment,
    LegacyVerifyPayment,
    VerifyPayment,
)



urlpatterns=[
    path("checkout/preview/", CheckoutPreview.as_view()),
    path("checkout/create-order/", CreatePayment.as_view()),
    path("checkout/verify/", VerifyPayment.as_view()),
    path("payment/", LegacyCreatePayment.as_view()),
    path("verify/", LegacyVerifyPayment.as_view()),
]
