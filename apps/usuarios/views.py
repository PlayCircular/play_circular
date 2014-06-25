# coding=utf-8

# Copyright (C) 2014 by Víctor Romero Blanco <info at playcircular dot com>.
# http://playcircular.com/
# It's licensed under the AFFERO GENERAL PUBLIC LICENSE unless stated otherwise.
# You can get copies of the licenses here: http://www.affero.org/oagpl.html
# AFFERO GENERAL PUBLIC LICENSE is also included in the file called "LICENSE".

from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, render_to_response
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from usuarios.models import *
from usuarios.forms import *
from registration.forms import *
from grupos.models import *
from economia.models import *
from twitter.models import *
from twitter.forms import *
#from utilidades.views import *
from django.contrib.auth.decorators import login_required
from django.template import RequestContext, loader
from django.utils.translation import ugettext as _
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator, InvalidPage, EmptyPage


#######################################################################################################################################################

@login_required
def editar_perfil(request):

	try:
		perfil = request.user.perfil
	except:
		p = Perfil_usuario(usuario_id = request.user.id)
		p.save()
		perfil = request.user.perfil

	if request.method == "POST":

		user_form = UserForm(request.POST, instance=request.user)

		if user_form.is_valid():

			user_form.save()
			p = perfil
			p.save()

			return HttpResponseRedirect(reverse("portada"))
	else:

		user_form = UserForm(instance=request.user)

	return render_to_response('usuarios/editar_perfil.html',
	{'user_form': user_form},
	context_instance=RequestContext(request))

#######################################################################################################################################################

@login_required
def sumar_visita(request):
	
	visita = Visitas_usuario()
	visita.usuario = request.user
	visita.visitante = request.user
	visita.save()

	return HttpResponseRedirect(reverse("portada"))
	


#######################################################################################################################################################

@login_required
def correspondencia(request):
	
	situacion = _(u'mensajes')

	mensajes_qs = Correspondencia.objects.filter(destinatario=request.user).order_by('-creado')
	return render_to_response('usuarios/correspondencia.html',
							{'mensajes_qs': mensajes_qs, 'situacion': situacion },
							context_instance=RequestContext(request))

	

#######################################################################################################################################################



@login_required
def mensaje(request, id_mensaje=None):
	
	situacion = _(u'mensajes')

	mensaje = get_object_or_404(Correspondencia, pk= int(id_mensaje))
	mensaje.leido = True
	mensaje.save()
	#try:
		#del request.session['mensajes']
	#except KeyError:
		#pass
	return render_to_response('usuarios/mensaje.html',{'mensaje': mensaje, 'situacion': situacion },context_instance=RequestContext(request))


	

#######################################################################################################################################################


@login_required
def index(request):
	
	situacion = _(u'busqueda de usuarios')
	
	grupos_qs = Miembro.objects.filter(usuario=request.user).values('grupo')
	mis_grupos = Grupo.objects.filter(pk__in=grupos_qs, activo=True)
	
	if len(mis_grupos) > 0:
		mi_grupo = mis_grupos[0]
	else:
		mi_grupo = []
	
	form = Form_busqueda_usuarios(initial={'grupo':mi_grupo})
	
	datos = {'form': form, 'situacion': situacion }

	return render_to_response('usuarios/inicio_usuarios.html',datos,context_instance=RequestContext(request))



#######################################################################################################################################################

def busqueda_usuario(request):
	
	"""Paso los datos del form a sessions porque para paginar, la página 2, 3, etc... no llevan un POST"""
	
	situacion = _(u'busqueda de usuarios')
	
	try: 
		page = int(request.POST.get("page", '1'))
	except ValueError: 
		page = 1

	if request.method == 'POST':
		form = Form_busqueda_usuarios(request.POST)
		if form.is_valid():
			
			
			if form.cleaned_data['grupo']:
				usuarios_qs = Miembro.objects.filter(grupo=form.cleaned_data['grupo'],activo=True).values_list('usuario',flat=True)
				busqueda_qs = Perfil.objects.filter(usuario__is_active=True, usuario__in=usuarios_qs)
			else:
				busqueda_qs = Perfil.objects.filter(usuario__is_active=True)
				
		#busqueda_qs = busqueda_qs.filter(usuario=form.cleaned_data['usuario'])
			#if form.cleaned_data['condicion']:
				#busqueda_qs = busqueda_qs.filter(condicion=form.cleaned_data['condicion'])
			if form.cleaned_data['usuario']:
				busqueda_qs = busqueda_qs.filter(usuario__username=form.cleaned_data['usuario'])
			if form.cleaned_data['nombre']:
				busqueda_qs = busqueda_qs.filter(nombre=form.cleaned_data['nombre'])
			if form.cleaned_data['apellidos']:
				busqueda_qs = busqueda_qs.filter(apellidos=form.cleaned_data['apellidos'])
			if form.cleaned_data['poblacion']:
				busqueda_qs = busqueda_qs.filter(poblacion=form.cleaned_data['poblacion'])
			if form.cleaned_data['telefono']:
				busqueda_qs = busqueda_qs.filter(telefono=form.cleaned_data['telefono'])
			if form.cleaned_data['email']:
				busqueda_qs = busqueda_qs.filter(usuario__email=form.cleaned_data['email'])
				#busqueda_qs = busqueda_qs.filter(usuario=form.cleaned_data['usuario'])
			if form.cleaned_data['miembro']:
				miembros_qs = Miembro.objects.filter(activo=True, clave=form.cleaned_data['miembro']).values_list('usuario',flat=True)
				busqueda_qs = Perfil.objects.filter(usuario__is_active=True,usuario__in=miembros_qs)
				#print 'Aqui !!! > busqueda_qs'
				#print busqueda_qs
			if form.cleaned_data['cuenta']:
				cuenta_qs = Cuenta.objects.filter(activo=True, cuenta=form.cleaned_data['cuenta']).values_list('titulares',flat=True)
				busqueda_qs = Perfil.objects.filter(usuario__is_active=True,usuario__in=cuenta_qs)
			if form.cleaned_data['orden']:
				orden = form.cleaned_data['orden']
				if orden == u'fecha de alta':
					orden = 'creado'
				else:
					orden = 'usuario__last_login'
				
				busqueda_qs = busqueda_qs.order_by(orden)
				
			
			paginator = Paginator(busqueda_qs, 20)
			try:
				n_paginas = paginator.page(page)
			except (InvalidPage, EmptyPage):
				n_paginas = paginator.page(paginator.num_pages)
			
			datos = {"busqueda_qs" : busqueda_qs, "n_paginas": n_paginas, 'situacion': situacion, 'form':form}

			if not request.is_ajax():
				return render_to_response('usuarios/busqueda_usuarios.html',datos,context_instance=RequestContext(request))
			else:
				import time
				time.sleep(0.1)
				return render_to_response('usuarios/paginacion_usuarios.html',datos,context_instance=RequestContext(request))
			
		else:
			busqueda_qs = False
			form = Form_busqueda_usuarios(request.POST)
			datos = {'form': form, 'situacion': situacion }
			return render_to_response('usuarios/inicio_usuarios.html',datos,context_instance=RequestContext(request))
		
	else:
		datos = {"busqueda_qs" : [], "n_paginas": [], 'situacion': situacion }
		return render_to_response('usuarios/busqueda_usuarios.html',datos,context_instance=RequestContext(request))
		
			

	
	
#######################################################################################################################################################
		
	
