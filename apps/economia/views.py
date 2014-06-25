# coding=utf-8

# Copyright (C) 2014 by Víctor Romero Blanco <info at playcircular dot com>.
# http://playcircular.com/
# It's licensed under the AFFERO GENERAL PUBLIC LICENSE unless stated otherwise.
# You can get copies of the licenses here: http://www.affero.org/oagpl.html
# AFFERO GENERAL PUBLIC LICENSE is also included in the file called "LICENSE".

from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, render_to_response, render
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from usuarios.models import *
from economia.models import *
from grupos.models import *
from economia.forms import *
from actividades.models import *
#No puedo importar actividades.views porque allí estoy importando economia.views
#from actividades.views import *
#from utilidades.views import *
from django.contrib.auth.decorators import login_required
from django.template import RequestContext, loader
from django.utils.translation import ugettext as _
from django.utils.encoding import smart_str
from django.db.models import Sum
from django.db.models import Q
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core import serializers
from decimal import *

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.sites.models import get_current_site
from django.contrib import messages
#from django.contrib.formtools.preview import FormPreview

#######################################################################################################################################################

def get_intercambios_publicos(request, id_grupo=False,id_usuario=False):
	
	situacion = _(u'intercambios públicos')
	current_site = get_current_site(request)
	sitio = current_site.domain
	idioma=request.LANGUAGE_CODE
	
	if request.user.is_authenticated():
		mis_grupos_qs = Miembro.objects.filter(usuario=request.user).values_list('grupo',flat=True)
		if id_usuario:
			usuario = get_object_or_404(User, pk=int(id_usuario))
			intercambios_p = Intercambio.objects.filter((Q(origen=usuario) | Q(destino=usuario)) & Q(publico=True) & Q(tipo='Normal') & Q(cantidad__gt=0) & Q(estado=u'Concluído')).order_by('-creado')
			url = unicode(sitio) + '/' + unicode(idioma) + '/economia/intercambios_publicos/usuario/' + unicode(id_usuario)
			situacion_1 = _(u'Intercambios públicos del usuario ') + unicode(usuario)
		if id_grupo:
			grupo = get_object_or_404(Grupo,pk=int(id_grupo))
			intercambios_p = Intercambio.objects.filter((Q(grupo_origen=grupo) | Q(grupo_destino=grupo)) & Q(cantidad__gt=0) & Q(tipo='Normal') & Q(publico=True)  & Q(estado=u'Concluído')).order_by('-creado')
			url = unicode(sitio) + '/' + unicode(idioma) + '/economia/intercambios_publicos/grupo/' + unicode(id_grupo)
			situacion_1 = _(u'Intercambios públicos del grupo ') + unicode(grupo)
		if not id_grupo and not id_usuario:
			mis_grupos_qs = Miembro.objects.filter(usuario=request.user).values_list('grupo',flat=True)
			if len(mis_grupos_qs) > 0:
				situacion_1 = _(u'Intercambios públicos de tus grupos')
				intercambios_p = Intercambio.objects.filter((Q(grupo_origen__in=mis_grupos_qs) | Q(grupo_destino__in=mis_grupos_qs)) & Q(publico=True)  & Q(cantidad__gt=0) & Q(tipo='Normal') & Q(estado=u'Concluído')).order_by('-creado')
			else:
				situacion_1 = _(u'Intercambios públicos del sitio')
				intercambios_p = Intercambio.objects.filter(publico=True, cantidad__gt=0,tipo='Normal',estado=u'Concluído').order_by('-creado')
			url = unicode(sitio) + '/' + unicode(idioma) + '/economia/intercambios_publicos/todos/'
	else:
		url = unicode(sitio) + '/' + unicode(idioma) + '/economia/intercambios_publicos/todos/'
		situacion_1 = _(u'Intercambios públicos del sitio')
		intercambios_p = Intercambio.objects.filter(publico=True, cantidad__gt=0, tipo='Normal',estado=u'Concluído').order_by('-creado')
		
	try: 
		page = int(request.GET.get("page", '1'))
	except ValueError: 
		page = 1
		
	paginator = Paginator(intercambios_p, 25)
	try:
		n_paginas = paginator.page(page)
	except (InvalidPage, EmptyPage):
		n_paginas = paginator.page(paginator.num_pages)
		
	datos = {'situacion':situacion,'situacion_1':situacion_1,'intercambios_p':n_paginas.object_list,'n_paginas': n_paginas, 'url':url }
	
	if not request.is_ajax():
		return render_to_response('economia/intercambios_publicos.html',datos,context_instance=RequestContext(request))
	else:
		import time
		time.sleep(0.3)
		return render_to_response('economia/paginacion_ipublicos.html',datos,context_instance=RequestContext(request))
		
	

#######################################################################################################################################################		

def adjuntar_datos_actividad(request,item=None,opinion=False):
	
	try:
		idioma = Idiomas_actividad.objects.get(actividad=item.pk, idioma=request.LANGUAGE_CODE)
	except Idiomas_actividad.DoesNotExist:
		idiomas_qs = Idiomas_actividad.objects.filter(actividad=item.pk).order_by('-idioma_default')
		idioma = idiomas_qs[0]
		
	try:
		idioma_categoria = Idiomas_categoria.objects.get(categoria=item.categoria, idioma=request.LANGUAGE_CODE)
	except Idiomas_categoria.DoesNotExist:
		idiomas_categoria_qs = Idiomas_categoria.objects.filter(categoria=item.categoria).order_by('-idioma_default')
		if len(idiomas_categoria_qs) > 0:
			idioma_categoria = idiomas_categoria_qs[0]
		else:
			idioma_categoria = False
			

	item.actividad = idioma.nombre_actividad
	item.intro = idioma.intro
	item.descripcion = idioma.descripcion
	item.robots = idioma.robots
	item.meta_descripcion = idioma.meta_descripcion
	item.palabras_clave = idioma.palabras_clave
	item.tags = idioma.get_tags()
	item.get_categoria = idioma_categoria
	
	
	if opinion:
		
		ya_intercambiada = Intercambio.objects.filter(actividad=item,origen=request.user,tipo='Normal',estado=u'Concluído').count()
		
		if ya_intercambiada > 0:
			ya_intercambiada = True
		else:
			ya_intercambiada = False
			
		item.ya_intercambiada = ya_intercambiada
		
		try:
			o = Opinion_actividad.objects.get(usuario=request.user,actividad=item.pk,ya_opinado=True)
			item.me_gusta_para_mi = o.me_gusta_para_mi
			item.rating_para_mi_antes = o.rating_para_mi_antes
			item.rating_para_mi_despues = o.rating_para_mi_despues
			item.bien_comun = o.bien_comun
			item.rating_para_bien_comun = o.rating_para_bien_comun
			item.comentario = o.comentario
			item.ya_opinado = True
		except Opinion_actividad.DoesNotExist:
			item.me_gusta_para_mi = False
			item.rating_para_mi_antes = False
			item.rating_para_mi_despues = False
			item.bien_comun = False
			item.rating_para_bien_comun = False
			item.comentario = False
			item.ya_opinado = False
		
	return item

