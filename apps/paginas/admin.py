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
from django.contrib.contenttypes import generic
from django.conf.urls import patterns, include, url
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from sorl.thumbnail import default
from sorl.thumbnail.admin import AdminImageMixin

from paginas.models import *
from paginas.forms import *
from mptt.admin import MPTTModelAdmin
# Si utilizo el DjangoMpttAdmin no funciona el def queryset
from django_mptt_admin.admin import DjangoMpttAdmin
from tinymce import models as tinymce_models
from tinymce.models import HTMLField
from django.db.models import Q
from django.db.utils import DatabaseError,IntegrityError

ADMIN_THUMBS_SIZE = '80x30'

############################################################################################################################
class Fotos_Entrada_Inline(admin.TabularInline):
	model = Fotos_entrada
	extra = 2
	max_num = 14
	verbose_name = _(u'foto')
############################################################################################################################
class Fotos_Pagina_Inline(admin.TabularInline):
	model = Fotos_pagina
	extra = 2
	max_num = 14
	verbose_name = _(u'foto')

############################################################################################################################

class MetatagInline(generic.GenericStackedInline):
	model = Metatag
	extra = 1
	max_num = 1
	verbose_name = "SEO"
	
############################################################################################################################
class Idiomas_Categoria_Entrada_Inline(admin.StackedInline):
	model = Idiomas_categoria_entrada
	formset = Idioma_requerido_formset
	prepopulated_fields = {"slug": ("nombre",)}
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
class Idiomas_Pagina_Inline(admin.StackedInline):
	model = Idiomas_pagina
	formset = Idioma_requerido_formset
	prepopulated_fields = {"slug": ("titulo",)}
	extra = 1
	max_num = 5
	
	def get_extra(self, request, obj=None, **kwargs):
		extra = 1
		if obj:
			extra = 0
			return extra
		return extra
	verbose_name = _(u'idioma de la pagina')
	verbose_name_plural = _(u'idiomas')
	
############################################################################################################################
class Idiomas_Entrada_Inline(admin.StackedInline):
	model = Idiomas_entrada
	formset = Idioma_requerido_formset
	prepopulated_fields = {"slug": ("titulo",)}
	extra = 1
	max_num = 5
	
	def get_extra(self, request, obj=None, **kwargs):
		extra = 1
		if obj:
			extra = 0
			return extra
		return extra
	verbose_name = _(u'idioma de la entrada')
	verbose_name_plural = _(u'idiomas')

############################################################################################################################
				
class Categoria_Entrada_Admin(admin.ModelAdmin):
	list_display = ('nombre_de_categoria','usuario','grupos','idiomas','creada','creada_por','modificada','modificada_por')
	search_fields = ['nombre']
	form = Form_Categoria_Entrada_Admin
	inlines = [
		Idiomas_Categoria_Entrada_Inline,
	]
	
	#Esto es para que funcione el Form_Categoria_Entrada_Admin. Para pasarle el request
	def get_form(self, request, obj=None, **kwargs):
		self.exclude = []
		if not request.user.is_superuser:
			self.exclude.append('superadmin')
		AdminForm = super(Categoria_Entrada_Admin, self).get_form(request, obj, **kwargs)
		class ModelFormMetaClass(AdminForm):
			def __new__(cls, *args, **kwargs):
				kwargs['request'] = request
				kwargs['user'] = request.user
				return AdminForm(*args, **kwargs)
		return ModelFormMetaClass

	def queryset(self, request):
		qs = super(Categoria_Entrada_Admin, self).queryset(request)
		#Si es superusuario lo ve todo
		if request.user.is_superuser:
			return qs
		else:
			# Si no es superusuario pero es administrador de grupo, ve todos los de su grupo.
			grupos_administrados = Miembro.objects.filter(usuario=request.user,nivel=u'Administrador').values_list('grupo', flat=True).order_by('grupo')
			
			if len(grupos_administrados) > 0:
				return qs.filter(grupo__in=grupos_administrados,superadmin=False)
			else:
				#Y si no ve solo lo suyo
				return qs.filter(usuario=request.user)
			
	def save_model(self, request, obj, form, change):
		
		try:
			c = Categoria_Entrada.objects.get(pk=obj.pk)
		except Categoria_Entrada.DoesNotExist:
			obj.usuario = request.user
			obj.creada_por = request.user
			
		obj.modificada_por = request.user	
		obj.save()
	
