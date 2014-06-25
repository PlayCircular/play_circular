# coding=utf-8

# Copyright (C) 2014 by Víctor Romero Blanco <info at playcircular dot com>.
# http://playcircular.com/
# It's licensed under the AFFERO GENERAL PUBLIC LICENSE unless stated otherwise.
# You can get copies of the licenses here: http://www.affero.org/oagpl.html
# AFFERO GENERAL PUBLIC LICENSE is also included in the file called "LICENSE".

from os import path
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.template.defaultfilters import slugify
from django.contrib.contenttypes import generic
from datetime import datetime, date, time
from utilidades.combox import *
from sorl.thumbnail import ImageField
from taggit.managers import TaggableManager
from tinymce import models as tinymce_models

def ruta_foto_usu(instance, filename):
	dir = "documentos/fotos_usuarios/%s/%s" % (instance.usuario, filename)
	return dir


############################################################################################################################

class Incidencias_usuario(models.Model):

	"""Incidencias que se pueden abrir a un usuario"""
	usuario = models.ForeignKey(User, related_name='incidencias_del_usuario')
	incidencia = models.TextField(_(u"Incidencia"),blank=True, help_text=_(u"Incidencia del usuario."))

	creado = models.DateTimeField(auto_now_add=True)
	creado_por = models.ForeignKey(User, related_name='autor_add_incidiencia_usu',editable=False,blank=True,null=True)
	modificado = models.DateTimeField(auto_now=True)
	modificado_por = models.ForeignKey(User, related_name='autor_mod_incidiencia_usu',editable=False,blank=True,null=True)

	def __unicode__(self):
		return unicode(self.creado)

	class Meta:
		ordering = ['-creado']
		verbose_name = _(u'Incidencias de usuario')
		verbose_name_plural = _(u'Incidencias de usuario')


############################################################################################################################

class Perfil(models.Model):
	
	usuario = models.OneToOneField(User, unique=True, related_name='perfil_usu',editable=False)
	nombre = models.CharField(_(u"Nombre"), max_length=150, blank=True)
	ocultar_nombre = models.BooleanField(_(u"Ocultar nombre"),default=False)
	apellidos = models.CharField(_(u"Apellidos"), max_length=250, blank=True)
	ocultar_apellidos = models.BooleanField(_(u"Ocultar apellidos"),default=False)
	pais = models.CharField(_(u"Pais"), default=_(u'España'), max_length=50, blank=True, choices=PAISES)

	provincia = models.CharField(_(u"Provincia"), max_length=80, choices=PROVINCIAS,blank=True, null=True)
	poblacion = models.CharField(_(u"Población"),max_length=250,blank=True, null=True)
	direccion = models.CharField(_(u"Dirección"), max_length=250, blank=True)
	ocultar_direccion = models.BooleanField(_(u"Ocultar direccion"),default=False)
	codigo_postal = models.CharField(_(u"Código postal"),max_length=6, blank=True)
	coordenadas = models.CharField(_(u'Coordenadas'), max_length=255,blank=True,null=True,
		help_text=_(u'Para marcar tu posición en un mapa. Debe parecer similar a: 40.42186,-3.700333'),)
	telefono = models.BigIntegerField(_(u"Móvil"),max_length=15, help_text=_(u"Movil o teléfono."),blank=True, null=True)
	ocultar_telefono = models.BooleanField(_(u"Ocultar telefono"),default=False)
	mi_email = models.EmailField(_(u"Email"),max_length=70)
	ocultar_email = models.BooleanField(_(u"Ocultar email"),default=False)
	descripcion = tinymce_models.HTMLField(_(u"Descripción"),max_length=750, help_text=_(u"Breve descripción personal."),blank=True, null=True)
	n_logins = models.PositiveIntegerField(default=0,editable=False)
	activo = models.BooleanField(_(u"Activo"), default=True, editable=False)
	creado = models.DateTimeField(_(u"Creado"),auto_now_add=True)
	creado_por = models.ForeignKey(User, related_name='autor_add_persona',editable=False,blank=True,null=True)
	modificado = models.DateTimeField(_(u"Modificado"),auto_now=True)
	modificado_por = models.ForeignKey(User, related_name='autor_mod_persona',editable=False,blank=True,null=True)

		
	def __unicode__(self):
		return unicode(self.usuario.username)
		
	def fotos(self):
		dato = self.fotos_personales.all()
		cadena = ''
		if dato:
			for item in dato:
				cadena = cadena + """<img alt="%s" title="%s" src="%s" widht="50px" height="50px"/> | """  % ((item.foto.name, item.foto, item.foto.url ))
	
		return cadena
	fotos.allow_tags = True
	
	def una_foto(self):
		fotos = self.fotos_personales.all()
		if len(fotos) > 0:
			return fotos[0]
		else:
			return False
	una_foto.allow_tags = True
	
	def logins(self):
		n = Visitas_usuario.objects.filter(usuario=self.usuario).count()
		return n
	logins.allow_tags = True

	def email(self):
		return unicode(self.usuario.email)

	def ultima_visita(self):
		return unicode(self.usuario.last_login)

	def nombre_completo(self):
		return unicode(self.usuario.first_name + ' ' + self.usuario.last_name)
	
	def get_nombre_visible(self):
		cadena = ''
		if self.ocultar_nombre == False:
			cadena += unicode(self.nombre)
		if self.ocultar_apellidos == False:
			cadena += ' ' + unicode(self.apellidos)
		if cadena == '':
			return False
		else:
			return cadena
		
	class Meta:
		verbose_name = _(u"perfil")
		verbose_name_plural = _(u"perfiles")
		ordering = ['-creado']

	
