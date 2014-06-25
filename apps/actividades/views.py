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
from django.contrib.auth.models import User
from actividades.models import *
from actividades.forms import *
from economia.models import *
from economia.views import *
from taggit.models import Tag
from twitter.models import *
from twitter.views import *
from django.contrib.sites.models import get_current_site
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _
from django.core.mail import send_mail, send_mass_mail, BadHeaderError
from settings import MEDIA_ROOT, MEDIA_URL
from django.template import RequestContext, loader
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from datetime import *
from django.utils.timezone import utc

from django.template import Context
from collections import defaultdict
from django.utils import simplejson
from django.core import serializers
from django.utils.encoding import smart_str
from django.contrib.contenttypes import generic

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
@login_required
def ver_actividad(request, clase=None, tipo=None, id_objeto=None, slug=None):

	id_objeto = int(id_objeto)
	actividades_qs = Actividad.objects.filter(pk=id_objeto, clase=clase, tipo=tipo)


	if len(actividades_qs) == 0:
		#raise HttpResponseNotAllowed() # Esto no funciona por alguna razón
		actividad = False
		return HttpResponseRedirect(reverse("portada"))
	else:
		actividad = actividades_qs[0]
		
		adjuntar_datos_actividad(request,item=actividad,opinion=True)
		
		try:
			v = Visitas_actividad.objects.get(actividad=actividad)
			"""Trato de salvar el problema del chrome. Precarga las páginas para acelerar la lectura y
				con ello distorsiona el número real de visitas. Cada vez que se recarga la página va de 5 en 5. 
				Le introduzco una demora de 20 segundos para evitar la distorsión de las precargas del google chrome."""
			ahora = datetime.utcnow().replace(tzinfo=utc)
			resta = ahora - v.modificado
			diferencia = resta.total_seconds()
			if diferencia > 20:
				v.visitas += 1
				v.save()
		except Visitas_actividad.DoesNotExist:
			v = Visitas_actividad()
			v.actividad = actividad
			v.visitas = 1
			v.save()
		
		if actividad.usuario == request.user:
			mi_actividad = True
			comentarios_actividad = Opinion_actividad.objects.filter(actividad=actividad)
		else:
			mi_actividad = False
			comentarios_actividad = []

		
		"""No puedeo añadirle el '#' porque la expresión regular de la url lo interpreta como comentario y no me deja"""
		#hashtag = 'Actividad-%s-D' % actividad.pk
		#datos = buscar(request, busqueda=hashtag, opcion=2)

	context = {'actividad':actividad,
				#'datos':actividad,
				#'hashtag':hashtag,
				'mi_actividad':mi_actividad,
				'comentarios_actividad':comentarios_actividad,
				'objeto':actividad.pk, 
				'pagina': 1,
				"n_paginas": 1,
				'retorno':1,
				'situacion':_(u'Esta actividad')}


	return render_to_response("actividades/este_anuncio.html",context,context_instance=RequestContext(request))

