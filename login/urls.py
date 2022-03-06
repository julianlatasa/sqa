# -*- coding: utf-8 -*-
"""
Created on Mon Feb 14 08:11:18 2022

@author: U54979
"""

from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_page, name='login_page'),
]