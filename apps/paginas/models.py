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
from datetime import datetime, date, time
from metatags.models import *
from grupos.models import *
from utilidades.combox import *
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from tinymce import models as tinymce_models
#from tinymce.models import HTMLField

import os
from PIL import Image as PImage
from settings import MEDIA_ROOT
from os.path import join as pjoin
from string import join
from mptt.models import MPTTModel, TreeForeignKey
from django.db.models import permalink
from django.db.models import Avg
from decimal import Decimal

def ruta_foto_pagina(instance, filename):
	dir = "documentos/fotos_paginas/%s/%s" % (instance.pagina.usuario, filename)
	return dir

def ruta_foto_entrada(instance, filename):
	dir = "documentos/fotos_entradas/%s/%s" % (instance.entrada.usuario, filename)
	return dir

def ruta_foto_banner(instance, filename):
	dir = "documentos/banner/%s/%s" % (instance.usuario, filename)
	return dir

########################################################################################################################################

class Categoria_Entrada(models.Model):
	
	usuario = models.ForeignKey(User, related_name='usu_categoria_entrada',editable=False)
	grupo = models.ManyToManyField(Grupo, related_name='grupo_categoria_entrada', null=True, blank=True)
	superadmin = models.BooleanField(_(u"Superadmin"), default=False)
	creada = models.DateTimeField(_(u"Creada"),auto_now_add=True)
	creada_por = models.ForeignKey(User, related_name='autor_add_cate_entrada',editable=False,blank=True,null=True)
	modificada = models.DateTimeField(_(u"Modificada"),auto_now=True)
	modificada_por = models.ForeignKey(User, related_name='autor_mod_cate_entrada',editable=False,blank=True,null=True)


	def __unicode__(self):
		idioma = self.idioma_categoria_entrada.all().order_by('-idioma_default')[0]
		return unicode(idioma.nombre) 
	
	def nombre_de_categoria(self):
		idioma = self.idioma_categoria_entrada.all().order_by('-idioma_default')[0]
		return unicode(idioma.nombre)
	nombre_de_categoria.allow_tags = True
	
	def idiomas(self):
		lst = [x['idioma'] for x in self.idioma_categoria_entrada.values()]
		return unicode(join(lst, '| '))
	idiomas.allow_tags = True
	
	def grupos(self):
		lst = [x['simbolo'] for x in self.grupo.values()]
		return unicode(join(lst, ', '))
	grupos.allow_tags = True

	#@permalink
	#def get_absolute_url(self):
		#return ('categorias', None, { 'slug': self.slug })
	

	class Meta:
		ordering=['creada']
		verbose_name = _(u"categorias de entrada")
		verbose_name_plural = _(u"categorias de entrada")
	
	
############################################################################################################################	

class Idiomas_categoria_entrada(models.Model):
	
	categoria = models.ForeignKey(Categoria_Entrada, related_name='idioma_categoria_entrada')
	idioma = models.CharField(_(u"Idioma"),max_length=80, choices=IDIOMAS, help_text=_(u'Idioma para esta categoria.'))
	idioma_default = models.BooleanField(_(u"Idioma por defecto"), default=False, help_text=_(u"Tipo de idioma por defecto de la categoria"))
	nombre = models.CharField(_(u"Nombre"),max_length=120, db_index=True, help_text=_(u"Nombre de la categoria."))
	slug = models.SlugField(_('Slug'), max_length=120)
	descripcion = models.TextField(_(u"Descripción"), null=True, blank=True,  help_text=_(u"Breve descripción de la categoria."))
		
	def __unicode__(self):
		return unicode(self.nombre)

	#def get_categoria(self):
		#return unicode(self.nombre)
			
	class Meta:
		ordering = ['-idioma_default']
		verbose_name = _(u"idioma de categoria")
		verbose_name_plural = _(u"idiomas de categorias")
		unique_together = ("idioma", "categoria")

########################################################################################################################################

