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
from django.contrib.auth.decorators import login_required
from django.template import RequestContext, loader
from django.utils.translation import ugettext as _
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.mail import send_mail, send_mass_mail, BadHeaderError,EmailMultiAlternatives
from django.core import serializers
from django.contrib.sites.models import get_current_site
from django.contrib import messages
from usuarios.models import *
from datetime import *
from django.utils.timezone import utc
from taggit.models import Tag
from paginas.models import *
from paginas.forms import *
from grupos.models import *
from django.db.models import permalink
from django.db.models import Q

#######################################################################################################################################################

def adjuntar_datos_entrada(request,item=None):
	
	try:
		idioma = Idiomas_entrada.objects.get(entrada=item.pk, idioma=request.LANGUAGE_CODE)
	except Idiomas_entrada.DoesNotExist:
		idiomas_qs = Idiomas_entrada.objects.filter(entrada=item.pk).order_by('-idioma_default')
		idioma = idiomas_qs[0]
		
	#item.get_absolute_url = idioma.get_absolute_url
	item.titulo = idioma.titulo
	item.slug = idioma.slug
	item.intro = idioma.intro
	#item.cuerpo = idioma.cuerpo
	#item.robots = idioma.robots
	#item.meta_descripcion = idioma.meta_descripcion
	#item.palabras_clave = idioma.palabras_clave
	#item.tags = idioma.get_tags()
		
	return item


#######################################################################################################################################################		

@login_required
def mandar_mensajes(request,comentarios,comentario,email_autor,url):
	
	current_site = get_current_site(request)
	sitio = current_site.domain
	
	destinatarios = [email_autor]
	for item in comentarios:
		if item.notificaciones:
			if not item.perfil.mi_email in destinatarios:
				destinatarios.append(item.perfil.mi_email)
				
	if request.user.email in destinatarios:
		destinatarios.remove(request.user.email)

	asunto = _(u'Nuevo comentario en Play Circular')
	
	mensaje = _(u'Hay un nuevo comentario en Play Circular en una zona en la que has participado.')
	
	html = """<p>&nbsp;</p>
			<table width="500" border="0" align="center" cellpadding="8" cellspacing="0" style="border: 2px solid #000000;">
			<tr>
				<td>Asunto:</td><td>%s</td>
			</tr>
			<tr>
				<td>Mensaje:</td><td>%s</td>
			</tr>
			<tr>
				<td>Comentario:</td><td>%s</td>
			</tr>
			<tr>
				<td>Enlace:</td><td>%s%s</td>
			</tr>
		</table>
		<p>&nbsp;</p>""" % (asunto, mensaje, comentario, sitio, url)
	
	
	from_email = 'info@playcircular.com'
	
	msg = EmailMultiAlternatives(asunto, asunto, from_email, destinatarios)
	msg.attach_alternative(html, "text/html")
	try:
		msg.send()
	except:
		pass
	
	return True

		
#######################################################################################################################################################		

def ver_pagina(request,id_pagina=None,slug=None):
	
	pagina = get_object_or_404(Pagina,pk=int(id_pagina))
	url = pagina.get_absolute_url()
	
	try:
		v = Visitas_pagina.objects.get(pagina=pagina)
		"""Trato de salvar el problema del chrome. Precarga las páginas para acelerar la lectura y
			con ello distorsiona el número real de visitas. Cada vez que se recarga la página va de 5 en 5. 
			Le introduzco una demora de 20 segundos para evitar la distorsión de las precargas del google chrome."""
		ahora = datetime.utcnow().replace(tzinfo=utc)
		resta = ahora - v.modificado
		diferencia = resta.total_seconds()
		if diferencia > 20:
			v.visitas += 1
			v.save()
	except Visitas_pagina.DoesNotExist:
		v = Visitas_pagina()
		v.pagina = pagina
		v.visitas = 1
		v.save()
	
	if not request.user.is_authenticated(): 
		if pagina.visibilidad == 'privada':
			return HttpResponseRedirect(reverse("account_login"))
	
	try:
		idioma = Idiomas_pagina.objects.get(pagina=pagina, idioma=request.LANGUAGE_CODE)
	except Idiomas_pagina.DoesNotExist:
		idiomas_qs = Idiomas_pagina.objects.filter(pagina=pagina).order_by('-idioma_default')
		idioma = idiomas_qs[0]
		
	fotos_p = Fotos_pagina.objects.filter(pagina=pagina)
	comentario = None
	if len(fotos_p) == 0:
		fotos_p = False
	situacion = pagina
	content_type = ContentType.objects.get_for_model(type(pagina))
	object_id = pagina.pk
	comentarios = Comentario.objects.filter(content_type=content_type,object_id=object_id,activo=True)
	
	if request.method == 'POST':
		form = Form_Comentario(request.POST,instance=comentario)
		if form.is_valid():
			c = form.save(commit=False)
			perfil = Perfil.objects.get(usuario=request.user)
			c.perfil = perfil
			c.creado_por = request.user
			c.modificado_por = request.user
			c.save()
			
			for grupo in pagina.grupo.all():
				c.grupo.add(grupo)
				
			mandar_mensajes(request,comentarios,c,pagina.usuario.email,url)
				
			return HttpResponseRedirect(reverse("ver-pagina", kwargs=dict(id_pagina=pagina.pk, slug=idioma.slug)))
			
		else:
			form = Form_Comentario(request.POST)
	else:
		initial_data = {'content_type':content_type,'object_id':object_id}
		form = Form_Comentario(initial=initial_data, instance=comentario)
			
	datos = {'pagina':pagina,
			'idioma':idioma,
			'fotos_p':fotos_p,
			'situacion':situacion,
			'form':form,
			'comentarios':comentarios}
	
	return render_to_response('paginas/esta_pagina.html',datos,context_instance=RequestContext(request))