#######################################################################################################################################################		

def hacer_intercambio(request,dic={}):

	c1 = Intercambio()
	c1.origen = dic['origen']
	c1.grupo_origen = dic['grupo_origen']
	c1.cuenta_origen = dic['cuenta_origen']
	c1.n_intercambio = dic['n_intercambio']
	c1.actividad = dic['actividad']
	c1.cantidad = dic['cantidad']
	c1.concepto = dic['concepto']
	c1.descripcion = dic['descripcion'] + '  ' + dic['all_info']
	c1.destino = dic['destino']
	c1.grupo_destino = dic['grupo_destino']
	c1.cuenta_destino = dic['cuenta_destino']
	c1.publico = dic['publico']
	c1.estado = dic['estado']
	c1.tipo = dic['tipo']
	c1.creado_por = dic['creado_por']
	c1.modificado_por = dic['modificado_por']
	c1.content_type = dic['content_type']
	c1.object_id = dic['object_id']
	c1.save()
	
	c_destino = dic['cuenta_destino']
	titulares_cuenta_destino = c_destino.titulares.all()
	for titular in titulares_cuenta_destino:
		c1.usuarios.add(titular)
	
	
	c2 = Intercambio()
	c2.origen = dic['origen']
	c2.grupo_origen = dic['grupo_origen']
	c2.cuenta_origen = dic['cuenta_origen']
	c2.n_intercambio = dic['n_intercambio']
	c2.actividad = dic['actividad']
	c2.cantidad = -(dic['cantidad'])
	c2.concepto = dic['concepto']
	c2.descripcion = dic['descripcion'] + '  ' + dic['all_info']
	c2.destino = dic['destino']
	c2.grupo_destino = dic['grupo_destino']
	c2.cuenta_destino = dic['cuenta_destino']
	c2.publico = dic['publico']
	c2.estado = dic['estado']
	c2.tipo = dic['tipo']
	c2.creado_por = dic['creado_por']
	c2.modificado_por = dic['modificado_por']
	c2.content_type = dic['content_type']
	c2.object_id = dic['object_id']
	c2.save()
	
	c_origen = dic['cuenta_origen']
	titulares_cuenta_origen = c_origen.titulares.all()
	for titular in titulares_cuenta_origen:
		c2.usuarios.add(titular)
	
	return c1.pk
	
	

#######################################################################################################################################################		

def cuentas_usuario(usuario):

	mis_cuentas = Cuenta.objects.filter(titulares=usuario).exclude(tipo='Intergrupos').order_by('creado')
	return mis_cuentas

#######################################################################################################################################################		

def comprueba_margenes(request,usuario,cuenta,cantidad,superior=True):
	
	margen_cuenta = cuenta.margen
	saldo_cuenta = cuenta.saldo()
	if not saldo_cuenta or saldo_cuenta == u'None':
		saldo_cuenta = 0
	saldo_cuenta = Decimal(saldo_cuenta)
	
	if superior:
		posible_futuro_saldo = saldo_cuenta + cantidad
		if margen_cuenta.superior >= posible_futuro_saldo:
			mensaje = _(u"La operación está dentro de los margenes permitidos del vendedor.")
			messages.add_message(request, messages.INFO,mensaje)
			return 1
		else:
			mensaje = _(u"La operación no está permitida porque excede el margen superior del vendedor. (+")
			mensaje += unicode(margen_cuenta.superior) + ')'
			messages.add_message(request, messages.WARNING,mensaje)
			return 0
	else:
		posible_futuro_saldo = saldo_cuenta - cantidad
		if margen_cuenta.inferior <= posible_futuro_saldo:
			mensaje = _(u"La operación está dentro de tus margenes permitidos de como comprador.")
			messages.add_message(request, messages.INFO,mensaje)
			return 1
		else:
			mensaje = _(u"La operación no está permitida porque excede tu margen inferior como comprador. (")
			mensaje += unicode(margen_cuenta.inferior) + ')'
			messages.add_message(request, messages.WARNING,mensaje)
			return 0

#######################################################################################################################################################		

