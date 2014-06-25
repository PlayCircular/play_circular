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
from economia.models import *
from economia.views import *
from economia.forms import *
from actividades.models import *
from grupos.models import *
from django.db.models import Q
from django.contrib.contenttypes import generic
from django.conf.urls import patterns, include, url
from django.contrib.auth.models import User

############################################################################################################################
class Incidecia_Cuenta_Inline(admin.TabularInline):
	model = Incidencia_Cuenta
	readonly_fields = ['editable',]
	extra = 1
	
	def has_add_permission(self, request, obj=None):
		if request.user.is_superuser:
			return True
		else:
			n_grupos_administrados = Miembro.objects.filter(usuario=request.user,nivel=u'Administrador').count()
			if n_grupos_administrados > 0:
				return True
			else:			
				return False
			

###################################################################################################
	
class Cuenta_Admin(admin.ModelAdmin):

	list_display = ('cuenta','titular','grupo','tipo','saldo','operaciones','margen','alias','activo','incidencias','creado','creado_por','modificado','modificado_por')
	readonly_fields = ['cuenta',]
	form = Form_Cuenta_Admin
	inlines = [Incidecia_Cuenta_Inline,]
	filter_horizontal = ['titulares',]
	list_filter = ('tipo','activo')
	search_fields = ['cuenta']
	change_form_template = 'admin/economia/cuenta/change_form.html'
		
	#Esto es para que funcione el Form_miembros. Para pasarle el request
	def get_form(self, request, obj=None, **kwargs):
		AdminForm = super(Cuenta_Admin, self).get_form(request, obj, **kwargs)
		class ModelFormMetaClass(AdminForm):
			def __new__(cls, *args, **kwargs):
				kwargs['request'] = request
				kwargs['user'] = request.user
				return AdminForm(*args, **kwargs)
		return ModelFormMetaClass
		
	def queryset(self, request):
		"""Pueden ver el grupo los usuarios que sean administradores o el superadministrador"""
		qs = super(Cuenta_Admin, self).queryset(request)
		#print u'que pasa'
		if request.user.is_superuser:
			return qs
		else:
			grupos_administrados = Miembro.objects.filter(usuario=request.user,nivel=u'Administrador').values_list('grupo', flat=True).order_by('grupo')
			#print u'hola'
			if len(grupos_administrados) > 0:
				qs_1 = qs.filter(grupo__in=grupos_administrados)
				return qs_1
			else:
				#qs_2 = Cuenta.objects.filter(usuario=request.user)
				return Cuenta.objects.filter(titulares=request.user)
			
	def has_add_permission(self, request, obj=None):
		if request.user.is_superuser:
			return True
		else:
			n_grupos_administrados = Miembro.objects.filter(usuario=request.user,nivel=u'Administrador').count()
			if n_grupos_administrados > 0:
				return True
			else:			
				return False
			
	def has_change_permission(self, request, obj=None):
		if request.user.is_superuser:
			return True
		else:
			n_grupos_administrados = Miembro.objects.filter(usuario=request.user,nivel=u'Administrador').count()
			if n_grupos_administrados > 0:
				return True
			else:			
				return False
			
	def has_delete_permission(self, request, obj=None):
		if request.user.is_superuser:
			return True
		else:
			n_grupos_administrados = Miembro.objects.filter(usuario=request.user,nivel=u'Administrador').count()
			if n_grupos_administrados > 0:
				return True
			else:			
				return False
		
	def get_actions(self, request):
		actions = super(Cuenta_Admin, self).get_actions(request)
		if request.user.is_superuser:
			return actions
		else:
			n_grupos_administrados = Miembro.objects.filter(usuario=request.user,nivel=u'Administrador').count()
			if n_grupos_administrados == 0:		
				if 'delete_selected' in actions:
					del actions['delete_selected']
				return actions
			else:
				return actions

		
	def save_model(self, request, obj, form, change):
		
		try:
			c = Cuenta.objects.get(pk=obj.pk)
			existe = True
		except Cuenta.DoesNotExist:
			#obj.usuario = request.user
			obj.creado_por = request.user
			existe = False
			#Siempre tiene que existir un contador porque se crea automaticamente al crear un grupo.
			contador = Contador.objects.filter(grupo=obj.grupo).latest('creado')
			
		obj.modificado_por = request.user
		
		if not existe:
			obj.cuenta = str(obj.grupo.simbolo) + str(contador.numero)
			contador.numero += 1
			contador.save()
			
		obj.save()
			

		

