from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="moderator_dashboard"),

    # Table views
    path("users/", views.users_table, name="moderator_users_table"),
    path("posts/", views.posts_table, name="moderator_posts_table"),
    path("reports/", views.reports_table, name="moderator_reports_table"),
    path("messages/", views.messages_table, name="moderator_messages_table"),
    path("trades/", views.trades_table, name="moderator_trades_table"),
    path("banned-users/", views.banned_users_table, name="moderator_banned_users"),

    # Users
    path("user/<int:user_id>/toggle-ban/", views.toggle_user_ban, name="moderator_toggle_ban"),
    path("user/<int:profile_id>/delete/", views.delete_user, name="moderator_delete_user"),
    path("post/<int:post_id>/delete/", views.delete_post_mod, name="moderator_delete_post"),
    path("user/<int:user_id>/ban/", views.ban_user, name="moderator_ban_user"),
    path("user/<int:user_id>/unban/", views.unban_user, name="moderator_unban_user"),

    # Reports
    path("report/<int:report_id>/resolve/", views.resolve_report, name="moderator_resolve_report"),
    path("report/<int:report_id>/dismiss/", views.dismiss_report, name="moderator_dismiss_report"),
]
