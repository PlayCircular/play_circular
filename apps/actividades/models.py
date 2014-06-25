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
import os
from os.path import join as pjoin
from string import join

from grupos.models import *
from usuarios.models import *
from utilidades.combox import *
from sorl.thumbnail import ImageField
from taggit.managers import TaggableManager
from django.utils.text import slugify
from django.db.models import permalink
from tinymce import models as tinymce_models


############################################################################################################################

def ruta_actividad(instance, filename):
	dir = "documentos/fotos_usuarios/%s/actividad/%s" % (instance.actividad.perfil, filename)
	return dir
############################################################################################################################	

class Categoria(models.Model):
	
	usuario = models.ForeignKey(User, related_name='usu_categoria',editable=False)
	grupo = models.ManyToManyField(Grupo, related_name='grupo_categoria_actividad', null=True, blank=True)
	superadmin = models.BooleanField(_(u"Superadmin"), default=False)
	creado = models.DateTimeField(_(u"Creado"),auto_now_add=True)
	creado_por = models.ForeignKey(User, related_name='autor_add_categoria_actividad',editable=False,blank=True,null=True)
	modificado = models.DateTimeField(_(u"Modificado"),auto_now=True)
	modificado_por = models.ForeignKey(User, related_name='autor_mod_categoria_actividad',editable=False,blank=True,null=True)
	
	def __unicode__(self):
		idioma = self.idioma_categoria.all().order_by('-idioma_default')[0]
		return unicode(idioma.nombre) 
	
	def nombre_de_categoria(self):
		idioma = self.idioma_categoria.all().order_by('-idioma_default')[0]
		return unicode(idioma.nombre)
	nombre_de_categoria.allow_tags = True
	
	def idiomas(self):
		lst = [x['idioma'] for x in self.idioma_categoria.values()]
		return unicode(join(lst, '| '))
	idiomas.allow_tags = True
	
	def grupos(self):
		lst = [x['simbolo'] for x in self.grupo.values()]
		return unicode(join(lst, ', '))
	grupos.allow_tags = True
	
	class Meta:
		verbose_name = _(u"categoria")
		verbose_name_plural = _(u"categorias")
	
############################################################################################################################	

class Idiomas_categoria(models.Model):
	
	categoria = models.ForeignKey(Categoria, related_name='idioma_categoria')
	idioma = models.CharField(_(u"Idioma"),max_length=80, choices=IDIOMAS, help_text=_(u'Idioma para esta categoria.'))
	idioma_default = models.BooleanField(_(u"Idioma por defecto"), default=False, help_text=_(u"Tipo de idioma por defecto de la categoria"))
	nombre = models.CharField(_(u"Nombre"),max_length=120, db_index=True, help_text=_(u"Nombre de la categoria."))
	slug = models.SlugField(_('Slug'), max_length=120)
	descripcion = models.TextField(_(u"Descripción"), null=True, blank=True,  help_text=_(u"Breve descripción de la categoria."))
		
	def __unicode__(self):
		return unicode(self.nombre)

	def get_categoria(self):
		return unicode(self.nombre)
			
	class Meta:
		ordering = ['-idioma_default']
		verbose_name = _(u"idioma de categoria")
		verbose_name_plural = _(u"idiomas de categorias")
		unique_together = ("idioma", "categoria")
		
		
############################################################################################################################