class Entrada(models.Model):

	grupo = models.ManyToManyField(Grupo, related_name='grupo_entrada', null=True, blank=True)
	superadmin = models.BooleanField(_(u"Superadmin"), default=False)
	usuario = models.ForeignKey(User, related_name='usu_entrada')
	tipo = models.CharField(_(u"Tipo"),max_length=120, choices=TIPO_ENTRADA, default='e_grupo')
	estado = models.CharField(_(u"Estado"),max_length=80, choices=ESTADO_PAGINA)
	visibilidad = models.CharField(_(u"Visibilidad"),max_length=120, choices=VISIBILIDAD_PAGINA,
		help_text=_(u"Si será pública para cualquier usuario registrado o sólo para los miembros de mis grupos."))
	comentarios = models.BooleanField(_(u"Permite comentarios"), default=False)
	creada = models.DateTimeField(_(u"Creada"),auto_now_add=True)
	creada_por = models.ForeignKey(User, related_name='autor_add_entrada',editable=False,blank=True,null=True)
	modificada = models.DateTimeField(_(u"Modificada"),auto_now=True)
	modificada_por = models.ForeignKey(User, related_name='autor_mod_entrada',editable=False,blank=True,null=True)
	categoria = models.ManyToManyField(Categoria_Entrada, related_name='categoria_entrada', null=True, blank=True)
	entradas_relacionadas = models.ManyToManyField("self", verbose_name=_("Entradas relacionadas"), blank=True)
	metatags = generic.GenericRelation('metatags.Metatag')


	def __unicode__(self):
		idioma = self.idiomas_entrada.all().order_by('-idioma_default')[0]
		return unicode(idioma.titulo)
	
	def _titulo(self):
		idioma = self.idiomas_entrada.all().order_by('-idioma_default')[0]
		return unicode(idioma.titulo)
	_titulo.allow_tags = True
	
	def idiomas(self):
		lst = [x['idioma'] for x in self.idiomas_entrada.values()]
		return unicode(join(lst, ' | '))
	idiomas.allow_tags = True
	
	def idiomas_disponibles(self):
		idiomas = self.idiomas_entrada.all()
		return idiomas
	
	def grupos(self):
		lst = [x['simbolo'] for x in self.grupo.values()]
		return unicode(join(lst, ', '))
	grupos.allow_tags = True
	
	def n_visitas(self):
		try:
			v = self.visita_entrada.latest('modificado')
			return v.visitas
		except:
			return 0
	n_visitas.allow_tags = True
	
	def get_total_valoraciones(self):
		n_total = self.rating_entrada.all().count()
		return n_total
	
	def get_valoraciones_positivas(self):
		n_positivas = self.rating_entrada.filter(a_favor=True).count()
		return n_positivas

	def get_media_valoraciones_positivas(self):
		qs_media = self.rating_entrada.filter(a_favor=True).aggregate(media=Avg('valor'))
		if qs_media['media']:
			media = Decimal(qs_media['media'])
			media = round(media,2)
		else:
			media = 0
		return media
	
	def get_valoraciones_negativas(self):
		n_negativas = self.rating_entrada.filter(a_favor=False).count()
		return n_negativas
	
	def get_media_valoraciones_negativas(self):
		qs_media = self.rating_entrada.filter(a_favor=False).aggregate(media=Avg('valor'))
		if qs_media['media']:
			media = Decimal(qs_media['media'])
			media = round(media,2)
		else:
			media = 0
		return media
	
	def get_n_comentarios(self):
		content_type = ContentType.objects.get_for_model(type(self))
		object_id = self.pk
		n_comentarios = Comentario.objects.filter(content_type=content_type,object_id=object_id,activo=True).count()
		return n_comentarios

	@permalink
	def get_absolute_url(self):
		idioma = self.idiomas_entrada.all().order_by('-idioma_default')[0]
		return ('ver-entrada', None, { 'id_entrada':self.pk, 'slug': idioma.slug })
			
	
	class Meta:
		ordering=['-creada']
		verbose_name = _(u"entrada")
		verbose_name_plural = _(u"entradas")
		
########################################################################################################################################