############################################################################################################################

class Fotos_personales(models.Model):
	
	usuario = models.ForeignKey(Perfil, related_name='fotos_personales')
	foto = ImageField(_(u'Foto propia'), upload_to=ruta_foto_usu, blank=True, null=True,
		help_text=_(u"Campo para subir fotografias propias."))

	creado = models.DateTimeField(_(u"Creado"),auto_now_add=True)
	creado_por = models.ForeignKey(User, related_name='autor_add_fotos',editable=False,blank=True,null=True)
	modificado = models.DateTimeField(_(u"Modificado"),auto_now=True)
	modificado_por = models.ForeignKey(User, related_name='autor_mod_fotos',editable=False,blank=True,null=True)
		
	class Meta:
		verbose_name = _(u'Fotos personales')
		verbose_name_plural = _(u'Fotos personales')
		
############################################################################################################################	

class Social_usu(models.Model):

	usuario = models.ForeignKey(Perfil, related_name='social_usu')
	nombre = models.CharField(_(u"Nombre"), max_length=250, help_text=_(u"Ejemplo: perfil en twitter, facebook, meneame, otra web, otro teléfono, etc..."))
	referencia = models.CharField(_(u"Referencia"), max_length=350, help_text=_(u"Url en twitter, facebook,meneame, flickr, lift, quora, otra web, weblogs, etc..."))

	creado = models.DateTimeField(_(u"Creado"),auto_now_add=True)
	creado_por = models.ForeignKey(User, related_name='autor_add_mas_info',editable=False,blank=True,null=True)
	modificado = models.DateTimeField(_(u"Modificado"),auto_now=True)
	modificado_por = models.ForeignKey(User, related_name='autor_mod_mas_info',editable=False,blank=True,null=True)

	def __unicode__(self):
		return unicode(self.nombre)
			
	class Meta:
		verbose_name = _(u"dato social")
		verbose_name_plural = _(u"más datos sociales")
		
############################################################################################################################

class Visitas_usuario(models.Model):

	usuario = models.ForeignKey(User, related_name='usu_visitado')
	visitante = models.ForeignKey(User, related_name='usu_visitante')
	creado = models.DateTimeField(_(u"Creado"),auto_now_add=True)

	def __unicode__(self):
		return unicode(self.usuario)
		
	class Meta:
		verbose_name = _(u'visita al usuario')
		verbose_name_plural = _(u'visitas al usuario')


###################################################################################################

class Correspondencia(models.Model):

	"""Copia de los mensajes que el sistema le puede enviar a cada usuario por email para auditorias, etc..."""

	destinatario = models.ForeignKey(User, related_name='destinatario',editable=False)
	id_remitente = models.PositiveIntegerField(_(u"Id remitente"),default=1, null=True, blank=True)
	remitente = models.CharField(_(u"Remitente"), max_length=150, blank=True, null=True)
	email_remitente = models.CharField(_(u"Email del remitente"), max_length=150, blank=True, null=True)
	asunto = models.CharField(_(u"Asunto"), max_length=150, blank=True, null=True)
	mensaje = models.TextField(blank=True)
	leido = models.BooleanField(_(u"Leído"), default=False, help_text=_(u'Pulsa aquí para marcarlo como leído'))
		
	creado = models.DateTimeField(_(u"Creado"),auto_now_add=True)
	creado_por = models.ForeignKey(User, related_name='autor_add_correspondencia',editable=False,blank=True,null=True)
	modificada = models.DateTimeField(_(u"Modificado"),auto_now=True)
	modificado_por = models.ForeignKey(User, related_name='autor_mod_correspondencia',editable=False,blank=True,null=True)

	class Meta:
		ordering = ["-creado"]
		verbose_name = _(u'mensaje del sistema')
		verbose_name_plural = _(u'mensajes del sistema')

############################################################################################################################

class Config_perfil(models.Model):

	usuario = models.OneToOneField(User, unique=True, related_name='config_perfil',editable=False)
	
	idioma = models.CharField(_(u"Idioma"),max_length=80, choices=IDIOMAS, 
		default=_(u'es'),help_text=_(u'Idioma por defecto.'))
	valorar_actividades = models.BooleanField(_(u"Valorar actividades"), default=True,
		help_text=_(u'Participar en el sistema de valoración global de actividades.'))
	intercambios_publicos = models.BooleanField(_(u"Intercambios públicos"), default=False,
		help_text=_(u'Marcar tus intercambios visibles para la comunidad por defecto.'))
	aviso_pago = models.BooleanField(_(u"Avisos de pago"), default=False,
		help_text=_(u'Recibir avisos de pago en moneda social al email.'))
	contacto_oculto = models.BooleanField(_(u"Contacto oculto"), default=False,
		help_text=_(u'Ocultar mi email y telefono y que se comuniquen conmigo por via interna mostrando las veces que lo hacen.'))

	creado = models.DateTimeField(_(u"Creado"),auto_now_add=True)
	creado_por = models.ForeignKey(User, related_name='autor_add_config_perfil',editable=False,blank=True,null=True)
	modificado = models.DateTimeField(_(u"Modificado"),auto_now=True)
	modificado_por = models.ForeignKey(User, related_name='autor_mod_config_perfil',editable=False,blank=True,null=True)

		
	def __unicode__(self):
		return unicode(self.usuario)
	
	class Meta:
		verbose_name = _(u"configuración del perfil")
		verbose_name_plural = _(u"configuración")


############################################################################################################################

