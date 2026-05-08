import razorpay
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    CheckoutCreateOrderSerializer,
    CheckoutPreviewSerializer,
    CheckoutVerifySerializer,
)
from .services import (
    create_checkout_order,
    create_legacy_payment_order,
    preview_checkout,
    verify_and_finalize_checkout,
)


class CheckoutPreview(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CheckoutPreviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        response_payload = preview_checkout(
            user=request.user,
            mode=data["mode"],
            item=data.get("item"),
        )
        return Response(response_payload, status=status.HTTP_200_OK)


class CreatePayment(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CheckoutCreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            response_payload = create_checkout_order(
                user=request.user,
                mode=data["mode"],
                item=data.get("item"),
                address_id=data["address_id"],
            )
            return Response(response_payload, status=status.HTTP_201_CREATED)
        except ValidationError as exc:
            return Response(exc.detail, status=status.HTTP_400_BAD_REQUEST)
        except razorpay.errors.BadRequestError as exc:
            return Response(
                {"error": "Unable to create Razorpay order.", "details": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as exc:
            return Response(
                {"error": "Checkout order creation failed.", "details": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class LegacyCreatePayment(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            response_payload = create_legacy_payment_order(
                user=request.user,
                amount=request.data.get("amount"),
            )
            return Response(response_payload, status=status.HTTP_200_OK)
        except ValidationError as exc:
            return Response(exc.detail, status=status.HTTP_400_BAD_REQUEST)
        except razorpay.errors.BadRequestError as exc:
            return Response(
                {"error": "Unable to create Razorpay order.", "details": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as exc:
            return Response(
                {"error": "Legacy payment creation failed.", "details": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class VerifyPayment(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CheckoutVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            order = verify_and_finalize_checkout(
                user=request.user,
                razorpay_order_id=data["razorpay_order_id"],
                razorpay_payment_id=data["razorpay_payment_id"],
                razorpay_signature=data["razorpay_signature"],
                address_id=request.data.get("address_id") or request.data.get("addressId"),
            )
            return Response(
                {
                    "message": "Payment verified successfully.",
                    "order_id": order.id,
                    "status": order.status,
                    "checkout_mode": order.checkout_mode,
                },
                status=status.HTTP_200_OK,
            )
        except ValidationError as exc:
            return Response(exc.detail, status=status.HTTP_400_BAD_REQUEST)
        except razorpay.errors.SignatureVerificationError:
            return Response(
                {"error": "Payment signature verification failed."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as exc:
            return Response(
                {"error": "Payment verification failed.", "details": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class LegacyVerifyPayment(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CheckoutVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            order = verify_and_finalize_checkout(
                user=request.user,
                razorpay_order_id=data["razorpay_order_id"],
                razorpay_payment_id=data["razorpay_payment_id"],
                razorpay_signature=data["razorpay_signature"],
                address_id=request.data.get("address_id") or request.data.get("addressId"),
            )
            return Response(
                {
                    "message": "Order placed successfully",
                    "order_id": order.id,
                },
                status=status.HTTP_200_OK,
            )
        except ValidationError as exc:
            return Response(exc.detail, status=status.HTTP_400_BAD_REQUEST)
        except razorpay.errors.SignatureVerificationError:
            return Response(
                {"error": "Payment signature verification failed."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as exc:
            return Response(
                {"error": "Payment verification failed.", "details": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
