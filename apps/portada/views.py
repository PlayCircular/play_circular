# coding=utf-8

# Copyright (C) 2014 by Víctor Romero Blanco <info at playcircular dot com>.
# http://playcircular.com/
# It's licensed under the AFFERO GENERAL PUBLIC LICENSE unless stated otherwise.
# You can get copies of the licenses here: http://www.affero.org/oagpl.html
# AFFERO GENERAL PUBLIC LICENSE is also included in the file called "LICENSE".

from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, render_to_response
from django.core.urlresolvers import reverse
from django.utils import translation
import locale
from configuracion.models import *
from usuarios.models import *
from grupos.models import *
from grupos.views import get_info_grupos
from twitter.models import *
from twitter.views import *
from actividades.models import *
from actividades.forms import *
from actividades.views import *
from economia.models import *
from paginas.models import *
from paginas.views import adjuntar_datos_entrada
#from utilidades.views import *
from settings import MEDIA_ROOT, MEDIA_URL
from django.template import RequestContext, loader
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from datetime import *
from decimal import *
from django.db.models import Sum, Avg, Count



#######################################################################################################################################################

def portada(request, portada=False):	

	request.session.set_test_cookie()
	if request.session.test_cookie_worked():
		request.session.delete_test_cookie()

	if request.user.is_authenticated() and not portada:

		direccion = "portada/index_2.html"
		
		#datos_sociales = get_perfil_social(request, request.user)
		mis_cuentas = Cuenta.objects.filter(titulares=request.user)
		mis_grupos_qs = Miembro.objects.filter(usuario=request.user).values_list('grupo',flat=True)
		#Pongo el .distinct() para evitar que salgan duplicadas o triplicadas si pertenecen a 2 o 3 grupos
		tipos_entrada = ['e_general','e_grupo']
		tipos_propuesta = ['propuesta_general','propuesta_grupo']
		
		if len(mis_grupos_qs) > 0:
			nodes = False
			ultimas_entradas_qs = Entrada.objects.filter(grupo__in=mis_grupos_qs,tipo__in=tipos_entrada,estado='publicada').distinct().order_by('-creada')[:5]
			ultimas_propuestas_qs = Entrada.objects.filter(grupo__in=mis_grupos_qs,tipo__in=tipos_propuesta,estado='publicada').distinct().order_by('-creada')[:5]
			actividades_qs = Actividad.objects.filter(grupo__in=mis_grupos_qs).distinct().order_by('-creado')[:5]
			ultimos_intercambios_p = Intercambio.objects.filter((Q(grupo_origen__in=mis_grupos_qs) | Q(grupo_destino__in=mis_grupos_qs)) & Q(cantidad__gt=0) & Q(estado='Concluído') & Q(tipo='Normal') & Q(publico=True)).order_by('-creado')[:5]
			qs_grupos = Grupo.objects.filter(pk__in=mis_grupos_qs)
		else:
			nodes = Pagina.objects.filter(tipo='p_principal',estado='publicada',visibilidad='publica',en_menu=True)
			ultimas_entradas_qs = Entrada.objects.filter(tipo='e_general',estado='publicada',visibilidad='publica').distinct().order_by('-creada')[:5]
			ultimas_propuestas_qs = Entrada.objects.filter(tipo='propuesta_general',estado='publicada',visibilidad='publica').distinct().order_by('-creada')[:5]
			actividades_qs = Actividad.objects.all().distinct().order_by('-creado')[:5]
			ultimos_intercambios_p = Intercambio.objects.filter(publico=True,tipo='Normal',estado='Concluído', cantidad__gt=0).order_by('-creado')[:5]
			qs_grupos = Grupo.objects.filter(activo=True)
		
		
		info_grupos = get_info_grupos(request,qs_grupos)

	else:
		#datos_sociales = []
		nodes = Pagina.objects.filter(tipo='p_principal',estado='publicada',visibilidad='publica',en_menu=True)
		mis_cuentas = False
		info_grupos = []
		ultimas_entradas_qs = Entrada.objects.filter(tipo='e_general',estado='publicada',visibilidad='publica').distinct().order_by('-creada')[:5]
		ultimas_propuestas_qs = Entrada.objects.filter(tipo='propuesta_general',estado='publicada',visibilidad='publica').distinct().order_by('-creada')[:5]
		actividades_qs = Actividad.objects.all().distinct().order_by('-creado')[:5]
		ultimos_intercambios_p = Intercambio.objects.filter(publico=True,tipo='Normal',estado='Concluído', cantidad__gt=0).order_by('-creado')[:5]
		direccion = "portada/index_1.html"

		
	ultimas_actividades = []
	for item in actividades_qs:
		adjuntar_datos_actividad(request,item=item)
		ultimas_actividades.append(item)
		
	ultimas_entradas = []
	for item in ultimas_entradas_qs:
		adjuntar_datos_entrada(request,item=item)
		ultimas_entradas.append(item)
		
	ultimas_propuestas = []
	for item in ultimas_propuestas_qs:
		adjuntar_datos_entrada(request,item=item)
		ultimas_propuestas.append(item)

	form_busqueda = Form_busqueda()

	datos = {'form_busqueda':form_busqueda,
			 'nodes':nodes,
			 'info_grupos':info_grupos,
			 'mis_cuentas':mis_cuentas,
			 'ultimas_entradas':ultimas_entradas,
			 'ultimas_propuestas':ultimas_propuestas,
			 'ultimas_actividades':ultimas_actividades,
			 'ultimos_intercambios_p':ultimos_intercambios_p}

	return render_to_response(direccion,datos,context_instance=RequestContext(request))

