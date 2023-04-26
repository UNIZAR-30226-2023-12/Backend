"""backendCore URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from frontApi import views as viewsApi

urlpatterns = [
    path('admin/', admin.site.urls),
    path('GetSong/', viewsApi.GetSong, name='GetSong'),
    path('SetSong/', viewsApi.SetSong, name='SetSong'),
    path('SetUser/', viewsApi.SetUser, name='SetUser'),
    path('GetUser/', viewsApi.GetUser, name='GetUser'),
    path('ValidateUser/', viewsApi.ValidateUser, name='ValidateUser'),
    path('SetLista/', viewsApi.SetLista, name='SetLista'),
    path('ChangeNameListRepUsr/', viewsApi.ChangeNameListRepUsr, name='ChangeNameListRepUsr'),
    path('SetSongLista/', viewsApi.SetSongLista, name='SetSongLista'),
    path('GetSongs/', viewsApi.GetSongs, name='GetSongs'),
    path('GetListaRepUsr/', viewsApi.GetListaRepUsr, name='GetListaRepUsr'),
    path('RemoveSongLista/', viewsApi.RemoveSongLista, name='RemoveSongLista'),
    path('AskAdminToBeArtist/', viewsApi.AskAdminToBeArtist, name='AskAdminToBeArtist'),
    path('AcceptArtist/', viewsApi.AcceptArtist, name='AcceptArtist'),
    path('ValidateUserEmail/', viewsApi.ValidateUserEmail, name='ValidateUserEmail'),
    path('GlobalSearch/', viewsApi.GlobalSearch, name='GlobalSearch'),
    path('echo/', viewsApi.echo, name='echo'),
    path('entrenar_recomendador/', viewsApi.entrenar_recomendador, name='entrenar_recomendador'),
    path('AlmacenarEjemplo/', viewsApi.AlmacenarEjemplo, name='AlmacenarEjemplo'),
]
