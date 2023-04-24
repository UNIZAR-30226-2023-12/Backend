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
from django.urls import path, include, re_path
from frontApi import views as viewsApi
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Melodia REST API",
        default_version='v1',
        description="API to access database storage of both apps.",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="testing@api.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('GetSong/', viewsApi.GetSong, name='GetSong'),
    path('GetFicheroSong/', viewsApi.GetFicheroSong, name='GetFicheroSong'),
    path('SetSong/', viewsApi.SetSong, name='SetSong'),
    path('SetUser/', viewsApi.SetUser, name='SetUser'),
    path('ValidateUser/', viewsApi.ValidateUser, name='ValidateUser'),
    path('SetLista/', viewsApi.SetLista, name='SetLista'),
    path('GetListasUsr/', viewsApi.GetListasUsr, name='GetListasUsr'),
    path('GetAudiosLista/', viewsApi.GetAudiosLista, name='GetAudiosLista'),
    path('ChangeNameListRepUsr/', viewsApi.ChangeNameListRepUsr, name='ChangeNameListRepUsr'),
    path('SetSongLista/', viewsApi.SetSongLista, name='SetSongLista'),
    path('GetSongs/', viewsApi.GetSongs, name='GetSongs'),
    path('GetLista/', viewsApi.GetLista, name='GetLista'),
    path('RemoveSongLista/', viewsApi.RemoveSongLista, name='RemoveSongLista'),
    path('AskAdminToBeArtist/', viewsApi.AskAdminToBeArtist, name='AskAdminToBeArtist'),
    path('AcceptArtist/', viewsApi.AcceptArtist, name='AcceptArtist'),
    path('ValidateUserEmail/', viewsApi.ValidateUserEmail, name='ValidateUserEmail'),
    path('GetTotRepTime/', viewsApi.GetTotRepTime, name='GetTotRepTime'),
    path('AddSecondsToSong/', viewsApi.AddSecondsToSong, name='AddSecondsToSong'),
    path('SetFolder/', viewsApi.SetFolder, name='SetFolder'),
    path('AddListToFolder/', viewsApi.AddListToFolder, name='AddListToFolder'),
    path('RemoveListFromFolder/', viewsApi.RemoveListFromFolder, name='RemoveListFromFolder'),
    path('RemoveFolder/', viewsApi.RemoveFolder, name='RemoveFolder'),
    path('GetFolder', viewsApi.GetFolder, name='GetFolder'),
    path('GetListasFolder/', viewsApi.GetListasFolder, name='GetListasFolder'),
    path('GetFoldersUsr/', viewsApi.GetFoldersUsr, name='GetFoldersUsr'),
    path('AskFriend/', viewsApi.AskFriend, name='AskFriend'),
    path('AcceptFriend/', viewsApi.AcceptFriend, name='AcceptFriend'),
    path('GetFriends/', viewsApi.GetFriends, name='GetFriends'),
    path('RemoveFriend/', viewsApi.RemoveFriend, name='RemoveFriend'),
    path('echo/', viewsApi.echo, name='echo'),
    path('entrenar_recomendador/', viewsApi.entrenar_recomendador, name='entrenar_recomendador'),
    re_path(r'^docs/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui')
]