def comprueba_margenes_grupo(request,grupo,cantidad,superior=True):
	
	config = Config_grupo.objects.get(grupo=grupo)
	cuenta_intergrupos = Cuenta.objects.get(grupo=grupo,tipo='Intergrupos')
	balance_del_grupo = cuenta_intergrupos.saldo()
	if not balance_del_grupo or balance_del_grupo == u'None':
		balance_del_grupo = 0
	balance_del_grupo = Decimal(balance_del_grupo)
	
	if superior:
		posible_futuro_saldo = balance_del_grupo + cantidad
		if config.margen_superior_grupo >= posible_futuro_saldo:
			mensaje = _(u"La operación está dentro de los margenes intergrupo permitidos del grupo ")
			mensaje += unicode(config.grupo)
			messages.add_message(request, messages.INFO,mensaje)
			return 1
		else:
			mensaje = _(u"La operación no está permitida porque excede el margen superior intergrupos del grupo ")
			mensaje += unicode(config.grupo) + ' (+' + unicode(config.margen_superior_grupo) + ')'
			messages.add_message(request, messages.WARNING,mensaje)
			return 0
	else:
		posible_futuro_saldo = balance_del_grupo - cantidad
		if config.margen_inferior_grupo <= posible_futuro_saldo:
			mensaje = _(u"La operación está dentro de los margenes intergrupo permitidos del grupo ")
			mensaje += unicode(config.grupo)
			messages.add_message(request, messages.INFO,mensaje)
			return 1
		else:
			mensaje = _(u"La operación no está permitida porque excede el margen inferior intergrupos del grupo ")
			mensaje += unicode(config.grupo) + ' (+' + unicode(config.margen_inferior_grupo) + ')'
			messages.add_message(request, messages.WARNING,mensaje)
			return 0

#######################################################################################################################################################
@login_required
def recarga_actividad_ajax(request):
	
	import time
	time.sleep(0.3)

	if request.is_ajax():
		if request.method == 'POST':
			
			id_actividad = request.POST.get('actividad')
			actividad = get_object_or_404(Actividad,pk=id_actividad)
			
			response = {'status':True}
			context = {'actividad': actividad}
			
			return render_to_response('actividades/contenido_actividad.html',context,context_instance=RequestContext(request))

		else:
			response = {'status':False}
			raise Http404
	else:
		response = {'status':False}
		raise Http404


#######################################################################################################################################################

@login_required
def posibles_cuentas_destino_ajax(request):
	
	if request.POST:
		id_cuenta_origen = request.POST.get('id_cuenta_origen')
		id_usu_destino = request.POST.get('destino')
		id_actividad = request.POST.get('actividad')
		
		if id_cuenta_origen and id_usu_destino:
			cuenta_origen = get_object_or_404(Cuenta,pk=id_cuenta_origen)
			grupo = cuenta_origen.grupo
			usu_destino = get_object_or_404(User,pk=id_usu_destino)
			
			if id_actividad != '':
				# Se fuerza a elegir entre las cuentas destino donde la actividad está publicada
				actividad = get_object_or_404(Actividad,pk=id_actividad)
				qs_grupos_actividad = actividad.grupo.all().values_list('pk',flat=True)
				cuentas_posibles_destino = Cuenta.objects.filter(titulares=usu_destino,grupo__in=qs_grupos_actividad).exclude(tipo=u'Intergrupos')
			else:
				# Si tiene alguna cuenta en el mismo grupo que el usuario origen, pues solo es posible entre esas cuentas
				cuentas_posibles_destino = Cuenta.objects.filter(titulares=usu_destino,grupo=grupo).exclude(tipo=u'Intergrupos')
	
			if len(cuentas_posibles_destino) > 0:
				cuentas = cuentas_posibles_destino
			else:
				cuentas = Cuenta.objects.filter(titulares=usu_destino).exclude(tipo=u'Intergrupos')
			
		else:
			#Se ha producido un error 
			cuentas = []
		
		#se devuelven los anios en formato json, solo nos interesa obtener como json
		data = serializers.serialize("json", cuentas, fields=('pk','cuenta'))
		
	return HttpResponse(data, mimetype="application/javascript")


#######################################################################################################################################################		

def cuentas_posibles(request,usu_origen=None, usu_destino=None, grupos=None):
	"""Esta función sirve para pasarle a los formularios las cuentas posibles de origen y destino en función de los grupos comunes que comparten.
	Prioridades:
	 1.- Si comparten grupos comunes se intentan seleccionar cuentas de esos grupos ( preferentemente los de la actividad publcada ) 
		para no hacer uso de la cuenta virtual intergrupos, evitando las cuentas en las que ambos son titulares y priorizando el grupo de destino.
	 2.- Si no comparten cuentas en los mismos grupos, las de grupos que permitan el comercio intergrupos si es posible."""
	
	# si no son los grupos de la actividad ( porque sea un pago a un usuario sin actividad vinculada) buscamos los grupos de las cuentas de destino
	if grupos == None:
		cuentas_posibles_destino = Cuenta.objects.filter(titulares=usu_destino,activo=True).exclude(tipo=u'Intergrupos')
	else:
		cuentas_posibles_destino = Cuenta.objects.filter(titulares=usu_destino,activo=True,grupo__in=grupos).exclude(tipo=u'Intergrupos')
		if len(cuentas_posibles_destino) == 0:
			#No es posible aplicar la selección del grupo de la actividad para hacer el comercio. 
			#Se tiene que pagar con otra cuenta distinta al grupo en que está publicada la actividad
			cuentas_posibles_destino = Cuenta.objects.filter(titulares=usu_destino,activo=True).exclude(tipo=u'Intergrupos')
		

	grupos_destino = []

	for item in cuentas_posibles_destino:
		if grupos_destino.count(item.grupo) == 0:
			grupos_destino.append(item.grupo)

	cuentas_posibles_origen = Cuenta.objects.filter(titulares=usu_origen,activo=True,grupo__in=grupos_destino).exclude(tipo=u'Intergrupos')

	n_cuentas_origen = len(cuentas_posibles_origen)
	n_cuentas_destino = len(cuentas_posibles_destino)
		
	comercio_intergrupos = False
	initial_data = {} # Para el posible formulario_1
	
	#Es posible el comercio dentro del grupo entre usuarios normales. Caso más normal. Precargo las cuentas.
	if n_cuentas_origen == 1 and n_cuentas_destino == 1:
		initial_data['cuenta_origen'] = cuentas_posibles_origen[0]
		initial_data['cuenta_destino'] = cuentas_posibles_destino[0]
		
	#No es posible dentro de un grupo. Puede ser comercio intergrupos o puede que no esté permitido. Se verá en el paso 2.
	# Hay que buscar entre todas las cuentas posibles de origen no condicionadas por los grupos del usuario destino.
	if n_cuentas_origen == 0 or n_cuentas_destino == 0:
		cuentas_posibles_origen = Cuenta.objects.filter(titulares=usu_origen,activo=True).exclude(tipo=u'Intergrupos')
		n_cuentas_origen = len(cuentas_posibles_origen)

	diccionario = {'cuentas_posibles_origen': cuentas_posibles_origen, 
				   'cuentas_posibles_destino':cuentas_posibles_destino,
				   'n_cuentas_origen':n_cuentas_origen,
				   'n_cuentas_destino':n_cuentas_destino,
				   'initial_data':initial_data}

	return diccionario
						
	
