from decimal import Decimal, ROUND_HALF_UP

import razorpay
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from Cart.models import Cart, CartItems
from Orders.models import Order, OrderItem
from Product.models import Product
from accounts.models import Address


TWO_DECIMAL_PLACES = Decimal("0.01")
MIN_ORDER_AMOUNT_PAISE = 100


def _format_money(amount):
    return str(amount.quantize(TWO_DECIMAL_PLACES))


def _to_paise(amount):
    return int((amount * Decimal("100")).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _get_razorpay_client():
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET))


def _build_buy_now_line_items(item):
    product_id = item["product_id"]
    quantity = item["quantity"]

    product = Product.objects.filter(id=product_id).first()
    if not product:
        raise ValidationError({"item": f"Product with id {product_id} does not exist."})

    if quantity > product.stock:
        raise ValidationError({"item": f"Only {product.stock} units left for {product.name}."})

    unit_price = Decimal(product.price)
    line_total = unit_price * quantity

    return [
        {
            "product": product,
            "product_id": product.id,
            "product_name": product.name,
            "quantity": quantity,
            "unit_price": unit_price,
            "line_total": line_total,
        }
    ]


def _build_cart_line_items(user):
    cart = Cart.objects.filter(user=user).first()
    if not cart:
        raise ValidationError({"cart": "Cart not found."})

    cart_items = list(CartItems.objects.select_related("product").filter(cart=cart))
    if not cart_items:
        raise ValidationError({"cart": "Cart is empty."})

    line_items = []
    for cart_item in cart_items:
        product = cart_item.product
        quantity = cart_item.quantity

        if quantity < 1:
            raise ValidationError({"cart": f"Invalid quantity for {product.name}."})

        if quantity > product.stock:
            raise ValidationError({"cart": f"Only {product.stock} units left for {product.name}."})

        unit_price = Decimal(product.price)
        line_total = unit_price * quantity

        line_items.append(
            {
                "product": product,
                "product_id": product.id,
                "product_name": product.name,
                "quantity": quantity,
                "unit_price": unit_price,
                "line_total": line_total,
            }
        )

    return line_items


def _build_line_items(user, mode, item):
    if mode == "buy_now":
        line_items = _build_buy_now_line_items(item)
    else:
        line_items = _build_cart_line_items(user)

    subtotal = sum((line_item["line_total"] for line_item in line_items), Decimal("0.00"))
    subtotal = subtotal.quantize(TWO_DECIMAL_PLACES)

    return line_items, subtotal


def _serialize_line_items(line_items):
    serialized = []
    for line_item in line_items:
        product = line_item["product"]
        image = product.images.first()
        serialized.append(
            {
                "product_id": line_item["product_id"],
                "product_name": line_item["product_name"],
                "quantity": line_item["quantity"],
                "unit_price": _format_money(line_item["unit_price"]),
                "line_total": _format_money(line_item["line_total"]),
                "image": image.image.url if image else None,
            }
        )
    return serialized


def preview_checkout(user, mode, item):
    line_items, subtotal = _build_line_items(user, mode, item)
    shipping = Decimal("0.00")
    discount = Decimal("0.00")
    grand_total = (subtotal + shipping - discount).quantize(TWO_DECIMAL_PLACES)

    return {
        "mode": mode,
        "line_items": _serialize_line_items(line_items),
        "totals": {
            "subtotal": _format_money(subtotal),
            "shipping": _format_money(shipping),
            "discount": _format_money(discount),
            "grand_total": _format_money(grand_total),
            "currency": "INR",
        },
    }


def create_checkout_order(user, mode, item, address_id):
    address = Address.objects.filter(id=address_id, user=user).first()
    if not address:
        raise ValidationError({"address_id": "Invalid address for current user."})

    line_items, subtotal = _build_line_items(user, mode, item)
    shipping = Decimal("0.00")
    discount = Decimal("0.00")
    grand_total = (subtotal + shipping - discount).quantize(TWO_DECIMAL_PLACES)
    amount_paise = _to_paise(grand_total)

    if amount_paise < MIN_ORDER_AMOUNT_PAISE:
        raise ValidationError({"amount": "Order amount must be at least INR 1.00."})

    receipt = f"order_{user.id}_{timezone.now().strftime('%Y%m%d%H%M%S%f')}"
    razorpay_client = _get_razorpay_client()
    razorpay_order = razorpay_client.order.create(
        {
            "amount": amount_paise,
            "currency": "INR",
            "payment_capture": 1,
            "receipt": receipt,
        }
    )

    with transaction.atomic():
        order = Order.objects.create(
            user=user,
            address=address,
            total_price=grand_total,
            checkout_mode=mode,
            razorpay_order_id=razorpay_order["id"],
            status="pending",
        )
        OrderItem.objects.bulk_create(
            [
                OrderItem(
                    order=order,
                    product=line_item["product"],
                    quantity=line_item["quantity"],
                    price=line_item["unit_price"],
                )
                for line_item in line_items
            ]
        )

    return {
        "message": "Checkout order created successfully.",
        "order_id": order.id,
        "mode": mode,
        "line_items": _serialize_line_items(line_items),
        "totals": {
            "subtotal": _format_money(subtotal),
            "shipping": _format_money(shipping),
            "discount": _format_money(discount),
            "grand_total": _format_money(grand_total),
            "currency": "INR",
        },
        "razorpay": {
            "key": settings.RAZORPAY_KEY_ID,
            "order_id": razorpay_order["id"],
            "amount": amount_paise,
            "currency": "INR",
        },
    }


