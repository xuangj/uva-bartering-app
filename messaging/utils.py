from .models import Message, ChatThread
from django.contrib.auth.models import User
from core.models import Trade
from .views import get_or_create_dm_thread

def send_trade_notification(trade: Trade, sender: User, message_type: str, text: str):
    """
    message_type → 'trade' or 'system'
    """

    # For trade notifications, always use the DM thread between offerer + receiver
    thread = get_or_create_dm_thread(trade.offerer, trade.receiver)

    return Message.objects.create(
        thread=thread,
        sender=sender,
        content=text,
        message_type=message_type,
        related_trade=trade,
    )

def notify_trade_offer(trade: Trade):
    return send_trade_notification(
        trade,
        sender=trade.offerer,
        message_type="trade",
        text=f"{trade.offerer.username} offered a trade for '{trade.item_requested.title}'."
    )


def notify_trade_cancelled(trade: Trade, user: User):
    return send_trade_notification(
        trade,
        sender=user,
        message_type="trade",
        text=f"{user.username} cancelled a trade offer for '{trade.item_requested.title}'."
    )


def notify_trade_accepted(trade: Trade, receiver: User):
    return send_trade_notification(
        trade,
        sender=receiver,
        message_type="trade",
        text=f"Trade accepted for '{trade.item_requested.title}'."
    )


def notify_trade_denied(trade: Trade, receiver: User):
    return send_trade_notification(
        trade,
        sender=receiver,
        message_type="trade",
        text=f"Trade denied for '{trade.item_requested.title}'."
    )
