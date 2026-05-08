from rest_framework import serializers


class CheckoutModeMixin:
    def _normalize_mode(self, attrs):
        mode = attrs.get("mode") or attrs.get("checkout_mode")
        buy_now = attrs.get("buy_now")
        if buy_now is None:
            buy_now = attrs.get("buyNow")

        if not mode:
            mode = "buy_now" if buy_now else "cart"

        if mode not in {"cart", "buy_now"}:
            raise serializers.ValidationError({"mode": "Mode must be either 'cart' or 'buy_now'."})

        attrs["mode"] = mode
        return attrs

    def _normalize_buy_now_item(self, attrs):
        item = attrs.get("item")
        product_id = attrs.get("product_id")
        if product_id is None:
            product_id = attrs.get("productId")
        quantity = attrs.get("quantity")
        if quantity is None:
            quantity = attrs.get("qty")

        if item is None and product_id is not None:
            item = {"product_id": product_id, "quantity": quantity or 1}

        if item is None:
            raise serializers.ValidationError({"item": "Item details are required for buy_now mode."})

        if not isinstance(item, dict):
            raise serializers.ValidationError({"item": "Item must be a valid object."})

        normalized_product_id = item.get("product_id") or item.get("productId") or item.get("id")
        normalized_quantity = (
            item.get("quantity")
            or item.get("qty")
            or quantity
            or attrs.get("quantity")
            or attrs.get("qty")
            or 1
        )

        if not normalized_product_id:
            raise serializers.ValidationError({"item": "product_id is required for buy_now mode."})

        try:
            normalized_quantity = int(normalized_quantity)
        except (TypeError, ValueError):
            raise serializers.ValidationError({"item": "quantity must be a valid integer."})

        if normalized_quantity < 1:
            raise serializers.ValidationError({"item": "quantity must be at least 1."})

        try:
            normalized_product_id = int(normalized_product_id)
        except (TypeError, ValueError):
            raise serializers.ValidationError({"item": "product_id must be a valid integer."})

        attrs["item"] = {
            "product_id": normalized_product_id,
            "quantity": normalized_quantity,
        }
        return attrs


class CheckoutPreviewSerializer(serializers.Serializer, CheckoutModeMixin):
    mode = serializers.ChoiceField(choices=["cart", "buy_now"], required=False)
    checkout_mode = serializers.ChoiceField(choices=["cart", "buy_now"], required=False, write_only=True)
    buy_now = serializers.BooleanField(required=False)
    buyNow = serializers.BooleanField(required=False, write_only=True)
    item = serializers.DictField(required=False)
    product_id = serializers.IntegerField(required=False)
    productId = serializers.IntegerField(required=False, write_only=True)
    quantity = serializers.IntegerField(min_value=1, required=False)
    qty = serializers.IntegerField(min_value=1, required=False, write_only=True)

    def validate(self, attrs):
        attrs = self._normalize_mode(attrs)

        if attrs["mode"] == "buy_now":
            attrs = self._normalize_buy_now_item(attrs)
        else:
            attrs["item"] = None

        return attrs


class CheckoutCreateOrderSerializer(CheckoutPreviewSerializer):
    address_id = serializers.IntegerField(required=False)
    addressId = serializers.IntegerField(required=False, write_only=True)

    def validate(self, attrs):
        if attrs.get("address_id") is None and attrs.get("addressId") is not None:
            attrs["address_id"] = attrs["addressId"]

        if attrs.get("address_id") is None:
            raise serializers.ValidationError({"address_id": "This field is required."})

        return super().validate(attrs)


class CheckoutVerifySerializer(serializers.Serializer):
    razorpay_order_id = serializers.CharField(required=False)
    razorpayOrderId = serializers.CharField(required=False, write_only=True)
    razorpay_payment_id = serializers.CharField(required=False)
    razorpayPaymentId = serializers.CharField(required=False, write_only=True)
    razorpay_signature = serializers.CharField(required=False)
    razorpaySignature = serializers.CharField(required=False, write_only=True)

    def validate(self, attrs):
        if attrs.get("razorpay_order_id") is None and attrs.get("razorpayOrderId") is not None:
            attrs["razorpay_order_id"] = attrs["razorpayOrderId"]
        if attrs.get("razorpay_payment_id") is None and attrs.get("razorpayPaymentId") is not None:
            attrs["razorpay_payment_id"] = attrs["razorpayPaymentId"]
        if attrs.get("razorpay_signature") is None and attrs.get("razorpaySignature") is not None:
            attrs["razorpay_signature"] = attrs["razorpaySignature"]

        missing = {}
        if not attrs.get("razorpay_order_id"):
            missing["razorpay_order_id"] = "This field is required."
        if not attrs.get("razorpay_payment_id"):
            missing["razorpay_payment_id"] = "This field is required."
        if not attrs.get("razorpay_signature"):
            missing["razorpay_signature"] = "This field is required."

        if missing:
            raise serializers.ValidationError(missing)

        return attrs
