# coding=utf-8

# Copyright (C) 2014 by Víctor Romero Blanco <info at playcircular dot com>.
# http://playcircular.com/
# It's licensed under the AFFERO GENERAL PUBLIC LICENSE unless stated otherwise.
# You can get copies of the licenses here: http://www.affero.org/oagpl.html
# AFFERO GENERAL PUBLIC LICENSE is also included in the file called "LICENSE".

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.template.defaultfilters import slugify
from django.contrib.contenttypes import generic
from metatags.models import *
from sorl.thumbnail import ImageField
from utilidades.combox import *
from tinymce import models as tinymce_models
from os.path import join as pjoin
from string import join
import os
from PIL import Image as PImage
from settings import MEDIA_ROOT

def ruta_foto_banner(instance, filename):
	dir = "documentos/banner/%s/%s" % (instance.usuario, filename)
	return dir

###################################################################################################

class Configuracion(models.Model):
	"""
	Datos para configuración del sitio
	"""
	usuario = models.ForeignKey(User, related_name='configuracion_general',editable=False)
	logo = ImageField(_(u'Logo'),upload_to='configuracion', help_text=_(u'Tamaño ideal de imagen: 180×180 (ancho×alto)'))
	nombre = models.CharField(verbose_name=_(u'Nombre'),max_length=120,unique=True,help_text=_(u'Título de la web'))
	favicon = ImageField(_(u'Favicon'),upload_to='configuracion',help_text=_(u'Tamaño ideal de imagen: 24×24 (ancho×alto)'))
	tiempo_diapositivas = models.IntegerField(_(u'Tiempo entre diapositivas'),default=5000,
		help_text=_(u'Tiempo entre cada diapositiva en milisegundos. 5000 ms = 5 segundos'))

	#google_analytics = models.TextField(verbose_name=_(u'Código de Analytics'),max_length=100,blank=True,null=True,)
	#verificacion_webmaster = models.CharField(verbose_name=_(u'Código de webmasters'),max_length=100,blank=True,null=True,)
	#verificacion_alexa = models.TextField(verbose_name=_(u'Código de Alexa'),max_length=100, blank=True,null=True,)
	google_maps_center = models.CharField(_(u'Coordenadas'), max_length=255,blank=True,null=True,
		help_text=_(u'Centrar el mapa en estas coordenadas. Debe parecer similar a: 40.42186,-3.700333'),)
	google_maps_zoom = models.IntegerField(_(u'Zoom'), blank=True,default=5,)

	#metatags = models.OneToOneField(Metatag, blank=True, null=True)

	creado = models.DateTimeField(_(u"Creado"),auto_now_add=True)
	creado_por = models.ForeignKey(User, related_name='autor_add_config_general',editable=False,blank=True,null=True)
	modificado = models.DateTimeField(_(u"Modificado"),auto_now=True)
	modificado_por = models.ForeignKey(User, related_name='autor_mod_config_general',editable=False,blank=True,null=True)

	def __unicode__(self):
		return unicode(self.nombre)
	
	def idiomas(self):
		lst = [x['idioma'] for x in self.idioma_configuracion.values()]
		return unicode(join(lst, ' | '))
	idiomas.allow_tags = True

	class Meta:
		verbose_name = _(u'Configuración general')
		verbose_name_plural = _(u'Configuración general')
		
############################################################################################################################	