#######################################################################################################################################################		

def ver_pagina_general(request,id_grupo=None,p=None):
	
	grupo = get_object_or_404(Grupo,pk=int(id_grupo))
	try:
		idioma = Idiomas_grupo.objects.get(grupo=grupo, idioma=request.LANGUAGE_CODE)
	except Idiomas_grupo.DoesNotExist:
		idiomas_qs = Idiomas_grupo.objects.filter(grupo=grupo).order_by('-idioma_default')
		idioma = idiomas_qs[0]
	
	if p == 'terminos_y_condiciones':
		direccion = 'paginas/terminos_y_condiciones.html'
		situacion = _(u'Términos y condiciones')
		config = False
		margenes = False
			
	else:
		direccion = 'paginas/configuracion.html'
		situacion = _(u'Configuración')
		config = get_object_or_404(Config_grupo,grupo=grupo)
		margenes = Margenes.objects.filter(config_grupo=config)
			
	datos = {'grupo':grupo,
			'idioma':idioma,
			'config':config,
			'margenes':margenes,
			'situacion':situacion}
	
	return render_to_response(direccion,datos,context_instance=RequestContext(request))

	
#######################################################################################################################################################
@login_required
def valorar_comentario(request):
	
	id_comentario = int(request.POST['comentario'])
	comentario = get_object_or_404(Comentario,pk=id_comentario)

	try:
		opinion = Opinion_comentario.objects.get(comentario=comentario,usuario=request.user)
	except Opinion_comentario.DoesNotExist:
		opinion = None
	
	if request.method == 'POST':
		form = Form_Opinion_Comentario(request.POST,instance=opinion)
		if form.is_valid():
			o = form.save(commit=False)
			o.usuario = request.user
			o.comentario = comentario
			o.a_favor = int(request.POST['a_favor'])
			o.save()
			
			suma_votos_positivos = Opinion_comentario.objects.filter(comentario=comentario,a_favor=True).count()
			suma_votos_negativos = Opinion_comentario.objects.filter(comentario=comentario,a_favor=False).count()
			
			comentario.votos_positivos = suma_votos_positivos
			comentario.votos_negativos = suma_votos_negativos
			comentario.save()
			
			if comentario.content_type.name == 'entrada':
				entrada = get_object_or_404(Entrada,pk=comentario.object_id)
				return HttpResponseRedirect(entrada.get_absolute_url())
			else:
				return HttpResponseRedirect(reverse("portada"))
			
		else:
			return HttpResponseRedirect(reverse("portada"))
			
	else:
		return HttpResponseRedirect(reverse("portada"))

#######################################################################################################################################################
@login_required
def valorar_entrada(request):
	
	id_rating = int(request.POST['rating'])
	try:
		rating = Rating_entrada.objects.get(pk=id_rating)
	except Rating_entrada.DoesNotExist:
		rating = None
	
	if request.method == 'POST':
		form = Form_Rating_Entrada(request.POST,instance=rating)
		if form.is_valid():
			entrada = get_object_or_404(Entrada,pk=int(request.POST['entrada']))
			c = form.save(commit=False)
			c.usuario = request.user
			c.entrada = entrada
			c.a_favor = int(request.POST['a_favor'])
			c.valor = form.cleaned_data['valor']
			c.creado_por = request.user
			c.modificado_por = request.user
			c.save()

			return HttpResponseRedirect(entrada.get_absolute_url())
		else:
			return HttpResponseRedirect(entrada.get_absolute_url())
			
	else:
		return HttpResponseRedirect(entrada.get_absolute_url())


