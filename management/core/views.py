from django.shortcuts import render
from django.core.cache import cache
from rest_framework.response import Response


def index(request):
    unauthorized_access = (
        request.GET.get("UnauthorizedAccess", "false").lower() == "true"
    )
    is_logged_in = (
        request.GET.get("welcome", "false").lower() == "true"
        and not unauthorized_access
    )
    context = {"is_logged_in": is_logged_in}
    print(context)
    return render(request, "login.html", context)


# from rest_framework.decorators import api_view


# @api_view(["GET"])
# def index(request):
#     value = cache.get("my_key")
#     if not value:
#         value = "Hello from Redis!"
#         cache.set("my_key", value, timeout=6000)
#     return Response({"message": value})
