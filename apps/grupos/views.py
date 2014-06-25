# coding=utf-8


# Copyright (C) 2014 by Víctor Romero Blanco <info at playcircular dot com>.
# http://playcircular.com/
# It's licensed under the AFFERO GENERAL PUBLIC LICENSE unless stated otherwise.
# You can get copies of the licenses here: http://www.affero.org/oagpl.html
# AFFERO GENERAL PUBLIC LICENSE is also included in the file called "LICENSE".

from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, render_to_response
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User,Group, Permission
from django.core.mail import send_mail, send_mass_mail, BadHeaderError,EmailMultiAlternatives
from django.contrib.sites.models import get_current_site
from usuarios.models import *
from grupos.models import *
from grupos.forms import *
from actividades.models import *
from configuracion.models import *
from economia.models import *
#from utilidades.views import *
from django.contrib.auth.decorators import login_required
from django.template import RequestContext, loader
from django.utils.translation import ugettext as _
from django.db.models import Sum, connection, Avg, Count
from django.db.models import Q
from datetime import *
from decimal import *
import qsstats # Sirve para hacer consultas sobre el número de cuentas abiertas por día, mes, año...
from django.core.paginator import Paginator, InvalidPage, EmptyPage

#######################################################################################################################################################

def get_info_grupos(request,qs_grupos=[]):	
			
	info_grupos = []
	for item in qs_grupos:

		item.n_miembros = Miembro.objects.filter(grupo=item, activo=True).count()
		item.n_admin = Miembro.objects.filter(grupo=item, activo=True,nivel=u'Administrador').count()
		item.n_actividades = Actividad.objects.filter(grupo=item, activo=True).count()
		#Operaciones en el grupo.
		qs_total_operaciones = Intercambio.objects.filter((Q(grupo_origen=item) | Q(grupo_destino=item)) & Q(cantidad__gt=0) & Q(tipo='Normal'))
		n_operaciones = len(qs_total_operaciones)
		item.n_operaciones = n_operaciones
		
		qs_media = Intercambio.objects.filter((Q(grupo_origen=item) | Q(grupo_destino=item)) & Q(cantidad__gt=0) & Q(tipo='Normal')).aggregate(media=Avg('cantidad'))
		if qs_media['media']:
			valor_medio_op = Decimal(qs_media['media'])
			valor_medio_op = round(valor_medio_op,2)
		else:
			valor_medio_op = 0

		hoy = date.today()
		hace_30_dias = hoy - timedelta(days=30)
		hace_7_dias = hoy - timedelta(days=7)

		fecha_inicio_grupo = item.creado.date()
		diferencia = hoy - fecha_inicio_grupo
		n_dias = diferencia.days
		n_dias = Decimal(n_dias)
		
		if n_dias > 0:
			operaciones_x_dia = round(n_operaciones/n_dias,3)
		else:
			operaciones_x_dia = 0
			
		item.valor_medio_op = valor_medio_op
		item.operaciones_x_dia = operaciones_x_dia
		item.op_ultimo_mes = qs_total_operaciones.filter(creado__gt=hace_30_dias).count()
		item.op_ultima_semana = qs_total_operaciones.filter(creado__gt=hace_7_dias).count()
		
		info_grupos.append(item)

	return info_grupos

#######################################################################################################################################################

def index(request):	
	
	qs_grupos = Grupo.objects.filter(activo=True).order_by('provincia')
	info_grupos = get_info_grupos(request,qs_grupos)
	situacion = _(u'grupos')

	return render_to_response("grupos/inicio_grupos.html", {'info_grupos': info_grupos, 'situacion': situacion} ,context_instance=RequestContext(request))

#######################################################################################################################################################

def get_admins(request,id_grupo=None):	
	
	grupo = get_object_or_404(Grupo,pk=id_grupo)
	config_grupo = Config_grupo.objects.get(grupo=grupo)
	admins = Miembro.objects.filter(grupo=grupo,nivel=u'Administrador')
	try:
		idioma = Idiomas_grupo.objects.get(grupo=grupo, idioma=request.LANGUAGE_CODE)
	except Idiomas_grupo.DoesNotExist:
		idiomas_qs = Idiomas_grupo.objects.filter(grupo=grupo).order_by('-idioma_default')
		idioma = idiomas_qs[0]

	situacion = _(u'administradores del grupo ') + str(grupo)
	
	datos = {'grupo': grupo, 
		     'situacion': situacion,
		     'config_grupo': config_grupo,
		     'idioma': idioma,
		     'admins':admins}

	return render_to_response("grupos/admins_grupo.html", datos ,context_instance=RequestContext(request))

#######################################################################################################################################################

def estadisticas_grupo(request, id_grupo=None):
	
	"""Estadísticas generales. Son las mismas que aparecen en portada."""
	
	grupo = get_object_or_404(Grupo,pk=id_grupo)
	config = Config_grupo.objects.get(grupo=grupo)
	try:
		idioma = Idiomas_grupo.objects.get(grupo=grupo, idioma=request.LANGUAGE_CODE)
	except Idiomas_grupo.DoesNotExist:
		idiomas_qs = Idiomas_grupo.objects.filter(grupo=grupo).order_by('-idioma_default')
		idioma = idiomas_qs[0]
	
	info = get_info_grupos(request,[grupo])

	situacion = _(u'estadisticas')
	datos = {'grupo':grupo,
			 'config':config,
			 'idioma':idioma,
			 'situacion':situacion,
			 'info':info}

	return render_to_response("grupos/estadisticas.html", datos ,context_instance=RequestContext(request))

####################################################################################################

