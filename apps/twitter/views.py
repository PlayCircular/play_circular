# -*- coding: utf-8 -*-
from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseNotAllowed
from django.core.urlresolvers import reverse
from twitter.models import *
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.models import User
#from django.contrib.auth import login, authenticate, logout
import datetime, re
from django.utils.datastructures import SortedDict
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from urllib import urlencode
from twitter.forms import *
from usuarios.models import *
from grupos.models import *
from paginas.models import *
from actividades.models import *
from economia.models import *
from utilidades.combox import *
#from utilidades.views import *
from django.utils.text import slugify

## No puedo importar las vistas de actividades porque allí estoy importando esta vista y crearía un error
#from actividades.views import *




############################################################################################################################
#def mis_seguimientos(request):
	#t = get_object_or_404(Tweet, id = tweet_id)

############################################################################################################################
		
def tendencias(n = 1, limit = None):
	
	"""¿Mide la importancia de cada hashtag? Creo que no y no es semantico."""
	hashtags = {}
	if limit is None:
		mensajes = Mensaje.objects.all()
	else:
		mensajes = Mensaje.objects.all().order_by('-creado')[:limit]
		
	for m in mensajes:
		f = re.findall('#[a-zA-Z0-9]+', m.contenido)
		#print 'f',f
		for hashtag in f:
			if not hashtag in hashtags:
				hashtags[hashtag] = 1
			else:
				hashtags[hashtag] += 1
	
	ordenar = []
	for hashtag in hashtags.keys():
		ordenar.append((hashtags[hashtag], hashtag))
	ordenar = sorted(ordenar)
	ordenar.reverse()

	final = []
	for e in ordenar[:n]:
		final.append(e[1][1:])
	return final

############################################################################################################################	

#def randuser(user, n = 1):
	#users = User.objects.all()
	#final = []
	#for x in range(0,n):
		#""" Se vuelve a ejectutar salvo que se llegue al lÃ­mite o que se haya
		#encontrado un usuario """
		#rebuscar, i = True, 0
		#while rebuscar and i<len(users):
			#i += 1
			#r = random.randint(0, len(users) - 1)
			#u = users[r]
			#p = Profile.objects.get(user = user)
			#if (not Follow.objects.filter(follower = p, followed = u) and
				#(not u in final) and (user != u)):
				#""" Si el usuario aleatorio nunca fue seguido por el otro """
				#rebuscar = False
				#final.append(u)
	#return final
	