#######################################################################################################################################################
@login_required
def pagar_paso_1(request, id_actividad=0, id_usu=0, ajax=0):
	"""La función para pagar tanto a usuarios directamente por cualquier concepto como actividades en concreto."""
	
	situacion = _(u'Realizar un pago. Paso 1 de 2')
	intercambio = None
	origen = request.user
	idioma = request.LANGUAGE_CODE
	url = '/' + unicode(idioma) + '/economia/pagar_paso_1/' + unicode(id_actividad) + '/' + unicode(id_usu) + '/0/'
	datos = {}
	id_actividad = int(id_actividad)
	id_usu = int(id_usu)
	
	if id_actividad > 0:
		actividad = get_object_or_404(Actividad, pk=id_actividad)
		item = adjuntar_datos_actividad(request,item=actividad,opinion=True)
		destino = actividad.perfil.usuario
		perfil_destino = actividad.perfil
		datos['actividad'] = actividad
		diccionario = cuentas_posibles(request,origen,destino,grupos=actividad.grupo.all())

	if id_usu > 0:
		destino = get_object_or_404(User, pk=id_usu)
		perfil_destino = get_object_or_404(Perfil, usuario_id=id_usu)
		diccionario = cuentas_posibles(request,origen,destino,grupos=None)
	
	mis_cuentas = cuentas_usuario(request.user)
	sus_cuentas = cuentas_usuario(destino)
	n_mis_cuentas = len(mis_cuentas)
	n_sus_cuentas = len(sus_cuentas)

	qs_actividades_destino = Actividad.objects.filter(perfil=perfil_destino)
	diccionario['actividades'] = qs_actividades_destino

	datos['situacion'] = situacion
	datos['url'] = url
	datos['mis_cuentas'] = mis_cuentas
	datos['n_mis_cuentas'] = n_mis_cuentas
	datos['sus_cuentas'] = sus_cuentas
	datos['n_sus_cuentas'] = n_sus_cuentas
	datos['origen'] = origen
	datos['destino'] = destino
	datos['perfil_destino'] = perfil_destino
	datos['grupos_destino'] = Miembro.objects.filter(usuario=destino, activo=True)
	initial_data = diccionario['initial_data']
	initial_data['origen'] = origen
	initial_data['destino'] = destino
	
	if id_actividad > 0:
		initial_data['cantidad'] = actividad.precio_moneda_social
		initial_data['concepto'] = unicode(actividad)
		initial_data['actividad'] = actividad

	
	if ajax == '0':
		#Si no hay ajax
		direccion = 'economia/paso_1.html'
		
		if request.method == 'POST':
			form = Form_pago(request.POST,diccionario=diccionario,instance=intercambio)
			if form.is_valid():
				datos = logica_del_pago(request, form=form, confirmacion=False, admin=False)
				new_form = Form_pago_confirmacion(request.POST,instance=intercambio,initial=initial_data)
				datos['form'] = new_form
				return render_to_response('economia/paso_2.html',datos,context_instance=RequestContext(request))
				#return HttpResponseRedirect(reverse("economia-pagar-2"),datos)
				#return render(request,'economia/paso_2.html',datos,context_instance=RequestContext(request))
			else:
				datos['form'] = form
				#return render_to_response(direccion,datos,context_instance = RequestContext(request))
				#return render_to_response('reboot/index.html', context, context_instance=RequestContext(request))
				return render(direccion,datos,context_instance=RequestContext(request))
		else:
			form = Form_pago(initial=initial_data,diccionario=diccionario,instance=intercambio)
			datos['form'] = form
			return render_to_response(direccion,datos,context_instance=RequestContext(request)) 
	else:
		import time
		time.sleep(0.3)
		form = Form_pago(initial=initial_data,diccionario=diccionario,instance=intercambio)
		datos['form'] = form
		response = {'status_2':True}
		direccion = 'economia/formulario_pago.html'
		return render_to_response(direccion,datos,context_instance=RequestContext(request))
	