#######################################################################################################################################################
@login_required
def valorar_actividad(request):

	import time
	time.sleep(0.3)

	if request.is_ajax():
		if request.method == 'POST':
			form = Form_valorar_actividad(request.POST)
			if form.is_valid():
				#new = form.save(commit=True)
				
				pagina = form.cleaned_data['pagina']
				n_paginas = form.cleaned_data['n_paginas']
				retorno = form.cleaned_data['retorno']
				
				try:
					item = Actividad.objects.get(pk=form.cleaned_data['objeto'])
					
					ya_intercambiada = Intercambio.objects.filter(actividad=item,origen=request.user,tipo='Normal',estado=u'Concluído').count()
					
					if ya_intercambiada > 0:
						ya_intercambiada = True
					else:
						ya_intercambiada = False
										
					try:
						o = Opinion_actividad.objects.get(usuario=request.user,actividad=item,ya_opinado=True)
						o.me_gusta_para_mi = form.cleaned_data['me_gusta_para_mi']
						# Retorno 3 es que viene de un formulario de valoración después de la compra.
						if retorno == 3 or ya_intercambiada:

							o.rating_para_mi_despues = form.cleaned_data['rating_para_mi']
						else:
							o.rating_para_mi_antes = form.cleaned_data['rating_para_mi']
						o.bien_comun = form.cleaned_data['bien_comun']
						o.rating_para_bien_comun = form.cleaned_data['rating_para_bien_comun']
						o.comentario = form.cleaned_data['comentario']
						o.ya_opinado = True
						o.save()
					except Opinion_actividad.DoesNotExist:
						o = Opinion_actividad()
						o.usuario = request.user
						o.actividad = item
						o.me_gusta_para_mi = form.cleaned_data['me_gusta_para_mi']
						# Retorno 3 es que viene de un formulario de valoración después de la compra.
						if retorno == 3 or ya_intercambiada:
							o.rating_para_mi_despues = form.cleaned_data['rating_para_mi']
						else:
							o.rating_para_mi_antes = form.cleaned_data['rating_para_mi']
						o.bien_comun = form.cleaned_data['bien_comun']
						o.rating_para_bien_comun = form.cleaned_data['rating_para_bien_comun']
						o.comentario = form.cleaned_data['comentario']
						o.ya_opinado = True
						o.save()
						
						# Solo se paga la primera vez. No puedes arruinar a nadie modificando tu opinión
					
					item.me_gusta_para_mi = o.me_gusta_para_mi
					item.rating_para_mi_antes = o.rating_para_mi_antes
					item.rating_para_mi_despues = o.rating_para_mi_despues
					item.bien_comun = o.bien_comun
					item.rating_para_bien_comun = o.rating_para_bien_comun
					item.comentario = o.comentario
					item.ya_opinado = o.ya_opinado
					item.ya_intercambiada = ya_intercambiada
					
					n_votaciones = Opinion_actividad.objects.filter(actividad=item,ya_opinado=True).count()
					n_interes_particular = Opinion_actividad.objects.filter(actividad=item,me_gusta_para_mi=True,ya_opinado=True).count()
					qs_media = Opinion_actividad.objects.filter(actividad=item,me_gusta_para_mi=True,ya_opinado=True).aggregate(media=Avg('rating_para_mi_antes'))
					if qs_media['media']:
						media_rating_para_mi_antes = Decimal(qs_media['media'])
						media_rating_para_mi_antes = round(media_rating_para_mi_antes,2)
					else:
						media_rating_para_mi_antes = 0
					n_interes_comunidad = Opinion_actividad.objects.filter(actividad=item,bien_comun=True,ya_opinado=True).count()
					qs_media = Opinion_actividad.objects.filter(actividad=item,bien_comun=True,ya_opinado=True).aggregate(media=Avg('rating_para_bien_comun'))
					if qs_media['media']:
						media_rating_para_bien_comun = Decimal(qs_media['media'])
						media_rating_para_bien_comun = round(media_rating_para_bien_comun,2)
					else:
						media_rating_para_bien_comun = 0
						
					item.n_votaciones = n_votaciones
					item.n_interes_particular = n_interes_particular
					item.media_rating_para_mi_antes = media_rating_para_mi_antes
					item.n_interes_comunidad = n_interes_comunidad
					item.media_rating_para_bien_comun = media_rating_para_bien_comun
					item.save()
					
					response = {'status':True}
					
					context = {'actividad': item, 'pagina': pagina, "n_paginas": n_paginas, 'retorno':retorno}
					
					if retorno == 1:
						return render_to_response('actividades/form_opinion.html',context,context_instance=RequestContext(request))
					if retorno == 3:
						return render_to_response('actividades/form_opinion.html',context,context_instance=RequestContext(request))
					else:
						# Si ha llegado al final
						if pagina == n_paginas:
							return render_to_response('actividades/valoracion_concluida.html',{},context_instance=RequestContext(request))
						else:

							return valorar_actividades(request, pagina=pagina, ajax='si')

				except Actividad.DoesNotExist:

					response = {'status':False}
					raise Http404
				
			else:
				response = {'status':False}
				raise Http404
		
	else:

		raise Http404
	

#######################################################################################################################################################


