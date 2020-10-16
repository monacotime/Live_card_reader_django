from django.http import request
from django.shortcuts import redirect


def home(request):
    return redirect(request, 'LivCam:detect')