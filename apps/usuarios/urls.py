# coding=utf-8

# Copyright (C) 2014 by Víctor Romero Blanco <info at playcircular dot com>.
# http://playcircular.com/
# It's licensed under the AFFERO GENERAL PUBLIC LICENSE unless stated otherwise.
# You can get copies of the licenses here: http://www.affero.org/oagpl.html
# AFFERO GENERAL PUBLIC LICENSE is also included in the file called "LICENSE".

from django.conf.urls import patterns, url
from django.conf import settings
from usuarios.models import *

urlpatterns = patterns('usuarios.views',

    url(r'^perfil/$', 'editar_perfil', name="usuarios-editar-perfil"),
    url(r'^mensajes/$', 'correspondencia', name='usuarios-mensajes'),
    url(r'^mensaje/(?P<id_mensaje>\d+)$', 'mensaje', name='usuarios-mensaje'),
    url(r'^visita/$', 'sumar_visita', name='usuarios-visita'),
    url(r'^index/$', 'index', name='usuarios-index'),
    url(r'^busqueda/$', 'busqueda_usuario', name='usuarios-busqueda'),

)
