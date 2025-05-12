from django.shortcuts import render


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