@login_required
def valorar_actividades(request, pagina=1, ajax='no'):

	pagina = int(pagina)

	mis_grupos_qs = Miembro.objects.filter(usuario=request.user).values_list('grupo',flat=True)
	miembros_qs = Miembro.objects.filter(grupo__in=mis_grupos_qs).exclude(usuario=request.user).values_list('usuario',flat=True)
	config_perfiles_participan_qs = Config_perfil.objects.filter(usuario__in=miembros_qs,valorar_actividades=True).values_list('usuario',flat=True)
	#perfiles_participan_qs = Perfil.objects.filter(usuario__in=config_perfiles_qs).values_list('pk',flat=True)
	
	actividades_ya_votadas_qs = Opinion_actividad.objects.filter(usuario=request.user,ya_opinado=True).values_list('actividad',flat=True)
	actividades_qs = Actividad.objects.filter(usuario__in=config_perfiles_participan_qs,activo=True,grupo__in=mis_grupos_qs).exclude(pk__in=actividades_ya_votadas_qs).distinct()
	n_actividades_x_opinar = Actividad.objects.filter(usuario__in=config_perfiles_participan_qs,activo=True,grupo__in=mis_grupos_qs).exclude(pk__in=actividades_ya_votadas_qs).distinct().count()
	
	#Con el distinct quitamos las actividades repetidas. Como algunas pertenecen a varios grupos salen 2 y 3 veces
	if n_actividades_x_opinar > 0:
		item = actividades_qs[0]
		adjuntar_datos_actividad(request,item=item,opinion=True)

	else:

		actividades_qs = Actividad.objects.filter(usuario__in=config_perfiles_participan_qs,activo=True,grupo__in=mis_grupos_qs).distinct().order_by('modificado')
		if len(actividades_qs) > 0:
			item = actividades_qs[0]
			adjuntar_datos_actividad(request,item=item,opinion=True)
		else:
			item = False
		
	

	paginator = Paginator(actividades_qs, 1)
	try:
		n_paginas = paginator.page(pagina)
	except (InvalidPage, EmptyPage):
		n_paginas = paginator.page(paginator.num_pages)


	situacion = u'Valorar actividades'

	context = {"actividades" : n_paginas.object_list,
				'pagina': n_paginas.number,
				"n_paginas": n_paginas.paginator.num_pages,
				'n_actividades_x_opinar':n_actividades_x_opinar,
				'opinando':True,
				'retorno':2,
				'form_busqueda':Form_busqueda,
				'actividad': item,
				'situacion':situacion }

	if ajax == 'no':
		return render_to_response('actividades/valorar_inicio.html',context,context_instance=RequestContext(request))
	else:
		return render_to_response('actividades/listado_2.html',context,context_instance=RequestContext(request))
	
#######################################################################################################################################################


def actividades(request, clase=False, id_usuario=False):
	
	"""Para los enlaces de bienes o servicios"""
	
	try: 
		page = int(request.GET.get("page", '1'))
	except ValueError: 
		page = 1
	
	if request.user.is_authenticated():
		mis_grupos_qs = Miembro.objects.filter(usuario=request.user).values_list('grupo',flat=True)
		if clase:
			actividades_qs = Actividad.objects.filter(clase=clase,grupo__in=mis_grupos_qs,activo=True).distinct()
		else:
			actividades_qs = Actividad.objects.filter(grupo__in=mis_grupos_qs,activo=True).distinct()
		if id_usuario:
			usuario = get_object_or_404(User, pk=int(id_usuario))
			actividades_qs = Actividad.objects.filter(usuario=usuario,activo=True).distinct()
	else:
		if clase:
			actividades_qs = Actividad.objects.filter(clase=clase, activo=True).distinct()
		else:
			actividades_qs = Actividad.objects.filter(activo=True).distinct()
		if id_usuario:
			usuario = get_object_or_404(User, pk=int(id_usuario))
			actividades_qs = Actividad.objects.filter(usuario=usuario,activo=True).distinct()
		
	current_site = get_current_site(request)
	sitio = current_site.domain
	idioma=request.LANGUAGE_CODE
	if clase:
		situacion = clase
		url = unicode(sitio) + '/' + unicode(idioma) + '/actividad/' + unicode(clase) + '/'
	if id_usuario:
		situacion = _(u'Actividades del usuario ') + unicode(usuario)
		url = unicode(sitio) + '/' + unicode(idioma) + '/actividad/usuario/' + unicode(id_usuario) + '/'
	if not clase and not id_usuario:
		situacion = _(u'Todas')
		url = unicode(sitio) + '/' + unicode(idioma) + '/actividad/todas/' 

	#Habría que quitar las actividades repetidas. Como algunas pertenecen a varios grupos salen 2 y 3 veces
	actividades = []
	for item in actividades_qs:
		adjuntar_datos_actividad(request,item=item,opinion=False)
		actividades.append(item)
		
	paginator = Paginator(actividades, 12)
	try:
		n_paginas = paginator.page(page)
	except (InvalidPage, EmptyPage):
		n_paginas = paginator.page(paginator.num_pages)
		
	
	context = {"actividades": n_paginas.object_list, "n_paginas": n_paginas, 'situacion':situacion, 'url':url, 'rss':'todas' }

	if not request.is_ajax():
		return render_to_response('actividades/clases.html',context,context_instance=RequestContext(request))
	else:
		return render_to_response('actividades/paginacion_clases.html',context_instance=RequestContext(request))
		

