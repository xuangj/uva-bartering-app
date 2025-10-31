from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from core import views

urlpatterns = [
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("accounts/", include("allauth.urls")),
    path("admin/", admin.site.urls),
    path("redirect/", views.login_redirect_view, name="login_redirect"),
    path("moderator/", views.moderator_dashboard, name="moderator_dashboard"),
    path("post/new/", views.post_create, name="post_create"),
]
