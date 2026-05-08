from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def send_order_status(user_id, order_id, status):

    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        "test_user",
        {
            "type": "send_status",
            "order_id": order_id,
            "status": status
        }
    )