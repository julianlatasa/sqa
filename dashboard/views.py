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
    template = loader.get_template(r'dashboard/index.html')
    context = {'user_name' : request.user.first_name + ' ' + request.user.last_name} #'Julian Latasa'}
    #context = {'user_name' : 'Julian Latasa'}
    return HttpResponse(template.render(context, request))

@ensure_csrf_cookie
def calendar(request):
    template = loader.get_template(r'dashboard/calendar.html')
    context = {}
    return HttpResponse(template.render(context, request))

@csrf_exempt
def ranking(request):
    template = loader.get_template(r'dashboard/ranking.html')
    context = {}
    return HttpResponse(template.render(context, request))


@ensure_csrf_cookie
def weekplan(request):
    template = loader.get_template(r'dashboard/weekplan.html')
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


import datetime
from django.http import StreamingHttpResponse
from .GarminConnectSession import GarminSession
import pandas as pd

class mytimedelta(datetime.timedelta):
   def __str__(self):
      seconds = self.total_seconds()
      hours = seconds // 3600
      minutes = (seconds % 3600) // 60
      seconds = seconds % 60
      str = '{:02d}:{:02d}:{:02d}'.format(int(hours), int(minutes), int(seconds))
      return (str)

@csrf_exempt
def rankingresult(request):
     data = json.loads( request.body.decode('utf8').replace("'", '"')  )

     template = loader.get_template(r'dashboard/ranking_result.html')
     context = {'result' : data}

     return HttpResponse(template.render(context, request))

@csrf_exempt
def rankingquery(request):
    if (request.method == 'POST'):
        datajson = json.loads( request.body.decode('utf8').replace("'", '"')  )
        fecha = datajson['fecha']
#    usuario = 'julianlatasas@gmail.com'
#    password = 'Julian80'

#    http = StreamingHttpResponse( stream_response_generator(usuario, password, fecha, request.user.pk), content_type='text/plain' , headers = {'X-Accel-Buffering' : 'no'} )
    http = StreamingHttpResponse( stream_response_generator(fecha, request.user.pk), content_type='text/plain' , headers = {'X-Accel-Buffering' : 'no'} )

    return http

from .models import Profile, CacheData
from django.core.exceptions import ObjectDoesNotExist

@csrf_exempt
def stream_response_generator(fecha, user_id):
    yield '{"procesando": ['
    yield '{"estado": "%d", "mensaje": "%s"},\n' % (200,"Iniciando consulta")
    
