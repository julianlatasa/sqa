from django.shortcuts import render, redirect

# Create your views here.

from django.http import HttpResponse,StreamingHttpResponse
from django.template import loader
import json

from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, logout
from django.contrib.auth.models import User

from .models import (#Profile, 
                     GarminProfile,
                     GarminSport,
                     GarminActivities,
                     AthleteCoach, 
                     PlanActivities
                     )
from django.core.exceptions import ObjectDoesNotExist

from .GarminConnectSession import GarminSession
import datetime
import pytz
import pandas as pd
import numpy as np

#from django.db.models.functions import ExtractWeekDay
from django.db.models import Count, Sum

class mytimedelta(datetime.timedelta):
   def __str__(self):
      seconds = self.total_seconds()
      hours = seconds // 3600
      minutes = (seconds % 3600) // 60
      seconds = seconds % 60
      str = '{:02d}:{:02d}:{:02d}'.format(int(hours), int(minutes), int(seconds))
      return (str)

@ensure_csrf_cookie
@login_required(login_url='../login/')
def index(request):
    template = loader.get_template(r'dashboard/index.html')
    context = {'user_name' : request.user.first_name + ' ' + request.user.last_name} #'Julian Latasa'}
    #context = {'user_name' : 'Julian Latasa'}
    return HttpResponse(template.render(context, request))

@ensure_csrf_cookie
def logout_page(request):
    logout(request)
    return redirect('../../login/')

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
def plan(request):
    data = []
    inidate = datetime.datetime(2022,2,21,0,0,0).astimezone(pytz.UTC)
    findate = datetime.datetime(2022,2,28,0,0,0).astimezone(pytz.UTC)
    coach_user = User.objects.get(username="nsantander")
    atletas = AthleteCoach.objects.filter(coach=coach_user)
    for atleta in atletas:
        #print(atleta.athlete)
        atleta_user = atleta.athlete
        atleta_plan = atleta.plan
        datos = {'Usuario' : atleta.athlete.first_name + ' ' + atleta.athlete.last_name, 
                 'TotalPorc': 0, 
                 'TotalRealizado': 0,
                 'TotalPlan': 0,
                 'Duracion': 0
                 }
        #actividades = PlanActivities.objects.filter(plan=atleta.plan)
        #datos = atleta.objects.select_related('Plan') #, 'PlanActivities')
        #for actividad in actividades:
            #print(actividad.activity.sport_type)
            #print(actividad.date.weekday())
        #test = PlanActivities.objects.annotate(weekday=ExtractWeekDay('date')).values('weekday').annotate(total=Count('activity')).values('weekday','total' )
        #test = PlanActivities.objects.select_related('activity__sport_type__name').annotate(total=Count('activity')).values('activity__sport_type__name','total' )
        planificacion = PlanActivities.objects.filter(plan=atleta_plan).select_related('activity__sport_type__name').values('activity__sport_type__name').annotate(total=Count('activity'))
        for planificado in planificacion:
            datos[planificado['activity__sport_type__name']+'Plan'] = planificado['total']
            datos['TotalPlan'] = datos['TotalPlan']+ planificado['total']
            #print(t)
        cumplido = GarminActivities.objects.filter(user=atleta_user).filter(datetime__range=[inidate, findate]).values('garmin_sport__sport__name').annotate(total=Count('garmin_activity_id')).annotate(duracion=Sum('duration'))
        for realizado in cumplido:
            datos[realizado['garmin_sport__sport__name']+'Realizado'] = realizado['total']
            datos[realizado['garmin_sport__sport__name']+'Duracion'] = str(mytimedelta(seconds=realizado['duracion'])) 
            #datos[realizado['garmin_sport__sport__name']+'Realizado'] = realizado['total']
            datos[realizado['garmin_sport__sport__name']+'Porc'] = realizado['total'] / datos[realizado['garmin_sport__sport__name']+'Plan'] * 100
            datos['TotalRealizado'] = datos['TotalRealizado']+ realizado['total']
            datos['Duracion'] = datos['Duracion'] + realizado['duracion']
            #print(t)
        datos['TotalPorc'] = datos['TotalRealizado'] / datos['TotalPlan'] * 100
        datos['TotalDuracion'] = str(mytimedelta(seconds=datos['Duracion'])) 
        data.append(datos)
                    
    template = loader.get_template(r'dashboard/plan_result.html')
    
    df = pd.DataFrame(data).replace({np.nan:0})
    df.sort_values(by=['Duracion'], inplace=True, ascending=False)

    df["NatacionRealizado"] = df["NatacionRealizado"].astype(int)

    context = {'result' : df.to_dict('records')}
    #return HttpResponse("Hola")
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