class Actividad(models.Model):

	grupo = models.ManyToManyField(Grupo, related_name='grupo_actividad', null=True, blank=True)
	superadmin = models.BooleanField(_(u"Superadmin"), default=False)
	usuario = models.ForeignKey(User, related_name='usu_actividad')
	perfil = models.ForeignKey(Perfil, related_name='perfil_actividad',editable=False)
	clase = models.CharField(_(u"Clase"),choices=CLASE_ACTIVIDAD, max_length=25, help_text=_(u"Si ofreces un bien o un servicio."))
	tipo = models.CharField(_(u"Tipo"),choices=TIPO_ACTIVIDAD, max_length=25, help_text=_(u"Si lo ofreces o lo demandas."))
	categoria = models.ForeignKey(Categoria, related_name='categoria_actividad',blank=True,null=True,
		help_text=_(u"Se expresará en el idioma que corresponda o en el que haya por defecto."))
	precio_euros = models.DecimalField(_(u"Euros"),default=0, max_digits=15, decimal_places=2, blank=True, null=True,
		help_text=_(u"Cantidad que pides en euros."), editable=False)
	precio_moneda_social = models.DecimalField(_(u"Moneda social"),default=0, max_digits=15, decimal_places=2,
		help_text=_(u"Cantidad que pides en la moneda social de tu comunidad."))
	activo = models.BooleanField(_(u"Activo"), default=True, help_text=_(u"Poner el anuncio en activo o inactivo."))
	
	n_votaciones = models.IntegerField(_(u"Nº de votaciones"),default=0,editable=False)
	n_interes_particular = models.IntegerField(_(u"Nº de votos de interés particular"),default=0,editable=False)
	media_rating_para_mi_antes = models.DecimalField(_(u"Media de interés particular antes"),default=0, max_digits=15, decimal_places=2,editable=False)
	media_rating_para_mi_despues = models.DecimalField(_(u"Media de interés particular después"),default=0, max_digits=15, decimal_places=2,editable=False)
	n_interes_comunidad = models.IntegerField(_(u"Nº de votos de interés comunidad"),default=0,editable=False)
	media_rating_para_bien_comun = models.DecimalField(_(u"Media de interés comunitario"),default=0, max_digits=15, decimal_places=2,editable=False)
	
	creado = models.DateTimeField(_(u"Creado"),auto_now_add=True)
	creado_por = models.ForeignKey(User, related_name='autor_add_actividad',editable=False,blank=True,null=True)
	modificado = models.DateTimeField(_(u"Modificado"),auto_now=True)
	modificado_por = models.ForeignKey(User, related_name='autor_mod_actividad',editable=False,blank=True,null=True)

	
	def __unicode__(self):
		idioma = self.idiomas_actividad.all().order_by('-idioma_default')[0]
		return unicode(idioma.nombre_actividad) 
	
	def monedas(self):
		lst = [x['unidad_p'] for x in self.grupo.values()]
		return unicode(join(lst, ' | '))
	monedas.allow_tags = True
		
	def nombre_de_actividad(self):
		idioma = self.idiomas_actividad.all().order_by('-idioma_default')[0]
		return unicode(idioma.nombre_actividad)
	nombre_de_actividad.allow_tags = True
	
	def get_fotos_usu(self):
		return self.perfil.fotos_personales.all()
	
	def idiomas(self):
		lst = [x['idioma'] for x in self.idiomas_actividad.values()]
		return unicode(join(lst, ' | '))
	idiomas.allow_tags = True
	
	def idiomas_disponibles(self):
		idiomas = self.idiomas_actividad.all()
		return idiomas

	def grupos(self):
		lst = [x['simbolo'] for x in self.grupo.values()]
		return unicode(join(lst, ', '))
	grupos.allow_tags = True
	
	def n_visitas(self):
		try:
			v = self.visita_actividad.latest('modificado')
			return v.visitas
		except:
			return 0
	n_visitas.allow_tags = True
	
	def n_compras(self):
		numero = self.actividad_asociada.filter(tipo='Normal',estado=u'Concluído').values('n_intercambio').distinct().count()
		return numero
	n_compras.allow_tags = True
	
	@permalink
	def get_absolute_url(self):
		idioma = self.idiomas_actividad.all().order_by('-idioma_default')[0]
		slug = slugify(unicode('%s' % (idioma.nombre_actividad)))
		return ('ver-actividad', None, { 'clase':self.clase, 'tipo':self.tipo, 'id_objeto':self.pk, 'slug': slug })

	class Meta:
		verbose_name = _(u"actividad")
		verbose_name_plural = _(u"actividades")
		ordering = ['tipo', '-creado']


############################################################################################################################	


