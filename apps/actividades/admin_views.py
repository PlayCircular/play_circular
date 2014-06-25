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
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _

from grupos.models import *
from grupos.forms import *
from actividades.models import *
from usuarios.models import *
from django.core import serializers
from django.db.models import Q

###################################################################################################
@login_required
def recarga_actividad(request):
	
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
				categorias = Idiomas_categoria.objects.filter((Q(categoria__grupo__in=id_grupos) | Q(categoria__superadmin=True)) & Q(idioma=request.LANGUAGE_CODE))
			except Idiomas_categoria.DoesNotExist:
				categorias = Idiomas_categoria.objects.filter(Q(categoria__grupo__in=id_grupos) | Q(categoria__superadmin=True)).order_by('-idioma_default')
			
			if request.user.is_superuser or n_grupos_administrados > 0:
				
				usuarios_qs = Miembro.objects.filter(grupo__in=id_grupos,activo=True).values_list('usuario', flat=True)
				if request.user.is_superuser:
					#El Superadmin puede publicar sin que pernezca a ningún grupo para que no lo controlen los Admin de los grupos
					usuarios_qs = list(usuarios_qs) + [request.user.pk]
				usuarios = User.objects.filter(pk__in=usuarios_qs).distinct()

			else:
				usuarios = User.objects.filter(pk=request.user.pk)
			
			datos = list(usuarios) + list(categorias)
		else:
			datos = []

	else:
		datos = []
		
	#se devuelven los anios en formato json, solo nos interesa obtener como json
	data = serializers.serialize("json", datos, fields=('pk','username','nombre','categoria'))
			
	return HttpResponse(data, mimetype="application/javascript")

###################################################################################################