def estadisticas_crecimiento_usuarios(request, id_grupo=None):
	
	situacion = _(u'crecimiento de usuarios')
	
	grupo = get_object_or_404(Grupo,pk=id_grupo)
	miembros_qs = Miembro.objects.filter(grupo=grupo, activo=True).values('usuario')
	#datos_personales_qs = Perfil.objects.filter(usuario__in=miembros_qs)
	
	hoy = date.today()
	#hace_30_dias = hoy - timedelta(days=30)
	#hace_7_dias = hoy - timedelta(days=7)
	hace_6_meses = hoy - timedelta(weeks=24)
	#hace_1_anio = hoy - timedelta(weeks=54)
	
	fecha_inicio_grupo = grupo.creado.date()
	diferencia = hoy - fecha_inicio_grupo
	n_dias = diferencia.days
	#n_dias = Decimal(n_dias)
	
	
	desde_inicio = hoy - timedelta(days=n_dias)
	
	"""Esto es para sacar las altas nuevas por día, semana, mes."""
	qss = qsstats.QuerySetStats(miembros_qs, 'creado')
	qs_altas_x_mes = qss.time_series(desde_inicio, hoy, interval='months')
	
	datos = {'grupo':grupo,
			 'situacion':situacion,
			 'qs_altas_x_mes':qs_altas_x_mes,
			 }

	
	return render_to_response("grupos/crecimiento_usuarios.html", datos ,context_instance=RequestContext(request))

####################################################################################################

def balance_usuarios(request, id_grupo=None):
	
	situacion = _(u'balance de usuarios')
	current_site = get_current_site(request)
	sitio = current_site.domain
	idioma=request.LANGUAGE_CODE
	url = unicode(sitio) + '/' + unicode(idioma) + '/grupos/balance_usuarios/' + unicode(id_grupo) + '/'
	
	grupo = get_object_or_404(Grupo,pk=id_grupo)
	miembros_qs = Miembro.objects.filter(grupo=grupo, activo=True).order_by('creado')
	
	info = []
	for miembro in miembros_qs:
		sus_cuentas = Cuenta.objects.filter(titulares=miembro.usuario).order_by('creado')
		dic = {'miembro':miembro,'sus_cuentas':sus_cuentas}
		info.append(dic)
		
	try: 
		page = int(request.GET.get("page", '1'))
	except ValueError: 
		page = 1
		
	paginator = Paginator(info, 25)
	try:
		n_paginas = paginator.page(page)
	except (InvalidPage, EmptyPage):
		n_paginas = paginator.page(paginator.num_pages)

	datos = {'grupo':grupo,
			 'situacion':situacion,
			 'info':n_paginas.object_list,
			 'n_paginas': n_paginas, 
			 'url':url }

	if not request.is_ajax():
		return render_to_response("grupos/balance_usuarios.html",datos,context_instance=RequestContext(request))
	else:
		import time
		time.sleep(0.3)
		return render_to_response('grupos/paginacion_balances.html',datos,context_instance=RequestContext(request))
	
	

####################################################################################################