#######################################################################################################################################################


def inicio_grupo(request,simbolo,slug=None):

	#El slug no sirve para nada. Solo para el SEO.
	
	grupo = get_object_or_404(Grupo,simbolo=simbolo)
	config_grupo = get_object_or_404(Config_grupo,grupo=grupo)
	situacion = grupo
	
	try:
		idioma = Idiomas_grupo.objects.get(grupo=grupo, idioma=request.LANGUAGE_CODE)
	except Idiomas_grupo.DoesNotExist:
		idiomas_qs = Idiomas_grupo.objects.filter(grupo=grupo).order_by('-idioma_default')
		idioma = idiomas_qs[0]
		
	grupo.palabras_clave = idioma.palabras_clave
	grupo.meta_descripcion = idioma.meta_descripcion
	grupo.robots = idioma.robots
	grupo.eslogan = idioma.eslogan
	grupo.pie_pagina = idioma.pie_pagina

	
	nodes = Pagina.objects.filter(grupo=grupo,tipo='p_grupo',estado='publicada',en_menu=True)
	tipos_entrada = ['e_general','e_grupo']
	ultimas_entradas_qs = Entrada.objects.filter(grupo=grupo,tipo__in=tipos_entrada).distinct().order_by('-creada')[:5]
	tipos_propuesta = ['propuesta_general','propuesta_grupo']
	ultimas_propuestas_qs = Entrada.objects.filter(grupo=grupo,tipo__in=tipos_propuesta).distinct().order_by('-creada')[:5]
	actividades_qs = Actividad.objects.filter(grupo=grupo).order_by('-creado')[:5]
	ultimos_intercambios_p = Intercambio.objects.filter((Q(grupo_origen=grupo) | Q(grupo_destino=grupo)) & Q(cantidad__gt=0) & Q(tipo='Normal')).order_by('-creado')[:5]
	banners = Banner.objects.filter(grupo=grupo,activo=True)
	if len(banners) == 0:
		banners = Banner_general.objects.filter(activo=True)
	
	ultimas_actividades = []
	for item in actividades_qs:
		adjuntar_datos_actividad(request,item=item)
		ultimas_actividades.append(item)
		
	ultimas_entradas = []
	for item in ultimas_entradas_qs:
		adjuntar_datos_entrada(request,item=item)
		ultimas_entradas.append(item)
		
	ultimas_propuestas = []
	for item in ultimas_propuestas_qs:
		adjuntar_datos_entrada(request,item=item)
		ultimas_propuestas.append(item)

	grupo.n_miembros = Miembro.objects.filter(grupo=grupo, activo=True).count()
	grupo.n_admin = Miembro.objects.filter(grupo=grupo, activo=True,nivel=u'Administrador').count()
	#Operaciones en el grupo.
	qs_total_operaciones = Intercambio.objects.filter((Q(grupo_origen=grupo) | Q(grupo_destino=grupo)) & Q(cantidad__gt=0) & Q(tipo='Normal'))
	n_operaciones = len(qs_total_operaciones)
	grupo.n_operaciones = n_operaciones
	
	qs_media = Intercambio.objects.filter((Q(grupo_origen=grupo) | Q(grupo_destino=grupo)) & Q(cantidad__gt=0) & Q(tipo='Normal')).aggregate(media=Avg('cantidad'))
	if qs_media['media']:
		valor_medio_op = Decimal(qs_media['media'])
		valor_medio_op = round(valor_medio_op,2)
	else:
		valor_medio_op = 0

	hoy = date.today()
	hace_30_dias = hoy - timedelta(days=30)
	hace_7_dias = hoy - timedelta(days=7)

	fecha_inicio_grupo = grupo.creado.date()
	diferencia = hoy - fecha_inicio_grupo
	n_dias = diferencia.days
	n_dias = Decimal(n_dias)
	
	if n_dias > 0:
		operaciones_x_dia = round(n_operaciones/n_dias,3)
	else:
		operaciones_x_dia = 0
		
	grupo.valor_medio_op = valor_medio_op
	grupo.operaciones_x_dia = operaciones_x_dia
	grupo.op_ultimo_mes = qs_total_operaciones.filter(creado__gt=hace_30_dias).count()
	grupo.op_ultima_semana = qs_total_operaciones.filter(creado__gt=hace_7_dias).count()
	
	datos = {'nodes':nodes,
			'grupo':grupo,
			'idioma':idioma,
			'banners':banners,
			'situacion':situacion,
			'ultimas_entradas':ultimas_entradas,
			'ultimas_propuestas':ultimas_propuestas,
			'ultimas_actividades':ultimas_actividades,
			'ultimos_intercambios_p':ultimos_intercambios_p}
	
	#Aquí no utilizo el custom_proc para que salgan los banners específicos del grupo.
	return render_to_response("portada/inicio_grupo.html",datos,context_instance=RequestContext(request))

#######################################################################################################################################################

def error_404(request):	

	return render_to_response("404.html", {} ,context_instance=RequestContext(request))
	
	
#######################################################################################################################################################



