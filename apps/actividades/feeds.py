# coding=utf-8

# Copyright (C) 2014 by Víctor Romero Blanco <info at playcircular dot com>.
# http://playcircular.com/
# It's licensed under the AFFERO GENERAL PUBLIC LICENSE unless stated otherwise.
# You can get copies of the licenses here: http://www.affero.org/oagpl.html
# AFFERO GENERAL PUBLIC LICENSE is also included in the file called "LICENSE".

from django.contrib.syndication.views import Feed
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.template.defaultfilters import slugify
from grupos.models import *
from actividades.models import *
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

########################################################################################################################################

class Actividades_Generales_Feed(Feed):
	title=u'Play Circular'
	link='http://www.playcircular.com/'
	description=_(u'Actividades en Play Circular')

	def items(self):
		actividades = Idiomas_actividad.objects.filter(idioma_default=True).order_by('-creado')[:15]
		return actividades

	def item_title(self, item):
		return item.nombre_actividad

	def item_description(self, item):
		return item.descripcion


class Actividades_Grupo_Feed(Feed):

	def get_object(self, request, simbolo):
		grupo = get_object_or_404(Grupo, simbolo=simbolo)
		return grupo

	def title(self, grupo):
		return _(u"Actividades del grupo %s") % grupo

	def link(self, grupo):
		return reverse("paginas-entradas-grupo", args=['entradas',grupo])

	def description(self, grupo):
		return _(u"Actividades del grupo %s") % grupo

	def items(self, grupo):
		actividades = Idiomas_actividad.objects.filter(actividad__grupo=grupo,idioma_default=True).order_by('-creado')[:15]
		return actividades
	
	def item_title(self, item):
		return item.nombre_actividad

	def item_description(self, item):
		return item.descripcion
	
		