#######################################################################################################################################################		

def ver_entrada(request,id_entrada=None,slug=None):
	
	entrada = get_object_or_404(Entrada,pk=int(id_entrada))
	url = entrada.get_absolute_url()
	try:
		v = Visitas_entrada.objects.get(entrada=entrada)
		"""Trato de salvar el problema del chrome. Precarga las páginas para acelerar la lectura y
			con ello distorsiona el número real de visitas. Cada vez que se recarga la página va de 5 en 5. 
			Le introduzco una demora de 20 segundos para evitar la distorsión de las precargas del google chrome."""
		ahora = datetime.utcnow().replace(tzinfo=utc)
		resta = ahora - v.modificado
		diferencia = resta.total_seconds()
		if diferencia > 20:
			v.visitas += 1
			v.save()
	except Visitas_entrada.DoesNotExist:
		v = Visitas_entrada()
		v.entrada = entrada
		v.visitas = 1
		v.save()

	try:
		idioma = Idiomas_entrada.objects.get(entrada=entrada.pk, idioma=request.LANGUAGE_CODE)
	except Idiomas_entrada.DoesNotExist:
		idiomas_qs = Idiomas_entrada.objects.filter(entrada=entrada.pk).order_by('-idioma_default')
		idioma = idiomas_qs[0]
			
	idiomas_categoria = []
	for item in entrada.categoria.all():
		try:
			idioma_categoria = Idiomas_categoria_entrada.objects.get(categoria=item, idioma=request.LANGUAGE_CODE)
		except Idiomas_categoria_entrada.DoesNotExist:
			idioma_categoria = Idiomas_categoria_entrada.objects.filter(categoria=item).order_by('-idioma_default')
			idioma_categoria = idioma_categoria[0]
		idiomas_categoria.append(idioma_categoria)

	perfil_autor = get_object_or_404(Perfil,usuario=entrada.usuario)
	fotos_e = Fotos_entrada.objects.filter(entrada=entrada)
	if len(fotos_e) == 0:
		fotos_e = False
	n_entradas_relacionadas = entrada.entradas_relacionadas.all().count()
	
	if request.user.is_authenticated(): 
		try:
			rating = Rating_entrada.objects.get(entrada=entrada, usuario=request.user)
		except Rating_entrada.DoesNotExist:
			rating = False
	else:
		rating = False
		#No se pueden ver las entradas privadas si no se está logeado.
		if entrada.visibilidad == 'privada':
			return HttpResponseRedirect(reverse("account_login"))
			
	
	if entrada.tipo == 'e_general' or entrada.tipo == 'e_grupo':
		situacion = _(u'entradas')
	else:
		situacion = _(u'propuestas')
		
	comentario = None
	content_type = ContentType.objects.get_for_model(type(entrada))
	object_id = entrada.pk
	comentarios = Comentario.objects.filter(content_type=content_type,object_id=object_id,activo=True)

	
	if request.method == 'POST':
		form = Form_Comentario(request.POST,instance=comentario)
		if form.is_valid():
			c = form.save(commit=False)
			perfil = Perfil.objects.get(usuario=request.user)
			c.perfil = perfil
			c.creado_por = request.user
			c.modificado_por = request.user
			c.save()
			
			for grupo in entrada.grupo.all():
				c.grupo.add(grupo)
				
			mandar_mensajes(request,comentarios,c,entrada.usuario.email,url)

			return HttpResponseRedirect(entrada.get_absolute_url())
			
		else:
			form = Form_Comentario(request.POST)
	else:
		initial_data = {'content_type':content_type,'object_id':object_id}
		form = Form_Comentario(initial=initial_data, instance=comentario)
		
	datos = {'entrada':entrada,
			'idioma':idioma,
			'idiomas_categoria':idiomas_categoria,
			'fotos_e':fotos_e,
			'perfil_autor':perfil_autor,
			'form':form,
			'rating':rating,
			'n_entradas_relacionadas':n_entradas_relacionadas,
			'situacion':situacion,
			'comentarios':comentarios}
		
	return render_to_response('paginas/esta_entrada.html',datos,context_instance=RequestContext(request))

