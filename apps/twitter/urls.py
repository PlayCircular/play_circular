# coding=utf-8
from django.conf.urls import patterns, include, url

urlpatterns = patterns('twitter.views',
	
	#url('^mis_seguimientos/$', 'mis_seguimientos', name='social-mis-contactos'),
	url(r'^perfil_social/(?P<username>([^/]+))/$', 'ver_perfil_social', name="social-perfil"),
	url('^seguir/$', 'seguir', name='social-seguir'),
	url('^escribir/$', 'escribir', name='social-escribir'),
	url('^reescribir/(?P<mensaje_id>\d+)/$', 'reescribir', name='social-reescribir'),
	url('^responder/(?P<mensaje_id>\d+)/$', 'responder', name='social-responder'),
	url('^borrar/(?P<mensaje_id>\d+)/$', 'borrar', name='social-borrar'),
	url('^conversacion/(?P<mensaje_id>\d+)/$', 'conversacion', name='social-conversacion'),
	url('^conversacion/(?P<mensaje_id>\d+)/page/(?P<page>\d+)/$', 'conversacion', name='social-conversacion'),
	url('^buscar/(?P<busqueda>([A-Za-z0-9_-]+))/(?P<opcion>[1-2]{1})/$', 'buscar', name='social-buscar'),
	#url('^buscar/(?P<busqueda>#([A-Za-z0-9_]+))/(?P<opcion>[1-2]{1})/page/(?P<page>\d+)/$', 'buscar', name='social-buscar'),


)