#######################################################################################################################################################
@login_required
def logica_del_pago(request,form=None, confirmacion=False,admin=False):
	"""La función para pagar tanto a usuarios directamente por cualquier concepto como actividades en concreto.
		Sirve tanto para la página principal como para la administración"""
	intercambio = None
	idioma = request.LANGUAGE_CODE
	
	# Esta función es llamada dos veces en el proceso de comprador
	# Borro los mensajes al principio porque la segunda vez muestra los mensajes duplicados
	storage = messages.get_messages(request)
	#for message in storage:
		#do_something_with(message)
	storage.used = True
	
	origen = form.cleaned_data['origen']
	mis_cuentas = cuentas_usuario(origen)
	destino = form.cleaned_data['destino']
	perfil_destino = get_object_or_404(Perfil, usuario=destino)
	sus_cuentas = cuentas_usuario(destino)
	n_mis_cuentas = len(mis_cuentas)
	n_sus_cuentas = len(sus_cuentas)
	
	datos = {}
	datos['mis_cuentas'] = mis_cuentas
	datos['n_mis_cuentas'] = n_mis_cuentas
	datos['sus_cuentas'] = sus_cuentas
	datos['n_sus_cuentas'] = n_sus_cuentas
	datos['origen'] = origen
	datos['destino'] = destino
	datos['perfil_destino'] = perfil_destino
	datos['grupos_destino'] = Miembro.objects.filter(usuario=destino, activo=True)
	
	n_intercambio =	get_n_intercambio(request)
	
	cuenta_origen = form.cleaned_data['cuenta_origen']
	cuenta_destino = form.cleaned_data['cuenta_destino']

	grupo_origen = get_object_or_404(Grupo,pk=cuenta_origen.grupo.pk)
	grupo_destino = get_object_or_404(Grupo,pk=cuenta_destino.grupo.pk)
	config_grupo_origen = get_object_or_404(Config_grupo,pk=grupo_origen.pk)
	config_grupo_destino = get_object_or_404(Config_grupo,pk=grupo_destino.pk)
	cantidad = form.cleaned_data['cantidad']

	actividad_elegida = form.cleaned_data['actividad']

	if actividad_elegida == None:
		actividad = None
		tipo = None
		object_id = None
	else:
		tipo = ContentType.objects.get_for_model(type(actividad_elegida))
		object_id = actividad_elegida.pk
		datos['actividad'] = actividad_elegida

	dic = {}
	dic['origen'] = origen
	dic['destino'] = datos['destino']
	dic['cuenta_origen'] = form.cleaned_data['cuenta_origen']
	dic['cuenta_destino'] = form.cleaned_data['cuenta_destino']
	dic['n_intercambio'] = n_intercambio
	dic['actividad'] = form.cleaned_data['actividad']
	dic['cantidad'] = form.cleaned_data['cantidad']
	dic['concepto'] = form.cleaned_data['concepto']
	dic['descripcion'] = form.cleaned_data['descripcion']
	dic['publico'] = form.cleaned_data['publico']
	dic['all_info'] = ''
	dic['info'] = ''
	
	#Si lo proceso desde la página princial
	if admin == False:
		dic['estado'] = _(u'Concluído')
		dic['tipo'] = _(u'Normal')
		dic['grupo_origen'] = grupo_origen
		dic['grupo_destino'] = grupo_destino
		dic['creado_por'] = origen
		dic['modificado_por'] = origen
	else:
		dic['estado'] = _(u'Pendiente')
		dic['tipo'] = _(u'Normal')
		dic['grupo_origen'] = form.cleaned_data['grupo_origen']
		dic['grupo_destino'] = form.cleaned_data['grupo_destino']
		dic['creado_por'] = request.user
		dic['modificado_por'] = request.user
	dic['content_type'] = tipo
	dic['object_id'] = object_id
	datos['dic'] = dic
	datos['dic']['cantidad_original'] = form.cleaned_data['cantidad']
	datos['dic']['moneda'] = grupo_origen.unidad_p
	
	check_margenes_origen = comprueba_margenes(request,origen,cuenta_origen,cantidad,superior=False)
	check_margenes_destino = comprueba_margenes(request,destino,cuenta_destino,cantidad,superior=True)
	
	if grupo_origen != grupo_destino:
		check_margenes_grupo_origen = comprueba_margenes_grupo(request,grupo_origen,cantidad,superior=False)
		check_margenes_grupo_destino = comprueba_margenes_grupo(request,grupo_destino,cantidad,superior=True)
	else:
		check_margenes_grupo_origen = 1
		check_margenes_grupo_destino = 1
		
	
	#Si todo es correcto cada función devuelve 1. Si no 0
	resultado_comprobar_todos_margenes = check_margenes_origen + check_margenes_destino + check_margenes_grupo_origen + check_margenes_grupo_destino
			
	if resultado_comprobar_todos_margenes == 4:
		datos['permitido'] = 1

		n_grupos_intercomercio_permitido = 0

		if grupo_origen != grupo_destino:

			cuenta_intergrupos_origen = Cuenta.objects.get(grupo=grupo_origen,tipo=u'Intergrupos')
			titulares_intergrupos_origen_qs = cuenta_intergrupos_origen.titulares.all()
			#Eligo uno porque el modelo intercambio no es ManyToManyField

			if len(titulares_intergrupos_origen_qs) > 0:
				titular_intergrupos_origen = titulares_intergrupos_origen_qs[0]
			else:
				datos['permitido'] = 0
				m1 = _(u'La operación no se puede realizar por un fallo en la configuración de la cuenta Inter grupos de origen')
				messages.add_message(request, messages.WARNING,m1 )

			#---------------------------------------------------------------------------------------------
			cuenta_intergrupos_destino = Cuenta.objects.get(grupo=grupo_destino,tipo=u'Intergrupos')
			titulares_intergrupos_destino_qs = cuenta_intergrupos_destino.titulares.all()

			if len(titulares_intergrupos_destino_qs) > 0:
				titular_intergrupos_destino = titulares_intergrupos_destino_qs[0]
			else:
				datos['permitido'] = 0
				m2 = _(u'La operación no se puede realizar por un fallo en la configuración de la cuenta Inter grupos de destino')
				messages.add_message(request, messages.WARNING,m2 )

			#---------------------------------------------------------------------------------------------

			cuenta_admin_origen = Cuenta.objects.get(grupo=grupo_origen,tipo=u'Administrador')
			titulares_admin_origen_qs = cuenta_admin_origen.titulares.all()

			if len(titulares_admin_origen_qs) > 0:
				titular_admin_origen = titulares_admin_origen_qs[0]
			else:
				datos['permitido'] = 0
				m3 = _(u'La operación no se puede realizar por un fallo en la configuración de la cuenta Administrador de origen')
				messages.add_message(request, messages.WARNING,m3 )

			#---------------------------------------------------------------------------------------------

			cuenta_admin_destino = Cuenta.objects.get(grupo=grupo_destino,tipo=u'Administrador')
			titulares_admin_destino_qs = cuenta_admin_destino.titulares.all()

			if len(titulares_admin_destino_qs) > 0:
				titular_admin_destino = titulares_admin_destino_qs[0]
			else:
				datos['permitido'] = 0
				m4 = _(u'La operación no se puede realizar por un fallo en la configuración de la cuenta Administrador de destino')
				messages.add_message(request, messages.WARNING,m4 )

			#---------------------------------------------------------------------------------------------

			if not config_grupo_origen.comercio_intergrupos:
				datos['permitido'] = 0
				m5 = _(u"""No es posible este intercambio.""")
				m5 += _(u' El grupo origen ') + unicode(config_grupo_origen.grupo) + _(u' no lo permite.')
				messages.add_message(request, messages.WARNING,m5 )
			else:
				n_grupos_intercomercio_permitido += 1

			#---------------------------------------------------------------------------------------------

			if not config_grupo_destino.comercio_intergrupos:
				datos['permitido'] = 0
				m6 = _(u"""No es posible este intercambio.""")
				m6 += _(u' El grupo destino ') + unicode(config_grupo_destino.grupo) + _(u' no lo permite.')
				messages.add_message(request, messages.WARNING,m6 )
			else:
				n_grupos_intercomercio_permitido += 1

			#---------------------------------------------------------------------------------------------
			# Si en los dos grupos está permitido el comercio intergrupos.
			if n_grupos_intercomercio_permitido == 2:
				
				#Impuestos intergrupos
				cantidad_libre_impuestos = round(cantidad,2)
				if config_grupo_origen.impuestos_intergrupos > 0:
					dic = get_info_impuestos_intergrupos(request,dic,cantidad,grupo_origen,config_grupo_origen,titular_admin_origen,cuenta_admin_origen,grupo_origen,grupo_origen)
					if confirmacion and datos['permitido'] == 1:
						#Intercambio impuestos intergrupo origen
						hacer_intercambio(request,dic)
						#dejo la info como estaba
						dic['grupo_origen'] = grupo_origen
						dic['grupo_destino'] = grupo_destino
					if dic['info'] != '' and datos['permitido'] == 1:
						messages.add_message(request, messages.WARNING,dic['info'])
					cantidad_libre_impuestos = cantidad_libre_impuestos - dic['cantidad']
				if config_grupo_destino.impuestos_intergrupos > 0:
					dic = get_info_impuestos_intergrupos(request,dic,cantidad,grupo_origen,config_grupo_destino,titular_admin_destino,cuenta_admin_destino,grupo_destino,grupo_destino)
					if confirmacion and datos['permitido'] == 1:
						#Intercambio impuestos intergrupo destino
						hacer_intercambio(request,dic)
						#dejo la info como estaba
						dic['grupo_origen'] = grupo_origen
						dic['grupo_destino'] = grupo_destino
					if dic['info'] != '' and datos['permitido'] == 1:
						messages.add_message(request, messages.WARNING,dic['info'])
					cantidad_libre_impuestos = cantidad_libre_impuestos - dic['cantidad']

				#Sobreescribo ciertos valores propios
				#Las cantidades para la transacción Intergrupos son las que están libres de impuestos

				dic['origen'] = titular_intergrupos_origen
				dic['cuenta_origen'] = cuenta_intergrupos_origen
				dic['destino'] = titular_intergrupos_destino
				dic['cuenta_destino'] = cuenta_intergrupos_destino
				dic['cantidad'] = cantidad_libre_impuestos
				dic['concepto'] = _(u'Intercambio integrupos')
				dic['tipo'] = _(u'Intergrupos')
				if confirmacion and datos['permitido'] == 1:
					#Intercambio intergrupos
					hacer_intercambio(request,dic)

				dic['origen'] = origen
				dic['cuenta_origen'] = cuenta_origen
				dic['destino'] = destino
				dic['cuenta_destino'] = cuenta_destino
				dic['cantidad'] = cantidad_libre_impuestos
				dic['concepto'] = form.cleaned_data['concepto']
				dic['tipo'] = _(u'Normal')
				if confirmacion and datos['permitido'] == 1:
					#Intercambio normal después de impuestos
					pk_c1 = hacer_intercambio(request,dic)

					dic['pk_c1'] = pk_c1
					enviar_mensaje = mandar_mensaje(request,dic)
					mensaje_ok = True
					mensaje_exito = _(u'La operación se ha realizado correctamente')
					messages.add_message(request, messages.INFO,mensaje_exito )
					datos['mensaje_ok'] = mensaje_ok

				mensaje_ok = True

			else:
				#n_grupos_intercomercio_permitido < 2 y no está permitido el comercio intergrupos
				mensaje_ko = True
				mensaje_error = _(u'La operación no se puede realizar porque alguno de los grupos no permite el comercio intergrupos')
				messages.add_message(request, messages.WARNING,mensaje_error )
				datos['mensaje_ko'] = mensaje_ko
				datos['permitido'] = 0

		else:
			#Es un intercambio dentro del grupo. #Si hay impuestos los dos tendrán el mismo
			
			if config_grupo_destino.impuestos_transaccion > 0:

				cuenta_admin_destino = Cuenta.objects.get(grupo=grupo_destino,tipo=u'Administrador')
				titulares_destino_qs = cuenta_admin_destino.titulares.all()
				#Eligo uno porque el modelo intercambio no es ManyToManyField

				if len(titulares_destino_qs) > 0:
					titular_admin_destino = titulares_destino_qs[0]
				else:
					m5 = _(u'La operación no se puede realizar por un fallo en la configuración de la cuenta Administrador de destino')
					messages.add_message(request, messages.WARNING,m5 )

				dic = get_info_impuestos(request,dic,cantidad,grupo_origen,config_grupo_origen,titular_admin_destino,cuenta_admin_destino)
				cantidad_libre_impuestos = round(cantidad,2)
				if confirmacion and datos['permitido'] == 1:
					#Intercambio impuestos
					hacer_intercambio(request,dic)
				if dic['info'] != '' and datos['permitido'] == 1:
					messages.add_message(request, messages.WARNING,dic['info'])
				cantidad_libre_impuestos = round(cantidad,2) - dic['cantidad']

				dic['concepto'] = form.cleaned_data['concepto']
				dic['destino'] = destino
				dic['cuenta_destino'] = cuenta_destino
				dic['cantidad'] = cantidad_libre_impuestos
				dic['tipo'] = _(u'Normal')

				if confirmacion and datos['permitido'] == 1:
					#Intercambio normal tras impuestos
					pk_c1 = hacer_intercambio(request,dic)
					dic['pk_c1'] = pk_c1
					enviar_mensaje = mandar_mensaje(request,dic)
					mensaje_ok = True
					mensaje_exito = _(u'La operación se ha realizado correctamente')
					messages.add_message(request, messages.INFO,mensaje_exito )
					datos['mensaje_ok'] = mensaje_ok
			else:
				#Intercambio normal sin impuestos
				if confirmacion and datos['permitido'] == 1:
			
					pk_c1 = hacer_intercambio(request,dic)
					dic['pk_c1'] = pk_c1
					enviar_mensaje = mandar_mensaje(request,dic)
					mensaje_ok = True
					mensaje_exito = _(u'La operación se ha realizado correctamente')
					messages.add_message(request, messages.INFO,mensaje_exito )
					datos['mensaje_ok'] = mensaje_ok
					
	else:
		datos['permitido'] = 0
		
	
	if confirmacion and datos['permitido'] == 1:
		situacion = _(u'Confirmación de la operación')
		
	if confirmacion == False and datos['permitido'] == 1:
		situacion = _(u'Realizar un pago. Paso 2 de 2')
		
	if datos['permitido'] == 0:
		situacion = _(u'Operación denegada')
		
	datos['situacion'] = situacion
		
	return datos



