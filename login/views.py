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
    template = loader.get_template(r'login\index.html')
    context = {}
    return HttpResponse(template.render(context, request))

@ensure_csrf_cookie
def login(request):
    data = json.loads(request.body.decode('utf-8') )
    user_email = data['usuario']
    password = data['password']
    #print('Autenticar a ' + user_email + ' con password ' + password)
    res = ''

    try:
        user_name = User.objects.get(email__exact=user_email)
        if (user_name is not None):
            user = authenticate(username=user_name, password=password)
            if user is not None: # and user.is_active:
                res = 'Usuario valido'
            else:
                res = "Error al validar"
    except User.DoesNotExist:
        res = 'Usuario no existe'
       
        
#        try:
#            user = User.objects.get(email__iexact=user_email)
#            if not check_password(password, user.password):
#                form._errors['password'] = ErrorList([u'That is not the correct Password.'])
#        except User.DoesNotExist:
#            form._errors['email'] = ErrorList([u'This email is not registered with us.'])
    
    
    
    return HttpResponse("Hello, World! " + res)