def estadisticas_actividad(request, id_grupo=None):
	
	situacion = _(u'estadísticas de actividades')
	
	grupo = get_object_or_404(Grupo,pk=id_grupo)
	actividades_qs = Actividad.objects.filter(grupo=grupo)
	miembros_qs = Miembro.objects.filter(grupo=grupo, activo=True).values('usuario')
	
	n_miembros = len(miembros_qs)
	n_ofertas_bienes = Actividad.objects.filter(grupo=grupo,activo=True,tipo=u'oferta',clase=u'bienes').count()
	n_ofertas_servicios = Actividad.objects.filter(grupo=grupo,activo=True,tipo=u'oferta',clase=u'servicios').count()
	n_demandas_bienes = Actividad.objects.filter(grupo=grupo,activo=True,tipo=u'demanda',clase=u'bienes').count()
	n_demandas_servicios = Actividad.objects.filter(grupo=grupo,activo=True,tipo=u'demanda',clase=u'servicios').count()
	n_total_ofertas = n_ofertas_bienes + n_ofertas_servicios
	n_total_demandas = n_demandas_bienes + n_demandas_servicios
	n_total_actividades = n_total_ofertas + n_total_demandas
	
	if n_total_actividades > 0:
		media_actividad_miembro = round(n_total_actividades/n_miembros,2)
	else:
		media_actividad_miembro = 0
		
	opiniones_1 = Opinion_actividad.objects.filter(usuario__in=miembros_qs,actividad__in=actividades_qs).aggregate(media=Avg('rating_para_mi_antes'))
	if opiniones_1['media']:
		media_valor_antes_total = round(opiniones_1['media'],2)
	else:
		media_valor_antes_total = 0
	
	ofertas_bienes_qs = Actividad.objects.filter(grupo=grupo,activo=True,tipo=u'oferta',clase=u'bienes')
	opiniones_2 = Opinion_actividad.objects.filter(usuario__in=miembros_qs,actividad__in=ofertas_bienes_qs).aggregate(media=Avg('rating_para_mi_antes'))
	if opiniones_2['media']:
		media_valor_antes_ofertas_bienes = round(opiniones_2['media'],2)
	else:
		media_valor_antes_ofertas_bienes = 0
	
	ofertas_servicios_qs = Actividad.objects.filter(grupo=grupo,activo=True,tipo=u'oferta',clase=u'servicios')
	opinion_3 = Opinion_actividad.objects.filter(usuario__in=miembros_qs,actividad__in=ofertas_servicios_qs).aggregate(media=Avg('rating_para_mi_antes'))
	if opinion_3['media']:
		media_valor_antes_ofertas_servicios = round(opinion_3['media'],2)
	else:
		media_valor_antes_ofertas_servicios = 0
		
	demanda_bienes_qs = Actividad.objects.filter(grupo=grupo,activo=True,tipo=u'demanda',clase=u'bienes')
	opiniones_4 = Opinion_actividad.objects.filter(usuario__in=miembros_qs,actividad__in=demanda_bienes_qs).aggregate(media=Avg('rating_para_mi_antes'))
	if opiniones_4['media']:
		media_valor_antes_demanda_bienes = round(opiniones_4['media'],2)
	else:
		media_valor_antes_demanda_bienes = 0
	
	demanda_servicios_qs = Actividad.objects.filter(grupo=grupo,activo=True,tipo=u'demanda',clase=u'servicios')
	opinion_5 = Opinion_actividad.objects.filter(usuario__in=miembros_qs,actividad__in=demanda_servicios_qs).aggregate(media=Avg('rating_para_mi_antes'))
	if opinion_5['media']:
		media_valor_antes_demanda_servicios = round(opinion_5['media'],2)
	else:
		media_valor_antes_demanda_servicios = 0
		
	me_interesa_1 = Opinion_actividad.objects.filter(usuario__in=miembros_qs,actividad__in=ofertas_bienes_qs,me_gusta_para_mi=True).values('actividad').distinct().count()
	if n_ofertas_bienes > 0:
		p_interes_oferta_bienes = (me_interesa_1 * 100)/n_ofertas_bienes
		p_interes_oferta_bienes = round(p_interes_oferta_bienes,2)
	else:
		p_interes_oferta_bienes = 0
		
	me_interesa_2 = Opinion_actividad.objects.filter(usuario__in=miembros_qs,actividad__in=ofertas_servicios_qs,me_gusta_para_mi=True).values('actividad').distinct().count()
	if n_ofertas_servicios > 0:
		p_interes_oferta_servicios = (me_interesa_2 * 100)/n_ofertas_servicios
		p_interes_oferta_servicios = round(p_interes_oferta_servicios,2)
	else:
		p_interes_oferta_servicios = 0
		
	me_interesa_3 = Opinion_actividad.objects.filter(usuario__in=miembros_qs,actividad__in=demanda_bienes_qs,me_gusta_para_mi=True).values('actividad').distinct().count()
	if n_demandas_bienes > 0:
		p_interes_demanda_bienes = (me_interesa_3 * 100)/n_demandas_bienes
		p_interes_demanda_bienes = round(p_interes_demanda_bienes,2)
	else:
		p_interes_demanda_bienes = 0
		
	me_interesa_4 = Opinion_actividad.objects.filter(usuario__in=miembros_qs,actividad__in=demanda_servicios_qs,me_gusta_para_mi=True).values('actividad').distinct().count()
	if n_demandas_servicios > 0:
		p_interes_demanda_servicios = (me_interesa_4 * 100)/n_demandas_servicios
		p_interes_demanda_servicios = round(p_interes_demanda_servicios,2)
	else:
		p_interes_demanda_servicios = 0
		
	ofertas_qs = Actividad.objects.filter(grupo=grupo,activo=True,tipo=u'oferta')
	me_interesa_5 = Opinion_actividad.objects.filter(usuario__in=miembros_qs,actividad__in=ofertas_qs,me_gusta_para_mi=True).values('actividad').distinct().count()
	if n_total_ofertas > 0:
		p_interes_ofertas = (me_interesa_5 * 100)/n_total_ofertas
		p_interes_ofertas = round(p_interes_ofertas,2)
	else:
		p_interes_ofertas = 0
		
	demandas_qs = Actividad.objects.filter(grupo=grupo,activo=True,tipo=u'demanda')
	me_interesa_6 = Opinion_actividad.objects.filter(usuario__in=miembros_qs,actividad__in=demandas_qs,me_gusta_para_mi=True).values('actividad').distinct().count()
	if n_total_demandas > 0:
		p_interes_demandas = (me_interesa_6 * 100)/n_total_demandas
		p_interes_demandas = round(p_interes_demandas,2)
	else:
		p_interes_demandas = 0

	hoy = date.today()
	hace_6_meses = hoy - timedelta(weeks=24)
	fecha_inicio_grupo = grupo.creado.date()
	diferencia = hoy - fecha_inicio_grupo
	n_dias = diferencia.days

	desde_inicio = hoy - timedelta(days=n_dias)
	
	"""Esto es para sacar las altas nuevas por día, semana, mes."""
	qss = qsstats.QuerySetStats(actividades_qs, 'creado')
	qs_altas_x_mes = qss.time_series(desde_inicio, hoy, interval='months')
	
	qs_ofertas = Actividad.objects.filter(grupo=grupo,tipo=u'oferta')
	qss = qsstats.QuerySetStats(qs_ofertas, 'creado')
	qs_ofertas_x_mes = qss.time_series(desde_inicio, hoy, interval='months')
	
	qs_demandas = Actividad.objects.filter(grupo=grupo,tipo=u'demanda')
	qss = qsstats.QuerySetStats(qs_demandas, 'creado')
	qs_demandas_x_mes = qss.time_series(desde_inicio, hoy, interval='months')
	
	qs_bienes = Actividad.objects.filter(grupo=grupo,clase=u'bienes')
	qss = qsstats.QuerySetStats(qs_bienes, 'creado')
	qs_bienes_x_mes = qss.time_series(desde_inicio, hoy, interval='months')
	
	qs_servicios = Actividad.objects.filter(grupo=grupo,clase=u'servicios')
	qss = qsstats.QuerySetStats(qs_servicios, 'creado')
	qs_servicios_x_mes = qss.time_series(desde_inicio, hoy, interval='months')
	
	datos = {'grupo':grupo,
	'situacion':situacion,
	'qs_altas_x_mes':qs_altas_x_mes,
	'qs_ofertas_x_mes':qs_ofertas_x_mes,
	'qs_demandas_x_mes':qs_demandas_x_mes,
	'qs_bienes_x_mes':qs_bienes_x_mes,
	'qs_servicios_x_mes':qs_servicios_x_mes,
	'n_ofertas_bienes':n_ofertas_bienes,
	'n_ofertas_servicios':n_ofertas_servicios,
	'n_demandas_bienes':n_demandas_bienes,
	'n_demandas_servicios':n_demandas_servicios,
	'n_total_ofertas':n_total_ofertas,
	'n_total_demandas':n_total_demandas,
	'n_total_actividades':n_total_actividades,
	'n_miembros':n_miembros,
	'media_actividad_miembro':media_actividad_miembro,
	'media_valor_antes_total':media_valor_antes_total,
	'media_valor_antes_ofertas_bienes':media_valor_antes_ofertas_bienes,
	'media_valor_antes_ofertas_servicios':media_valor_antes_ofertas_servicios,
	'media_valor_antes_demanda_bienes':media_valor_antes_demanda_bienes,
	'media_valor_antes_demanda_servicios':media_valor_antes_demanda_servicios,
	'p_interes_oferta_bienes':p_interes_oferta_bienes,
	'p_interes_oferta_servicios':p_interes_oferta_servicios,
	'p_interes_demanda_bienes':p_interes_demanda_bienes,
	'p_interes_demanda_servicios':p_interes_demanda_servicios,
	'p_interes_ofertas':p_interes_ofertas,
	'p_interes_demandas':p_interes_demandas,
	}
	
	
	return render_to_response("grupos/crecimiento_actividades.html", datos ,context_instance=RequestContext(request))


