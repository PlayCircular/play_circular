#coding=utf-8

# Copyright (C) 2014 by Víctor Romero <info at playcircular dot com>.
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
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from grupos.models import *
from grupos.forms import *
from actividades.models import *
from usuarios.models import *
from django.core import serializers



###################################################################################################

@login_required
def miembros_dependiente(request):
	
	if request.POST:
		grupo_id = request.POST.get('grupo_id')
		
		print 'hola'
		print grupo_id
		
		if grupo_id:
			#mi = Administrador.objects.get(pk=int(grupo_id))
			#miembros = Miembro.objects.filter(grupo=administrador.grupo).order_by('activo')
			miembros = Miembro.objects.filter(grupo_id=int(grupo_id)).values_list('usuario_id').order_by('activo')
			perfil = Perfil.objects.filter(usuario__in=miembros)
			
		else:
			usuarios = [1,'nop']

		
		#se devuelven los anios en formato json, solo nos interesa obtener como json
		data = serializers.serialize("json", usuarios, fields=('usuario','usuario'))

	return HttpResponse(data, mimetype="application/javascript")
