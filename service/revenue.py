from Orders.models import OrderItem,Order
from django.db.models import Sum, F, Count
from django.utils import timezone



from datetime import datetime

def current_month_revenue():
    now = timezone.now()
    start = datetime(now.year, now.month, 1)
    data = (
        OrderItem.objects
        .filter(order__created_at__gte=start)
        .aggregate(revenue=Sum(F("price") * F("quantity"))))
    return [data]



def avg_order_value(status=None):
    queryset = OrderItem.objects.all()

    if status:
        queryset = queryset.filter(order__status__iexact=status)
    data = queryset.aggregate(
        total_revenue=Sum(F("price") * F("quantity")),
        total_orders=Count("order", distinct=True),)
    total_revenue = data["total_revenue"] or 0
    total_orders = data["total_orders"] or 0

    if total_orders == 0:
        return 0
    return total_revenue / total_orders