class Idiomas_entrada(models.Model):

	entrada = models.ForeignKey(Entrada, related_name='idiomas_entrada')
	idioma = models.CharField(_(u"Idioma"),max_length=80, choices=IDIOMAS)
	idioma_default = models.BooleanField(_(u"Idioma por defecto"), default=False)
	titulo = models.CharField(_(u"Titulo"),max_length=180)
	slug = models.SlugField(_('Slug'), max_length=190, db_index=True)
	intro = models.TextField(_(u"Introducción"),max_length=550,
		help_text=_(u"Breve resumen o introducción."))
	cuerpo = tinymce_models.HTMLField(_(u"Cuerpo"))
	tags = TaggableManager(_(u"Tags"), help_text=_(u"Etiqueta donde englobar la entrada. Sepáralo por espacios o comas. Para 2 palabras o más utiliza el guión medio. Ejemplo 'renta-basica'."), blank=True)
	busqueda = models.TextField(_(u"Búsqueda"), null=True, blank=True, editable=False)
	robots = models.CharField(max_length=32, choices=ROBOTS_CHOICES, default='index, follow', verbose_name=_(u'meta robots'),
		help_text=_(u'Por defecto \"index, follow\"'))
	meta_descripcion = models.CharField(max_length=150, blank=True, null=True, verbose_name=_(u'meta description'),
		help_text=_(u'Breve descripción. Relacionado con el texto. Máx. 150 car.'))
	palabras_clave  = models.CharField(max_length=150, blank=True, null=True, verbose_name=_(u'meta keyword'), 
		help_text=_(u'Palabras clave separadas por comas. Relacionado con el texto. Máx. 150 car.'))
	creado = models.DateTimeField(_(u"Creado"),auto_now_add=True)
	modificado = models.DateTimeField(_(u"Modificado"),auto_now=True)

	def __unicode__(self):
		return unicode(self.titulo)
		
	def get_tags(self):
		return self.tags.all() 
	
	@permalink
	def get_absolute_url(self):
		return ('ver-entrada', None, { 'id_entrada':self.entrada.pk, 'slug': self.slug })


	def save(self, *args, **kwargs):
		super(Idiomas_entrada, self).save(*args, **kwargs)
		if self.pk:
			"""Guarda en el campo indexado 'busqueda' los valores más importantes de la página.
			Tengo que hacer aquí esto proque si llamo al metodo tags_ se graba en la bbdd como bound method..."""

			cadena = '%s %s %s' % (self.titulo, self.intro, self.cuerpo)
			self.busqueda = unicode(cadena)
			super(Idiomas_entrada, self).save(*args, **kwargs)
			
	class Meta:
		ordering = ['-idioma_default']
		verbose_name = _(u"idioma de la entrada")
		verbose_name_plural = _(u"idiomas")
		unique_together = ("idioma", "entrada")
			
########################################################################################################################################

class Fotos_entrada(models.Model):
	
	entrada = models.ForeignKey(Entrada, related_name='fotos_entrada')
	foto = ImageField(_(u'Foto'), upload_to=ruta_foto_entrada, blank=True, null=True,
		help_text=_(u"Campo para subir fotografias que se mostarán en la entrada."))

	creada = models.DateTimeField(_(u"Creada"),auto_now_add=True)
	creada_por = models.ForeignKey(User, related_name='autor_add_fotos_entreda',editable=False,blank=True,null=True)
	modificada = models.DateTimeField(_(u"Modificada"),auto_now=True)
	modificada_por = models.ForeignKey(User, related_name='autor_mod_fotos_entrada',editable=False,blank=True,null=True)
	
	def __unicode__(self):
		return unicode(self.foto)
		
	class Meta:
		verbose_name = _(u'foto de la entrada')
		verbose_name_plural = _(u'fotos de la entrada')

		
########################################################################################################################################

class Visitas_entrada(models.Model):

	entrada = models.ForeignKey(Entrada, related_name='visita_entrada')
	visitas = models.IntegerField(_(u"Visitas"), default=0)
	creado = models.DateTimeField(_(u"Creado"),auto_now_add=True)
	modificado = models.DateTimeField(_(u"Modificado"),auto_now=True)

	def __unicode__(self):
		return unicode(self.entrada)
		
	class Meta:
		verbose_name = _(u'visita de la entrada')
		verbose_name_plural = _(u'visitas de las entrada')
		
########################################################################################################################################

