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
from paginas.models import *
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

########################################################################################################################################

class Entradas_Generales_Feed(Feed):
	title=u'Play Circular'
	link='http://www.playcircular.com/'
	description=_(u'Entradas en Play Circular')

	def items(self):
		entradas = Idiomas_entrada.objects.filter(entrada__tipo='e_general',
												  entrada__estado='publicada',
												  entrada__visibilidad='publica',
												  idioma_default=True).order_by('-creado')[:15]
		return entradas

	def item_title(self, item):
		return item.titulo

	def item_description(self, item):
		return item.cuerpo


class Entradas_Grupo_Feed(Feed):

	def get_object(self, request, simbolo):
		if simbolo:
			grupo = get_object_or_404(Grupo, simbolo=simbolo)
		else:
			grupo = False
		return grupo 

	def title(self, grupo):
		return _(u"Entradas del grupo %s") % grupo

	def link(self, grupo):
		return reverse("paginas-entradas-grupo", args=['entradas',grupo])

	def description(self, grupo):
		return _(u"Entradas del grupo %s") % grupo

	def items(self, grupo):
		tipos_entrada = ['e_general','e_grupo','propuesta_general','propuesta_grupo']
		entradas = Idiomas_entrada.objects.filter(entrada__grupo=grupo,
												  entrada__tipo__in=tipos_entrada,
												  entrada__estado='publicada',
												  entrada__visibilidad='publica',
												  idioma_default=True).order_by('-creado')[:15]
		return entradas
	
	def item_title(self, item):
		return item.titulo

	def item_description(self, item):
		return item.cuerpo