####################################################################################################

def estadisticas_intercambio(request, id_grupo=None):
	
	situacion = _(u'estadísticas de intercambio')
	id_grupo = int(id_grupo)
	
	grupo = get_object_or_404(Grupo,pk=id_grupo)
	cuenta_intergrupos = Cuenta.objects.get(grupo=grupo,tipo='Intergrupos')
	miembros_qs = Miembro.objects.filter(grupo=grupo, activo=True).values_list('usuario',flat=True)
	cuentas_miembros_qs = Cuenta.objects.filter(titulares=miembros_qs).values_list('pk',flat=True).order_by('pk').distinct()
	
	n_total_op_dentro_grupo = Intercambio.objects.filter(grupo_origen=grupo,grupo_destino=grupo,cantidad__gt=0,tipo='Normal').count()
	
	#el grupo_origen es el grupo de quien paga. Siempre se paga, nunca se cobra. Por tanto el grupo origen se refiere al otro grupo, no al propio.
	n_total_op_importadas = Intercambio.objects.filter(grupo_origen=grupo,cantidad__lt=0,tipo='Normal').exclude(grupo_destino=grupo).count()
	#n_total_op_importadas_b = Intercambio.objects.filter(grupo_origen=grupo,cantidad__lt=0,tipo='Intergrupos').exclude(grupo_destino=grupo).count()
	n_total_op_exportadas = Intercambio.objects.filter(grupo_destino=grupo,cantidad__gt=0,tipo='Normal').exclude(grupo_origen=grupo).count()
	#n_total_op_exportadas_b = Intercambio.objects.filter(grupo_destino=grupo,cantidad__gt=0,tipo='Intergrupos').exclude(grupo_origen=grupo).count()
	
	#n_total_operaciones = n_total_op_dentro_grupo + n_total_op_importadas + n_total_op_exportadas
	qs_total_operaciones = Intercambio.objects.filter((Q(grupo_origen=grupo) | Q(grupo_destino=grupo)) & Q(cantidad__gt=0) & Q(tipo='Normal'))
	n_total_operaciones = len(qs_total_operaciones)
	
	imp_internos = Intercambio.objects.filter(grupo_origen=grupo,grupo_destino=grupo,cantidad__gt=0,tipo='Imp_interno')
	n_op_imp_internos = len(imp_internos)
	imp_internos = imp_internos.aggregate(suma_impuestos=Sum('cantidad'))
	if imp_internos['suma_impuestos']:
		valor_imp_internos = Decimal(imp_internos['suma_impuestos'])
	else:
		valor_imp_internos = 0
		
	imp_externos = Intercambio.objects.filter(grupo_origen=grupo,cantidad__gt=0,tipo='Imp_externo').exclude(grupo_destino=grupo)
	n_op_imp_externos = len(imp_externos)
	imp_externos = imp_externos.aggregate(suma_impuestos=Sum('cantidad'))
	if imp_externos['suma_impuestos']:
		valor_imp_externos = Decimal(imp_externos['suma_impuestos'])
	else:
		valor_imp_externos = 0
		
	n_total_op_impuestos = n_op_imp_internos + n_op_imp_externos
	valor_total_impuestos = valor_imp_internos + valor_imp_externos

	qs_op_importadas = Intercambio.objects.filter(grupo_origen=grupo,cantidad__lt=0,tipo='Normal').exclude(grupo_destino=grupo).aggregate(suma=Sum('cantidad'))
	#print qs_op_importadas
	if qs_op_importadas['suma']:
		valor_op_importadas = Decimal(qs_op_importadas['suma'])
	else:
		valor_op_importadas = 0
		
	qs_op_exportadas = Intercambio.objects.filter(grupo_destino=grupo,cantidad__gt=0,tipo='Normal').exclude(grupo_origen=grupo).aggregate(suma=Sum('cantidad'))
	#print qs_op_exportadas
	if qs_op_exportadas['suma']:
		valor_op_exportadas = Decimal(qs_op_exportadas['suma'])
	else:
		valor_op_exportadas = 0

	n_miembros = len(miembros_qs)
	n_total_op_dentro_grupo = Decimal(n_total_op_dentro_grupo)
	#n_miembros_con_operaciones_b = Intercambio.objects.filter((Q(grupo_origen=grupo) | Q(grupo_destino=grupo)) & Q(tipo='Normal')).values('usuarios').order_by('usuarios').distinct()
	n_miembros_con_operaciones = Intercambio.objects.filter(usuarios__in=miembros_qs,tipo='Normal').values('usuarios').order_by('usuarios').distinct().count()

	suma_de_operaciones_positivas = Intercambio.objects.filter(grupo_origen=grupo,grupo_destino=grupo,cantidad__gt=0,tipo='Normal').aggregate(suma=Sum('cantidad'))
	if suma_de_operaciones_positivas['suma']:
		valor_operaciones_positivas = Decimal(suma_de_operaciones_positivas['suma'])
	else:
		valor_operaciones_positivas = 0
		
	suma_de_operaciones_negativas = Intercambio.objects.filter(grupo_origen=grupo,grupo_destino=grupo,cantidad__lt=0,tipo='Normal').aggregate(resta=Sum('cantidad'))
	if suma_de_operaciones_negativas['resta']:
		valor_operaciones_negativas = Decimal(suma_de_operaciones_negativas['resta'])
	else:
		valor_operaciones_negativas = 0
		
	#balance_del_grupo = valor_operaciones_positivas + valor_operaciones_negativas + valor_op_importadas + valor_op_exportadas
	balance_del_grupo = cuenta_intergrupos.saldo
	
	qs_media = Intercambio.objects.filter((Q(grupo_origen=grupo) | Q(grupo_destino=grupo)) & Q(cantidad__gt=0) & Q(tipo='Normal')).aggregate(media=Avg('cantidad'))
	if qs_media['media']:
		valor_medio_operacion = Decimal(qs_media['media'])
		valor_medio_operacion = round(valor_medio_operacion,2)
	else:
		valor_medio_operacion = 0
		
	saldo_miembros_qs = Intercambio.objects.filter(usuarios__in=miembros_qs,tipo='Normal').values('usuarios').annotate(suma=Sum('cantidad'))
			
	cadena = ''
	for item in miembros_qs:
		cadena += "%s, " % item

	cadena  = str(cadena[:-2])
	
	query_1 = """SELECT YEAR(creado),MONTH(creado),ROUND(SUM(cantidad),2)
				 FROM economia_intercambio
				 WHERE cantidad > 0 
					AND tipo='Normal' 
					AND ((grupo_origen_id = %d) OR (grupo_destino_id = %d))
				 GROUP BY MONTH(creado)""" % (id_grupo, id_grupo)
				 
	query_2 = """SELECT YEAR(creado),MONTH(creado), DAY(creado),ROUND(SUM(cantidad),2)
				 FROM economia_intercambio
				 WHERE cantidad > 0 
					AND tipo='Normal' 
					AND ((grupo_origen_id = %d) OR (grupo_destino_id = %d))
				 GROUP BY DAY(creado)""" % (id_grupo, id_grupo)
				 
	cursor = connection.cursor()
	cursor.execute(query_1)
	sql = cursor.fetchall()
	cursor.close()
	
	suma_op_x_mes = []
	for item in sql:
		fecha = date(item[0],item[1],1)
		datos = (fecha,item[2])
		suma_op_x_mes.append(datos) 
		
	cursor = connection.cursor()
	cursor.execute(query_2)
	sql = cursor.fetchall()
	cursor.close()

	suma_op_x_dia = []
	for item in sql:
		fecha = date(item[0],item[1],item[2])
		datos = (fecha,item[3])
		suma_op_x_dia.append(datos) 

	hoy = date.today()
	fecha_inicio_grupo = grupo.creado.date()
	diferencia = hoy - fecha_inicio_grupo
	n_dias = diferencia.days
	desde_inicio = hoy - timedelta(days=n_dias)
	n_dias = Decimal(n_dias)
	
	if n_dias > 0:
		operaciones_x_dia = round(n_total_operaciones/n_dias,3)
	else:
		operaciones_x_dia = 0

	qss = qsstats.QuerySetStats(qs_total_operaciones, 'creado')
	qs_ope_x_mes = qss.time_series(desde_inicio, hoy, interval='months')
	qs_ope_x_dia = qss.time_series(desde_inicio, hoy, interval='days')
	
	datos = {'grupo':grupo,
	'situacion':situacion,
	'n_total_operaciones':n_total_operaciones,
	#'n_total_operaciones_b':n_total_operaciones_b,
	'n_total_op_dentro_grupo':n_total_op_dentro_grupo,
	'n_total_op_importadas':n_total_op_importadas,
	'n_total_op_exportadas':n_total_op_exportadas,
	#'n_total_op_importadas_b':n_total_op_importadas_b,
	#'n_total_op_exportadas_b':n_total_op_exportadas_b,
	'valor_op_importadas':valor_op_importadas,
	'valor_op_exportadas':valor_op_exportadas,
	'n_total_op_impuestos':n_total_op_impuestos,
	'valor_total_impuestos':valor_total_impuestos,
	'n_op_imp_internos':n_op_imp_internos,
	'valor_imp_internos':valor_imp_internos,
	'n_op_imp_externos':n_op_imp_externos,
	'valor_imp_externos':valor_imp_externos,
	'n_miembros':n_miembros,
	'n_miembros_con_operaciones':n_miembros_con_operaciones,
	#'miembros_saldo_positivo':miembros_saldo_positivo,
	#'miembros_saldo_neutro':miembros_saldo_neutro,
	#'miembros_saldo_negativo':miembros_saldo_negativo,
	'operaciones_x_dia':operaciones_x_dia,
	'n_dias':n_dias,
	'valor_operaciones_positivas':valor_operaciones_positivas,
	'valor_operaciones_negativas':valor_operaciones_negativas,
	'balance_del_grupo':balance_del_grupo,
	#'balance_del_grupo_b':balance_del_grupo_b,
	'valor_medio_operacion':valor_medio_operacion,
	'qs_ope_x_mes':qs_ope_x_mes,
	'qs_suma_x_mes':suma_op_x_mes,
	'qs_ope_x_dia':qs_ope_x_dia,
	'qs_suma_x_dia':suma_op_x_dia,
	}
	
	
	return render_to_response("grupos/crecimiento_intercambios.html", datos ,context_instance=RequestContext(request))

