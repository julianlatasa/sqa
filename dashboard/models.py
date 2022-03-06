from django.db import models

# Create your models here.

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.contrib import admin

class Sport(models.Model):
    name = models.CharField(max_length=100, null=False, blank=True, default='')

    def __str__(self):
        return f"{self.name}"

class UserType(models.Model):
    name = models.CharField(max_length=100, null=False, blank=True, default='')

    def __str__(self):
        return f"{self.name}"

class PlanningType(models.Model):
    name = models.CharField(max_length=100, null=False, blank=True, default='')

    def __str__(self):
        return f"{self.name}"

class Plan(models.Model):
    name = models.CharField(max_length=100, null=False, blank=True, default='')
    planning_type = models.ForeignKey(PlanningType, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.name}"

class Activity(models.Model):
    name = models.CharField(max_length=100, null=False, blank=True, default='')
    sport_type = models.ForeignKey(Sport, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.name}"

class PlanActivities(models.Model):
    order = models.IntegerField(blank=True,null=True)
    date = models.DateField(null=True, blank=True)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, blank=True, related_name='actividades')
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, blank=True, related_name='planificado')

    def __str__(self):
        return f"{self.activity.name}"

class AthleteCoach(models.Model):
    athlete = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='athlete')
    coach = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='coach')
    planning_type = models.ForeignKey(PlanningType, on_delete=models.CASCADE, blank=True, null=True)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.coach}, {self.athlete}"

class GarminSport(models.Model):
    name = models.CharField(max_length=100)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.name}"

import pytz

class GarminActivities(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    garmin_activity_id = models.CharField(max_length=200, blank=True)
    garmin_sport = models.ForeignKey(GarminSport, on_delete=models.CASCADE)    
    datetime = models.DateTimeField(null=True, blank=True)
    duration = models.BigIntegerField(null=True, blank=True)
    garmin_object = models.TextField(blank=True)
    garmin_file = models.BinaryField(blank=True, editable=False, null=True)


    @admin.display(description='Fecha')
    def fecha_actividad(self):
        return self.datetime.astimezone(pytz.timezone("America/Buenos_Aires")).strftime("%d/%m/%Y, %H:%M:%S")

    @admin.display(description='Usuario')
    def usuario_actividad(self):
        return f"{self.user.first_name} {self.user.last_name}"

    @admin.display(description='Tipo Actividad')
    def tipo_actividad(self):
        return f"{self.garmin_sport.sport.name}"

    def __str__(self):
        return f"{self.garmin_sport.name}, {self.user.username}, {self.datetime}"

class Team(models.Model):
    name = models.CharField(max_length=100, null=False, blank=True, default='')

    def __str__(self):
        return f"{self.name}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, blank=True, null=True)
    usertype = models.ForeignKey(UserType, on_delete=models.CASCADE, blank=True, null=True)
    #usertype = models.OneToOneField(UserType, on_delete=models.CASCADE, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    weight = models.DecimalField(max_digits = 5, decimal_places = 2, blank=True, default=0)
    height = models.DecimalField(max_digits = 5, decimal_places = 2, blank=True, default=0)

    def __str__(self):
        return f"{self.user.username}"

class GarminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    garmin_id = models.CharField(max_length=200, blank=True, null=True)
    garmin_user_id = models.CharField(max_length=10, blank=True, null=True)
    garmincookies = models.TextField(blank=True, null=True)
    garmin_user = models.CharField(max_length=200, blank=True, null=True)
    garmin_password = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}"
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        GarminProfile.objects.create(user=instance)

#@receiver(post_save, sender=User)
#def save_user_profile(sender, instance, **kwargs):
#    instance.Profile.save()
#    instance.GarminProfile.save()

    