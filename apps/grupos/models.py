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
from usuarios.models import *
from utilidades.combox import *
from metatags.models import *
from sorl.thumbnail import ImageField
from tinymce import models as tinymce_models
from os.path import join as pjoin
from string import join


def ruta_foto_grupo(instance, filename):
	dir = "documentos/grupos/fotos/%s/%s" % (instance.simbolo, filename)
	return dir

def ruta_foto(instance, filename):
	dir = "documentos/grupos/fotos/%s/%s" % (instance.grupo.simbolo, filename)
	return dir
			
############################################################################################################################

class Grupo(models.Model):

	nombre = models.CharField(_(u"Nombre del grupo"), max_length=250, unique=True)
	simbolo = models.CharField(_(u"Símbolo del grupo"), max_length=4, unique=True, 
		help_text=_(u'Máximo 4 caracteres. Si va a importar del CES, es recomendable utilizar el mismo símbolo que allí.'))
	logo = ImageField(_(u"Logotipo del grupo"), upload_to=ruta_foto_grupo, help_text=_(u'Tamaño ideal es 300×170'))
	unidad_s = models.CharField(_(u'Nombre de la unidad'), max_length=65, help_text=_(u'Nombre de la unidad de intercambio en singular'))
	unidad_p = models.CharField(_(u'Nombre de la unidad en plural'), max_length=65, help_text=_(u'Nombre de la unidad en plural'))

	pais = models.CharField(_(u"Pais"), max_length=50, choices=PAISES,default=_(u'España'))
	provincia = models.CharField(_(u"Provincia"), max_length=80, choices=PROVINCIAS)
	poblacion = models.CharField(_(u"Población"),max_length=250)
	direccion = models.CharField(_(u"Dirección"), max_length=250, blank=True)
	codigo_postal = models.CharField(_(u"Código postal"),max_length=6, blank=True)
	telefono = models.BigIntegerField(_(u"Teléfono"),max_length=15)
	#movil = models.BigIntegerField(_(u"Móvil"),max_length=15,blank=True, null=True)
	email = models. EmailField(_(u"Email"),max_length=75)

	google_maps_center = models.CharField(_(u'Coordenadas'), max_length=255, blank=True, null=True,
		help_text=_(u'Centrar el mapa en estas coordenadas. Debe parecer similar a: 40.42186,-3.700333 (No implementado aún)'),)
	google_maps_zoom = models.IntegerField(_(u'Zoom'),	blank=True,default=5,)

	activo = models.BooleanField(_(u"Activo"), default=True,editable=False)
	creado = models.DateTimeField(_(u"Creado"),auto_now_add=True)
	creado_por = models.ForeignKey(User, related_name='autor_add_grupo',editable=False,blank=True,null=True)
	modificado = models.DateTimeField(_(u"Modificado"),auto_now=True)
	modificado_por = models.ForeignKey(User, related_name='autor_mod_grupo',editable=False,blank=True,null=True)

	def __unicode__(self):
		return unicode(self.simbolo)
	
	def idiomas(self):
		lst = [x['idioma'] for x in self.idiomas_grupo.values()]
		return unicode(join(lst, ' | '))
	idiomas.allow_tags = True

	class Meta:
		verbose_name = _(u"grupo")
		verbose_name_plural = _(u"grupos")
		

		
############################################################################################################################

