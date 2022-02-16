from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse, StreamingHttpResponse
from django.template import loader


import garminconnect
import datetime
import pandas as pd

cache = {}

class mytimedelta(datetime.timedelta):
   def __str__(self):
      seconds = self.total_seconds()
      hours = seconds // 3600
      minutes = (seconds % 3600) // 60
      seconds = seconds % 60
      str = '{:02d}:{:02d}:{:02d}'.format(int(hours), int(minutes), int(seconds))
      return (str)


class Garmin(garminconnect.Garmin):
    """Class for fetching data from Garmin Connect."""

    def get_connections_count(self):  #
        """Fetch available heart rates data 'cDate' format 'YYYY-mm-dd'."""
        self.garmin_connect_connections_count_url = "proxy/connection-service/connection/connections/count"

        url = f"{self.garmin_connect_connections_count_url}"

        return self.modern_rest_client.get(url).json()


    def get_connections(self):  #
        """Fetch available heart rates data 'cDate' format 'YYYY-mm-dd'."""
        self.garmin_connect_connections_url = (
            "proxy/connection-service/connection/connections/pagination"
        )

        url = f"{self.garmin_connect_connections_url}/{self.display_name}"
        params = {
            "start": str(1),
            "limit": str(self.get_connections_count()),
        }

        return self.modern_rest_client.get(url, params=params).json()

    def get_connection_activities(self, connection_display_name, start, limit):
        """Return available activities."""
        self.garmin_connect_connection_activities = (
            "proxy/activitylist-service/activities"
        )

        url = f"{self.garmin_connect_connection_activities}/{connection_display_name}"
        params = {"start": str(start), "limit": str(limit)}

        return self.modern_rest_client.get(url, params=params).json()

cache = {}

from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie

@ensure_csrf_cookie
def index(request):
    template = loader.get_template(r'ranking\index.html')
    context = {}
    return HttpResponse(template.render(context, request))

@csrf_exempt
def resultado(request):
     #data = [{'Usuario':'Nestor Santander ','Actividades':6,'Duracion':94348.390137},{'Usuario':'Sofia Pierantoni ','Actividades':6,'Duracion':19285.46582},{'Usuario':'Stelli ','Actividades':5,'Duracion':19879.184326},{'Usuario':'Zampo ','Actividades':5,'Duracion':19628.871094},{'Usuario':'degreefnacho ','Actividades':5,'Duracion':19588.374756},{'Usuario':'Guillermo Pagano ','Actividades':5,'Duracion':16861.946045},{'Usuario':'Julian Latasa ','Actividades':4,'Duracion':16469.471924},{'Usuario':'Gabriel Marti ','Actividades':4,'Duracion':15276.486816},{'Usuario':'PAOLA ','Actividades':4,'Duracion':11683.031982},{'Usuario':'lucasmartino88 ','Actividades':3,'Duracion':12260.957031},{'Usuario':'Osvaldo Victorel ','Actividades':3,'Duracion':11582.469849},{'Usuario':'Matías Lacoppola ','Actividades':3,'Duracion':11109.210449},{'Usuario':'Martin Escurra ','Actividades':2,'Duracion':8044.748047},{'Usuario':'Pedro Rocca ','Actividades':2,'Duracion':5875.759033},{'Usuario':'Alejandro Avalos ','Actividades':0,'Duracion':0.0},{'Usuario':'Ariel Gonzalez ','Actividades':0,'Duracion':0.0},{'Usuario':'Fernando Goya ','Actividades':0,'Duracion':0.0},{'Usuario':'Sebastian Pollo salerno ','Actividades':0,'Duracion':0.0},{'Usuario':'Tomas Scally ','Actividades':0,'Duracion':0.0}]
     data = cache['data']
     cache['data'] = None
     df = pd.DataFrame(data)
     df.sort_values(by=['Actividades','Duracion'], inplace=True, ascending=False)
     df['Duracion'] = df['Duracion'].apply(lambda x: str(mytimedelta(seconds=x)))
     df['Posicion'] = df.groupby(['Actividades']).ngroup(ascending=False) + 1    #df.sort_values(by=['Actividades','Duracion'], inplace=True, ascending=False)

     template = loader.get_template(r'ranking\ranking.html')
     context = {'result' : df.to_dict('records'),}

     return HttpResponse(template.render(context, request))


import json
#@csrf_exempt
def ranking(request):
    if (request.method == 'POST'):
        datajson = json.loads( request.body.decode('utf8').replace("'", '"')  )
        usuario = datajson['usuario']
        password = datajson['password']
        fecha = datajson['fecha']
    resp = StreamingHttpResponse( stream_response_generator(usuario, password, fecha), content_type='text/plain')
    #resp = HttpResponse('Usuario: ' + usuario)
    return resp

def stream_response_generator(usuario, password, fecha):
   #usuario = 'julianlatasa@gmail.com'
    #password = 'Julian80'
    #fecha = '2022-02-13'
    yield "Iniciando consulta\n" 
        
    if ((not usuario) or (not password)):
        return "No se ingreso un usuario o una clave" 
    
    if (not fecha):
        return "No se ingreso una fecha",403

    try:
        today = datetime.datetime.strptime(fecha, "%Y-%m-%d").date()
    except:
        return "La fecha tiene un formato no valido", 403

    api = Garmin(usuario, password)
    try:
        if (api.login() == False):
            return "Error al loguearse a Garmin", 403
    except:
        return "Error inesperado al loguearse a Garmin", 403

    yield "Obteniendo contactos\n"
    
    try:
        connections = api.get_connections()
    except:
        return "Error al obtener contactos", 403

    if (not(connections) or not(len(connections)>0) or not('userConnections' in connections) ):
        return "Error al procesar contactos", 403

    userConnections = connections['userConnections']

    data = {'Usuario':'','Actividades':0, 'Duracion':0}

    date_list = [today - datetime.timedelta(days=x) for x in range(7)]
    dates = {'Usuario' : ''}
    for d in date_list:
        dates[d] = []

    yield "Obteniendo actividades del usuario\n"
    
    try:
        activities = api.get_activities(0,25)
    except:
        return "Error al obtener mis actividades", 403

    if (not(activities) or not(len(activities)>0)):
        return "Error al comenzar a procesar actividades", 403

    try:
        data['Usuario'] = api.get_full_name()
        dates['Usuario'] = api.get_full_name()
    except:
        return "Error al obtener mi nombre completo", 403

    dur = 0
    for activitie in activities:
        if (activitie['activityType']['typeKey'] in ('running','indoor_cycling','lap_swimming','cycling','open_water_swimming','mountain_biking','treadmill_running','road_biking')):
            datetime_object = datetime.datetime.strptime(activitie['startTimeLocal'], '%Y-%m-%d %H:%M:%S')
            if ((datetime_object.date() in dates) and not(activitie['activityType']['typeKey'] in dates[datetime_object.date()])):
                dates[datetime_object.date()].append(activitie['activityType']['typeKey']) #dates[datetime_object.date()] + 1
            #if (today >= datetime_object.date() > lastweek):
                #data['Actividades'] = data['Actividades'] + 1
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
            return "Error al obtener nombre completo del usuario numero " + str(user), 403

        yield "Obteniendo actividades de " + user['fullName'] + "\n"
        
        try:
            activities = api.get_connection_activities(user['displayName'],0,25)
        except:
            #return "Error al obtener actividades de " + user['fullName'], 403
            activities = {'activityList':[]}

        if (not(activities) or not(len(activities)>0) or not('activityList' in activities) ):
            return "Error al comenzar a procesar actividades de " + user['fullName'], 403

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

        cache['data'] = datalist

        api.logout
   