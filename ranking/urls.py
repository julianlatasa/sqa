# -*- coding: utf-8 -*-
"""
Created on Mon Feb 14 08:11:18 2022

@author: U54979
"""

from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('resultado/', views.resultado, name='resultado'),
    path('ranking/', views.ranking, name='ranking'),
]