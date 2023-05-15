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
    path('GetFicheroSong/', viewsApi.GetFicheroSong, name='GetFicheroSong'),
    path('SetSong/', viewsApi.SetSong, name='SetSong'),
    path('SetUser/', viewsApi.SetUser, name='SetUser'),
    path('GetUser/', viewsApi.GetUser, name='GetUser'),
    path('ValidateUser/', viewsApi.ValidateUser, name='ValidateUser'),
    path('SetLista/', viewsApi.SetLista, name='SetLista'),
    path('GetListasUsr/', viewsApi.GetListasUsr, name='GetListasUsr'),
    path('RemoveListaRepUsr/', viewsApi.RemoveListaRepUsr, name='RemoveListaRepUsr'),
    path('GetAudiosLista/', viewsApi.GetAudiosLista, name='GetAudiosLista'),
    path('ChangeNameListRepUsr/', viewsApi.ChangeNameListRepUsr, name='ChangeNameListRepUsr'),
    path('SetSongLista/', viewsApi.SetSongLista, name='SetSongLista'),
    path('GetSongs/', viewsApi.GetSongs, name='GetSongs'),
    path('GetLista/', viewsApi.GetLista, name='GetLista'),
    path('RemoveSongLista/', viewsApi.RemoveSongLista, name='RemoveSongLista'),
    path('AskAdminToBeArtist/', viewsApi.AskAdminToBeArtist, name='AskAdminToBeArtist'),
    path('AcceptArtist/', viewsApi.AcceptArtist, name='AcceptArtist'),
    path('RejectArtista/', viewsApi.RejectArtista, name='RejectArtista'),
    path('ValidateUserEmail/', viewsApi.ValidateUserEmail, name='ValidateUserEmail'),
    path('GetTotRepTime/', viewsApi.GetTotRepTime, name='GetTotRepTime'),
    path('AddSecondsToSong/', viewsApi.AddSecondsToSong, name='AddSecondsToSong'),
    path('GetSongSeconds/', viewsApi.GetSongSeconds, name='GetSongSeconds'),
    path('SetFolder/', viewsApi.SetFolder, name='SetFolder'),
    path('AddListToFolder/', viewsApi.AddListToFolder, name='AddListToFolder'),
    path('RemoveListFromFolder/', viewsApi.RemoveListFromFolder, name='RemoveListFromFolder'),
    path('RemoveFolder/', viewsApi.RemoveFolder, name='RemoveFolder'),
    path('GetFolder/', viewsApi.GetFolder, name='GetFolder'),
    path('GetListasFolder/', viewsApi.GetListasFolder, name='GetListasFolder'),
    path('GetFoldersUsr/', viewsApi.GetFoldersUsr, name='GetFoldersUsr'),
    path('AskFriend/', viewsApi.AskFriend, name='AskFriend'),
    path('AcceptFriend/', viewsApi.AcceptFriend, name='AcceptFriend'),
    path('RejectFriend/', viewsApi.RejectFriend, name='RejectFriend'),
    path('GetFriends/', viewsApi.GetFriends, name='GetFriends'),
    path('RemoveFriend/', viewsApi.RemoveFriend, name='RemoveFriend'),
    path('SubscribeToArtist/', viewsApi.SubscribeToArtist, name='SubscribeToArtist'),
    path('UnsubscribeToArtist/', viewsApi.UnsubscribeToArtist, name='UnsubscribeToArtist'),
    path('GetSubscriptionsUsr/', viewsApi.GetSubscriptionsUsr, name='GetSubscriptionsUsr'),
    path('IsSubscribedToArtist/', viewsApi.IsSubscribedToArtist, name='IsSubscribedToArtist'),
    path('GetNotificationsUsr/', viewsApi.GetNotificationsUsr, name='GetNotificationsUsr'),
    path('GetNotification/', viewsApi.GetNotification, name='GetNotification'),
    path('RemoveNotification/', viewsApi.RemoveNotification, name='RemoveNotification'),
    path('SetLastSecondHeared/', viewsApi.SetLastSecondHeared, name='SetLastSecondHeared'),
    path('GetLastSecondHeared/', viewsApi.GetLastSecondHeared, name='GetLastSecondHeared'),
    path('GetLinkAudio/', viewsApi.GetLinkAudio, name='GetLinkAudio'),
    path('GetAudioFromLink/', viewsApi.GetAudioFromLink, name='GetAudioFromLink'),
    path('GetSongsArtist/', viewsApi.GetSongsArtist, name='GetSongsArtist'),
    path('RemoveUser/', viewsApi.RemoveUser, name='RemoveUser'),
    path('GetCauseError/', viewsApi.GetCauseError, name='GetCauseError'),
    path('GetEmailUsr/', viewsApi.GetEmailUsr, name='GetEmailUsr'),
    path('SetEmailUsr/', viewsApi.SetEmailUsr, name='SetEmailUsr'),
    path('GetAliasUsr/', viewsApi.GetAliasUsr, name='GetAliasUsr'),
    path('SetAliasUsr/', viewsApi.SetAliasUsr, name='SetAliasUsr'),
    path('GetContrasenyaUsr/', viewsApi.GetContrasenyaUsr, name='GetContrasenyaUsr'),
    path('SetContrasenyaUsr/', viewsApi.SetContrasenyaUsr, name='SetContrasenyaUsr'),
    path('GetTipoUsr/', viewsApi.GetTipoUsr, name='GetTipoUsr'),
    path('SetTipoUsr/', viewsApi.SetTipoUsr, name='SetTipoUsr'),
    path('GetImagenPerfilUsr/', viewsApi.GetImagenPerfilUsr, name='GetImagenPerfilUsr'),
    path('SetImagenPerfilUsr/', viewsApi.SetImagenPerfilUsr, name='SetImagenPerfilUsr'),
    path('GetNombreListaRep/', viewsApi.GetNombreListaRep, name='GetNombreListaRep'),
    path('SetNombreListaRep/', viewsApi.SetNombreListaRep, name='SetNombreListaRep'),
    path('GetPrivacidadListaRep/', viewsApi.GetPrivacidadListaRep, name='GetPrivacidadListaRep'),
    path('SetPrivacidadListaRep/', viewsApi.SetPrivacidadListaRep, name='SetPrivacidadListaRep'),
    path('GetNombreCarpeta/', viewsApi.GetNombreCarpeta, name='GetNombreCarpeta'),
    path('SetNombreCarpeta/', viewsApi.SetNombreCarpeta, name='SetNombreCarpeta'),
    path('GetPrivacidadCarpeta/', viewsApi.GetPrivacidadCarpeta, name='GetPrivacidadCarpeta'),
    path('SetPrivacidadCarpeta/', viewsApi.SetPrivacidadCarpeta, name='SetPrivacidadCarpeta'),
    path('GetUsuarioListaRep/', viewsApi.GetUsuarioListaRep, name='GetUsuarioListaRep'),
    path('GetImagenAudio/', viewsApi.GetImagenAudio, name='GetImagenAudio'),
    path('SetImagenAudio/', viewsApi.SetImagenAudio, name='SetImagenAudio'),
    path('GlobalSearch/', viewsApi.GlobalSearch, name='GlobalSearch'),
    path('echo/', viewsApi.echo, name='echo'),
    path('entrenar_recomendador/', viewsApi.entrenar_recomendador, name='entrenar_recomendador'),
    path('AlmacenarEjemplo/', viewsApi.AlmacenarEjemplo, name='AlmacenarEjemplo'),
    path('GetRecomendedAudio/', viewsApi.GetRecomendedAudio, name='GetRecomendedAudio'),
    path('GenerateRandomCodeUsr/', viewsApi.GenerateRandomCodeUsr, name='GenerateRandomCodeUsr'),
    path('RecuperarContrasenya/', viewsApi.RecuperarContrasenya, name='RecuperarContrasenya'),
    path('GetTopReproducciones/', viewsApi.GetTopReproducciones, name='GetTopReproducciones'),
    path('GetValoracion/', viewsApi.GetValoracion, name='GetValoracion'),
    path('GetValoracionMedia/', viewsApi.GetValoracionMedia, name='GetValoracionMedia'),
    path('SetValoracion/', viewsApi.SetValoracion, name='SetValoracion'),
    path('SetCalidadPorDefectoUsr/', viewsApi.SetCalidadPorDefectoUsr, name='SetCalidadPorDefectoUsr'),
    path('GetCalidadPorDefectoUsr/', viewsApi.GetCalidadPorDefectoUsr, name='GetCalidadPorDefectoUsr'),
    path('GetLinkAudio/', viewsApi.GetLinkAudio, name='GetLinkAudio'),
    path('GetAudioFromLink/', viewsApi.GetAudioFromLink, name='GetAudioFromLink'),
]