def create_legacy_payment_order(user, amount=None):
    line_items, subtotal = _build_line_items(user, "cart", None)
    shipping = Decimal("0.00")
    discount = Decimal("0.00")
    grand_total = (subtotal + shipping - discount).quantize(TWO_DECIMAL_PLACES)
    computed_amount_paise = _to_paise(grand_total)

    if amount is not None:
        try:
            requested_amount_paise = int((Decimal(str(amount)) * Decimal("100")).quantize(Decimal("1")))
        except Exception:
            raise ValidationError({"amount": "Invalid amount."})
        if requested_amount_paise < MIN_ORDER_AMOUNT_PAISE:
            raise ValidationError({"amount": "Amount must be at least INR 1.00."})
    else:
        requested_amount_paise = computed_amount_paise

    if computed_amount_paise < MIN_ORDER_AMOUNT_PAISE:
        raise ValidationError({"amount": "Order amount must be at least INR 1.00."})

    receipt = f"legacy_order_{user.id}_{timezone.now().strftime('%Y%m%d%H%M%S%f')}"
    razorpay_client = _get_razorpay_client()
    razorpay_order = razorpay_client.order.create(
        {
            "amount": computed_amount_paise,
            "currency": "INR",
            "payment_capture": 1,
            "receipt": receipt,
        }
    )

    with transaction.atomic():
        order = Order.objects.create(
            user=user,
            address=None,
            total_price=grand_total,
            checkout_mode="cart",
            razorpay_order_id=razorpay_order["id"],
            status="pending",
        )
        OrderItem.objects.bulk_create(
            [
                OrderItem(
                    order=order,
                    product=line_item["product"],
                    quantity=line_item["quantity"],
                    price=line_item["unit_price"],
                )
                for line_item in line_items
            ]
        )

    return {
        "order": razorpay_order,
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "order_id": order.id,
        "computed_amount": computed_amount_paise,
        "requested_amount": requested_amount_paise,
    }


def _adjust_cart_after_paid_order(user, order):
    cart = Cart.objects.filter(user=user).first()
    if not cart:
        return

    ordered_quantities = {}
    for order_item in order.items.all():
        ordered_quantities[order_item.product_id] = (
            ordered_quantities.get(order_item.product_id, 0) + order_item.quantity
        )

    cart_items = CartItems.objects.select_for_update().filter(
        cart=cart,
        product_id__in=ordered_quantities.keys(),
    )

    for cart_item in cart_items:
        remaining = cart_item.quantity - ordered_quantities.get(cart_item.product_id, 0)
        if remaining > 0:
            cart_item.quantity = remaining
            cart_item.save(update_fields=["quantity"])
        else:
            cart_item.delete()


def verify_and_finalize_checkout(
    user,
    razorpay_order_id,
    razorpay_payment_id,
    razorpay_signature,
    address_id=None,
):
    razorpay_client = _get_razorpay_client()
    razorpay_client.utility.verify_payment_signature(
        {
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature,
        }
    )

    with transaction.atomic():
        order = (
            Order.objects.select_for_update()
            .prefetch_related("items")
            .filter(user=user, razorpay_order_id=razorpay_order_id)
            .first()
        )

        if not order:
            raise ValidationError({"order": "No pending local order found for this Razorpay order."})

        if order.status == "paid":
            return order

        if order.address_id is None and address_id is not None:
            try:
                normalized_address_id = int(address_id)
            except (TypeError, ValueError):
                raise ValidationError({"address_id": "Address id must be a valid integer."})

            address = Address.objects.filter(id=normalized_address_id, user=user).first()
            if not address:
                raise ValidationError({"address_id": "Invalid address for current user."})

            order.address = address
            order.save(update_fields=["address"])

        order_items = list(order.items.all())
        if not order_items:
            raise ValidationError({"order": "Order has no items."})

        product_ids = [order_item.product_id for order_item in order_items]
        products = Product.objects.select_for_update().filter(id__in=product_ids)
        product_map = {product.id: product for product in products}

        for order_item in order_items:
            product = product_map.get(order_item.product_id)
            if not product:
                raise ValidationError({"order": f"Product {order_item.product_id} no longer exists."})

            if order_item.quantity > product.stock:
                raise ValidationError({"order": f"Insufficient stock for {product.name}."})

            product.stock = product.stock - order_item.quantity
            product.save(update_fields=["stock"])

        order.status = "paid"
        order.payment_id = razorpay_payment_id
        order.save(update_fields=["status", "payment_id"])

        if order.checkout_mode == "cart":
            _adjust_cart_after_paid_order(user, order)

    return order
