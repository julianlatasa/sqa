from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.template import loader
import json

from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie

from django.contrib.auth import authenticate
from django.contrib.auth.models import User

@ensure_csrf_cookie
def index(request):
    template = loader.get_template(r'dashboard\index.html')
    context = {}
    return HttpResponse(template.render(context, request))