############################################################################################################################
				
class Entrada_Admin(admin.ModelAdmin):
	list_display = ('usuario','_titulo','tipo','grupos','idiomas','visibilidad','estado','comentarios','creada','creada_por','modificada','modificada_por')
	list_filter = ('visibilidad','estado')
	search_fields = ['usuario','Idiomas_entrada__titulo']
	filter_horizontal = ['categoria','entradas_relacionadas']
	form = Form_Entrada_Admin
	change_form_template = 'admin/paginas/entrada/change_form.html'

	inlines = [
		Idiomas_Entrada_Inline,
		Fotos_Entrada_Inline,
	]
	
	#Esto es para que funcione el Form_Entrada_Admin. Para pasarle el request
	def get_form(self, request, obj=None, **kwargs):
		self.exclude = []
		if not request.user.is_superuser:
			self.exclude.append('superadmin')
		AdminForm = super(Entrada_Admin, self).get_form(request, obj, **kwargs)
		class ModelFormMetaClass(AdminForm):
			def __new__(cls, *args, **kwargs):
				kwargs['request'] = request
				kwargs['user'] = request.user
				return AdminForm(*args, **kwargs)
		return ModelFormMetaClass


	def queryset(self, request):
		qs = super(Entrada_Admin, self).queryset(request)
	
		#Si es superusuario lo ve todo
		if request.user.is_superuser:
			return qs
		else:
			# Si no es superusuario pero es administrador de grupo, ve todos los de su grupo.
			grupos_administrados = Miembro.objects.filter(usuario=request.user,nivel=u'Administrador').values_list('grupo', flat=True).order_by('grupo')
			
			if len(grupos_administrados) > 0:
				return qs.filter(grupo__in=grupos_administrados,superadmin=False)
			else:
				#Y si no ve solo lo suyo
				return qs.filter(usuario=request.user)
			
	def save_model(self, request, obj, form, change):
		
		try:
			c = Entrada.objects.get(pk=obj.pk)
		except Entrada.DoesNotExist:
			#obj.usuario = request.user
			obj.creada_por = request.user
			
		obj.modificada_por = request.user
		obj.save()

############################################################################################################################

class Pagina_Admin(DjangoMpttAdmin):

	list_display = ('_titulo','parent','usuario','grupos','idiomas','tipo','visibilidad','en_menu','estado','comentarios','creada','creada_por','modificada','modificada_por')
	form = Form_Pagina_Admin
	change_form_template = 'admin/paginas/pagina/change_form.html'
	list_filter = ('tipo','estado')
	search_fields = ['usuario']


	inlines = [
		Idiomas_Pagina_Inline,
		Fotos_Pagina_Inline,
	]
	
	#Esto es para que funcione el Form_Pagina_Admin. Para pasarle el request
	def get_form(self, request, obj=None, **kwargs):
		self.exclude = []
		if not request.user.is_superuser:
			self.exclude.append('tipo')
			self.exclude.append('superadmin')
		AdminForm = super(Pagina_Admin, self).get_form(request, obj, **kwargs)
		class ModelFormMetaClass(AdminForm):
			def __new__(cls, *args, **kwargs):
				kwargs['request'] = request
				kwargs['user'] = request.user
				return AdminForm(*args, **kwargs)
		return ModelFormMetaClass

	def queryset(self, request):
		qs = super(Pagina_Admin, self).queryset(request)
	
		#Si es superusuario lo ve todo
		if request.user.is_superuser:
			return qs
		else:
			# Si no es superusuario pero es administrador de grupo, ve todos los de su grupo.
			grupos_administrados = Miembro.objects.filter(usuario=request.user,nivel=u'Administrador').values_list('grupo', flat=True).order_by('grupo')
			
			if len(grupos_administrados) > 0:
				return qs.filter(grupo__in=grupos_administrados,superadmin=False)
			else:
				#Un usuario normal no ve páginas
				return qs.none()
			
	def save_model(self, request, obj, form, change):
		
		try:
			c = Pagina.objects.get(pk=obj.pk)
		except Pagina.DoesNotExist:
			obj.usuario = request.user
			obj.creada_por = request.user
			
		obj.modificada_por = request.user	
		obj.save()


