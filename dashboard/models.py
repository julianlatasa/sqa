from django.db import models

# Create your models here.

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

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

class AthleteCoach(models.Model):
    athlete = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='athlete')
    coach = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='coach')
    planning_type = models.ForeignKey(PlanningType, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.coach}"

class GarminSport(models.Model):
    name = models.CharField(max_length=100)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name

class GarminActivity(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    garmin_activity_id = models.CharField(max_length=200, blank=True)
    garmin_sport = models.OneToOneField(GarminSport, on_delete=models.CASCADE)    
    date = models.DateField(null=True, blank=True)
    duration = models.BigIntegerField(null=True, blank=True)

class Team(models.Model):
    name = models.CharField(max_length=100, null=False, blank=True, default='')

    def __str__(self):
        return f"{self.name}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, blank=True, null=True)
    usertype = models.ForeignKey(UserType, on_delete=models.CASCADE, blank=True, null=True)
    #usertype = models.OneToOneField(UserType, on_delete=models.CASCADE, null=True, blank=True)
    garmin_user = models.CharField(max_length=200, blank=True)
    garmin_id = models.CharField(max_length=200, blank=True)
    garmin_password = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    weight = models.DecimalField(max_digits = 5, decimal_places = 2, blank=True)
    height = models.DecimalField(max_digits = 5, decimal_places = 2, blank=True)

    def __str__(self):
        return f"{self.user.username, self.garmin_user}"

class CacheData(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    garmincookies = models.TextField(blank=True)
    cache = models.TextField(blank=True)

    
#@receiver(post_save, sender=User)
#def create_user_profile(sender, instance, created, **kwargs):
#    if created:
#        Profile.objects.create(user=instance)

#@receiver(post_save, sender=User)
#def save_user_profile(sender, instance, **kwargs):
#    instance.profile.save()