class Config_grupo(models.Model):

	grupo = models.OneToOneField(Grupo, unique=True, related_name='config_grupo')
	
	equivalencia_unidad = models.DecimalField(_(u"Equivalencia"), default=1, max_digits=12, decimal_places=2, 
		help_text=_(u"Equivalencia con el euro. Un euro es igual a..."))
	equivalencia_hora = models.DecimalField(_(u"Equivalencia hora"), default=10, max_digits=12, decimal_places=2,
		help_text=_(u"A cuentas horas horas equivale la unidad."))
	impuestos_transaccion = models.DecimalField(_(u"Impuestos por transacción"), default=0, max_digits=12, decimal_places=2, 
		help_text=_(u"Los impuestos van a parar a la administración del grupo expresados en porcentaje"))
	oxidacion = models.BooleanField(_(u"Aplicar oxidación"), default=True, 
		help_text=_(u'Habilita o no la oxidación en las cuentas. (No implementado aún)'))
	interes_negativo = models.DecimalField(_(u'Interés negativo'), default=2, max_digits=12, decimal_places=2,
		help_text=_(u'Tasa de interés que se aplica por retener la moneda (Tasa de oxidación) expresados en porcentaje. (No implementado aún)'))
	periodicidad_interes = models.IntegerField(_(u"Periodicidad del interés"),default=30, 
		help_text=_(u'Cada cuentos días se aplica la oxidación. (No implementado aún)'))
	comercio_intergrupos = models.BooleanField(_(u"Comercio intergrupos"), default=True, 
		help_text=_(u'Habilita o no el intercambio entre miembros de distintos grupos.'))
	impuestos_intergrupos = models.DecimalField(_(u"Impuestos intergrupos"), default=0, max_digits=12, decimal_places=2, 
		help_text=_(u"Los impuestos van a parar a la administración del grupo en caso de estar permitido el comercio intergrupo expresados en porcentaje"))
	tipo_alta = models.CharField(_(u"Tipo de alta"), max_length=180, choices=TIPO_ALTA,default=_(u'Online'),
		help_text=_(u'Permitir altas online en el grupo, revisandolo o no un administrador, o desabilitarlo para que sean presenciales.'))
	cuenta_x_miembro = models.BooleanField(_(u"Cuenta por miembro"), default=False, 
		help_text=_(u"""Por defecto a todos los usuarios nuevos en el sistema se les crea una cuenta en el grupo solicitado. 
					Pero si solicitan entrar en más de un grupo no se le crea otra cuenta en el nuevo grupo, obligando así al comercio intergrupos. 
					Marca esta casilla para habilitar la creación de cuentas en el grupo solicitado en el alta de cada nuevo usuario.
					De este modo el usuario tendrá al menos dos cuentas en distintos grupos, pero sus intercambios no se marcarán como Intergrupos."""))

	margen_superior_grupo = models.IntegerField(_(u"Margen superior del grupo"),default=3000, help_text=_(u"Margen superior para la cuenta Intergrupos"))
	margen_inferior_grupo = models.IntegerField(_(u"Margen inferior del grupo"),default=-3000, help_text=_(u"Margen inferior para la cuenta Intergrupos"))
	margen_grupo_dinamico = models.BooleanField(_(u"Margenes dinámicos de grupo"), default=True,
		help_text=_(u'El sistema aumenta los automáticamente los margenes del grupo en función de unas variables  (No implementado aún).'))
	margenes_usuarios_dinamicos = models.BooleanField(_(u"Margenes dinámicos de usuarios"), default=True,
		help_text=_(u'El sistema aumenta los automáticamente los margenesdel individuo en función de la confianza del grupo en él.  (No implementado aún)'))
	valorar_actividades = models.BooleanField(_(u"Valorar actividades"), default=True,
		help_text=_(u'Se habilita el sistema de valoración global de actividades.'))
	precio_palabra =  models.DecimalField(_(u'Precio por palabra'), default=0.0004, max_digits=8, decimal_places=6,
		help_text=_(u'Tasa que se aplica para el cálculo de las transacciones por valoración de actividades  (No implementado aún)'), editable=False)
	intercambios_publicos = models.BooleanField(_(u"Intercambios públicos"), default=True,
		help_text=_(u'Que los intercambios de la comunidad sean públicos por defecto.'))
	comercio_empresa_individuo = models.BooleanField(_(u"Comercio empresas individuo"), default=True,
		help_text=_(u'Permitir que las empresas puedan comerciar con servicios de usuarios o solo con bienes.  (No implementado aún)'), editable=False)
	equi_empresa_usu = models.DecimalField(_(u"Equivalencia empresa ususario"), default=1, max_digits=12, decimal_places=2, 
		help_text=_(u"Equivalencia entre la moneda social de una empresa de la comunidad y un usuario. O tasa de descuento.  (No implementado aún)"), editable=False)
	equi_empresa_usu_dinamico = models.BooleanField(_(u"Tabla de equivalencia dinámica"), default=True,
		help_text=_(u"Equivalencia entre empresas y usuarios calculada de forma dinámica.  (No implementado aún)"), editable=False)

	activo = models.BooleanField(_(u"Activo"), default=True, editable=False)
	creado = models.DateTimeField(_(u"Creado"),auto_now_add=True)
	creado_por = models.ForeignKey(User, related_name='autor_add_config_grupo',editable=False,blank=True,null=True)
	modificado = models.DateTimeField(_(u"Modificado"),auto_now=True)
	modificado_por = models.ForeignKey(User, related_name='autor_mod_config_grupo',editable=False,blank=True,null=True)

	def __unicode__(self):
		return unicode(self.grupo)

	class Meta:
		verbose_name = _(u"configuración del grupo")
		verbose_name_plural = _(u"configuración")
		
############################################################################################################################	