############################################################################################################################
				
class Banner_Admin(admin.ModelAdmin):
	list_display = ('thumb_banner','titulo','grupos','url','tipo','dimensiones','visibilidad','activo','orden','creado','creado_por','modificado','modificado_por')
	form = Form_Banner_Admin
	list_filter = ('tipo','visibilidad')

	def thumb_banner(self, obj):
		thumb = default.backend.get_thumbnail(obj.banner.file, ADMIN_THUMBS_SIZE)
		return u'<img width="%s" src="%s" />' % (thumb.width, thumb.url)
	thumb_banner.short_description = 'Banner'
	thumb_banner.allow_tags = True
	
	
	#Esto es para que funcione el Form_Banner_Admin. Para pasarle el request
	def get_form(self, request, obj=None, **kwargs):
		self.exclude = []
		if not request.user.is_superuser:
			self.exclude.append('superadmin')
		AdminForm = super(Banner_Admin, self).get_form(request, obj, **kwargs)
		class ModelFormMetaClass(AdminForm):
			def __new__(cls, *args, **kwargs):
				kwargs['request'] = request
				kwargs['user'] = request.user
				return AdminForm(*args, **kwargs)
		return ModelFormMetaClass

	def queryset(self, request):
		qs = super(Banner_Admin, self).queryset(request)
		#Si es superusuario lo ve todo
		if request.user.is_superuser:
			return qs
		else:
			# Si no es superusuario pero es administrador de grupo, ve todos los de su grupo.
			grupos_administrados = Miembro.objects.filter(usuario=request.user,nivel=u'Administrador').values_list('grupo', flat=True).order_by('grupo')
			
			if len(grupos_administrados) > 0:
				return qs.filter(grupo__in=grupos_administrados,superadmin=False)
			else:
				#El usuario normal no ve banners
				return qs.none()
			
	def save_model(self, request, obj, form, change):
		
		try:
			b = Banner.objects.get(pk=obj.pk)
		except Banner.DoesNotExist:
			obj.usuario = request.user
			obj.creado_por = request.user
			
		obj.modificado_por = request.user	
		obj.save()
		
############################################################################################################################
		
class Comentarios_Admin(admin.ModelAdmin):
	list_display = ('perfil','grupos','content_type','creado','creado_por','modificado','modificado_por')
	search_fields = ['perfil']
	readonly_fields = ('perfil','grupo','content_type','parent','object_id')

	def queryset(self, request):
		qs = super(Comentarios_Admin, self).queryset(request)
		#Si es superusuario lo ve todo
		if request.user.is_superuser:
			return qs
		else:
			# Si no es superusuario pero es administrador de grupo, ve todos los de su grupo.
			grupos_administrados = Miembro.objects.filter(usuario=request.user,nivel=u'Administrador').values_list('grupo', flat=True).order_by('grupo')
			
			if len(grupos_administrados) > 0:
				#miembros_administrados = Miembro.objects.filter(grupo__in=grupos_administrados).values_list('usuario', flat=True).order_by('usuario')
				return qs.filter(grupo__in=grupos_administrados)
			else:
				#Y si no ve solo lo suyo
				return qs.filter(pagina__usuario=request.user)
			

############################################################################################################################



admin.site.register(Categoria_Entrada,Categoria_Entrada_Admin)
admin.site.register(Entrada,Entrada_Admin)
admin.site.register(Pagina,Pagina_Admin)
admin.site.register(Comentario,Comentarios_Admin)
admin.site.register(Banner,Banner_Admin)


