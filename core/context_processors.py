from messaging.models import Message, MessageRead
from core.models import Trade, Report
from django.db.models import Q, Count

def navbar_notifications(request):
    if not request.user.is_authenticated:
        return {}

    user = request.user

    # UNREAD MESSAGES
    unread_messages = Message.objects.filter(
        thread__participants=user
    ).exclude(sender=user).exclude(
        reads__user=user
    ).count()

    # ACTIVE TRADES (pending only)
    active_trades = Trade.objects.filter(
        receiver=user,
        status="Pending",
    ).count()
    active_trades += Trade.objects.filter(
        offerer=user,
        status="Pending",
    ).count()

    # UNRESOLVED REPORTS (mods only)
    unresolved_reports = 0
    if user.is_staff:
        unresolved_reports = Report.objects.filter(
            Q(resolution__isnull=True) |
            Q(resolution__status="open")
        ).count()

    # TOTAL NOTIFICATIONS
    total = unread_messages + active_trades + unresolved_reports

    return {
        "notif_unread_messages": unread_messages,
        "notif_trades": active_trades,
        "notif_reports": unresolved_reports,
        "notif_total": total,
    }
