# coding=utf-8

# Copyright (C) 2014 by Víctor Romero Blanco <info at playcircular dot com>.
# http://playcircular.com/
# It's licensed under the AFFERO GENERAL PUBLIC LICENSE unless stated otherwise.
# You can get copies of the licenses here: http://www.affero.org/oagpl.html
# AFFERO GENERAL PUBLIC LICENSE is also included in the file called "LICENSE".

from django.conf.urls import patterns, include, url
from paginas.models import *
from paginas.views import *


urlpatterns = patterns('paginas.views',
					   
	url(r'^(?P<id_pagina>\d+)/(?P<slug>([^/]+))$', 'ver_pagina', name="ver-pagina"),
	url(r'^entrada/(?P<id_entrada>\d+)/(?P<slug>([^/]+))$', 'ver_entrada', name="ver-entrada"),
	url(r'^(?P<tipo>(entradas|propuestas))/$', 'get_entradas', name="paginas-entradas"),
	url(r'^entradas/(?P<username>([^/]+))/$', 'get_entradas_usu', name="paginas-entradas-usu"),
	url(r'^(?P<tipo>(entradas|propuestas))/grupo/(?P<simbolo>([^/]+))/$', 'get_entradas_grupo', name="paginas-entradas-grupo"),
	url(r'^valorar_entrada/$', 'valorar_entrada', name="pagina-valorar"),
	url(r'^valorar_comentario/$', 'valorar_comentario', name="comentario-valorar"),
	url(r'^general/(?P<id_grupo>\d+)/(?P<p>(terminos_y_condiciones|configuracion))/$', 'ver_pagina_general', name="ver-pagina-general"),
	url(r'^tag/(?P<tag>([A-Za-z0-9_-]+))','get_entradas_clasificadas', name='entradas-tag'),
	url(r'^categoria/(?P<id_categoria>\d+)/$','get_entradas_clasificadas', name='entradas-categoria'),
	
)