class Rating_entrada(models.Model):

	usuario = models.ForeignKey(User, related_name='usu_rating_entrada')
	entrada = models.ForeignKey(Entrada, related_name='rating_entrada')
	a_favor = models.BooleanField(_(u"A favor"), default=False, help_text=_(u"Indicar si estás a favor o en contra"))
	valor = models.IntegerField(_(u"Valor"), default=0)
	creado = models.DateTimeField(_(u"Creado"),auto_now_add=True)
	creado_por = models.ForeignKey(User, related_name='autor_add_rating_entrada',blank=True,null=True)
	modificado = models.DateTimeField(_(u"Modificado"),auto_now=True,blank=True,null=True)
	modificado_por = models.ForeignKey(User, related_name='autor_mod_rating_entrada',blank=True,null=True)

	def __unicode__(self):
		return unicode(self.entrada)
		
	class Meta:
		verbose_name = _(u'rating de la entrada')
		verbose_name_plural = _(u'ratings de entradas')
			
########################################################################################################################################

class Pagina(MPTTModel):

	usuario = models.ForeignKey(User, related_name='usu_pagina',editable=False)
	grupo = models.ManyToManyField(Grupo, related_name='grupo_pagina', null=True, blank=True)
	superadmin = models.BooleanField(_(u"Superadmin"), default=False)
	parent = TreeForeignKey('self', verbose_name=_(u'Padre'), null=True, blank=True, related_name='children')
	tipo = models.CharField(_(u"Tipo"),max_length=120, choices=TIPO_PAGINA,default='p_grupo')
	visibilidad = models.CharField(_(u"Visibilidad"),max_length=120, choices=VISIBILIDAD_PAGINA,
		help_text=_(u"Si será pública para cualquier usuario registrado o sólo para los miembros de mis grupos."))
	estado = models.CharField(_(u"Estado"),max_length=80, choices=ESTADO_PAGINA)
	en_menu = models.BooleanField(_(u"En el menú"), default=True,
		help_text=_(u"Si será una página aislada que no aparezca en el menú o no."))
	comentarios = models.BooleanField(_(u"Comentarios"), default=False,help_text=_(u"Si los permite o no."))
	creada = models.DateTimeField(_(u"Creada"),auto_now_add=True)
	creada_por = models.ForeignKey(User, related_name='autor_add_pagina',editable=False,blank=True,null=True)
	modificada = models.DateTimeField(_(u"Modificada"),auto_now=True)
	modificada_por = models.ForeignKey(User, related_name='autor_mod_pagina',editable=False,blank=True,null=True)
	

	def __unicode__(self):
		idioma = self.idiomas_pagina.all().order_by('-idioma_default')[0]
		return unicode(idioma.titulo)
	
	def _titulo(self):
		idioma = self.idiomas_pagina.all().order_by('-idioma_default')[0]
		return unicode(idioma.titulo)
	_titulo.allow_tags = True
	
	def grupos(self):
		lst = [x['simbolo'] for x in self.grupo.values()]
		return unicode(join(lst, ', '))
	grupos.allow_tags = True
	
	def idiomas(self):
		lst = [x['idioma'] for x in self.idiomas_pagina.values()]
		return unicode(join(lst, ' | '))
	idiomas.allow_tags = True
	
	def idiomas_disponibles(self):
		idiomas = self.idiomas_pagina.all()
		return idiomas
		
	def n_visitas(self):
		try:
			v = self.visita_pagina.latest('modificado')
			return v.visitas
		except:
			return 0
	n_visitas.allow_tags = True
	
	@permalink
	def get_absolute_url(self):
		idioma = self.idiomas_pagina.all().order_by('-idioma_default')[0]
		return ('ver-pagina', None, { 'id_pagina':self.pk,'slug': idioma.slug })
	
	class Meta:
		order_with_respect_to = 'parent'
		verbose_name = _(u"pagina")
		verbose_name_plural = _(u"paginas")
		
	class MPTTMeta:
		order_insertion_by = []
		
########################################################################################################################################