class Idioma_configuracion(models.Model):

	configuracion = models.ForeignKey(Configuracion, related_name='idioma_configuracion')
	idioma = models.CharField(_(u"Idioma"),max_length=80, choices=IDIOMAS)
	idioma_default = models.BooleanField(_(u"Idioma por defecto"), default=False, help_text=_(u"Tipo idioma por defecto del grupo"))
	eslogan = models.CharField(_(u'Eslogan'),blank=True,max_length=255,null=True, help_text=_(u'Eslogan de la web. 255 caracteres max.'))
	condiciones = tinymce_models.HTMLField(_(u"Condiciones de uso"), help_text=_(u"Texto que debe aceptar cada usuario que se quiera registrar en el sitio."))
	pie_pagina = tinymce_models.HTMLField(_(u"Pie de página"), help_text=_(u"Texto que aparecerá en el pie de página general."))
	texto_email = tinymce_models.HTMLField(_(u"Texto del email de bienvenida"), 
		help_text=_(u"Texto que recibirá cada nuevo usuario registrado en su email."))
	robots = models.CharField(max_length=32, choices=ROBOTS_CHOICES, default='index, follow', verbose_name=_(u'meta robots'),
		help_text=_(u'Por defecto \"index, follow\"'))
	meta_descripcion = models.CharField(max_length=150, blank=True, null=True, verbose_name=_(u'meta description'),
		help_text=_(u'Breve descripción. Relacionado con el texto. Máx. 150 car.'))
	palabras_clave  = models.CharField(max_length=150, blank=True, null=True, verbose_name=_(u'meta keyword'), 
		help_text=_(u'Palabras clave separadas por comas. Relacionado con el texto. Máx. 150 car.'))
	creado = models.DateTimeField(_(u"Creado"),auto_now_add=True)
	creado_por = models.ForeignKey(User, related_name='autor_add_idioma_configuracion',editable=False,blank=True,null=True)
	modificado = models.DateTimeField(_(u"Modificado"),auto_now=True)
	modificado_por = models.ForeignKey(User, related_name='autor_mod_idioma_configuracion',editable=False,blank=True,null=True)

	def __unicode__(self):
		return unicode(self.idioma)
			
	class Meta:
		ordering = ['-idioma_default']
		verbose_name = _(u"idioma")
		verbose_name_plural = _(u"idiomas")

###################################################################################################

class Banner_general(models.Model):

	usuario = models.ForeignKey(User, related_name='usu_banner_general',editable=False)
	banner = ImageField(_(u'Banner'), upload_to=ruta_foto_banner,
		help_text=_(u"Campo para subir banner que se mostarán en el grupo. Tamaño recomendado 970x300 px."))
	titulo = models.CharField(_(u"Título"),max_length=180,blank=True,null=True,
		help_text=_(u"Texto que se mostrará debajo del banner"))
	url = models.URLField(_(u"Url"),max_length=200,blank=True,null=True,
		help_text=_(u"Url a la que apuntará el banner"))
	tipo = models.CharField(_(u"Tipo"),max_length=120, choices=TIPO_BANNER)
	visibilidad = models.CharField(_(u"Visibilidad"),max_length=120, choices=VISIBILIDAD_PAGINA,
		help_text=_(u"Si será pública para cualquier usuario registrado o sólo para los miembros de mis grupos."))
	orden = models.PositiveIntegerField(_(u"Orden"), default=1,
		help_text=_(u"Orden en que se mostrará el banner."))
	activo = models.BooleanField(_(u"Activo"), default=True, help_text=_(u"Poner el banner en activo o inactivo."))
	width = models.IntegerField(_(u"Ancho"),blank=True, null=True,editable=False)
	height = models.IntegerField(_(u"Alto"),blank=True, null=True,editable=False)
	creado = models.DateTimeField(_(u"Creada"),auto_now_add=True)
	creado_por = models.ForeignKey(User, related_name='autor_add_banner_general',editable=False,blank=True,null=True)
	modificado = models.DateTimeField(_(u"Modificada"),auto_now=True)
	modificado_por = models.ForeignKey(User, related_name='autor_mod_banner_general',editable=False,blank=True,null=True)

	def __unicode__(self):
		return unicode(self.banner)
	
	class Meta:
		ordering = ["orden"]
		verbose_name = _(u"banner general")
		verbose_name_plural = _(u"banner general")
		
	def save(self, *args, **kwargs):
		"""Save banner dimensions."""
		super(Banner_general, self).save(*args, **kwargs)
		im = PImage.open(os.path.join(MEDIA_ROOT, self.banner.name))
		self.width, self.height = im.size
		super(Banner_general, self).save(*args, ** kwargs)

	def dimensiones(self):
		"""Banner_general size."""
		return "%s x %s" % (self.width, self.height)
	dimensiones.allow_tags = True


###################################################################################################









