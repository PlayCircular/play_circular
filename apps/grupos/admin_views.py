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
from grupos.forms import *
from django.core import serializers
from django.views.decorators.csrf import csrf_protect, csrf_exempt

	
###################################################################################################

@login_required
def grupos_miembros_dependientes(request):
	
	if request.is_ajax():
	
		if request.POST:
			grupo_id = request.POST.get('grupo_id')
	
			if grupo_id:
				miembros = Miembro.objects.filter(grupo_id=grupo_id,activo=True).values_list('usuario', flat=True)
				usuarios = User.objects.filter(id__in=miembros)
			else:
				usuarios = User.objects.none()
		else:
			usuarios = User.objects.none()
	else:
		usuarios = User.objects.none()
		
	#se devuelven los anios en formato json, solo nos interesa obtener como json
	data = serializers.serialize("json", usuarios, fields=('pk','username'))
			
	return HttpResponse(data, mimetype="application/javascript")

###################################################################################################
