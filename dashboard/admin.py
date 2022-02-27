from django.contrib import admin

# Register your models here.
from dashboard.models import (Sport, 
                              UserType, 
                              PlanningType, 
                              Plan, 
                              Activity,
                              PlanActivities,
                              AthleteCoach, 
                              GarminSport, 
                              GarminActivities, 
                              Team, 
                              Profile, 
                              GarminProfile,
                              )
from django import forms

from django.contrib.admin.widgets import FilteredSelectMultiple

class SportForm(forms.ModelForm):
    name = forms.CharField(max_length=100)
    sport = forms.ModelMultipleChoiceField(queryset=GarminSport.objects.all(), 
                                                  widget=FilteredSelectMultiple("sport", is_stacked=False), required=False)

    # garminsports = forms.ModelMultipleChoiceField(
    #     queryset=GarminSport.objects.all(), required=False
    # )

    class Meta:
        model = Sport
        fields = ["name","sport"]

    def __init__(self, *args, **kwargs):
        super(SportForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields["sport"].initial = self.instance.garminsport_set.all()

    def save_m2m(self):
        pass

    def save(self, *args, **kwargs):
        self.fields["sport"].initial.update(sport=None)
        sport_instance = Sport()
        sport_instance .pk = self.instance.pk
        sport_instance .name = self.instance.name
        sport_instance .save()
        self.cleaned_data["sport"].update(sport=sport_instance )
        return sport_instance 

class AthleteCoachForm(forms.ModelForm):
    coach = forms.CharField(max_length=100)
    athlete = forms.ModelMultipleChoiceField(queryset=AthleteCoach.objects.all(), 
                                                  widget=FilteredSelectMultiple("athlete", is_stacked=False), required=False)

    class Meta:
        model = AthleteCoach
        fields = ["coach","athlete"]

    def __init__(self, *args, **kwargs):
        super(AthleteCoachForm, self).__init__(*args, **kwargs)
        #if self.instance:
            #self.fields["athlete"].initial = self.instance.athlete_set.all()

    def save_m2m(self):
        pass

    def save(self, *args, **kwargs):
        self.fields["athlete"].initial.update(athlete=None)
        athlete_instance = AthleteCoach()
        athlete_instance.pk = self.instance.pk
        athlete_instance.name = self.instance.name
        athlete_instance.save()
        self.cleaned_data["athlete"].update(athlete=athlete_instance )
        return athlete_instance 


@admin.register(Sport)
class SportsAdmin(admin.ModelAdmin):
    form = SportForm

@admin.register(PlanningType)
class PlanningTypesAdmin(admin.ModelAdmin):
    pass

@admin.register(Plan)
class PlansAdmin(admin.ModelAdmin):
    pass

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    pass

@admin.register(PlanActivities)
class PlanActivitiesAdmin(admin.ModelAdmin):
    pass

@admin.register(AthleteCoach)
class AthleteCoachsAdmin(admin.ModelAdmin):
 #   form = AthleteCoachForm
    list_display = ['athlete','coach','plan']
    pass

@admin.register(GarminSport)
class GarminSportsAdmin(admin.ModelAdmin):
    pass

@admin.register(GarminActivities)
class GarminActivitiesAdmin(admin.ModelAdmin):
    list_display = ['tipo_actividad', 'garmin_sport', 'usuario_actividad', 'fecha_actividad']
    #pass

@admin.register(UserType)
class UserTypesAdmin(admin.ModelAdmin):
    pass

@admin.register(Team)
class TeamsAdmin(admin.ModelAdmin):
    pass

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass

@admin.register(GarminProfile)
class GarminProfileAdmin(admin.ModelAdmin):
    pass
