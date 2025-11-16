from django.shortcuts import redirect
from django.contrib.auth import logout

class BanMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.user.is_authenticated:
            if hasattr(request.user, "profile") and request.user.profile.banned:

                logout(request)
                return redirect("/banned/")

        return self.get_response(request)

class FirstLoginRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            profile = getattr(request.user, "profile", None)
            if profile and not profile.has_logged_in_before:
                profile.has_logged_in_before = True
                profile.save()
                return redirect("user_profile", username=request.user.username)

        return response