############################################################################################################################
class Incidecia_Intercambio_Inline(admin.TabularInline):
	model = Incidencia_Intercambio
	readonly_fields = ['editable',]
	extra = 1
	#max_num = 8
	#verbose_name = _(u'incidencia de intercambio')
	
	def has_add_permission(self, request, obj=None):
		if request.user.is_superuser:
			return True
		else:
			n_grupos_administrados = Miembro.objects.filter(usuario=request.user,nivel=u'Administrador').count()
			if n_grupos_administrados > 0:
				return True
			else:			
				return False
			
		 
###################################################################################################
	
class Intercambio_Admin(admin.ModelAdmin):

	list_display = ('origen',
					'destino',
					'n_intercambio',
					'cuenta_origen',
					'cuenta_destino',
					'grupo_origen',
					'grupo_destino',
					'cantidad',
					'concepto',
					'tipo',
					'publico','estado','creado','creado_por','modificado','modificado_por')

	list_editable = ['estado','publico']
	list_filter = ('tipo', 'estado','publico')
	search_fields = ['usuario__username']
	list_per_page = 40
	list_max_show_all = 80
	inlines = [Incidecia_Intercambio_Inline,]
	readonly_fields = ['estado','tipo']
	form = Form_Intercambio_Admin
	change_form_template = 'admin/economia/intercambio/change_form.html'
	
	#Esto es para que funcione el Form_Intercambio_Admin. Para pasarle el request
	def get_form(self, request, obj=None, **kwargs):
		AdminForm = super(Intercambio_Admin, self).get_form(request, obj, **kwargs)
		class ModelFormMetaClass(AdminForm):
			def __new__(cls, *args, **kwargs):
				kwargs['request'] = request
				kwargs['user'] = request.user
				return AdminForm(*args, **kwargs)
		return ModelFormMetaClass
	
	def queryset(self, request):
		qs = super(Intercambio_Admin, self).queryset(request)

		if request.user.is_superuser:
			return qs
		else:
			grupos_administrados = Miembro.objects.filter(usuario=request.user,nivel=u'Administrador').values_list('grupo', flat=True).order_by('grupo')
			if len(grupos_administrados) > 0:
				qs_1 = qs.filter(Q(grupo_origen__in=grupos_administrados) | Q(grupo_destino__in=grupos_administrados))
				return qs_1
			else:
				return qs.filter(usuarios=request.user)
			
	def has_add_permission(self, request, obj=None):
		if request.user.is_superuser:
			return True
		else:
			n_grupos_administrados = Miembro.objects.filter(usuario=request.user,nivel=u'Administrador').count()
			if n_grupos_administrados > 0:
				return True
			else:			
				return False
			
	def has_change_permission(self, request, obj=None):
		if request.user.is_superuser:
			return True
		else:
			n_grupos_administrados = Miembro.objects.filter(usuario=request.user,nivel=u'Administrador').count()
			if n_grupos_administrados > 0:
				return True
			else:			
				return False
			
	def has_delete_permission(self, request, obj=None):
		if request.user.is_superuser:
			return True
		else:
			n_grupos_administrados = Miembro.objects.filter(usuario=request.user,nivel=u'Administrador').count()
			if n_grupos_administrados > 0:
				return True
			else:			
				return False
		
	def get_actions(self, request):
		actions = super(Intercambio_Admin, self).get_actions(request)
		if request.user.is_superuser:
			return actions
		else:
			n_grupos_administrados = Miembro.objects.filter(usuario=request.user,nivel=u'Administrador').count()
			if n_grupos_administrados == 0:		
				if 'delete_selected' in actions:
					del actions['delete_selected']
				return actions
			else:
				return actions
		
	def save_model(self, request, obj, form, change):
		try:
			c = Intercambio.objects.get(pk=obj.pk)
			obj.save()
		except Intercambio.DoesNotExist:
			datos = logica_del_pago(request, form=form, confirmacion=True, admin=True)


###################################################################################################

admin.site.register(Cuenta,Cuenta_Admin)
admin.site.register(Intercambio,Intercambio_Admin)