#######################################################################################################################################################


def actividades_grupo(request, simbolo):
	
	grupo = get_object_or_404(Grupo, simbolo=simbolo)
	
	situacion = _(u'Actividades del grupo ') + unicode(grupo.nombre) + '(' + unicode(simbolo) + ')'
	
	try: 
		page = int(request.GET.get("page", '1'))
	except ValueError: 
		page = 1
		
	actividades_qs = Actividad.objects.filter(grupo=grupo,activo=True).distinct()
	
	current_site = get_current_site(request)
	sitio = current_site.domain
	idioma=request.LANGUAGE_CODE

	url = unicode(sitio) + '/' + unicode(idioma) + '/actividad/' + unicode(simbolo) + '/actividades/' 

	#Habría que quitar las actividades repetidas. Como algunas pertenecen a varios grupos salen 2 y 3 veces
	actividades = []
	for item in actividades_qs:
		adjuntar_datos_actividad(request,item=item,opinion=False)
		actividades.append(item)
		
	paginator = Paginator(actividades, 12)
	try:
		n_paginas = paginator.page(page)
	except (InvalidPage, EmptyPage):
		n_paginas = paginator.page(paginator.num_pages)
		
	
	context = {"actividades": n_paginas.object_list, "n_paginas": n_paginas, 'situacion':situacion, 'url':url, 'rss':'grupo', 'grupo':grupo }

	if not request.is_ajax():
		return render_to_response('actividades/clases.html',context,context_instance=RequestContext(request))
	else:
		return render_to_response('actividades/paginacion_clases.html',context,context_instance=RequestContext(request))
	

#######################################################################################################################################################


def actividades_clasificadas(request, id_categoria=False, tag=False):
	
	current_site = get_current_site(request)
	sitio = current_site.domain
	idioma=request.LANGUAGE_CODE
	
	if id_categoria:
		categoria = get_object_or_404(Categoria,pk=id_categoria)
		try:
			# Intento ponerla en el idioma en que está la página.
			idioma_categoria = Idiomas_categoria.objects.get(categoria=id_categoria, idioma=request.LANGUAGE_CODE)
			situacion = _(u'Actividades en la categoria ') + unicode(idioma_categoria.nombre)
		except Idiomas_categoria.DoesNotExist:
			situacion = _(u'Actividades en la categoria ') + unicode(categoria)
		actividades_qs = Actividad.objects.filter(categoria=categoria,activo=True).distinct()
		url = unicode(sitio) + '/' + unicode(idioma) + '/actividad/categoria/' + unicode(id_categoria) + '/' 
	else:
		actividades_qs = Actividad.objects.filter(idiomas_actividad__tags__name=tag).distinct()
		situacion = _(u'Actividades en la etiqueta ') + unicode(tag)
		url = unicode(sitio) + '/' + unicode(idioma) + '/actividad/tag/' + unicode(tag) + '/' 
	
	try: 
		page = int(request.GET.get("page", '1'))
	except ValueError: 
		page = 1

	#Habría que quitar las actividades repetidas. Como algunas pertenecen a varios grupos salen 2 y 3 veces
	actividades = []
	for item in actividades_qs:
		adjuntar_datos_actividad(request,item=item,opinion=False)
		actividades.append(item)
		
	paginator = Paginator(actividades, 12)
	try:
		n_paginas = paginator.page(page)
	except (InvalidPage, EmptyPage):
		n_paginas = paginator.page(paginator.num_pages)
		
	
	context = {"actividades": n_paginas.object_list, "n_paginas": n_paginas, 'situacion':situacion, 'url':url}

	if not request.is_ajax():
		return render_to_response('actividades/clases.html',context,context_instance=RequestContext(request))
	else:
		return render_to_response('actividades/paginacion_clases.html',context,context_instance=RequestContext(request))


#######################################################################################################################################################

