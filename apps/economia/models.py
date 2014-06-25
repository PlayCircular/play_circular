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
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.template.defaultfilters import slugify
from datetime import datetime, date, time
from usuarios.models import *
from actividades.models import *
from grupos.models import *
from utilidades.combox import *
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db.models import Sum,Count


###################################################################################################

class Cuenta(models.Model):
	"""
	Cuenta de cada usuario por grupo al que pertenece. La cuenta se formará así: user-n$simbolo-grupo.
	"""
	grupo = models.ForeignKey(Grupo, related_name='grupo_cuenta')
	titulares = models.ManyToManyField(User, related_name='titulares_cuenta')
	tipo = models.CharField(_(u"Tipo de cuenta"),max_length=120, blank=True, null=True, choices=TIPOS_CUENTA)
	cuenta = models.CharField(_(u"Cuenta"),unique=True, max_length=225)
	margen = models.ForeignKey(Margenes, related_name='margen_cuenta',blank=True, null=True)
	alias = models.CharField(_(u"Alias"),max_length=120, blank=True, null=True,
		help_text=_(u"Escribe un alias para identificarla mejor."))
	activo = models.BooleanField(_(u"Activo"), default=True)
	creado = models.DateTimeField(_(u"Creado"),auto_now_add=True)
	creado_por = models.ForeignKey(User, related_name='autor_add_cuenta',editable=False,blank=True,null=True)
	modificado = models.DateTimeField(_(u"Modificado"),auto_now=True)
	modificado_por = models.ForeignKey(User, related_name='autor_mod_cuenta',editable=False,blank=True,null=True)

	def __unicode__(self):
		return self.cuenta
	
	def saldo(self):
		titulares = self.titulares.all()
		un_titular = titulares[0]
		intercambio_qs = Intercambio.objects.filter(Q(usuarios=un_titular) & (Q(cuenta_origen=self) | Q(cuenta_destino=self)))
		intercambio_qs = intercambio_qs.aggregate(cantidad=Sum('cantidad'))
		saldo = intercambio_qs['cantidad']
		return unicode(saldo)
	saldo.allow_tags = True
	
	def operaciones(self):
		titulares = self.titulares.all()
		un_titular = titulares[0]
		intercambio_qs = Intercambio.objects.filter(Q(usuarios=un_titular) & (Q(cuenta_origen=self) | Q(cuenta_destino=self)))
		intercambio_qs = intercambio_qs.values('n_intercambio').order_by('n_intercambio').distinct().count()
		operaciones = intercambio_qs
		return unicode(operaciones)
	operaciones.allow_tags = True
	
	def ultimo_intercambio(self):
		titulares = self.titulares.all()
		un_titular = titulares[0]
		try:
			ultimo_intercambio = Intercambio.objects.filter(usuarios=un_titular).latest('creado')
		except Intercambio.DoesNotExist:
			ultimo_intercambio = None
		return unicode(ultimo_intercambio)
	ultimo_intercambio.allow_tags = True
	
	def titular(self):
		titulares = []
		for titular in self.titulares.all():
			titulares.append(titular.username)
		return unicode(join(titulares, ', '))
	titular.allow_tags = True
	
	def incidencias(self):
		n_incidencias = self.incidencia_cuenta.count()
		return unicode(n_incidencias)
	incidencias.allow_tags = True
	
	class Meta:
		ordering = ["-creado"]
		verbose_name = _(u"cuenta")
		verbose_name_plural = _(u"cuentas")
		
#############################################################################################################################

class Incidencia_Cuenta(models.Model):

	cuenta = models.ForeignKey(Cuenta, related_name='incidencia_cuenta',editable=False)
	nombre = models.CharField(_(u"Nombre"), max_length=250)
	descripcion = models.TextField()
	activo = models.BooleanField(_(u"Activo"), default=True)
	editable = models.BooleanField(_(u"Editable"), default=True,editable=False)
	creado = models.DateTimeField(_(u"Creado"),auto_now_add=True)
	creado_por = models.ForeignKey(User, related_name='autor_add_incidencia_cuenta',editable=False,blank=True,null=True)
	modificado = models.DateTimeField(_(u"Modificado"),auto_now=True)
	modificado_por = models.ForeignKey(User, related_name='autor_mod_incidencia_cuenta',editable=False,blank=True,null=True)

	class Meta:
		ordering = ["creado"]
		verbose_name = _(u'incidencia de cuenta')
		verbose_name_plural = _(u'incidencia de cuenta')

