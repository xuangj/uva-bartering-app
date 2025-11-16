from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models

from core.models import Profile, Post, Report, Trade
from messaging.models import Message

from .models import ModerationAction, ReportResolution


# ---------------------------------------------------------------------
# Helper Decorator
# ---------------------------------------------------------------------
def staff_required(view_func):
    """Wrapper ensuring only staff users can access mod pages."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            return HttpResponseForbidden("You are not allowed to access moderation tools.")
        return view_func(request, *args, **kwargs)
    return wrapper


# ---------------------------------------------------------------------
# Moderator Dashboard (Overview)
# ---------------------------------------------------------------------
@login_required
@staff_required
def dashboard(request):
    """Main dashboard with summary data."""

    profiles = Profile.objects.select_related("user").all()

    # Filtering
    name_query = request.GET.get("name")
    role_query = request.GET.get("role")

    if name_query:
        profiles = profiles.filter(user__username__icontains=name_query)
    if role_query:
        profiles = profiles.filter(role=role_query)

    context = {
        "profiles": profiles,
        "post_count": Post.objects.count(),
        "report_count": Report.objects.count(),
        "message_count": Message.objects.count(),
        "trade_count": Trade.objects.count(),
    }

    return render(request, "moderator/dashboard.html", context)


# ---------------------------------------------------------------------
# User Table
# ---------------------------------------------------------------------
@login_required
@staff_required
def users_table(request):
    users = User.objects.select_related("profile").all()
    return render(request, "moderator/users_table.html", {"users": users})


# ---------------------------------------------------------------------
# Posts Table
# ---------------------------------------------------------------------
@login_required
@staff_required
def posts_table(request):
    posts = Post.objects.select_related("poster").order_by("-created_at")
    return render(request, "moderator/posts_table.html", {"posts": posts})


# ---------------------------------------------------------------------
# Reports Table
# ---------------------------------------------------------------------
@login_required
@staff_required
def reports_table(request):
    reports = (
        Report.objects
        .select_related("reporter", "reported_user", "reported_post")
        .order_by("-created_at")
    )
    return render(request, "moderator/reports_table.html", {"reports": reports})


# ---------------------------------------------------------------------
# Messages Table
# ---------------------------------------------------------------------
@login_required
@staff_required
def messages_table(request):
    messages_qs = (
        Message.objects
        .select_related("sender", "thread")
        .order_by("-created_at")
    )
    return render(request, "moderator/messages_table.html", {"messages": messages_qs})


# ---------------------------------------------------------------------
# Trades Table
# ---------------------------------------------------------------------
@login_required
@staff_required
def trades_table(request):
    trades = (
        Trade.objects
        .select_related("offerer", "receiver", "item_requested")
        .prefetch_related("offered_posts")
        .order_by(
            models.Case(
                models.When(status="Pending", then=0),
                models.When(status="Accepted", then=1),
                models.When(status="Denied", then=2),
                default=3,
                output_field=models.IntegerField(),
            ),
            "-created_at",
        )
    )

    return render(request, "moderator/trades_table.html", {"trades": trades})

@login_required
@staff_required
def view_trade(request, trade_id):
    trade = get_object_or_404(Trade, id=trade_id)
    return render(request, "moderator/trade_detail.html", {"trade": trade})


# ---------------------------------------------------------------------
# User moderation actions
# ---------------------------------------------------------------------

@login_required
@staff_required
def toggle_user_ban(request, user_id):
    """Ban or unban a user by toggling is_active."""
    user = get_object_or_404(User, id=user_id)

    user.is_active = not user.is_active
    user.save()

    ModerationAction.objects.create(
        moderator=request.user,
        target_user=user,
        action_type="ban" if not user.is_active else "unban",
        reason="Moderator toggled ban status.",
    )

    messages.success(
        request,
        f"{'Unbanned' if user.is_active else 'Banned'} user {user.username}."
    )
    return redirect("moderator_users_table")


@login_required
@staff_required
def delete_user(request, profile_id):
    """Deletes a user and logs the action."""
    profile = get_object_or_404(Profile, id=profile_id)
    user = profile.user

    ModerationAction.objects.create(
        moderator=request.user,
        target_user=user,
        action_type="delete_user",
        reason="Moderator deleted user.",
    )

    user.delete()

    messages.error(request, "User deleted permanently.")
    return redirect("moderator_users_table")


# ---------------------------------------------------------------------
# Post moderation actions
# ---------------------------------------------------------------------
@login_required
@staff_required
def delete_post_mod(request, post_id):
    """Moderator deletes a post."""
    post = get_object_or_404(Post, id=post_id)

    ModerationAction.objects.create(
        moderator=request.user,
        target_post=post,
        action_type="delete_post",
        reason="Post removed by moderator.",
    )

    post.delete()
    messages.info(request, "Post removed.")
    return redirect("moderator_posts_table")


# ---------------------------------------------------------------------
# Report Resolution
# ---------------------------------------------------------------------
@login_required
@staff_required
def resolve_report(request, report_id):
    """Mark a report as resolved."""
    report = get_object_or_404(Report, id=report_id)

    resolution, _ = ReportResolution.objects.get_or_create(report=report)
    resolution.status = "resolved"
    resolution.moderator = request.user
    resolution.save()

    ModerationAction.objects.create(
        moderator=request.user,
        target_report=report,
        action_type="resolve_report",
        reason="Report resolved.",
    )

    messages.success(request, "Report marked as resolved.")
    return redirect("moderator_reports_table")


@login_required
@staff_required
def dismiss_report(request, report_id):
    """Dismiss a report as invalid/unnecessary."""
    report = get_object_or_404(Report, id=report_id)

    resolution, _ = ReportResolution.objects.get_or_create(report=report)
    resolution.status = "dismissed"
    resolution.moderator = request.user
    resolution.save()

    ModerationAction.objects.create(
        moderator=request.user,
        target_report=report,
        action_type="dismiss_report",
        reason="Report dismissed.",
    )

    messages.warning(request, "Report dismissed.")
    return redirect("moderator_reports_table")

# Ban a user
@login_required
@staff_required
def ban_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = user.profile

    if profile.banned:
        messages.warning(request, "User is already banned.")
        return redirect("moderator_users_table")

    # Mark banned
    profile.banned = True
    profile.banned_at = timezone.now()
    profile.save()

    # DELETE posts
    Post.objects.filter(poster=user).delete()

    # DELETE trades (remove ALL trades involving banned user)
    Trade.objects.filter(offerer=user).delete()
    Trade.objects.filter(receiver=user).delete()

    # Mark messages
    Message.objects.filter(sender=user).update(
        content="[Message sent by banned user]"
    )

    messages.success(request, f"{user.username} has been banned.")
    return redirect("moderator_users_table")

# Unban a user
@login_required
@staff_required
def unban_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = user.profile

    if not profile.banned:
        messages.warning(request, "User is not banned.")
        return redirect("moderator_users_table")

    profile.banned = False
    profile.banned_at = None
    profile.save()

    messages.success(request, f"{user.username} has been unbanned.")
    return redirect("moderator_users_table")

# Banned users table view
@login_required
@staff_required
def banned_users_table(request):
    banned_users = Profile.objects.filter(banned=True).select_related("user")

    return render(request, "moderator/banned_users.html", {
        "banned_users": banned_users
    })
