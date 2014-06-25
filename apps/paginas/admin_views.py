#coding=utf-8

# Copyright (C) 2014 by Víctor Romero Blanco <info at playcircular dot com>.
# http://playcircular.com/
# It's licensed under the AFFERO GENERAL PUBLIC LICENSE unless stated otherwise.
# You can get copies of the licenses here: http://www.affero.org/oagpl.html
# AFFERO GENERAL PUBLIC LICENSE is also included in the file called "LICENSE".

from django.contrib import admin
from django.conf import settings
from configuracion.models import *
from django.contrib.auth.models import User
from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseNotAllowed
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from grupos.models import *
from paginas.models import *
from paginas.forms import *
from django.core import serializers
from django.db.models import Q

###################################################################################################
@login_required
def recarga_entrada(request):
	
	if request.is_ajax() and request.POST:
		seleccionados = request.POST.get('seleccionados')
		str_grupos = seleccionados.split(',')
		id_grupos = []
		for item in str_grupos:
			numero = int(item)
			id_grupos.append(numero)
		if len(id_grupos) > 0:
			
			n_grupos_administrados = Miembro.objects.filter(usuario=request.user,activo=True,nivel=u'Administrador').count()
			try:
				categorias = Idiomas_categoria_entrada.objects.filter((Q(categoria__grupo__in=id_grupos) | Q(categoria__superadmin=True)) & Q(idioma=request.LANGUAGE_CODE))
			except Idiomas_categoria_entrada.DoesNotExist:
				categorias = Idiomas_categoria_entrada.objects.filter(Q(categoria__grupo__in=id_grupos) | Q(categoria__superadmin=True)).order_by('-idioma_default')
				
			try:
				entradas_relacionadas = Idiomas_entrada.objects.filter((Q(entrada__grupo__in=id_grupos) | Q(entrada__superadmin=True)) & Q(idioma=request.LANGUAGE_CODE))
			except Idiomas_entrada.DoesNotExist:
				entradas_relacionadas = Idiomas_entrada.objects.filter(Q(entrada__grupo__in=id_grupos) | Q(entrada__superadmin=True)).order_by('-idioma_default')
			
			#categorias = Categoria_Entrada.objects.filter(Q(grupo__in=id_grupos) | Q(superadmin=True)).distinct()
			#entradas_relacionadas = Entrada.objects.filter(Q(grupo__in=id_grupos) | Q(superadmin=True)).distinct()
			#n_grupos_administrados = Miembro.objects.filter(usuario=request.user,activo=True,nivel=u'Administrador').count()
			
			if request.user.is_superuser or n_grupos_administrados > 0:
				grupos_qs = Miembro.objects.filter(grupo__in=id_grupos,activo=True).values_list('usuario', flat=True)
				if request.user.is_superuser:
					#El Superadmin puede publicar sin que pernezca a ningún grupo para que no lo controlen los Admin de los grupos
					grupos_qs = list(grupos_qs) + [request.user.pk]
				usuarios = User.objects.filter(pk__in=grupos_qs).distinct()
			else:
				usuarios = User.objects.filter(pk=request.user.pk)
			
			datos = list(usuarios) + list(categorias) + list(entradas_relacionadas)
		else:
			datos = []
	else:
		datos = []
		
	#se devuelven los anios en formato json, solo nos interesa obtener como json
	data = serializers.serialize("json", datos, fields=('pk','username','nombre','titulo','entrada','categoria'))
			
	return HttpResponse(data, mimetype="application/javascript")

###################################################################################################
@login_required
def recarga_pagina(request):
	
	if request.is_ajax() and request.POST:
		seleccionados = request.POST.get('seleccionados')
		str_grupos = seleccionados.split(',')
		id_grupos = []
		for item in str_grupos:
			numero = int(item)
			id_grupos.append(numero)
		if id_grupos:
			try:
				idiomas_qs = Idiomas_pagina.objects.filter(pagina__grupo__in=id_grupos, idioma=request.LANGUAGE_CODE).distinct()
			except Idiomas_pagina.DoesNotExist:
				idiomas_qs = Idiomas_pagina.objects.filter(pagina__grupo__in=id_grupos, idioma_default=True).distinct()
		else:
			idiomas_qs = []
	else:
		idiomas_qs = []
		
	#se devuelven los anios en formato json, solo nos interesa obtener como json
	data = serializers.serialize("json", idiomas_qs, fields=('pagina','titulo'))
			
	return HttpResponse(data, mimetype="application/javascript")














