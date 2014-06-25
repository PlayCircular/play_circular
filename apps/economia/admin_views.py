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
from economia.models import *
from grupos.models import *
from actividades.models import *
from usuarios.models import *
from economia.forms import *
from django.core import serializers

###################################################################################################
@login_required
def eco_cuenta_codas_dependientes(request):
	
	if request.is_ajax():
		if request.POST:
			grupo_id = request.POST.get('grupo_id')
			try:
				config = Config_grupo.objects.get(grupo_id=int(grupo_id))
				margenes_qs = Margenes.objects.filter(config_grupo=config)
			except Config_grupo.DoesNotExist:
				margenes_qs = Margenes.objects.none()

			miembros = Miembro.objects.filter(grupo_id=grupo_id,activo=True).values_list('usuario', flat=True)
			usuarios = User.objects.filter(id__in=miembros)
			datos = list(usuarios) + list(margenes_qs)
		else:
			datos = []
	else:
		datos = []
		
	#se devuelven los anios en formato json, solo nos interesa obtener como json
	data = serializers.serialize("json", datos, fields=('pk','username','nombre'))
			
	return HttpResponse(data, mimetype="application/javascript")


###################################################################################################
@login_required
def eco_cosas_dependientes_1(request):
	
	if request.is_ajax():
		if request.POST:
			id_origen = request.POST.get('id_origen')
			
			if request.user.is_superuser:
				mis_grupos = Miembro.objects.filter(usuario_id=id_origen,activo=True).values_list('grupo', flat=True)
				grupos_posibles = Grupo.objects.filter(pk__in=mis_grupos)
				cuenta_origen = Cuenta.objects.filter(titulares=id_origen,activo=True,grupo__in=grupos_posibles).exclude(tipo='Intergrupos').distinct()
			else:
				grupos_administrados = Miembro.objects.filter(usuario_id=request.user,activo=True,nivel='Administrador').values_list('grupo', flat=True)
				grupos_posibles = Grupo.objects.filter(pk__in=grupos_administrados)
				cuenta_origen = Cuenta.objects.filter(titulares=id_origen,activo=True,grupo__in=grupos_posibles).exclude(tipo='Intergrupos').distinct()
			datos = list(cuenta_origen) + list(grupos_posibles)
		else:
			datos = []
	else:
		datos = []
		
	#se devuelven los anios en formato json, solo nos interesa obtener como json
	data = serializers.serialize("json", datos, fields=('pk','cuenta','simbolo'))
			
	return HttpResponse(data, mimetype="application/javascript")

###################################################################################################
@login_required
def eco_cosas_dependientes_2(request):
	
	if request.is_ajax():
		if request.POST:
			id_grupo_destino = request.POST.get('id_grupo_destino')
			miembros_destino = Miembro.objects.filter(grupo_id=id_grupo_destino,activo=True).values_list('usuario',flat=True)
			usuarios_destino = User.objects.filter(pk__in=miembros_destino)
			cuentas_destino = Cuenta.objects.filter(grupo_id=id_grupo_destino,activo=True).exclude(tipo='Intergrupos').distinct()
			qs_actividades = Actividad.objects.filter(grupo=id_grupo_destino,activo=True).values_list('pk',flat=True)
			idioma = Idiomas_actividad.objects.filter(actividad_id__in=qs_actividades, idioma_default=True)
			datos = list(usuarios_destino) + list(cuentas_destino) + list(idioma)
		else:
			datos = []
	else:
		datos = []
		
	#se devuelven los anios en formato json, solo nos interesa obtener como json
	data = serializers.serialize("json", datos, fields=('pk','username','cuenta','simbolo','actividad','nombre_actividad'))
			
	return HttpResponse(data, mimetype="application/javascript")


###################################################################################################
@login_required
def eco_cosas_dependientes_3(request):
	
	if request.is_ajax():
		if request.POST:
			id_destino = request.POST.get('id_destino')
			perfil_destino = Perfil.objects.get(usuario=id_destino)
			cuentas_destino = Cuenta.objects.filter(titulares=id_destino,activo=True).exclude(tipo='Intergrupos').distinct()
			qs_actividades = Actividad.objects.filter(perfil=perfil_destino,activo=True).values_list('pk',flat=True)
			idioma = Idiomas_actividad.objects.filter(actividad_id__in=qs_actividades, idioma_default=True)
			datos = list(cuentas_destino) + list(idioma)
		else:
			datos = []
	else:
		datos = []
		
	#se devuelven los anios en formato json, solo nos interesa obtener como json
	data = serializers.serialize("json", datos, fields=('pk','cuenta','simbolo','actividad','nombre_actividad'))
			
	return HttpResponse(data, mimetype="application/javascript")

###################################################################################################

@login_required
def eco_cosas_dependientes_4(request):
	
	if request.is_ajax():
		if request.POST:
			id_actividad = request.POST.get('id_actividad')
			actividad = Actividad.objects.filter(pk=id_actividad,activo=True)
			idioma = Idiomas_actividad.objects.filter(actividad=actividad, idioma_default=True)
			datos = list(actividad) + list(idioma)
		else:
			datos = []
	else:
		datos = []
		
	#se devuelven los anios en formato json, solo nos interesa obtener como json
	data = serializers.serialize("json", datos, fields=('precio_moneda_social','nombre_actividad'))
			
	return HttpResponse(data, mimetype="application/javascript")

###################################################################################################








