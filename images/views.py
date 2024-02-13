from django.http import HttpResponse


def index(request):
    return HttpResponse("this is the homepage for images.")

def image(request,image_id):
    return HttpResponse("You're looking at image %s." % image_id)
