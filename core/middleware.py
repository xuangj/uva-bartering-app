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
