# coding=utf-8


# Copyright (C) 2014 by Víctor Romero Blanco <info at playcircular dot com>.
# http://playcircular.com/
# It's licensed under the AFFERO GENERAL PUBLIC LICENSE unless stated otherwise.
# You can get copies of the licenses here: http://www.affero.org/oagpl.html
# AFFERO GENERAL PUBLIC LICENSE is also included in the file called "LICENSE".

from django.conf.urls import patterns, url
from economia.models import *
from economia.views import *


urlpatterns = patterns('economia.views',

	url(r'^index/(?P<id_cuenta>\d+)$', 'inicio', name='economia-index'),
	url(r'^intercambios_publicos/usuario/(?P<id_usuario>\d+)$', 'get_intercambios_publicos', name='economia-i-p-usuario'),
	url(r'^intercambios_publicos/grupo/(?P<id_grupo>\d+)$', 'get_intercambios_publicos', name='economia-i-p-grupo'),
	url(r'^intercambios_publicos/todos/$', 'get_intercambios_publicos', name='economia-i-p-todos'),
	url(r'^movimiento/(?P<id_movimiento>\d+)$', 'este_movimiento', name='economia-este-movimiento'),
	url(r'^actualizar_saldo/$', 'actualiza_saldo', name='economia-actualizar-saldo-ajax'),
	url(r'^recarga_actividad/$', 'recarga_actividad_ajax', name='economia-recarga-actividad-ajax'),
	url(r'^cuentas_posibles/$', 'posibles_cuentas_destino_ajax', name='economia-cuentas-posibles-ajax'),
	url(r'^pagar_paso_1/(?P<id_actividad>\d+)/(?P<id_usu>\d+)/(?P<ajax>[0-1]{1})/$','pagar_paso_1', name='economia-pagar-1'),
	url(r'^pagar_paso_2/$','pagar_paso_2', name='economia-pagar-2'),
	url(r'^resultado/(?P<ok>\d+)/(?P<id_actividad>\d+)$','confirmacion', name='economia-pagar-resultado'),

)
