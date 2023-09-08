import re

from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import urlquote_plus

CHECKOUT_PATH = re.compile("^/ledger/checkout/checkout")


class FirstTimeNagScreenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            not request.user.is_authenticated
            or not request.method == "GET"
            or "api" in request.path
            or "admin" in request.path
            or "static" in request.path
        ):
            return self.get_response(request)

        if (
            request.user.first_name
            and request.user.last_name
            and request.user.residential_address_id
            and request.user.postal_address_id
        ):
            return self.get_response(request)

        path_ft = reverse("account-firstime")
        if request.path in (path_ft, reverse("logout")):
            return self.get_response(request)

        return redirect(path_ft + "?next=" + urlquote_plus(request.get_full_path()))


class CacheControlMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.path[:5] == "/api/" or request.path == "/":
            response["Cache-Control"] = "private, no-store"
        elif request.path[:8] == "/static/":
            response["Cache-Control"] = "public, max-age=86400"
        return response