class Idiomas_pagina(models.Model):

	pagina = models.ForeignKey(Pagina, related_name='idiomas_pagina')
	idioma = models.CharField(_(u"Idioma"),max_length=80, choices=IDIOMAS)
	idioma_default = models.BooleanField(_(u"Idioma por defecto"), default=False, help_text=_(u"Marcar para hacerlo idioma por defecto"))
	titulo = models.CharField(_(u"Título"),max_length=180)
	slug = models.SlugField(_('Slug'), max_length=120)
	cuerpo = tinymce_models.HTMLField(_(u"Cuerpo"))
	#tags = TaggableManager(_(u"Tags"), help_text=_(u"Etiqueta donde englobar la página. Sepáralo por comas."), blank=True)
	busqueda = models.TextField(_(u"Búsqueda"), null=True, blank=True, editable=False)
	robots = models.CharField(max_length=32, choices=ROBOTS_CHOICES, default='index, follow', verbose_name=_(u'meta robots'),
		help_text=_(u'Por defecto \"index, follow\"'))
	meta_descripcion = models.CharField(max_length=150, blank=True, null=True, verbose_name=_(u'meta description'),
		help_text=_(u'Breve descripción. Relacionado con el texto. Máx. 150 car.'))
	palabras_clave  = models.CharField(max_length=150, blank=True, null=True, verbose_name=_(u'meta keyword'), 
		help_text=_(u'Palabras clave separadas por comas. Relacionado con el texto. Máx. 150 car.'))
	creado = models.DateTimeField(_(u"Creado"),auto_now_add=True)
	modificado = models.DateTimeField(_(u"Modificado"),auto_now=True)

	def __unicode__(self):
		return unicode(self.titulo)
		
	def get_tags(self):
		return self.tags.all() 
	
	@permalink
	def get_absolute_url(self):
		return ('ver-pagina', None, { 'id_pagina':self.pagina.pk,'slug': self.slug })
	
	#def get_categoria(self):
		#return unicode(self.nombre)

	def save(self, *args, **kwargs):
		super(Idiomas_pagina, self).save(*args, **kwargs)
		if self.pk:
			"""Guarda en el campo indexado 'busqueda' los valores más importantes de la página.
			Tengo que hacer aquí esto proque si llamo al metodo tags_ se graba en la bbdd como bound method..."""

			cadena = '%s %s' % (self.titulo, self.cuerpo)
			self.busqueda = unicode(cadena)
			super(Idiomas_pagina, self).save(*args, **kwargs)
			
	class Meta:
		ordering = ['-idioma_default']
		verbose_name = _(u"idioma de la página")
		verbose_name_plural = _(u"idiomas")
		unique_together = ("idioma", "pagina")
		
########################################################################################################################################

class Fotos_pagina(models.Model):
	
	pagina = models.ForeignKey(Pagina, related_name='fotos_pagina')
	foto = ImageField(_(u'Foto'), upload_to=ruta_foto_pagina, blank=True, null=True,
		help_text=_(u"Campo para subir fotografias que se mostarán en la página."))

	creada = models.DateTimeField(_(u"Creada"),auto_now_add=True)
	creada_por = models.ForeignKey(User, related_name='autor_add_fotos_pagina',editable=False,blank=True,null=True)
	modificada = models.DateTimeField(_(u"Modificada"),auto_now=True)
	modificada_por = models.ForeignKey(User, related_name='autor_mod_fotos_pagina',editable=False,blank=True,null=True)
	
	def __unicode__(self):
		return unicode(self.foto)
		
	class Meta:
		verbose_name = _(u'Fotos')
		verbose_name_plural = _(u'Fotos')

########################################################################################################################################

class Visitas_pagina(models.Model):

	pagina = models.ForeignKey(Pagina, related_name='visita_pagina')
	visitas = models.IntegerField(_(u"Visitas"), default=0)
	creado = models.DateTimeField(_(u"Creado"),auto_now_add=True)
	modificado = models.DateTimeField(_(u"Modificado"),auto_now=True)

	def __unicode__(self):
		return unicode(self.pagina)
		
	class Meta:
		verbose_name = _(u'visita de la pagina')
		verbose_name_plural = _(u'visitas de las paginas')
		

########################################################################################################################################