class Idiomas_actividad(models.Model):

	actividad = models.ForeignKey(Actividad, related_name='idiomas_actividad')
	idioma = models.CharField(_(u"Idioma"),max_length=80, choices=IDIOMAS, help_text=_(u'Idioma por defecto de la actividad.'))
	idioma_default = models.BooleanField(_(u"Idioma por defecto"), default=False, help_text=_(u"Tipo de idioma por defecto de la actividad"))
	nombre_actividad = models.CharField(_(u"Actividad"),max_length=190, help_text=_(u"Nombre de la actividad que ofreces o demandas."))
	intro = models.TextField(_(u"Introducción"),max_length=550,help_text=_(u"Breve resumen o introducción."))
	descripcion = tinymce_models.HTMLField(_(u"Descripción"),  help_text=_(u"Breve descripción de la actividad que ofreces o demandas."))
	tags = TaggableManager(_(u"Tags"), help_text=_(u"Etiqueta donde englobar la actividad. Sepáralo por espacios o comas. Para 2 palabras o más utiliza el guión medio. Ejemplo 'renta-basica'."), blank=True)
	robots = models.CharField(max_length=32, choices=ROBOTS_CHOICES, default='index, follow', verbose_name=_(u'meta robots'),
		help_text=_(u'Por defecto \"index, follow\"'))
	meta_descripcion = models.CharField(max_length=150, blank=True, null=True, verbose_name=_(u'meta description'),
		help_text=_(u'Breve descripción. Relacionado con el texto. Máx. 150 car.'))
	palabras_clave  = models.CharField(max_length=150, blank=True, null=True, verbose_name=_(u'meta keyword'), 
		help_text=_(u'Palabras clave separadas por comas. Relacionado con el texto. Máx. 150 car.'))
	creado = models.DateTimeField(_(u"Creado"),auto_now_add=True)
	busqueda = models.TextField(_(u"Búsqueda"), null=True, blank=True, editable=False)
	creado = models.DateTimeField(_(u"Creado"),auto_now_add=True)
	modificado = models.DateTimeField(_(u"Modificado"),auto_now=True)

	def __unicode__(self):
		return unicode(self.nombre_actividad)
	
	@permalink
	def get_absolute_url(self):
		slug = slugify(unicode('%s' % (self.nombre_actividad)))
		return ('ver-actividad', None, { 'clase':self.actividad.clase, 'tipo':self.actividad.tipo, 'id_objeto':self.actividad.pk, 'slug': slug })
		
	def get_tags(self):
		return self.tags.all()  


	def save(self, *args, **kwargs):
		super(Idiomas_actividad, self).save(*args, **kwargs)
		if self.pk:
			"""Guarda en el campo indexado 'busqueda' los valores más importantes de la actividad.
			Tengo que hacer aquí esto proque si llamo al metodo tags_ se graba en la bbdd como bound method...
			Guardo dos veces porque me da este error debido al campo tags:
			Idiomas_actividad objects need to have a primary key value before you can access their tags."""

			cadena = '%s %s %s' % (self.nombre_actividad, self.descripcion, self.intro)
			self.busqueda = unicode(cadena)
			super(Idiomas_actividad, self).save(*args, **kwargs)
			
	class Meta:
		ordering = ['-idioma_default']
		verbose_name = _(u"idioma de la actividad")
		verbose_name_plural = _(u"idiomas")
		unique_together = ("idioma", "actividad")
		

		
############################################################################################################################

class Fotos_actividad(models.Model):
	
	actividad = models.ForeignKey(Actividad, related_name='fotos_actividad')
	foto = ImageField(_(u'Foto'), upload_to=ruta_actividad, blank=True, null=True,
		help_text=_(u"Campo para subir fotografias explicativas de la actividad."))

	creado = models.DateTimeField(_(u"Creado"),auto_now_add=True)
	creado_por = models.ForeignKey(User, related_name='autor_add_fotos_actividad',editable=False,blank=True,null=True)
	modificado = models.DateTimeField(_(u"Modificado"),auto_now=True)
	modificado_por = models.ForeignKey(User, related_name='autor_mod_fotos_actividad',editable=False,blank=True,null=True)
		
	class Meta:
		verbose_name = _(u'foto de la actividad')
		verbose_name_plural = _(u'fotos de las actividades')

############################################################################################################################