#    if ((not usuario) or (not password)):
#        yield '{"estado": "%d", "mensaje": "%s"},\n' % (400, "No se ingreso un usuario o una clave")
#        return

    if (not fecha):
        yield '{"estado": "%d", "mensaje": "%s"},\n' % (400, "No se ingreso una fecha")
        return

    try:
        today = datetime.datetime.strptime(fecha, "%Y-%m-%d").date()
    except:
        yield '{"estado": "%d", "mensaje": "%s"},\n' % (400, "La fecha tiene un formato no valido")
        return

    apicookies = None
    authuser = User.objects.get(pk=user_id)

    try:
        user_profile = Profile.objects.get(user=authuser)
        if ((len(user_profile.garmin_user) > 0) and (len(user_profile.garmin_password) > 0)):
            usuario = user_profile.garmin_user
            password = user_profile.garmin_password
    except ObjectDoesNotExist:
        yield '{"estado": "%d", "mensaje": "%s"},\n' % (400,"No existe usuraio y clave garmin registrado")
        return

    try:
        cache = CacheData.objects.get(user=authuser)
        if (len(cache.garmincookies) > 0):
            apicookies = json.loads(cache.garmincookies)
    except ObjectDoesNotExist:
        apicookies = None
        
    api = GarminSession() 
    
    try:
        if (api.login(usuario,password, apicookies) == False):
            yield '{"estado": "%d", "mensaje": "%s"},\n' % (400,"Error al loguearse a Garmin")
            return
    except Exception as e:
        yield '{"estado": "%d", "mensaje": "%s"},\n' % (400,"Error inesperado al loguearse a Garmin:\\n" + str(e))
        return   

    if (api.saved_session is not None):
        try:
            cache = CacheData.objects.get(user=authuser)
            cache.garmincookies = json.dumps(api.saved_session)
        except ObjectDoesNotExist:
            cache = CacheData(user=authuser,garmincookies=json.dumps(api.saved_session))
        cache.save()

    yield '{"estado": "%d", "mensaje": "%s"},\n' % (200,"Obteniendo contactos")
    try:
        connections = api.get_connections()
    except:
        yield '{"estado": "%d", "mensaje": "%s"},\n' % (400,"Error al obtener contactos")
        return

    if (not(connections) or not(len(connections)>0) or not('userConnections' in connections) ):
        yield '{"estado": "%d", "mensaje": "%s"},\n' % (400, "Error al procesar contactos")
        return

    userConnections = connections['userConnections']

    data = {'Usuario':'','Actividades':0, 'Duracion':0}

    date_list = [today - datetime.timedelta(days=x) for x in range(7)]
    dates = {'Usuario' : ''}
    for d in date_list:
        dates[d] = []

    yield '{"estado": "%d", "mensaje": "%s"},\n' % (200,"Obteniendo actividades del usuario")

    try:
        activities = api.get_activities(0,25)
    except:
        yield '{"estado": "%d", "mensaje": "%s"},\n' % (400,"Error al obtener mis actividades")
        return

    if (not(activities) or not(len(activities)>0)):
        yield '{"estado": "%d", "mensaje": "%s"},\n' % (400,"Error al comenzar a procesar actividades")
        return

    try:
        data['Usuario'] = api.get_full_name()
        dates['Usuario'] = api.get_full_name()
    except:
        yield '{"estado": "%d", "mensaje": "%s"},\n' % (400,"Error al obtener mi nombre completo")
        return
    
    dur = 0
    for activitie in activities:
        if (activitie['activityType']['typeKey'] in ('running','indoor_cycling','lap_swimming','cycling','open_water_swimming','mountain_biking','treadmill_running','road_biking')):
            datetime_object = datetime.datetime.strptime(activitie['startTimeLocal'], '%Y-%m-%d %H:%M:%S')
            if ((datetime_object.date() in dates) and not(activitie['activityType']['typeKey'] in dates[datetime_object.date()])):
                dates[datetime_object.date()].append(activitie['activityType']['typeKey']) #dates[datetime_object.date()] + 1
                dur = dur + activitie['duration']

    for d in date_list:
        data['Actividades'] = data['Actividades'] + len(dates[d])

    data['Duracion'] = dur

    dateslist = []
    dateslist.append(dates)
    datalist = []
    datalist.append(data)

    for user in userConnections:

        data = {'Usuario':'','Actividades':0, 'Duracion':0}

        date_list = [today - datetime.timedelta(days=x) for x in range(7)]
        dates = {'Usuario' : ''}
        for d in date_list:
            dates[d] = []

        try:
            data['Usuario'] = user['fullName']
            dates['Usuario'] = user['fullName']
        except:
            yield '{"estado": "%d", "mensaje": "%s"},\n' % (400,"Error al obtener nombre completo del usuario numero " + str(user))
            return

        yield '{"estado": "%d", "mensaje": "%s"},\n' % (200,"Obteniendo actividades de " + user['fullName'])

        try:
            activities = api.get_connection_activities(user['displayName'],0,25)
        except:
            #return "Error al obtener actividades de " + user['fullName'], 403
            activities = {'activityList':[]}

        if (not(activities) or not(len(activities)>0) or not('activityList' in activities) ):
            yield '{"estado": "%d", "mensaje": "%s"},\n' % (400,"Error al comenzar a procesar actividades de " + user['fullName'])
            return

        dur = 0
        for activitie in activities['activityList']:
            if (activitie['activityType']['typeKey'] in ('running','indoor_cycling','lap_swimming','cycling','open_water_swimming','mountain_biking','treadmill_running','road_biking')):
                datetime_object = datetime.datetime.strptime(activitie['startTimeLocal'], '%Y-%m-%d %H:%M:%S')
                if ((datetime_object.date() in dates) and not(activitie['activityType']['typeKey'] in dates[datetime_object.date()])):
                    dates[datetime_object.date()].append(activitie['activityType']['typeKey']) #dates[datetime_object.date()] + 1
                    dur = dur + activitie['duration']

        for d in date_list:
            data['Actividades'] = data['Actividades'] + len(dates[d])

        data['Duracion'] = dur

        dateslist.append(dates)
        datalist.append(data)

    yield '{"estado": "%d", "mensaje": "%s"}' % (200,"Procesando datos")
    
    api.logout
    df = pd.DataFrame(datalist)
    df.sort_values(by=['Actividades','Duracion'], inplace=True, ascending=False)
    df['Duracion'] = df['Duracion'].apply(lambda x: str(mytimedelta(seconds=x)))
    df['Posicion'] = df.groupby(['Actividades']).ngroup(ascending=False) + 1
    
    yield '], "resultado" : ' + json.dumps(df.to_dict('records')) + '}'
    
    return 