#######################################################################################################################################################		



def get_entradas(request,tipo=None):
	
	current_site = get_current_site(request)
	sitio = current_site.domain
	idioma=request.LANGUAGE_CODE
	url = unicode(sitio) + '/' + unicode(idioma) + '/p/' + unicode(tipo) + '/'
	
			
	if request.user.is_authenticated():
		
		if tipo == 'entradas':
			tipos = ['e_general','e_grupo']
			situacion = _(u'entradas')
		else:
			tipos = ['propuesta_general','propuesta_grupo']
			situacion = _(u'propuestas')
			
		mis_grupos_qs = Miembro.objects.filter(usuario=request.user).values_list('grupo',flat=True).distinct()
		#Pongo el .distinct() para evitar que salgan duplicadas o triplicadas si pertenecen a 2 o 3 grupos
		
		if len(mis_grupos_qs) > 0:
			entradas_qs = Entrada.objects.filter(grupo__in=mis_grupos_qs,tipo__in=tipos,estado='publicada').distinct().order_by('-creada')
		else:
			tipos = ['e_general','propuesta_general']
			entradas_qs = Entrada.objects.filter(tipo__in=tipos,estado='publicada',visibilidad='publica').distinct().order_by('-creada')
	else:
		
		if tipo == 'entradas':
			tipos = 'e_general'
			situacion = _(u'entradas') 
		else:
			tipos = 'propuesta_general'
			situacion = _(u'propuestas')
		entradas_qs = Entrada.objects.filter(estado='publicada',visibilidad='publica',tipo=tipos).distinct().order_by('-creada')

	try: 
		page = int(request.GET.get("page", '1'))
	except ValueError: 
		page = 1
		
	entradas = []
	for item in entradas_qs:
		adjuntar_datos_entrada(request,item=item)
		entradas.append(item)
		
	paginator = Paginator(entradas, 12)
	try:
		n_paginas = paginator.page(page)
	except (InvalidPage, EmptyPage):
		n_paginas = paginator.page(paginator.num_pages)
		
	
	datos = {'entradas': n_paginas.object_list,
			'n_paginas': n_paginas,
			'situacion':situacion,
			'url':url,
			'rss':'general'}
	
	if not request.is_ajax():
		return render_to_response('paginas/entradas.html',datos,context_instance=RequestContext(request)) 
	else:
		return render_to_response('paginas/paginacion_entradas.html',datos,context_instance=RequestContext(request))
		
	

#######################################################################################################################################################		


def get_entradas_usu(request,username=None):
	
	usuario = get_object_or_404(User, username=username)
	situacion = _(u'entradas del usuario ') + unicode(usuario)
	current_site = get_current_site(request)
	sitio = current_site.domain
	idioma=request.LANGUAGE_CODE
	url = unicode(sitio) + '/' + unicode(idioma) + '/p/entradas/' + unicode(usuario) + '/'
	
	if request.user.is_authenticated():
		grupos_del_visitante = Miembro.objects.filter(usuario=request.user).values_list('grupo',flat=True).distinct()
		entradas_qs = Entrada.objects.filter( (Q(grupo__in=grupos_del_visitante) & Q(usuario=usuario)) | (Q(usuario=usuario) & Q(estado='publicada') & Q(visibilidad='publica')) ).distinct().order_by('-creada')
	else:
		entradas_qs = Entrada.objects.filter(usuario=usuario,estado='publicada',visibilidad='publica').distinct().order_by('-creada')
		
	entradas = []
	for item in entradas_qs:
		adjuntar_datos_entrada(request,item=item)
		entradas.append(item)

	try: 
		page = int(request.GET.get("page", '1'))
	except ValueError: 
		page = 1
		
	paginator = Paginator(entradas, 12)
	try:
		n_paginas = paginator.page(page)
	except (InvalidPage, EmptyPage):
		n_paginas = paginator.page(paginator.num_pages)
		
	
	datos = {'entradas': n_paginas.object_list,
			'n_paginas': n_paginas,
			'situacion':situacion,
			'url':url,
			'rss':'usuario'}
		
	if not request.is_ajax():
		return render_to_response('paginas/entradas.html',datos,context_instance=RequestContext(request))
	else:
		return render_to_response('paginas/paginacion_entradas.html',datos,context_instance = RequestContext(request))

#######################################################################################################################################################

