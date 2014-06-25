# coding=utf-8


# Copyright (C) 2014 by Víctor Romero Blanco <info at playcircular dot com>.
# http://playcircular.com/
# It's licensed under the AFFERO GENERAL PUBLIC LICENSE unless stated otherwise.
# You can get copies of the licenses here: http://www.affero.org/oagpl.html
# AFFERO GENERAL PUBLIC LICENSE is also included in the file called "LICENSE".


from django.conf.urls import patterns, url
from django.conf import settings
from grupos.models import *

urlpatterns = patterns('grupos.views',

    url(r'^$', 'index', name='grupos-index'),
    url(r'^solicita_ser_miembro/(?P<id_grupo>\d+)/$', 'solicita_ser_miembro', name='grupos-solicitud-miembro'),
     url(r'^administradores/(?P<id_grupo>\d+)/$', 'get_admins', name='grupos-get-admins'),
    url(r'^estadisticas_grupo/(?P<id_grupo>\d+)/$', 'estadisticas_grupo', name='grupos-estadisticas'),
    url(r'^crecimiento_usuarios/(?P<id_grupo>\d+)/$', 'estadisticas_crecimiento_usuarios', name='grupos-estadis-crecimiento_usus'),
    url(r'^balance_usuarios/(?P<id_grupo>\d+)/$', 'balance_usuarios', name='grupos-balance-usus'),
    url(r'^estadisticas_actividad/(?P<id_grupo>\d+)/$', 'estadisticas_actividad', name='grupos-estadis-actividad'),
    url(r'^estadisticas_intercambio/(?P<id_grupo>\d+)/$', 'estadisticas_intercambio', name='grupos-estadis-intercambio'),

)
