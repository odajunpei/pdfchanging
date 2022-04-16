from django.contrib import admin
from django.urls import path
from . import views

app_name ="pdfchanging"

urlpatterns = [
    path('top/', views.top, name='top'),
]
