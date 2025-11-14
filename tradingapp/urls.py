from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from core.views import home, login_redirect_view, moderator_dashboard, post_create, user_profile, edit_profile,report_post  
from messaging.views import chat, get_or_create_dm_thread, inbox, start_chat

urlpatterns = [
    path("", home, name="home"),
    path("accounts/", include("allauth.urls")),
    path("admin/", admin.site.urls),
    path("redirect/", login_redirect_view, name="login_redirect"),
    path("moderator/", moderator_dashboard, name="moderator_dashboard"),
    path("post/new/", post_create, name="post_create"),
    path("inbox/", inbox, name="inbox"),
    path("chat/<int:thread_id>/", chat, name="chat"),
    path("inbox/", inbox, name="inbox"),
    path("report/<int:post_id>/", report_post, name='report_post'),
    path("start/<int:user_id>/", start_chat, name="start_chat"),
    path("user/<str:username>/", user_profile, name="user_profile"),
    path("user/<str:username>/edit/", edit_profile, name="edit_profile"),
]