####################################################################################################

@login_required
def solicita_ser_miembro(request, id_grupo=None):
	
	grupo = get_object_or_404(Grupo,pk=id_grupo)
	config = grupo.config_grupo
	n_miembros = Miembro.objects.filter(grupo=grupo).count()
	admins = Miembro.objects.filter(grupo=grupo,nivel=u'Administrador')
	situacion = _(u'solicitud de entrada en el grupo')
	
	try:
		idioma = Idiomas_grupo.objects.get(grupo=grupo, idioma=request.LANGUAGE_CODE)
	except Idiomas_grupo.DoesNotExist:
		idiomas_qs = Idiomas_grupo.objects.filter(grupo=grupo).order_by('-idioma_default')
		idioma = idiomas_qs[0]
	
	try:
		"""No se audita a los miembros ya registrados y activos del grupo"""
		es_miembro = Miembro.objects.get(usuario=request.user,grupo=grupo, activo=True)
		return HttpResponseRedirect(reverse("portada"))
	except Miembro.DoesNotExist:

		if request.method == 'POST':
			form = Form_solicitud_miembro(request.POST)
			if form.is_valid():

				contador = Contador.objects.filter(grupo=grupo).latest('creado')
				config_grupo = grupo.config_grupo
				
				nuevo_miembro = Miembro()
				nuevo_miembro.grupo = grupo
				nuevo_miembro.usuario = request.user
				nuevo_miembro.nivel = 'Normal'
				nuevo_miembro.clave = str(grupo.simbolo) + str(contador.numero)
				
				if config_grupo.tipo_alta == 'Online':
					nuevo_miembro.activo = True
					nuevo_miembro.pendiente = False
				if config_grupo.tipo_alta == 'Revisada':
					nuevo_miembro.activo = False
					nuevo_miembro.pendiente = True
				if config_grupo.tipo_alta == 'Presencial':
					nuevo_miembro.activo = False
					nuevo_miembro.pendiente = True
				
					
				nuevo_miembro.creado_por = request.user
				nuevo_miembro.modificado_por = request.user
				nuevo_miembro.save()
				
				nuevo_grupo = grupo_normal()
				request.user.groups.add(nuevo_grupo)
	
				es_admin = Miembro.objects.filter(usuario=request.user, activo=True,nivel=u'Administrador')
				es_miembro = Miembro.objects.filter(usuario=request.user, activo=True)
				
				current_site = get_current_site(request)
				sitio = current_site.domain
				idioma=request.LANGUAGE_CODE
				
				administradores = Miembro.objects.filter(grupo=grupo, activo=True,nivel=u'Administrador')
				emails_admin = []
				admins = []
				for a in administradores:
					emails_admin.append(a.usuario.email)
					admins.append(a.usuario)
				
				#Si es miembro de más de un grupo y el grupo está configurado para que no se creen cuentas si exiten por otro grupo no se le crea
				if len(es_miembro) > 1 and config_grupo.cuenta_x_miembro == False:
					mensaje_1 = _(u"""Como es un usuario registrado en otros grupos de intercambio no se le creará por defecto una nueva cuenta en el grupo solicitado. 
									Si hace operaciones con otros grupos utilizará sus otras cuentas y hará uso de la cuenta virtual intergrupos.
									No obstante puede asignarsele una cuenta del grupo solicitado desde administración.""")
				else:
					# Se le crea una cuenta en el grupo
					if config.tipo_alta == 'Revisada':
						mensaje_1 = _(u"""Como no es miembro de otras comunidades de intercambio se le ha creado una cuenta normal con la que operar.""")
					else:
						#No mando email al administrador por no sobrecargar. Es un alta normal
						mensaje_1 = _(u"""Como no es miembro de otras comunidades de intercambio se le ha creado una cuenta normal con la que operar.""")
						admins = []
						
					margenes = Margenes.objects.filter(config_grupo=config_grupo, default=True).order_by('default')
					if len(margenes) > 0:
						margen_defecto = margenes[0]
					else:
						margen_defecto = None
						
					cuenta_normal = Cuenta()
					cuenta_normal.grupo = grupo
					cuenta_normal.tipo = 'Normal'
					cuenta_normal.alias = _(u"Cuenta personal ") + str(request.user.username) + ' en '+ str(grupo.simbolo)
					cuenta_normal.cuenta = str(grupo.simbolo) + str(contador.numero)
					cuenta_normal.margen = margen_defecto
					cuenta_normal.creado_por = request.user
					cuenta_normal.modificado_por = request.user
					cuenta_normal.save()
					cuenta_normal.titulares.add(request.user)
				
				contador.numero += 1
				contador.save()

				
				solicitante = request.user.username + ' (' + request.user.first_name + ' ' + request.user.last_name + ')'
				registrado_desde = request.user.date_joined

				cadena_miembro = ''
				for item in es_miembro:
					cadena_miembro += "%s (desde el %s - Activo: %s - Pendiente: %s ), <br/>" % (item.grupo, item.creado, item.activo, item.pendiente )
					
				cadena_miembro = str(cadena_miembro[:-7])
				
				cadena_admin = ''
				for item in es_admin:
					cadena_admin += "%s (desde el %s - Activo: %s ), <br/>" % (item.grupo, item.creado, item.activo )
				cadena_admin  = str(cadena_admin[:-7])


				asunto = _(u'Nuevo usuario registrado')
					
				mensaje = _(u'Un nuevo usuario ha solicitado la entrada en el grupo.')
				
				html = """<p>&nbsp;</p>
						<table width="500" border="0" align="center" cellpadding="8" cellspacing="0" style="border: 2px solid #000000;">
						<tr>
							<td colspan="2"><div align="center"><img src="%s/media/%s" width="48px" alt="%s"/> </div></td>
						</tr>
						<tr>
							<td>Asunto:</td><td>%s. %s</td>
						</tr>
						<tr>
							<td>Remitente:</td><td>%s</td>
						</tr>
						<tr>
							<td>Alta en el sistema:</td><td>%s</td>
						</tr>
						<tr>
							<td>Solicita ser miembro del grupo:</td><td>%s</td>
						</tr>
						<tr>
							<td>Es miembro de los siguientes grupos:</td><td>%s</td>
						</tr>
						<tr>
							<td>Es administrador de los siguientes grupos:</td><td>%s</td>
						</tr>
						<tr>
							<td colspan="2">%s</td>
						</tr>
					</table>
					<p>&nbsp;</p>""" % (sitio,grupo.logo.name, grupo.logo.name,asunto, mensaje, solicitante, registrado_desde, grupo, cadena_miembro, cadena_admin, mensaje_1)
				
				from_email = 'info@playcircular.com'
				
				msg = EmailMultiAlternatives(asunto, asunto, from_email, emails_admin)
				msg.attach_alternative(html, "text/html")
				try:
					msg.send()
				except:
					pass

				
				for admin in admins:
					correspondencia = Correspondencia()
					correspondencia.destinatario = admin
					correspondencia.id_remitente = admin.pk
					correspondencia.remitente = _(u'El sistema')
					correspondencia.email_remitente = 'no-reply@no-responder.com'
					correspondencia.asunto = asunto
					correspondencia.mensaje = html
					correspondencia.save()

				#try:
					#send_mass_mail(mensajes, fail_silently=False)
				#except BadHeaderError:
					#return HttpResponse('Invalid header found.')

				
				return HttpResponseRedirect(reverse("grupos-index"))
			else:
				form = Form_solicitud_miembro(request.POST)
			
		else:
			form = Form_solicitud_miembro()

	return render_to_response("grupos/solicitud_miembro.html", 
				{'form': form, 
				 'grupo':grupo,
				 'config':config,
				 'situacion': situacion, 
				 'n_miembros': n_miembros, 
				 'admins': admins,
				 'idioma': idioma} ,
				context_instance=RequestContext(request))