class Idiomas_grupo(models.Model):

	grupo = models.ForeignKey(Grupo, related_name='idiomas_grupo')
	idioma = models.CharField(_(u"Idioma"),max_length=80, choices=IDIOMAS)
	idioma_default = models.BooleanField(_(u"Idioma por defecto"), default=False, help_text=_(u"Tipo idioma por defecto del grupo"))
	eslogan = models.CharField(_(u"Eslogan"), max_length=255, blank=True, null=True, help_text=_(u'Mini texto de acompañamiento al nombre'))
	condiciones = tinymce_models.HTMLField(_(u"Condiciones de uso"), help_text=_(u"Texto que debe aceptar cada usuario que se quiera unir al grupo."))
	pie_pagina = tinymce_models.HTMLField(_(u"Pie de página"), help_text=_(u"Texto que aparecerá en el pie de página del grupo."))
	texto_email = tinymce_models.HTMLField(_(u"Texto del email de bienvenida"), 
		help_text=_(u"Texto que recibirá cada nuevo usuario registrado en su email.  (No implementado aún)"))
	robots = models.CharField(max_length=32, choices=ROBOTS_CHOICES, default='index, follow', verbose_name=_(u'meta robots'),
		help_text=_(u'Por defecto \"index, follow\"'))
	meta_descripcion = models.CharField(max_length=150, blank=True, null=True, verbose_name=_(u'meta description'),
		help_text=_(u'Breve descripción. Relacionado con el texto. Máx. 150 car.'))
	palabras_clave  = models.CharField(max_length=150, blank=True, null=True, verbose_name=_(u'meta keyword'), 
		help_text=_(u'Palabras clave separadas por comas. Relacionado con el texto. Máx. 150 car.'))
	creado = models.DateTimeField(_(u"Creado"),auto_now_add=True)
	creado_por = models.ForeignKey(User, related_name='autor_add_idioma_grupo',editable=False,blank=True,null=True)
	modificado = models.DateTimeField(_(u"Modificado"),auto_now=True)
	modificado_por = models.ForeignKey(User, related_name='autor_mod_idioma_grupo',editable=False,blank=True,null=True)

	def __unicode__(self):
		return unicode(self.idioma)
			
	class Meta:
		ordering = ['-idioma_default']
		verbose_name = _(u"idioma del grupo")
		verbose_name_plural = _(u"idiomas")
		unique_together = ("idioma", "grupo")
		

############################################################################################################################	

class Social_grupo(models.Model):

	grupo = models.ForeignKey(Grupo, related_name='social_grupo')
	nombre = models.CharField(_(u"Nombre"), max_length=250, help_text=_(u"Ejemplo: perfil en twitter, facebook, meneame, flickr, lift, quora, otra web, weblogs, etc..."))
	referencia = models.CharField(_(u"Referencia"), max_length=350, help_text=_(u"Url en twitter, facebook, meneame, flickr, lift, quora, otra web, weblogs, etc..."))
	creado = models.DateTimeField(_(u"Creado"),auto_now_add=True)
	creado_por = models.ForeignKey(User, related_name='autor_add_social_grupo',editable=False,blank=True,null=True)
	modificado = models.DateTimeField(_(u"Modificado"),auto_now=True)
	modificado_por = models.ForeignKey(User, related_name='autor_mod_social_grupo',editable=False,blank=True,null=True)

	def __unicode__(self):
		return unicode(self.nombre)
			
	class Meta:
		#ordering = ['-creado']
		verbose_name = _(u"dato social del grupo")
		verbose_name_plural = _(u"datos sociales")
		
############################################################################################################################

class Mas_fotos(models.Model):
	
	grupo = models.ForeignKey(Grupo, related_name='mas_fotos_grupo')
	foto = ImageField(_(u'Foto'), upload_to=ruta_foto, blank=True, null=True,
		help_text=_(u"Campo para subir más fotografias del grupo."))
	creado = models.DateTimeField(_(u"Creado"),auto_now_add=True)
	creado_por = models.ForeignKey(User, related_name='autor_add_fotos_grupo',editable=False,blank=True,null=True)
	modificado = models.DateTimeField(_(u"Modificado"),auto_now=True)
	modificado_por = models.ForeignKey(User, related_name='autor_mod_fotos_grupo',editable=False,blank=True,null=True)	

		
	class Meta:
		verbose_name = _(u'foto del grupo')
		verbose_name_plural = _(u'fotos del grupo')
		
############################################################################################################################	