class Incidencias_actividad(models.Model):

	actividad = models.ForeignKey(Actividad, related_name='incidencia_actividad')
	usuario_avisador = models.ForeignKey(User, related_name='usu_avisador')
	incidencia = models.TextField(_(u"Incidencia"),blank=True, help_text=_(u"Incidencia de la actividad."))
	abuso = models.BooleanField(_(u"Reportar abuso"), default=False, help_text=_(u"Marca esta casilla si ves algo abusivo en esta actividad."))
	no_respondida = models.BooleanField(_(u"Actividad no respondida"), default=False, help_text=_(u"Marca esta casilla si el usuario anunciante no responde a tu solicitud."))
	activo = models.BooleanField(_(u"Activo"), default=True, help_text=_(u"Poner la incidencia en activo o inactivo."))
	creado = models.DateTimeField(auto_now_add=True)
	creado_por = models.ForeignKey(User, related_name='autor_add_incidencias_actividad',editable=False,blank=True,null=True)
	modificado = models.DateTimeField(auto_now=True)
	modificado_por = models.ForeignKey(User, related_name='autor_mod_incidencias_actividad',editable=False,blank=True,null=True)
	
	def __unicode__(self):
		return unicode(self.creado)

	class Meta:
		ordering = ['-creado']
		verbose_name = _(u'incidencia de actividad')
		verbose_name_plural = _(u'incidencias de actividades')
		

############################################################################################################################


class Opinion_actividad(models.Model):

	usuario = models.ForeignKey(User, related_name='usu_opinion_actividad',editable=False)
	actividad = models.ForeignKey(Actividad, related_name='opinion_actividad',editable=False)
	me_gusta_para_mi = models.BooleanField(_(u"Me interesa para mi"), default=False, help_text=_(u"Indicar si la actividad te interesa o no."))
	rating_para_mi_antes = models.IntegerField(_(u"Opinión sin usar la actividad"),editable=False, default=0)
	rating_para_mi_despues = models.IntegerField(_(u"Valoración tras usar la actividad"),editable=False, default=0)
	bien_comun = models.BooleanField(_(u"Me interesa para el grupo"), default=False, help_text=_(u"Propuesta para el bien común."))
	rating_para_bien_comun = models.IntegerField(_(u"Opinión sin usar la actividad"),editable=False, default=0)
	comentario = models.TextField(_(u"Comentario"),max_length=400, blank=True, help_text=_(u"Puedes dejarle un comentario anónimo."))
	ya_opinado = models.BooleanField(_(u"Ya opinado"), default=True, help_text=_(u"Marcar como opinión realizada o no."))
	creado = models.DateTimeField(_(u"Creada"),auto_now_add=True)
	modificado = models.DateTimeField(_(u"Modificada"),auto_now=True)

	def __unicode__(self):
		return unicode(self.actividad)

	class Meta:
		verbose_name = _(u"opinion sobre una actividad")
		verbose_name_plural = _(u"opiniones sobre actividades")
		

############################################################################################################################

class Visitas_actividad(models.Model):

	actividad = models.ForeignKey(Actividad, related_name='visita_actividad')
	visitas = models.IntegerField(_(u"Visitas"), default=0)
	creado = models.DateTimeField(_(u"Creado"),auto_now_add=True)
	modificado = models.DateTimeField(_(u"Modificado"),auto_now=True)

	def __unicode__(self):
		return unicode(self.actividad)
		
	class Meta:
		verbose_name = _(u'visita de la actividad')
		verbose_name_plural = _(u'visitas de las actividades')
		

############################################################################################################################

class Historico_interes_actividad(models.Model):

	actividad = models.ForeignKey(Actividad, related_name='historico_interes_actividad')
	creado = models.DateTimeField(_(u"Creado"),auto_now_add=True)
	porcentaje_interes = models.IntegerField(_(u"Porcentaje de interés"),editable=False, default=0)

	def __unicode__(self):
		return unicode(self.porcentaje_interes)
		
	class Meta:
		verbose_name = _(u'historico de interés')
		verbose_name_plural = _(u'historicos de interés')
		
############################################################################################################################

class Historico_interes_actividades_grupo(models.Model):

	grupo = models.ForeignKey(Grupo, related_name='historico_interes_grupo')
	creado = models.DateTimeField(_(u"Creado"),auto_now_add=True)
	porcentaje_interes = models.IntegerField(_(u"Porcentaje de interés"),editable=False, default=0)

	def __unicode__(self):
		return unicode(self.porcentaje_interes)
		
	class Meta:
		verbose_name = _(u'historico de interés')
		verbose_name_plural = _(u'historicos de interés')

############################################################################################################################

		