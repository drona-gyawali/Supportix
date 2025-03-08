from django.http import HttpResponse


def index(request):
    return HttpResponse("messge:Pushed to rabbitmq")