class Margenes(models.Model):

	config_grupo = models.ForeignKey(Config_grupo, related_name='margenes_grupo')
	nombre = models.CharField(_(u"Nombre"), max_length=250, help_text=_(u"Descripción breve de los margenes. Ej: 100/-100, 300/-200, etc..."))
	superior = models.IntegerField(_(u"Margen superior"),default=100, help_text=_(u"Límite superior de acumulación de moneda"))
	inferior = models.IntegerField(_(u"Margen inferior"),default=-100, help_text=_(u"Límite inferior de endeudamiento."))

	default = models.BooleanField(_(u"Por defecto"), default=False, help_text=_(u"Tipo de margen aplicado por defecto a todos los miembros del grupo"))
	creado = models.DateTimeField(_(u"Creado"),auto_now_add=True)
	creado_por = models.ForeignKey(User, related_name='autor_add_margenes',editable=False,blank=True,null=True)
	modificado = models.DateTimeField(_(u"Modificado"),auto_now=True)
	modificado_por = models.ForeignKey(User, related_name='autor_mod_margenes',editable=False,blank=True,null=True)

	def __unicode__(self):
		return unicode(self.nombre)
			
	class Meta:
		ordering = ['-default','nombre']
		verbose_name = _(u"margen de usuario")
		verbose_name_plural = _(u"margenes de usuarios")
		

############################################################################################################################

class Contador(models.Model):
	#Para mantener la nomemclarura del CES
	grupo = models.ForeignKey(Grupo, unique=True,related_name='grupo_contador')
	numero = models.IntegerField(_(u"Número"),default=0, help_text=_(u"Último número de usuario registrado en el grupo"))
	creado = models.DateTimeField(auto_now_add=True)
	modificado = models.DateTimeField(auto_now=True)
	
############################################################################################################################

class Miembro(models.Model):

	"""Miembros de un grupo en distintos niveles""" 

	grupo = models.ForeignKey(Grupo, related_name='grupo_miembro')
	usuario = models.ForeignKey(User, related_name='usuario_miembro')
	clave = models.CharField(_(u"Clave de usuario"),max_length=25, editable=False, help_text=_(u"Clave de usuario en este grupo"))
	nivel = models.CharField(_(u"Nivel"),max_length=80, choices=GRADO, default=_(u'Usuario'))
	activo = models.BooleanField(_(u"Activo"), default=True)
	pendiente = models.BooleanField(_(u"Pendiente"), default=True)
	creado = models.DateTimeField(auto_now_add=True)
	creado_por = models.ForeignKey(User, related_name='autor_add_miembro',editable=False,blank=True,null=True)
	modificado = models.DateTimeField(auto_now=True)
	modificado_por = models.ForeignKey(User, related_name='autor_mod_miembro',editable=False,blank=True,null=True)

	def __unicode__(self):
		return unicode(self.usuario)

	def nombre_completo(self):
		return unicode(self.usuario.first_name + ' ' + self.usuario.last_name)
		
	def email(self):
		return unicode(self.usuario.email)

	def fotos(self):
		a = Perfil.object.get(usuario=self.usuario)
		dato = a.fotos_personales.all()
		cadena = ''
		if dato:
			for item in dato:
				cadena = cadena + """<img alt="%s" title="%s" src="%s" widht="50px" height="50px"/> | """  % ((item.foto.name, item.foto, item.foto.url_315x450 ))
	
		return cadena
	fotos.allow_tags = True

	class Meta:
		ordering = ['-creado']
		verbose_name = _(u'miembro al grupo')
		verbose_name_plural = _(u'miembros')
		unique_together = (("grupo", "usuario"),("grupo", "clave"))
		
		
############################################################################################################################

class Incidencias_grupo(models.Model):

	"""Incidencias que se pueden abrir a un grupo"""
	grupo = models.ForeignKey(Grupo, related_name='incidencias_del_grupo')
	usuario_incidencia = models.ForeignKey(User)
	incidencia = models.TextField(_(u"Incidencia"),blank=True, help_text=_(u"Incidencia del usuario."))

	creado = models.DateTimeField(auto_now_add=True)
	creado_por = models.ForeignKey(User, related_name='autor_add_incidencias_grupo',editable=False,blank=True,null=True)
	modificado = models.DateTimeField(auto_now=True)
	modificado_por = models.ForeignKey(User, related_name='autor_mod_incidencias_grupo',editable=False,blank=True,null=True)

	def __unicode__(self):
		return unicode(self.creado)

	class Meta:
		ordering = ['-creado']
		verbose_name = _(u'incidencias de grupo')
		verbose_name_plural = _(u'incidencias de grupo')
		
############################################################################################################################

class Visitas_grupo(models.Model):

	grupo = models.ForeignKey(Grupo, related_name='visita_grupo')
	usuario = models.ForeignKey(User, related_name='usu_visitante_grupo')
	creado = models.DateTimeField(_(u"Creado"),auto_now_add=True)

	def __unicode__(self):
		return unicode(self.usuario)
		
	class Meta:
		verbose_name = _(u'visita al usuario')
		verbose_name_plural = _(u'visitas al usuario')


		
		
