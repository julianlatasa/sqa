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

@ensure_csrf_cookie
def calendar(request):
    template = loader.get_template(r'dashboard\calendar.html')
    context = {}
    return HttpResponse(template.render(context, request))

@ensure_csrf_cookie
def weekplan(request):
    template = loader.get_template(r'dashboard\weekplan.html')
    context = {'weekdays1' : [{'name' : 'Semana'},
                              {'name' : 'Lunes'},
                              {'name' : 'Martes'},
                              {'name' : 'Miercoles'},
                              {'name' : 'Jueves'},
                              {'name' : 'Viernes'},
                              {'name' : 'Sabado'},
                              {'name' : 'Domingo'},
                             ]}
    return HttpResponse(template.render(context, request))