####################################################################################################

def grupo_visitante():
	
	try:
		grupo_visitante = Group.objects.get(name=u'Visitante')
	except:
		lista_grupo_visitante = [u'add_config_grupo',
								u'add_grupo',
								u'add_idiomas_grupo',
								u'add_margenes',
								u'add_mas_fotos',
								u'add_miembro',
								u'add_social_grupo',
								u'change_idiomas_grupo',
								u'change_margenes',
								u'change_mas_fotos',
								u'delete_margenes',
								u'delete_mas_fotos',
								u'add_metatag',
								u'change_metatag',
								u'add_fotos_personales',
								u'add_social_usu',
								u'change_config_perfil',
								u'change_fotos_personales',
								u'change_perfil',
								u'change_social_usu',
								u'delete_fotos_personales',
								u'delete_social_usu']

		grupo_visitante, created = Group.objects.get_or_create(name='Visitante')
		if created:
			grupo_visitante.save()
		
		qs = Permission.objects.filter(codename__in=lista_grupo_visitante)
		grupo_visitante.permissions = qs
		
		grupo_visitante.save()
		
	return grupo_visitante
	  
#######################################################################################################################################################

def grupo_normal():
	try:
		grupo_normal = Group.objects.get(name=u'Normal')
	except:	          
		lista_grupo_normal = [u'add_actividad',
								u'add_categoria',
								u'add_fotos_actividad',
								u'add_idiomas_actividad',
								u'add_idiomas_categoria',
								u'change_actividad',
								u'change_categoria',
								u'change_fotos_actividad',
								u'change_idiomas_actividad',
								u'change_idiomas_categoria',
								u'delete_actividad',
								u'delete_categoria',
								u'delete_fotos_actividad',
								u'delete_idiomas_actividad',
								u'delete_idiomas_categoria',
								u'add_grupo',
								u'add_idiomas_grupo',
								u'add_margenes',
								u'add_mas_fotos',
								u'add_social_grupo',
								u'change_grupo',
								u'change_idiomas_grupo',
								u'change_margenes',
								u'change_mas_fotos',
								u'change_social_grupo',
								u'delete_idiomas_grupo',
								u'delete_margenes',
								u'delete_mas_fotos',
								u'delete_social_grupo',
								u'add_metatag',
								u'change_metatag',
								u'delete_metatag',
								u'add_comentarios_pagina',
								u'change_comentarios_pagina',
								u'delete_comentarios_pagina',
								u'add_fotos_personales',
								u'add_social_usu',
								u'change_config_perfil',
								u'change_correspondencia',
								u'change_fotos_personales',
								u'change_perfil',
								u'change_social_usu',
								u'delete_fotos_personales',
								u'delete_social_usu',
								u'add_entrada',
								u'add_fotos_entrada',
								u'change_entrada',
								u'change_fotos_entrada',
								u'delete_entrada',
								u'delete_fotos_entrada',
								u'add_entrada',
								u'add_fotos_entrada',
								u'change_entrada',
								u'change_fotos_entrada',
								u'delete_entrada',
								u'add_idiomas_entrada',
								u'change_idiomas_entrada',
								u'delete_idiomas_entrada']

		grupo_normal, created  = Group.objects.get_or_create(name='Normal')
		if created:
			grupo_normal.save()
		
		qs = Permission.objects.filter(codename__in=lista_grupo_normal)
		
		grupo_normal.permissions = qs
		
		grupo_normal.save()

	return grupo_normal