############################################################################################################################
def get_perfil_social(request, username=None):

	#n = MENSAJES_EN_PAGINA
		
	if request.user.is_authenticated():
		try: 
			usuario = User.objects.get(username=username)
			este_perfil = Perfil.objects.get(usuario_id=usuario.pk)
			grupos = Miembro.objects.filter(usuario=usuario.pk)
			n_logins = Visitas_usuario.objects.filter(usuario=usuario.pk).count()
			
			tipos_entrada = ['e_general','e_grupo','propuesta_general','propuesta_grupo']
			
			grupos_del_visitante = Miembro.objects.filter(usuario=request.user).values_list('grupo',flat=True).distinct()
			ult_entradas = Entrada.objects.filter( (Q(grupo__in=grupos_del_visitante) & Q(usuario=usuario)) | 
													(Q(usuario=usuario) & Q(estado='publicada') & Q(visibilidad='publica')) ).distinct().order_by('-creada')[:5]
			n_entradas = Entrada.objects.filter(usuario=usuario,tipo__in=tipos_entrada,estado='Publicada').distinct().count()
			ult_actividades = Actividad.objects.filter(perfil=este_perfil).distinct().order_by('-creado')[:5]
			n_actividades = Actividad.objects.filter(perfil=este_perfil).distinct().count()
			ult_intercambios_p = Intercambio.objects.filter((Q(origen=usuario) | Q(destino=usuario)) & Q(publico=True) & Q(tipo='Normal') & Q(cantidad__gt=0))[:5]
			n_intercambios = Intercambio.objects.filter((Q(origen=usuario) | Q(destino=usuario)) & Q(publico=True) & Q(tipo='Normal') & Q(cantidad__gt=0)).count()
			
			
			#seguidor = Seguimiento.objects.filter(seguidor=usuario.pk,activo=True) #Busca los users que sigue el usuario
			#seguido = Seguimiento.objects.filter(seguido=usuario.pk,activo=True) #Busca los users que siguen al usuario

			#users = [u.seguido for u in seguidor] #Hace que users sea un array de los usuarios que sigue
			#users.append(request.user) #Le agrega el usuario actual
			
			#n_mensajes_publicados = Mensaje.objects.filter(usuario=usuario, activo=True).count()
			#mensajes_ = Mensaje.objects.filter(usuario__in=users, activo=True).order_by('-creado')[0:MENSAJES_EN_PAGINA]
			
			##Procesa mensajes
			#mensajes = []
			#for m in mensajes_:
				#if m.reescrito == True:
					#rm = Mensaje.objects.get(pk=int(m.contenido))
					#rm.reescrito = 1
					#rm.reescrito_por = m.usuario
					#rm.mensaje_id = m.id
					#mensajes.append(rm)
				#else:
					#mensajes.append(m)
			
			#try:
				#s = Seguimiento.objects.get(seguidor=request.user, seguido=usuario.pk,activo=True)
				#if s:
					#es_seguido = True
				#else:
					#es_seguido = False
			#except Seguimiento.DoesNotExist:
				#es_seguido = False
				
			#datos = {'este_perfil':este_perfil, 
					 #'grupos':grupos, 
					 #'seguidor':seguidor, 
					 #'seguido':seguido, 
					 #'mensajes': mensajes,
					 #'n_mensajes':n_mensajes_publicados,
					 #'tendencias':tendencias(5, 200),
					 #'es_seguido': es_seguido}
			
			datos = {'este_perfil':este_perfil, 
					 'grupos':grupos, 
					 'ult_entradas':ult_entradas, 
					 'n_entradas':n_entradas, 
					 'ult_actividades': ult_actividades,
					 'n_actividades':n_actividades,
					 'ult_intercambios_p':ult_intercambios_p,
					 'n_intercambios': n_intercambios,
					 'n_logins':n_logins}
					 
			return datos
			
		except Perfil.DoesNotExist:
			return False
			#return HttpResponseRedirect(reverse("login"))
	else:
		return False


	
