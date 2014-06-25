# coding=utf-8

# Copyright (C) 2014 by Víctor Romero <info at playcircular dot com>.
# http://playcircular.com/
# It's licensed under the AFFERO GENERAL PUBLIC LICENSE unless stated otherwise.
# You can get copies of the licenses here: http://www.affero.org/oagpl.html
# AFFERO GENERAL PUBLIC LICENSE is also included in the file called "LICENSE".

from django.conf.urls import patterns, url
from ces.models import *
from ces.views import *

urlpatterns = patterns('ces.views',

	url(r'^importar/$', 'importar_1', name='ces-importar-1'),

)