class Comentario(MPTTModel):
	
	"""Sirve tanto para páginas como para entradas"""

	perfil = models.ForeignKey(Perfil, related_name='perfil_comentario')
	grupo = models.ManyToManyField(Grupo, related_name='grupo_comentario')
	superadmin = models.BooleanField(_(u"Superadmin"), default=False)
	parent = models.ForeignKey('self', verbose_name=_(u'Comentario Padre'), null=True, blank=True, related_name='children')
	comentario = models.TextField(_(u"Comentario"))
	notificaciones = models.BooleanField(_(u"Notificaciones"), default=True,
		help_text=_(u"Recibir un email notificación cuando se publiquen nuevos comentarios en la entrada."))
	content_type = models.ForeignKey(ContentType)
	object_id   = models.PositiveIntegerField()
	content_object  = generic.GenericForeignKey('content_type', 'object_id')
	votos_positivos = models.IntegerField(_(u"Votos positivos"), default=0)
	votos_negativos = models.IntegerField(_(u"Votos negativos"), default=0)
	activo = models.BooleanField(_(u"Activo"), default=True)
	creado = models.DateTimeField(_(u"Creado"),auto_now_add=True)
	creado_por = models.ForeignKey(User, related_name='autor_add_comentario',editable=False,blank=True,null=True)
	modificado = models.DateTimeField(_(u"Modificado"),auto_now=True)
	modificado_por = models.ForeignKey(User, related_name='autor_mod_comentario',editable=False,blank=True,null=True)
	
	def grupos(self):
		lst = [x['simbolo'] for x in self.grupo.values()]
		return unicode(join(lst, ', '))
	grupos.allow_tags = True
	
	class MPTTMeta:
		order_insertion_by = []
		
	def __unicode__(self):
		return unicode(self.comentario)

	class Meta:
		ordering = ["-creado"]
		verbose_name = _(u'comentario')
		verbose_name_plural = _(u'comentarios')
		
########################################################################################################################################


class Opinion_comentario(models.Model):

	usuario = models.ForeignKey(User, related_name='usu_opinion_comentario')
	comentario = models.ForeignKey(Comentario, related_name='opinion_comentario')
	a_favor = models.BooleanField(_(u"A favor"), default=False, help_text=_(u"Indicar si estás a favor o en contra del comentario"))
	valor = models.IntegerField(_(u"Valor"), default=0)
	

	def __unicode__(self):
		return unicode(self.comentario)

	class Meta:
		verbose_name = _(u"opinion sobre un comentario")
		verbose_name_plural = _(u"opiniones sobre comentarios")
		
########################################################################################################################################

class Rating_comentarios(models.Model):

	usuario = models.ForeignKey(User, related_name='usu_rating_comentario')
	comentario = models.ForeignKey(Comentario, related_name='rating_comentario')
	valor = models.IntegerField(_(u"Valor"), default=0)

	def __unicode__(self):
		return unicode(self.usuario)
		
	class Meta:
		verbose_name = _(u'rating de comentario')
		verbose_name_plural = _(u'ratings de comentario')

########################################################################################################################################

class Banner(models.Model):

	usuario = models.ForeignKey(User, related_name='usu_banner',editable=False)
	grupo = models.ManyToManyField(Grupo, related_name='grupo_banner', null=True, blank=True)
	superadmin = models.BooleanField(_(u"Superadmin"), default=False)
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
	width = models.IntegerField(_(u"Ancho"),blank=True, null=True,editable=False)
	height = models.IntegerField(_(u"Alto"),blank=True, null=True,editable=False)
	activo = models.BooleanField(_(u"Activo"), default=True, help_text=_(u"Poner el banner en activo o inactivo."))
	creado = models.DateTimeField(_(u"Creada"),auto_now_add=True)
	creado_por = models.ForeignKey(User, related_name='autor_add_banner',editable=False,blank=True,null=True)
	modificado = models.DateTimeField(_(u"Modificada"),auto_now=True)
	modificado_por = models.ForeignKey(User, related_name='autor_mod_banner',editable=False,blank=True,null=True)

	def __unicode__(self):
		return unicode(self.banner)
	
	def grupos(self):
		lst = [x['simbolo'] for x in self.grupo.values()]
		return unicode(join(lst, ', '))
	grupos.allow_tags = True
	
	class Meta:
		ordering = ["orden"]
		verbose_name = _(u"banner")
		verbose_name_plural = _(u"banner")
		
	def save(self, *args, **kwargs):
		"""Save banner dimensions."""
		super(Banner, self).save(*args, **kwargs)
		im = PImage.open(os.path.join(MEDIA_ROOT, self.banner.name))
		self.width, self.height = im.size
		super(Banner, self).save(*args, ** kwargs)

	def dimensiones(self):
		"""Banner size."""
		return "%s x %s" % (self.width, self.height)
	dimensiones.allow_tags = True

########################################################################################################################################


		


