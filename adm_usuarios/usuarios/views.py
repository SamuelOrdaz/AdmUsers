from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .jason import json_serializer
from django.http import HttpResponse

#Pagina API
def api(request):    
    queryset = json_serializer(request)
    return render(request, "API.html", {"API": queryset})
#Pagina de Inicio   
def index(request):
    return render(request, "index.html")
