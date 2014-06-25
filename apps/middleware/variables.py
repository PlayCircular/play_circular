# coding=utf-8

# coding=utf-8

# Copyright (C) 2014 by Víctor Romero Blanco <info at playcircular dot com>.
# http://playcircular.com/
# It's licensed under the AFFERO GENERAL PUBLIC LICENSE unless stated otherwise.
# You can get copies of the licenses here: http://www.affero.org/oagpl.html
# AFFERO GENERAL PUBLIC LICENSE is also included in the file called "LICENSE".

from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, render_to_response
from django.core.urlresolvers import reverse
from usuarios.models import *
from grupos.models import *
from economia.models import *
from paginas.models import *
from settings import MEDIA_ROOT, MEDIA_URL, STATIC_ROOT, STATIC_URL
from django.template import RequestContext, loader
from django.template.response import TemplateResponse
from django.db.models import Sum
from configuracion.models import *
from random import randint

class globales(object):
	
	"""Middleware para hacer presente en todo el sitio las sessiones de mensajería, los banners y los grupos a los que se pertenece"""
	
	def process_request(self, request):

		# Tres horas de session
		request.session.set_expiry(10800)
		request.session.set_test_cookie()

		if request.session.test_cookie_worked():
			request.session.delete_test_cookie()
			cookie = True
		else:
			cookie = False

		d = {'cookie': cookie}
		if request.user.is_authenticated():

			n_mensajes = Correspondencia.objects.filter(destinatario=request.user, leido=False).count()
			mis_grupos_qs = Miembro.objects.filter(usuario=request.user).values_list('grupo',flat=True)
			if len(mis_grupos_qs) > 0:
				d['n_grupos'] = 1
				
				mis_grupos = []
				for pk in mis_grupos_qs:
					grupo = Grupo.objects.get(pk=pk)
					try:
						idioma = Idiomas_grupo.objects.get(grupo=pk, idioma=request.LANGUAGE_CODE)
					except Idiomas_grupo.DoesNotExist:
						idiomas_qs = Idiomas_grupo.objects.filter(grupo=pk).order_by('-idioma_default')
						idioma = idiomas_qs[0]
						
					grupo.eslogan = idioma.eslogan
					grupo.pie_pagina = idioma.pie_pagina
					grupo.meta_descripcion = idioma.meta_descripcion
					grupo.palabras_clave = idioma.palabras_clave
					mis_grupos.append(grupo)
				
				d['mis_grupos'] = mis_grupos
				banners = Banner.objects.filter(activo=True,grupo__in=mis_grupos_qs)
				if len(banners) == 0:
					banners = Banner_general.objects.filter(activo=True)
			else:
				try:
					idioma = Idioma_configuracion.objects.get(configuracion=1, idioma=request.LANGUAGE_CODE)
				except Idioma_configuracion.DoesNotExist:
					idiomas_qs = Idioma_configuracion.objects.filter(configuracion=1).order_by('-idioma_default')
					if len(idiomas_qs) > 0:
						idioma = idiomas_qs[0]
					else:
						idioma = False
				try:
					config_general = Configuracion.objects.get(pk=1)
					config_general.eslogan = idioma.eslogan
					config_general.pie_pagina = idioma.pie_pagina
					config_general.meta_descripcion = idioma.meta_descripcion
					config_general.palabras_clave = idioma.palabras_clave
					d['mis_grupos'] = [config_general]
				except Configuracion.DoesNotExist:
					config_general = False
					d['mis_grupos'] = []
				banners = Banner_general.objects.filter(activo=True)
				
				d['n_grupos'] = 0

			d['n_mensajes'] = n_mensajes
			d['banners'] = banners
		else:
			d['n_grupos'] = 0
			try:
				idioma = Idioma_configuracion.objects.get(configuracion=1, idioma=request.LANGUAGE_CODE)
			except Idioma_configuracion.DoesNotExist:
				idiomas_qs = Idioma_configuracion.objects.filter(configuracion=1).order_by('-idioma_default')
				if len(idiomas_qs) > 0:
					idioma = idiomas_qs[0]
				else:
					idioma = False
			try:
				config_general = Configuracion.objects.get(pk=1)
				config_general.eslogan = idioma.eslogan
				config_general.pie_pagina = idioma.pie_pagina
				config_general.meta_descripcion = idioma.meta_descripcion
				config_general.palabras_clave = idioma.palabras_clave
				d['mis_grupos'] = [config_general]
			except Configuracion.DoesNotExist:
				config_general = False
				d['mis_grupos'] = []
			banners = Banner_general.objects.filter(activo=True)
			d['n_mensajes'] = 0
			d['banners'] = banners
			
		n = len(d['mis_grupos']) - 1
		if n > 0:
			aleatorio = randint(0,n)
			d['config'] = d['mis_grupos'][aleatorio]
		else:
			aleatorio = 0
			d['config'] = {}

		request.datos = d
		return

