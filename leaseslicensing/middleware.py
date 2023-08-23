import re
from urllib.parse import quote_plus

from django.shortcuts import redirect
from django.urls import reverse
from reversion.middleware import RevisionMiddleware
from reversion.views import _request_creates_revision

CHECKOUT_PATH = re.compile("^/ledger/checkout/checkout")


class FirstTimeNagScreenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            request.user.is_authenticated()
            and request.method == "GET"
            and "api" not in request.path
            and "admin" not in request.path
        ):
            if (not request.user.first_name) or (
                not request.user.last_name
            ):  # or (not request.user.dob):
                path_ft = reverse("first_time")
                path_logout = reverse("accounts:logout")
                if request.path not in (path_ft, path_logout):
                    return redirect(
                        reverse("first_time")
                        + "?next="
                        + quote_plus(request.get_full_path())
                    )


class RevisionOverrideMiddleware(RevisionMiddleware):

    """
    Wraps the entire request in a revision.

    override venv/lib/python2.7/site-packages/reversion/middleware.py
    """

    # exclude ledger payments/checkout from revision - hack
    # to overcome basket (lagging status) issue/conflict with reversion
    def request_creates_revision(self, request):
        return (
            _request_creates_revision(request)
            and "checkout" not in request.get_full_path()
        )


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