############################################################################################################################
def ver_perfil_social(request, username=None):
	
	datos = get_perfil_social(request, username)
	
	if datos:
		return render_to_response('social/perfil_social.html', datos, context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect(reverse("portada"))


############################################################################################################################
def seguir(request):
	
	if request.method == 'POST':
		form = Form_seguir(request.POST)
		if form.is_valid():
			
			usuario_seguido = get_object_or_404(User, pk=form.cleaned_data['usu'])
			
			"""Uno no puede seguirse a sí mismo"""
			if usuario_seguido != request.user:	
				try:
					s = Seguimiento.objects.get(seguidor=request.user, seguido=form.cleaned_data['usu'])
					
					"""Si el usuario ya ha sido seguido anteriormente y quiere seguirlo (1), lo pongo en activo si es que no lo está ya"""
					if form.cleaned_data['accion'] == 1:
						s.activo = True
					else:
						s.activo = False
						
					s.save()
					
				except Seguimiento.DoesNotExist:
					
					s = Seguimiento()
					s.seguidor = request.user
					s.seguido = usuario_seguido
					s.activo = form.cleaned_data['accion']
					s.save()
					
			return HttpResponseRedirect(reverse("social-perfil", kwargs=dict(username=usuario_seguido)))
		else:
			return HttpResponseRedirect(reverse("portada"))
	else:
		return HttpResponseRedirect(reverse("portada"))


############################################################################################################################

def escribir(request):

	if request.method == 'POST':
		form = Form_escribir(request.POST)
		if form.is_valid():
			
			usuario = get_object_or_404(User, pk=form.cleaned_data['usu'])
			if  int(request.POST['respuesta']) == 0:
				respuesta = None
			else:
				respuesta = int(request.POST['respuesta'])

			m = Mensaje()
			m.usuario = request.user
			m.contenido = form.cleaned_data['contenido']
			if respuesta is not None:
				m.respuesta = form.cleaned_data['respuesta']
			m.save()
		else:
			return HttpResponseRedirect(reverse("portada"))
		
	else:
		return HttpResponseRedirect(reverse("portada"))

	return HttpResponseRedirect(reverse("social-perfil", kwargs=dict(username=usuario)))
	
############################################################################################################################

def reescribir(request, mensaje_id):
	
	m = get_object_or_404(Mensaje, pk=mensaje_id)
	
	"""El usuario del mensaje no puede reescribirlo"""
	if request.POST.has_key('confirma') and m.usuario != request.user: 
	
		m = Mensaje()
		m.usuario = request.user
		m.contenido = str(mensaje_id)
		m.reescrito = True
		m.save()

		return HttpResponseRedirect(reverse("portada"))
	else:
		return render_to_response('social/reescribir.html',	{'mensaje':get_object_or_404(Mensaje,pk=mensaje_id)}, context_instance=RequestContext(request))

############################################################################################################################	
	
def responder(request, mensaje_id):
	
	m = get_object_or_404(Mensaje, pk=mensaje_id)
	if m.usuario != request.user:
		return render_to_response('social/responder.html',	{'mensaje':get_object_or_404(Mensaje,pk=mensaje_id)}, context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect(reverse("portada"))

############################################################################################################################	

def borrar(request, mensaje_id):
	m = get_object_or_404(Mensaje, pk=mensaje_id)
	if m.usuario == request.user: #El usuario actual es el propietario del mensaje 
		m.activo = False
		m.save()
		return HttpResponseRedirect(reverse("portada"))
	else:
		return HttpResponseRedirect(reverse("social-perfil", kwargs=dict(username=request.user)))


############################################################################################################################


def conversacion(request, mensaje_id, page = 1):
	if page < 2:
		page = 1
	n = MENSAJES_EN_PAGINA * (int(page) - 1)
	mensajes = []
	#m = get_object_or_404(Mensaje, pk=mensaje_id)
	#mensajes.append(m)
	#while m.respuesta: #Mientras este contestando a otro tweet
		#m = get_object_or_404(Mensaje, pk = int(m.respuesta))
		#mensajes.append(m)
	 
	"""Esto de abajo deja al sistema colgado. Es para intentar recojer todas las conversaciones, 
	no solo respuesta 1 usu 1 > respuesta 1 usu 2 > respuesta 2 usu 1, respuesta 2 usu 2...
	Si el usu 1 responde 2 cosas a algun mensaje de usu 2, en la conversación solo sale una de ellas."""
	
	m = get_object_or_404(Mensaje, pk=mensaje_id)
	mensajes.append(m)
	while m.respuesta: #Mientras este contestando a otro tweet
		#m = get_object_or_404(Mensaje, pk = int(m.respuesta))
		qs_mensaje = Mensaje.objects.filter(respuesta=int(m.respuesta)).exclude(pk=m.pk).order_by('-creado')
		for item in qs_mensaje:
			mensajes.append(item)
		m = get_object_or_404(Mensaje, pk = int(m.respuesta))
		mensajes.append(m)
		
			
	return render_to_response('social/mensajes.html',
	{
		'next' : int(page) + 1,
		'page' : page,
		'prev' : int(page) - 1,
		'mensajes' : mensajes,
		'page_prefix' : 'conversacion/%s/' % mensaje_id,
	}, context_instance=RequestContext(request)) 

############################################################################################################################	

def buscar(request, busqueda=False, opcion=1):

	try: 
		page = int(request.GET.get("page", '1'))
	except ValueError: 
		page = 1

	if busqueda:
		
		"""Tengo que añadirle el '#' porque la expresión regular de la url lo interpreta como comentario y no me deja"""
		hashtag = '#%s' % busqueda
		n = MENSAJES_EN_PAGINA * (int(page) - 1)
		mensajes = Mensaje.objects.filter(contenido__icontains=hashtag).order_by('-creado')[n:n + MENSAJES_EN_PAGINA]
		
		paginator = Paginator(mensajes, 3)
		try:
			n_paginas = paginator.page(page)
		except (InvalidPage, EmptyPage):
			n_paginas = paginator.page(paginator.num_pages)
		
		datos = {'mensajes':mensajes,'busqueda':hashtag,"n_paginas":n_paginas}

		if opcion == '1':
				"""Si el hashtag es de una actividad, lo mando para la ficha de la actividad que genera los hashtag"""
				#if hashtag[0:11] == '#Actividad-':
					#id_actividad = hashtag[11:]
				if hashtag.startswith('#Actividad-'):
					# Ejemplo hashtag: '#Actividad-23-D'
					trozos = hashtag.split('-')
					id_actividad = trozos[1]
					try:
						pk = int(id_actividad)
						try:
							actividad = Actividad.objects.get(pk=pk)
							slug = slugify(unicode('%s' % (actividad)))
							#datos = dict(clase=actividad.clase, tipo=actividad.tipo, id_objeto=actividad.pk, slug=actividad.slug)
							#datos = SortedDict({'clase':actividad.clase, 'tipo':actividad.tipo, 'id_objeto':actividad.pk, 'slug':actividad.slug})
							return HttpResponseRedirect(reverse("ver-actividad", kwargs=dict(clase=actividad.clase, tipo=actividad.tipo, id_objeto=actividad.pk, slug=slug)))
						except Actividad.DoesNotExist:
							return render_to_response('social/mensajes.html',datos, context_instance=RequestContext(request))
					except ValueError:
						return render_to_response('social/mensajes.html',datos, context_instance=RequestContext(request))
				else:
					return render_to_response('social/mensajes.html',datos, context_instance=RequestContext(request))
		else:
			return datos
	else:
		return HttpResponseRedirect(reverse("portada"))

############################################################################################################################	



#def conf(request):
	#u = request.user
	#p = get_object_or_404(Profile, user = u)
	#try:
		#if not u.check_password(request.POST['oldpass']):
			#return render_to_response('twitter/conf.html',{
				#'mensaje' : '<h3>Introduzca su contraseña actual correctamente</h3>',
				#'nombre' : u.first_name,
				#'apellido' : u.last_name,
				#'email' : u.email,
				#'ubicacion' : p.ubicacion,
				#'bio' : p.frase,
				#'logueado' : request.user,
				#'ntweets' : len(Tweet.objects.filter(user = request.user)),
				#'u_seguidores' : len(Follow.objects.filter(activo = True,
					#follower = Profile.objects.get(user = request.user))),
				#'u_siguiendo' : len(Follow.objects.filter(activo = True,
					#followed = request.user)),
				#}, RequestContext(request))
		#if request.POST['procesa'] == 'profile':
			#u.first_name = request.POST['firstname']
			#u.last_name = request.POST['lastname']
			#u.email = request.POST['email']
			#u.save()

			#p.ubicacion = request.POST['ubicacion']
			#p.frase = request.POST['bio']
			#p.save()
		#elif request.POST['procesa'] == 'pass':
			#if request.POST['pass'] == request.POST['pass2']:
				#u.set_password(request.POST['pass'])
				#u.save()
				#logout(request)
				#return HttpResponseRedirect('/twitter/')
			#else:
				#return render_to_response('twitter/conf.html',{
					#'mensaje' : 'Las contraseñas no coinciden',
					#'nombre' : u.first_name,
					#'apellido' : u.last_name,
					#'email' : u.email,
					#'ubicacion' : p.ubicacion,
					#'bio' : p.frase,
					#'logueado' : request.user,
					#'ntweets' : len(Tweet.objects.filter(user = request.user)),
					#'u_seguidores' : len(Follow.objects.filter(activo = True,
						#follower = Profile.objects.get(user = request.user))),
					#'u_siguiendo' : len(Follow.objects.filter(activo = True,
						#followed = request.user)),
					#}, RequestContext(request))
		#return HttpResponseRedirect('/twitter/configuracion/')
	#except KeyError:
		#return render_to_response('twitter/conf.html',{
			#'nombre' : u.first_name,
			#'apellido' : u.last_name,
			#'email' : u.email,
			#'ubicacion' : p.ubicacion,
			#'bio' : p.frase,
			#'logueado' : request.user,
			#'ntweets' : len(Tweet.objects.filter(user = request.user)),
			#'u_seguidores' : len(Follow.objects.filter(activo = True,
				#follower = Profile.objects.get(user = request.user))),
			#'u_siguiendo' : len(Follow.objects.filter(activo = True,
				#followed = request.user)),
			#}, RequestContext(request))