#######################################################################################################################################################
@login_required
def pagar_paso_2(request):
	"""La función para confirmar el tanto a usuarios directamente por cualquier concepto como actividades en concreto."""
	intercambio = None
	datos = {}

	if request.method == 'POST':
		form = Form_pago_confirmacion(request.POST,instance=intercambio)
		if form.is_valid():

			if form.cleaned_data['permitido'] == 1:
				datos = logica_del_pago(request, form=form, confirmacion=True, admin=False)
				ok = 1
				if datos['actividad'] == None:
					id_actividad = 0
				else:
					actividad = datos['actividad']
					id_actividad = actividad.pk

				return HttpResponseRedirect(reverse("economia-pagar-resultado", args=[ok, id_actividad]))
			else:
				datos = logica_del_pago(request, form=form, confirmacion=False, admin=False)
				return render_to_response('economia/paso_2.html',datos,context_instance=RequestContext(request))
		else:
			## el form no es valid
			ok = 0
			id_actividad = 0
			return HttpResponseRedirect(reverse("economia-pagar-resultado", args=[ok, id_actividad]))

	else:
		## No es request.method == 'POST':
		form = Form_pago_confirmacion(instance=intercambio)
		datos = logica_del_pago(request, form=form, confirmacion=False, admin=False)
		return render_to_response('economia/paso_2.html',datos,context_instance=RequestContext(request))
	
