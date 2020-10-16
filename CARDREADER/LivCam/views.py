from django.http import request
from django.shortcuts import render
from django.http import StreamingHttpResponse, HttpResponse
from .videoCamera import gen, VideoCamera, get_image, detectcard
from django.views.decorators.csrf import csrf_exempt

def feed(request):
    return StreamingHttpResponse(gen(VideoCamera()), content_type='multipart/x-mixed-replace; boundary=frame')

def detect(request):
    return render(request, 'detect.html')

@csrf_exempt 
def scan(request):
    if request.is_ajax():
        return detectcard(get_image())
    else:
        return HttpResponse("hi")