@csrf_exempt
def rankingresult(request):
     data = json.loads( request.body.decode('utf8').replace("'", '"')  )

     template = loader.get_template(r'dashboard/ranking_result.html')
     context = {'result' : data}

     return HttpResponse(template.render(context, request))

class ErrorLoginGarmin(Exception):
    pass

class GarminProfileDontExist(Exception):
    pass


class GarminData:
    def __init__(self, request):
        self.__user = User.objects.get(pk=request.user.pk)
        self.__apicookies = None
        self.__username = None
        self.__password = None
        self.__api = None
        self.__logged_in = False
        
    def activities_of(self, start, end, user=None):
        if (self.__logged_in == False):
            if (self.__login() == False):
                return None
        api = self.__api
        activities = None
        try:
            if (user is None):        
                activities = api.get_activities(start,end)
            else:
                activities = api.get_connection_activities(user,start,end)
        except:
            return None

        if ((activities) and (len(activities)>0)):
            return activities

    def connections(self):
        connections = None
        if (self.__logged_in == False):
            if (self.__login() == False):
                return None

        api = self.__api
        try:
            connections = api.get_connections()
        except:
            return None
        
        if ( (connections) and (len(connections)>0) and ('userConnections' in connections) ):
            return connections['userConnections']

    def download_activity(self, activity_id):
        if (self.__logged_in == False):
            if (self.__login() == False):
                return None
        api = self.__api
        return api.download_activity(activity_id, dl_fmt=api.ActivityDownloadFormat.ORIGINAL)
    
    def __login(self):
        user = self.__user
        if (self.__load_data_of(user) == False):
            raise ErrorLoginGarmin()
        
        username = self.__username
        password = self.__password
        apicookies = self.__apicookies
        
        api = GarminSession(username,password, session_data=apicookies) 
        
        try:
            if (api.login() == False):
                return False
        except Exception as e:
            return False        

        self.__api = api

        if (api.session_data is not None):
            self.__save_data_of(user)
            
        self.__logged_in = True
        return True

    def __load_data_of(self, user):
        user_profile = None
        try:
            user_profile = GarminProfile.objects.get(user=user)
            if (len(user_profile.garmincookies) > 0):
                self.__apicookies = json.loads(user_profile.garmincookies)
            if ((len(user_profile.garmin_user) > 0) and (len(user_profile.garmin_password) > 0)):
                self.__username = user_profile.garmin_user
                self.__password = user_profile.garmin_password
        except ObjectDoesNotExist:
            raise GarminProfileDontExist()
        return True
    
    def __save_data_of(self, user):
        api = self.__api
        try:
            user_profile = GarminProfile.objects.get(user=user)
            user_profile.garmincookies = json.dumps(api.session_data)
        except ObjectDoesNotExist:
            user_profile = GarminProfile(user=user,garmincookies=json.dumps(api.session_data))
        user_profile.save()
        
from zipfile import ZipFile
import io
import fitdecode

class GarminActivity():
    def __init__(self, activity_id, content):
        self.activity_id = activity_id
        self.content = content
    
    def __zip(self):
        return_value = None
        zip_file = ZipFile(io.BytesIO(self.content))
        return_value = zip_file.read(self.activity_id + '_ACTIVITY.fit')
        zip_file.close()
        return return_value
        
    def sport(self):
        activity_data = self.__zip()
        sport = self.get_dataframes(activity_data)
        return sport
    
    def get_dataframes(self, data):
        sport = None
        with fitdecode.FitReader(data) as fit_file:
            for frame in fit_file:
                if isinstance(frame, fitdecode.records.FitDataMessage):
                    if frame.name == 'sport':
                        sport = frame.get_value('sport')
        
        return sport



@csrf_exempt
def activities(request):
    garmin_data = GarminData(request)
    user = request.user
    http = StreamingHttpResponse( stream_activities(garmin_data, user), content_type='text/plain' , headers = {'X-Accel-Buffering' : 'no'} )

    return http

