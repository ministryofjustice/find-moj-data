from django.conf import settings

def env(request):
    return {'env': settings.ENV}
