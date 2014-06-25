#coding=utf-8

# Copyright (C) 2014 by Víctor Romero Blanco <info at playcircular dot com>.
# http://playcircular.com/
# It's licensed under the AFFERO GENERAL PUBLIC LICENSE unless stated otherwise.
# You can get copies of the licenses here: http://www.affero.org/oagpl.html
# AFFERO GENERAL PUBLIC LICENSE is also included in the file called "LICENSE".

from django.contrib import admin
from django.conf import settings
from settings import MEDIA_ROOT, STATIC_ROOT

from django.utils.translation import ugettext as _
#from django.core.mail import send_mail, send_mass_mail, BadHeaderError
from datetime import datetime, date, time

from usuarios.models import *
from grupos.models import *
from actividades.models import *
from actividades.forms import *

############################################################################################################################
class Fotos_Activiadad_Inline(admin.TabularInline):
	model = Fotos_actividad
	extra = 2
	max_num = 5
	verbose_name = _(u'foto del anuncio')
	
############################################################################################################################
class Idiomas_Categoria_Inline(admin.StackedInline):
	model = Idiomas_categoria
	formset = Idioma_requerido_formset
	extra = 1
	max_num = 5
	
	def get_extra(self, request, obj=None, **kwargs):
		extra = 1
		if obj:
			extra = 0
			return extra
		return extra
	verbose_name = _(u'idioma de categoria')
	verbose_name_plural = _(u'idiomas de categorias')

############################################################################################################################
				
class Categoria_Actividad_Admin(admin.ModelAdmin):
	list_display = ('nombre_de_categoria','grupos','idiomas','creado','creado_por','modificado','modificado_por')
	form = Form_categoria_actividad_admin
	inlines = [
		Idiomas_Categoria_Inline,
	]
	
	def get_form(self, request, obj=None, **kwargs):
		self.exclude = []
		if not request.user.is_superuser:
			self.exclude.append('superadmin')
		AdminForm = super(Categoria_Actividad_Admin, self).get_form(request, obj, **kwargs)
		class ModelFormMetaClass(AdminForm):
			def __new__(cls, *args, **kwargs):
				kwargs['request'] = request
				kwargs['user'] = request.user
				return AdminForm(*args, **kwargs)
		return ModelFormMetaClass

	def queryset(self, request):
		qs = super(Categoria_Actividad_Admin, self).queryset(request)
		"""Por si el admin todavía no tiene los datos personales"""
		
		#Si es superusuario lo ve todo
		if request.user.is_superuser:
			return qs
		else:
			# Si no es superusuario pero es administrador de grupo, ve todos los de su grupo.
			grupos_administrados = Miembro.objects.filter(usuario=request.user,nivel=u'Administrador').values_list('grupo', flat=True).order_by('grupo')
			if len(grupos_administrados) > 0:
				return qs.filter(grupo__in=grupos_administrados,superadmin=False)
			else:
				return qs.filter(usuario=request.user)
			
	def has_delete_permission(self, request, obj=None):
		if request.user.is_superuser:
			return True
		else:
			return False
			
	def save_model(self, request, obj, form, change):
		try:
			categoria = Categoria.objects.get(pk=obj.pk)
			pass
		except Categoria.DoesNotExist:
			obj.usuario = request.user
			obj.creado_por = request.user
			
		obj.modificado_por = request.user
		obj.save()
	
	
############################################################################################################################
class Idiomas_Inline(admin.StackedInline):
	model = Idiomas_actividad
	formset = Idioma_requerido_formset
	extra = 1
	max_num = 5
	
	def get_extra(self, request, obj=None, **kwargs):
		extra = 1
		if obj:
			extra = 0
			return extra
		return extra
	verbose_name = _(u'idiomas')

############################################################################################################################
				
class Actividad_Admin(admin.ModelAdmin):
	list_display = ('nombre_de_actividad','usuario','grupos','idiomas','clase','tipo','precio_moneda_social','activo','creado','creado_por','modificado','modificado_por')
	form = Form_actividad_admin

	inlines = [
		Idiomas_Inline,
		Fotos_Activiadad_Inline,
	]
	
	#Esto es para que funcione el Form_actividad_admin. 
	# Para que devuelva solo los usuarios que pertenecen al grupo administrado.
	def get_form(self, request, obj=None, **kwargs):
		self.exclude = []
		if not request.user.is_superuser:
			self.exclude.append('superadmin')
		AdminForm = super(Actividad_Admin, self).get_form(request, obj, **kwargs)
		class ModelFormMetaClass(AdminForm):
			def __new__(cls, *args, **kwargs):
				kwargs['request'] = request
				kwargs['user'] = request.user
				return AdminForm(*args, **kwargs)
		return ModelFormMetaClass
	
	def queryset(self, request):
		qs = super(Actividad_Admin, self).queryset(request)
		
		#Si es superusuario lo ve todo
		if request.user.is_superuser:
			return qs
		else:
			# Si no es superusuario pero es administrador de grupo, ve todos los de su grupo.
			grupos_administrados = Miembro.objects.filter(usuario=request.user,nivel=u'Administrador').values_list('grupo', flat=True).order_by('grupo')
			
			if len(grupos_administrados) > 0:
				#miembros_administrados = Miembro.objects.filter(grupo__in=grupos_administrados).values_list('usuario', flat=True).order_by('usuario')
				#return qs.filter(usuario__in=miembros_administrados,superadmin=False)
				return qs.filter(grupo__in=grupos_administrados,superadmin=False)
			else:
				#Y si no ve solo lo suyo
				return qs.filter(usuario=request.user)
		
		
	def has_add_permission(self, request):
		try:
			datos = Perfil.objects.get(usuario=request.user)
		except Perfil.DoesNotExist:
			datos = False

		if datos:
			return True
		else:
			mensaje = _(u"Para añadir actividades tienes que completar tus datos personales primero.")
			self.message_user(request, mensaje)
			return False

	def save_model(self, request, obj, form, change):
		try:
			actividad = Actividad.objects.get(pk=obj.pk)
			perfil = Perfil.objects.get(usuario=obj.usuario)
			obj.perfil = perfil
		except Actividad.DoesNotExist:
			perfil = Perfil.objects.get(usuario=obj.usuario)
			obj.perfil = perfil
			obj.creado_por = request.user
			
		obj.modificado_por = request.user
		obj.save()


############################################################################################################################
admin.site.register(Actividad,Actividad_Admin)
admin.site.register(Categoria,Categoria_Actividad_Admin)







