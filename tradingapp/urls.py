import os

from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

from core.views import home, login_redirect_view, moderator_dashboard, post_create, user_profile, edit_profile, my_trades, view_post, view_trade, accept_trade, deny_trade, delete_trade_offer, report_post, change_pfp
from messaging.views import chat, get_or_create_dm_thread, inbox, start_chat, groupchat_create, groupchat_select_users

urlpatterns = [
    path("", home, name="home"),
    path("accounts/", include("allauth.urls")),
    
    

    path("admin/", admin.site.urls),
    path("redirect/", login_redirect_view, name="login_redirect"),
    path("moderator/", moderator_dashboard, name="moderator_dashboard"),

    path("post/new/", post_create, name="post_create"),
    path("post/<int:post_id>/", view_post, name="view_post"),

    path("inbox/", inbox, name="inbox"),
    path("chat/<int:thread_id>/", chat, name="chat"),
    path("inbox/", inbox, name="inbox"),
    path("group/new/", groupchat_select_users, name="groupchat_select_users"),
    path("group/create/", groupchat_create, name="groupchat_create"),

    path("report/<int:post_id>/", report_post, name='report_post'),
    path("start/<int:user_id>/", start_chat, name="start_chat"),

    path("user/<str:username>/", user_profile, name="user_profile"),
    path("user/<str:username>/edit/", edit_profile, name="edit_profile"),
    
    path("trades/active/", my_trades, name="my_trades"),
    path("trades/<int:trade_id>/accept/", accept_trade, name="accept_trade"),
    path("trades/<int:trade_id>/deny/", deny_trade, name="deny_trade"),
    path("trades/<int:trade_id>/delete/", delete_trade_offer, name="delete_trade_offer"),
    path("trade/<int:trade_id>/", view_trade, name="view_trade"),
    path("user/<str:username>/edit/pfp", change_pfp, name="change_pfp"),

]


# if on local, serve media files during development
if not os.getenv("DATABASE_URL"):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
