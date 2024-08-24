from django.contrib import admin
from django.urls import path
from day import views

urlpatterns = [
    path('', views.index,name='index'),
  
    path('main/', views.main, name='main'),  # Add this line
   
]