#######################################################################################################################################################
@login_required
def confirmacion(request,ok=1,id_actividad=0):
	
	datos = {}
	if ok:
		datos['situacion'] = _(u'¡El pago se ha realizado con éxito!')
	else:
		datos['situacion'] = _(u'¡Error en el proceso de pago!')
	
	if id_actividad > 0:
		a = get_object_or_404(Actividad, pk=int(id_actividad))
		actividad = adjuntar_datos_actividad(request,item=a,opinion=True)
		#Datos para que el Form_valorar_actividad sea valido 
		datos['pagina'] = 1
		datos['n_paginas'] = 1
		datos['retorno'] = 3
	else:
		actividad = False
		datos['retorno'] = False
		
	datos['ok'] = ok
	datos['actividad'] = actividad

	return render_to_response('economia/confirmacion.html',datos,context_instance=RequestContext(request))


########################################################################################################################################################		
				 
@login_required
def mandar_mensaje(request,dic={}):
	
	current_site = get_current_site(request)
	sitio = current_site.domain
	idioma=request.LANGUAGE_CODE
	destino = dic['destino']
	origen = dic['origen']
	cantidad  = dic['cantidad']
	pk_c1 = dic['pk_c1']

	asunto = _(u'Pago realizado con éxito')
	
	t1 = _(u'Concepto: ') + dic['concepto'] + u'<br>'
	t2 = _(u'Moneda social: ') + unicode(cantidad) + u'<br>'
	t3 = _(u'Para ver el detalle del movimiento, pincha aquí:') + u'<br><br><a href="'
	t4 = unicode(sitio) + '/' + unicode(idioma) + unicode('/economia/movimiento/') + unicode(pk_c1)
	t5 = '">Detalle del movimiento</a>'
	t6 = '</br></br>' + dic['all_info']
	
	mensaje = t1 + t2 + t3 + t4 + t5 + t6
	
	correspondencia = Correspondencia()
	correspondencia.destinatario = destino
	correspondencia.id_remitente = origen.pk
	correspondencia.remitente = origen.username
	correspondencia.email_remitente = origen.email
	correspondencia.asunto = asunto
	correspondencia.mensaje = mensaje
	correspondencia.save()
	
	return True

########################################################################################################################################################			
	