@csrf_exempt
def stream_activities(garmin_data, user):
    conns = garmin_data.connections()
    for c in conns:
        yield c        
    for activity in GarminActivities.objects.filter(user=user):
        if (activity.garmin_file):
            ga = GarminActivity(activity.garmin_activity_id,activity.garmin_file)
            yield  ga.sport() + ' - ' + activity.garmin_sport.name
    return
    #for activity in GarminActivities.objects.filter(user=user):
    #    yield 'actividad pedida: ' + activity.garmin_activity_id + '\n'
    #    garmin_file = garmin_data.download_activity(activity.garmin_activity_id)
    #    yield 'actividad guardada: ' + activity.garmin_activity_id + '\n'
    #    if not(garmin_file == None):
    #        activity.garmin_file = garmin_file
    #        activity.save()
            


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
        user_profile = GarminProfile.objects.get(user=authuser)
        if (len(user_profile.garmincookies) > 0):
            apicookies = json.loads(user_profile.garmincookies)
        if ((len(user_profile.garmin_user) > 0) and (len(user_profile.garmin_password) > 0)):
            usuario = user_profile.garmin_user
            password = user_profile.garmin_password
    except ObjectDoesNotExist:
        yield '{"estado": "%d", "mensaje": "%s"},\n' % (400,"No existe usuraio y clave garmin registrado")
        return

        
    api = GarminSession(usuario,password, session_data=apicookies) 
    
    try:
        if (api.login() == False):
            yield '{"estado": "%d", "mensaje": "%s"},\n' % (400,"Error al loguearse a Garmin")
            return
    except Exception as e:
        yield '{"estado": "%d", "mensaje": "%s"},\n' % (400,"Error inesperado al loguearse a Garmin:\\n" + str(e))
        return   

    if (api.session_data is not None):
        try:
            user_profile = GarminProfile.objects.get(user=authuser)
            user_profile.garmincookies = json.dumps(api.session_data)
        except ObjectDoesNotExist:
            user_profile = GarminProfile(user=authuser,garmincookies=json.dumps(api.session_data))
        user_profile.save()

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

        try:
            garmin_sport_obj = GarminSport.objects.get(name=activitie['activityType']['typeKey'])
            try:        
                garmin_activity = GarminActivities.objects.get(garmin_activity_id=activitie['activityId'])
            except ObjectDoesNotExist:
                localdatetime = datetime.datetime.strptime(activitie['startTimeLocal'], "%Y-%m-%d %H:%M:%S").astimezone(pytz.timezone("America/Buenos_Aires"))
                garmin_activity = GarminActivities(datetime=localdatetime,
                                                   user=authuser,
                                                   garmin_activity_id=activitie['activityId'],
                                                   garmin_sport=garmin_sport_obj,
                                                   duration=activitie['duration'],
                                                   garmin_object=json.dumps(activitie))
    #                                               garmin_file)
            garmin_activity.save()
        except ObjectDoesNotExist:
            print(activitie['activityType']['typeKey'])
        
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

        profile_id = user['userId']

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
            try:
                garmin_sport_obj = GarminSport.objects.get(name=activitie['activityType']['typeKey'])
                garmin_user = GarminProfile.objects.get(garmin_id=user['displayName'])
                try:        
                    garmin_activity = GarminActivities.objects.get(garmin_activity_id=activitie['activityId'])
                except ObjectDoesNotExist:
                    localdatetime = datetime.datetime.strptime(activitie['startTimeLocal'], "%Y-%m-%d %H:%M:%S").astimezone(pytz.timezone("America/Buenos_Aires"))
                    garmin_activity = GarminActivities(datetime=localdatetime,
                                                       user=garmin_user.user,
                                                       garmin_activity_id=activitie['activityId'],
                                                       garmin_sport=garmin_sport_obj,
                                                       duration=activitie['duration'],
                                                       garmin_object=json.dumps(activitie))
        #                                               garmin_file)
                garmin_activity.save()
            except ObjectDoesNotExist:
                print(activitie['activityType']['typeKey'])
                print(user['displayName'])

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
    
    #api.logout
    df = pd.DataFrame(datalist)
    df.sort_values(by=['Actividades','Duracion'], inplace=True, ascending=False)
    df['Duracion'] = df['Duracion'].apply(lambda x: str(mytimedelta(seconds=x)))
    df['Posicion'] = df.groupby(['Actividades']).ngroup(ascending=False) + 1
    
    yield '], "resultado" : ' + json.dumps(df.to_dict('records')) + '}'
    
    return 
