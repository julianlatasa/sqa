# -*- coding: utf-8 -*-
"""
Created on Mon Feb 14 08:11:18 2022

@author: U54979
"""

from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('calendar/', views.calendar, name='calendar'),
    path('weekplan/', views.weekplan, name='weekplan'),
    path('ranking/', views.ranking, name='ranking'),
    path('ranking/query/', views.rankingquery, name='rankingquery'),
    path('ranking/result/', views.rankingresult, name='rankingresult'),
]