def busqueda_actividad(request):
	
	"""Paso los datos del form a sessions porque para paginar, la página 2, 3, etc... no llevan un POST"""
	
	try: 
		page = int(request.GET.get("page", '1'))
	except ValueError: 
		page = 1
		
	situacion = _(u'busqueda')

	if request.method == 'POST':
		form_busqueda = Form_busqueda(request.POST)
		if form_busqueda.is_valid():
			datos_busqueda = {'busqueda':form_busqueda.cleaned_data['busqueda'],
							'clase': form_busqueda.cleaned_data['clase'],
							'tipo': form_busqueda.cleaned_data['tipo'],
							'grupos': form_busqueda.cleaned_data['grupos'],
							'orden': form_busqueda.cleaned_data['orden']}
							
			request.session['play-a'] = datos_busqueda		
			datos_session = datos_busqueda
		else:
			datos_session = False
	else:	
		if request.session.get('play-a','') != '':
			datos_session = request.session.get('play-a','')
		else:
			datos_session = False

	if datos_session:
		busqueda_qs = Idiomas_actividad.objects.filter(busqueda__icontains=datos_session['busqueda']).order_by('modificado')
				
		if datos_session['clase']:
			busqueda_qs = busqueda_qs.filter(actividad__clase=datos_session['clase'])
		if datos_session['tipo']:
			busqueda_qs = busqueda_qs.filter(actividad__tipo=datos_session['tipo'])
		if datos_session['grupos'] and request.user.is_authenticated():
			if datos_session['grupos'] == u'Mis grupos':
				#print 'ZONA GRUPOS'
				#print datos_session['grupos']
				grupos_qs = Miembro.objects.filter(usuario=request.user).values('grupo')
				busqueda_qs = busqueda_qs.filter(actividad__grupo__in=grupos_qs)
			else:
				pass
			
		busqueda_qs = busqueda_qs.values_list('actividad',flat=True)
		if datos_session['orden']:
			busqueda_qs = busqueda_qs.order_by(datos_session['orden'])
			
		actividades_qs = Actividad.objects.filter(pk__in=busqueda_qs)

		busqueda = []
		for item in actividades_qs:
			adjuntar_datos_actividad(request,item=item,opinion=False)
			busqueda.append(item)
			
		paginator = Paginator(busqueda, 15)
		try:
			n_paginas = paginator.page(page)
		except (InvalidPage, EmptyPage):
			n_paginas = paginator.page(paginator.num_pages)
		
	else:
		busqueda = []
		n_paginas = 0
		form_busqueda = Form_busqueda()
		datos_session = request.session.get('play-a','')
		
	context = {"busqueda_qs" : busqueda, "n_paginas": n_paginas, 'form_busqueda':Form_busqueda, 'datos':datos_session, 'situacion':situacion}
	
	if not request.is_ajax():
		return render_to_response('actividades/busqueda.html',context,context_instance=RequestContext(request))
	else:
		return render_to_response('actividades/paginacion_busqueda.html',context,context_instance=RequestContext(request))
		

#######################################################################################################################################################	
@login_required
def mis_favoritos(request):
	
	try: 
		page = int(request.GET.get("page", '1'))
	except ValueError: 
		page = 1
		
	situacion = _(u'Mis favoritos')

	if request.user.is_authenticated():
		mis_favoritos_qs = Actividad.objects.filter(opinion_actividad__usuario=request.user,opinion_actividad__me_gusta_para_mi=True,opinion_actividad__ya_opinado=True) 
		mis_favoritos_qs = mis_favoritos_qs.filter(activo=True).distinct().order_by('-modificado')
	else:
		mis_favoritos_qs = []
		
	mis_favoritos = []
	for item in mis_favoritos_qs:
		adjuntar_datos_actividad(request,item=item,opinion=False)
		mis_favoritos.append(item)

	paginator = Paginator(mis_favoritos, 12)

	try:
		n_paginas = paginator.page(page)
	except (InvalidPage, EmptyPage):
		n_paginas = paginator.page(paginator.num_pages)
	
	datos = {"mis_favoritos":mis_favoritos, "n_paginas":n_paginas, 'situacion':situacion}
	
	if not request.is_ajax():
		return render_to_response('actividades/mis_favoritos.html',datos,context_instance=RequestContext(request)) 
	else:
		return render_to_response('actividades/paginacion_favoritos.html',datos,context_instance=RequestContext(request))


#######################################################################################################################################################