def get_entradas_grupo(request,tipo=None,simbolo=None):
	
	grupo = get_object_or_404(Grupo, simbolo=simbolo)
	current_site = get_current_site(request)
	sitio = current_site.domain
	idioma=request.LANGUAGE_CODE
	url = unicode(sitio) + '/' + unicode(idioma) + '/p/' + unicode(tipo) + '/grupo/' + unicode(grupo.simbolo) + '/'
	
	if tipo == 'entradas':
		tipos = ['e_general','e_grupo']
		situacion = _(u'entradas del grupo ') + unicode(grupo)
		
	else:
		tipos = ['propuesta_general','propuesta_grupo']
		situacion = _(u'propuestas del grupo ') + unicode(grupo)
	
	if request.user.is_authenticated():
		visitante_es_miembro = Miembro.objects.filter(usuario=request.user,grupo=grupo).count()
		if visitante_es_miembro > 0:
			entradas_qs = Entrada.objects.filter(grupo=grupo,tipo__in=tipos,estado='publicada').distinct().order_by('-creada')
		else:
			entradas_qs = Entrada.objects.filter(grupo=grupo,tipo__in=tipos,estado='publicada',visibilidad='publica').distinct().order_by('-creada')
	else:
		entradas_qs = Entrada.objects.filter(grupo=grupo,tipo__in=tipos,estado='publicada',visibilidad='publica').distinct().order_by('-creada')
		
	entradas = []
	for item in entradas_qs:
		adjuntar_datos_entrada(request,item=item)
		entradas.append(item)

	try: 
		page = int(request.GET.get("page", '1'))
	except ValueError: 
		page = 1
		
	paginator = Paginator(entradas, 12)
	try:
		n_paginas = paginator.page(page)
	except (InvalidPage, EmptyPage):
		n_paginas = paginator.page(paginator.num_pages)
		
	
	datos = {'entradas': n_paginas.object_list,
			'n_paginas': n_paginas,
			'situacion':situacion,
			'url':url,
			'rss':'grupo',
			'grupo':grupo}
		
	if not request.is_ajax():
		return render_to_response('paginas/entradas.html',datos,context_instance=RequestContext(request))
	else:
		return render_to_response('paginas/paginacion_entradas.html',datos,context_instance = RequestContext(request))
	
#######################################################################################################################################################


def get_entradas_clasificadas(request, id_categoria=False, tag=False):
	
	current_site = get_current_site(request)
	sitio = current_site.domain
	idioma=request.LANGUAGE_CODE
	
	if id_categoria:
		categoria = get_object_or_404(Categoria_Entrada,pk=id_categoria)	
		try:
			# Intento ponerla en el idioma en que está la página.
			idioma_categoria_entrada = Idiomas_categoria_entrada.objects.get(categoria=id_categoria, idioma=request.LANGUAGE_CODE)
			situacion = _(u'Entradas en la categoria ') + unicode(idioma_categoria_entrada.nombre)
		except Idiomas_categoria_entrada.DoesNotExist:
			situacion = _(u'Entradas en la categoria ') + unicode(categoria)
			
		entradas_qs = Entrada.objects.filter(categoria=categoria,estado='publicada',visibilidad='publica').distinct()
		url = unicode(sitio) + '/' + unicode(idioma) + '/p/categoria/' + unicode(id_categoria) + '/' 
	else:
		if request.user.is_authenticated():
			entradas_qs = Entrada.objects.filter(idiomas_entrada__tags__name=tag,estado='publicada').distinct()
		else:
			entradas_qs = Entrada.objects.filter(idiomas_entrada__tags__name=tag,estado='publicada',visibilidad='publica').distinct()
		situacion = _(u'Entradas en la etiqueta ') + unicode(tag)
		url = unicode(sitio) + '/' + unicode(idioma) + '/p/tag/' + unicode(tag) + '/' 
	
	entradas = []
	for item in entradas_qs:
		adjuntar_datos_entrada(request,item=item)
		entradas.append(item)

	try: 
		page = int(request.GET.get("page", '1'))
	except ValueError: 
		page = 1
		
	paginator = Paginator(entradas, 12)
	try:
		n_paginas = paginator.page(page)
	except (InvalidPage, EmptyPage):
		n_paginas = paginator.page(paginator.num_pages)
		
	
	datos = {'entradas': n_paginas.object_list,
			'n_paginas': n_paginas,
			'situacion':situacion,
			'url':url}

	if not request.is_ajax():
		return render_to_response('paginas/entradas.html',datos,context_instance=RequestContext(request))
	else:
		return render_to_response('paginas/paginacion_entradas.html',datos,context_instance = RequestContext(request))

#######################################################################################################################################################		

