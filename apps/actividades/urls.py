# coding=utf-8

# Copyright (C) 2014 by Víctor Romero Blanco <info at playcircular dot com>.
# http://playcircular.com/
# It's licensed under the AFFERO GENERAL PUBLIC LICENSE unless stated otherwise.
# You can get copies of the licenses here: http://www.affero.org/oagpl.html
# AFFERO GENERAL PUBLIC LICENSE is also included in the file called "LICENSE".

#Eliminado en django 1.6
#from django.conf.urls.defaults import *
from django.conf.urls import patterns, url
from actividades.models import *
from actividades.views import *

urlpatterns = patterns('actividades.views',

	url(r'^todas/$', 'actividades', name='actividades'),
	url(r'^usuario/(?P<id_usuario>\d+)/$', 'actividades', name='actividad-usuario'),
	url(r'^(?P<clase>(bienes|servicios))/$', 'actividades', name='actividad-clase'),
	url(r'^(?P<simbolo>([^/]+))/actividades/$', 'actividades_grupo', name='actividad-grupo'),
	url(r'^(?P<clase>(bienes|servicios))/(?P<tipo>(oferta|demanda))/(?P<id_objeto>\d+)/(?P<slug>([^/]+))$', 'ver_actividad', name="ver-actividad"),
	url(r'^valorar_actividades/(?P<pagina>\d+)/(?P<ajax>(si|no))/$', 'valorar_actividades', name='actividad-valorar'),
	url(r'^valorar_actividad/$', 'valorar_actividad', name='actividad-valorar-ajax'),
	url(r'^busqueda_actividad/$', 'busqueda_actividad', name='actividad-busqueda'),
	url(r'^favoritos/$', 'mis_favoritos', name='actividad-mis-favoritos'), 
	url(r'^tag/(?P<tag>([A-Za-z0-9_-]+))','actividades_clasificadas', name='actividad-tag'),
	url(r'^categoria/(?P<id_categoria>\d+)/$','actividades_clasificadas', name='actividad-categoria'),

)