#######################################################################################################################################################

def grupo_administrador():
	try:
		grupo_administrador = Group.objects.get(name=u'Administrador')
	except:	          
		lista_grupo_administrador = [u'add_actividad',
								u'add_categoria',
								u'add_fotos_actividad',
								u'add_idiomas_actividad',
								u'add_idiomas_categoria',
								u'add_incidencias_actividad',
								u'change_actividad',
								u'change_categoria',
								u'change_fotos_actividad',
								u'change_idiomas_actividad',
								u'change_idiomas_categoria',
								u'change_incidencias_actividad',
								u'delete_actividad',
								u'delete_categoria',
								u'delete_fotos_actividad',
								u'delete_idiomas_actividad',
								u'delete_idiomas_categoria',
								u'delete_incidencias_actividad',
								u'add_cuenta',
								u'add_incidencia_cuenta',
								u'add_incidencia_intercambio',
								u'add_intercambio',
								u'change_cuenta',
								u'change_incidencia_cuenta',
								u'change_incidencia_intercambio',
								u'change_intercambio',
								u'delete_cuenta',
								u'delete_incidencia_cuenta',
								u'delete_incidencia_intercambio',
								u'delete_intercambio',
								u'add_config_grupo',
								u'add_grupo',
								u'add_idiomas_grupo',
								u'add_incidencias_grupo',
								u'add_margenes',
								u'add_mas_fotos',
								u'add_miembro',
								u'add_social_grupo',
								u'change_config_grupo',
								u'change_grupo',
								u'change_idiomas_grupo',
								u'change_incidencias_grupo',
								u'change_margenes',
								u'change_mas_fotos',
								u'change_miembro',
								u'change_social_grupo',
								u'delete_grupo',
								u'delete_idiomas_grupo',
								u'delete_incidencias_grupo',
								u'delete_margenes',
								u'delete_mas_fotos',
								u'delete_miembro',
								u'delete_social_grupo',
								u'add_metatag',
								u'change_metatag',
								u'delete_metatag',
								u'add_fotos_pagina',
								u'add_idiomas_pagina',
								u'add_opinion_comentario',
								u'add_pagina',
								u'change_fotos_pagina',
								u'change_idiomas_pagina',
								u'change_opinion_comentario',
								u'change_pagina',
								u'delete_fotos_pagina',
								u'delete_idiomas_pagina',
								u'delete_opinion_comentario',
								u'delete_pagina',
								u'change_comentario',
								u'delete_comentario',
								u'add_votos_mensaje',
								u'change_votos_mensaje',
								u'delete_votos_mensaje',
								u'add_config_perfil',
								u'add_fotos_personales',
								u'add_incidencias_usuario',
								u'add_perfil',
								u'add_social_usu',
								u'change_config_perfil',
								u'change_fotos_personales',
								u'change_incidencias_usuario',
								u'change_perfil',
								u'change_social_usu',
								u'delete_fotos_personales',
								u'delete_incidencias_usuario',
								u'delete_social_usu',	
								u'add_banner',
								u'add_categoria_entrada',
								u'add_entrada',
								u'add_fotos_entrada',
								u'add_fotos_pagina',
								u'add_idiomas_pagina',
								u'add_pagina',
								u'add_pie_de_pagina',
								u'change_banner',
								u'change_categoria_entrada',
								u'change_entrada',
								u'change_fotos_entrada',
								u'change_fotos_pagina',
								u'change_idiomas_pagina',
								u'change_pagina',
								u'change_pie_de_pagina',
								u'change_rating_entrada',
								u'delete_banner',
								u'delete_categoria_entrada',
								u'delete_entrada',
								u'delete_fotos_entrada',
								u'delete_fotos_pagina',
								u'delete_idiomas_pagina',
								u'delete_pagina',
								u'delete_pie_de_pagina'
								u'add_idiomas_categoria_entrada',
								u'change_idiomas_categoria_entrada',
								u'delete_idiomas_categoria_entrada',
								u'add_idiomas_entrada',
								u'change_idiomas_entrada',
								u'delete_idiomas_entrada']

		grupo_administrador, created  = Group.objects.get_or_create(name='Administrador')
		if created:
			grupo_administrador.save()
		
		qs = Permission.objects.filter(codename__in=lista_grupo_administrador)
		
		grupo_administrador.permissions = qs
		
		grupo_administrador.save()

	return grupo_administrador
#######################################################################################################################################################

