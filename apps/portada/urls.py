# coding=utf-8

# Copyright (C) 2014 by Víctor Romero Blanco <info at playcircular dot com>.
# http://playcircular.com/
# It's licensed under the AFFERO GENERAL PUBLIC LICENSE unless stated otherwise.
# You can get copies of the licenses here: http://www.affero.org/oagpl.html
# AFFERO GENERAL PUBLIC LICENSE is also included in the file called "LICENSE".

from django.conf.urls import patterns, include, url
from paginas.models import *
from paginas.views import *

urlpatterns = patterns('portada.views',
	
	url(r'^(?P<portada>(general))$', 'portada', name="portada-general"),
	url(r'^(?P<simbolo>([^/]+))/(?P<slug>([^/]+))$', 'inicio_grupo', name="portada-grupo"),
)