@login_required
def inicio(request,id_cuenta=0):
	
	situacion = _(u'contabilidad')
	id_cuenta = int(id_cuenta)
	
	try: 
		page = int(request.GET.get("page", '1'))
	except ValueError: 
		page = 1
	
	if request.user.is_authenticated():
		
		mis_cuentas = Cuenta.objects.filter(titulares=request.user)
		n_cuentas = len(mis_cuentas)
		
		if id_cuenta > 0:
			intercambio_qs = Intercambio.objects.filter(Q(usuarios=request.user) & (Q(cuenta_origen_id=id_cuenta)|Q(cuenta_destino_id=id_cuenta)))
			intercambio_qs = intercambio_qs.exclude(tipo=u'Intergrupos').order_by('-creado')
		else:
			intercambio_qs = Intercambio.objects.filter(usuarios=request.user).exclude(tipo=u'Intergrupos').order_by('-creado')
			
		n_intercambios = len(intercambio_qs)
		
		paginator = Paginator(intercambio_qs, 25)
		try:
			n_paginas = paginator.page(page)
		except (InvalidPage, EmptyPage):
			n_paginas = paginator.page(paginator.num_pages)
			
		context = {'situacion': situacion, 
				  'mis_cuentas':mis_cuentas, 
				  'n_cuentas':n_cuentas,
				  'intercambio_qs': n_paginas.object_list,
				  'n_intercambios':n_intercambios,
				  "n_paginas": n_paginas,
				  'id_cuenta':id_cuenta}
		
		# Funciona, pero insertar contenido en una table es más complicado. Habría que utilizar mejor div's
		if not request.is_ajax():
			return render_to_response('economia/inicio.html',context,context_instance=RequestContext(request)) 
		else:
			import time
			time.sleep(0.3)
			return render_to_response('economia/paginacion_contabilidad.html',context,context_instance=RequestContext(request))
		
	else:
		return HttpResponseRedirect(reverse("portada"))
	
#######################################################################################################################################################			
	
@login_required
def este_movimiento(request,id_movimiento=None):
	
	situacion = _(u'Detalle del movimiento')
	id_cont = int(id_movimiento)
	mis_cuentas = cuentas_usuario(request.user)
	n_cuentas = len(mis_cuentas)
	
	try:
		intercambio_qs = Intercambio.objects.filter(usuarios=request.user,pk=id_movimiento)
		intercambio = intercambio_qs[0]
		print 'intercambio_qs'
		print intercambio
		cuentas_origen = intercambio.cuenta_origen.titulares.all()
		context = {'situacion': situacion,
					'mis_cuentas':mis_cuentas, 
					'n_cuentas':n_cuentas,
					'intercambio': intercambio}
		return render_to_response('economia/este_movimiento.html',context,context_instance=RequestContext(request)) 
	
	except Intercambio.DoesNotExist:
		return HttpResponseRedirect(reverse("portada"))
	

#######################################################################################################################################################	
@login_required
def get_n_intercambio(request):
	
	try:
		ultimo_intercambio = Intercambio.objects.latest('creado')
		n_intercambio = ultimo_intercambio.n_intercambio + 1
	except Intercambio.DoesNotExist:
		n_intercambio = 1
		
	return n_intercambio
		
#######################################################################################################################################################		

@login_required
def actualiza_saldo(request):
	
	import time
	time.sleep(0.6)
	
	try:
		"""Si el admin no da de alta sus datos_personales, como las activades están referenciadas a los datos personales, fallan."""
		#datos_personales = Personal.objects.get(usuario=request.user)
		n_mensajes = Correspondencia.objects.filter(destinatario=request.user, leido=False).count()

		contabilidad = Intercambio.objects.filter(usuarios=request.user).aggregate(cantidad=Sum('cantidad'))
		saldo = contabilidad['cantidad']
		#Tengo que pasarlo a string porque las session en django ya no soportan el tipo decimal por defecto. 
		saldo_aux = unicode(saldo)

		if saldo == None:
			saldo = 0
			
		datos = {'n_mensajes': n_mensajes, 'saldo':saldo_aux }
		request.session['mensajes'] = datos
		mensaje_sistema = datos
	except Personal.DoesNotExist:
		mensaje_sistema = False
		saldo = 0

	return render_to_response('economia/mi_saldo.html',{'saldo':saldo},context_instance=RequestContext(request)) 
		

#######################################################################################################################################################

@login_required
def get_info_impuestos(request,dic,cantidad=None,grupo=None,config_grupo=None,destino=None,cuenta_destino=None):
	
	tasa = (cantidad * config_grupo.impuestos_transaccion)/100
	tasa = round(tasa,2)
	info = _(u'El grupo ') + unicode(grupo) + _(u' tiene una tasa de transacción del ') + unicode(config_grupo.impuestos_transaccion)
	info += _(u'%. Equivale a ') + unicode(tasa) + ' ' + unicode(grupo.unidad_p) + '. '
	#Sobreescribo ciertos valores con los de la cuenta adminiunicodeador
	dic['concepto'] = _('Impuestos ') + unicode(grupo) + _(u', op: ') + unicode(dic['n_intercambio'])
	dic['cantidad'] = tasa
	dic['destino'] = destino
	dic['cuenta_destino'] = cuenta_destino
	dic['grupo_origen'] = grupo
	dic['grupo_destino'] = grupo
	dic['all_info'] += info
	dic['info'] = info
	dic['tipo'] = u'Imp_interno'
	
	return dic

#######################################################################################################################################################

@login_required
def get_info_impuestos_intergrupos(request,dic,cantidad=None,grupo_origen=None,config_grupo_origen=None,destino=None,cuenta_destino=None,grupo_destino=None,titulo=None):

	tasa = (cantidad * config_grupo_origen.impuestos_intergrupos)/100
	tasa = round(tasa,2)
	info = _(u'Las operaciones intergrupos del grupo ') + unicode(grupo_origen) + _(u' tienen una tasa del  ') + unicode(config_grupo_origen.impuestos_intergrupos)
	info += _(u'%. Equivale a ') + unicode(tasa) + ' ' + unicode(grupo_origen.unidad_p) + '. '
	#Sobreescribo ciertos valores con los de la cuenta intergrupos
	dic['concepto'] = _('Impuesto intergrupo ') + unicode(titulo) + _(u', op: ') + unicode(dic['n_intercambio'])
	dic['cantidad'] = tasa
	dic['destino'] = destino
	dic['cuenta_destino'] = cuenta_destino
	dic['grupo_origen'] = grupo_origen
	dic['grupo_destino'] = grupo_destino
	dic['all_info'] += info
	dic['info'] = info
	dic['tipo'] = u'Imp_externo'
	
	return dic
#######################################################################################################################################################



