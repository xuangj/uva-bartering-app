from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

import os
from django.conf import settings
from django.conf.urls.static import static

from core.views import home, login_redirect_view, moderator_dashboard, post_create, user_profile, edit_profile, change_pfp
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
    path("start/<int:user_id>/", start_chat, name="start_chat"),
    path("user/<str:username>/", user_profile, name="user_profile"),
    path("user/<str:username>/edit/", edit_profile, name="edit_profile"),
    path("user/<str:username>/edit/pfp", change_pfp, name="change_pfp"),

]


# if on local, serve media files during development
if not os.getenv("DATABASE_URL"):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)