###################################################################################################
       
class Intercambio(models.Model):

	usuarios = models.ManyToManyField(User, related_name='usus_intercambio',editable=False)
	origen = models.ForeignKey(User, related_name='usu_origen')
	cuenta_origen = models.ForeignKey(Cuenta, related_name='cuenta_origen', help_text=_(u"Cuenta desde la que se pagará."))
	grupo_origen = models.ForeignKey(Grupo, related_name='grupo_origen')
	grupo_destino = models.ForeignKey(Grupo, related_name='grupo_destino')
	destino = models.ForeignKey(User, related_name='usu_destino')
	cuenta_destino = models.ForeignKey(Cuenta, related_name='cuenta_destino', help_text=_(u"Cuenta a la que llegará el pago."))
	actividad = models.ForeignKey(Actividad, related_name='actividad_asociada', blank=True, null=True)
	concepto = models.CharField(_(u"Concepto del intercambio"),max_length=120)
	cantidad = models.DecimalField(_(u"Cantidad"), max_digits=15, decimal_places=2, blank=False, null=False,
		help_text=_(u"Cantidad de horas o monedas que se intercambia."))
	descripcion = models.TextField(_(u"Descripción"),blank=True, null=True, help_text=_(u"Descripción de la operación."))
	publico = models.BooleanField(_(u"Público"), default=False, help_text=_(u"Si quieres que este intercambio sea público."))
	estado = models.CharField(_(u"Estado"),max_length=120, choices=ESTADO, default=u'Concluído')
	tipo = models.CharField(_(u"Tipo"),max_length=120, choices=TIPO_INTERCAMBIO, default=_(u'Normal'))
	n_intercambio = models.PositiveIntegerField(_(u"Op"), editable=False, blank=True, null=True, 
		help_text=_(u"Número de operación"))
	creado = models.DateTimeField(_(u"Creado"),auto_now_add=True)
	creado_por = models.ForeignKey(User, related_name='autor_add_intercambio',editable=False,blank=True,null=True)
	modificado = models.DateTimeField(_(u"Modificado"),auto_now=True)
	modificado_por = models.ForeignKey(User, related_name='autor_mod_intercambio',editable=False,blank=True,null=True)
	content_type = models.ForeignKey(ContentType, editable=False, null=True)
	object_id = models.PositiveIntegerField(editable=False, null=True)
	content_object  = generic.GenericForeignKey('content_type', 'object_id')

	def __unicode__(self):
		return unicode(self.concepto)
		
	def modelo(self):
		modelo = self.content_type.name
		return unicode(modelo)
	modelo.allow_tags = True

	class Meta:
		ordering = ["-creado"]
		verbose_name = _(u"intercambio")
		verbose_name_plural = _(u"intercambios")
		
#############################################################################################################################

class Incidencia_Intercambio(models.Model):

	intercambio = models.ForeignKey(Intercambio, related_name='incidencia_intercambio',editable=False)
	nombre = models.CharField(_(u"Nombre"), max_length=250)
	descripcion = models.TextField()
	activo = models.BooleanField(_(u"Activo"), default=True)
	editable = models.BooleanField(_(u"Editable"), default=True,editable=False)
	creado = models.DateTimeField(_(u"Creado"),auto_now_add=True)
	creado_por = models.ForeignKey(User, related_name='autor_add_incidencia_intercambio',editable=False,blank=True,null=True)
	modificado = models.DateTimeField(_(u"Modificado"),auto_now=True)
	modificado_por = models.ForeignKey(User, related_name='autor_mod_incidencia_intercambio',editable=False,blank=True,null=True)

	class Meta:
		ordering = ["creado"]
		verbose_name = _(u'incidencia de intercambio')
		verbose_name_plural = _(u'incidencia de intercambio')
		
###################################################################################################

