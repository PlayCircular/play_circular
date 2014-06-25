#coding=utf-8

# Copyright (C) 2014 by Víctor Romero Blanco <info at playcircular dot com>.
# http://playcircular.com/
# It's licensed under the AFFERO GENERAL PUBLIC LICENSE unless stated otherwise.
# You can get copies of the licenses here: http://www.affero.org/oagpl.html
# AFFERO GENERAL PUBLIC LICENSE is also included in the file called "LICENSE".

from django.contrib import admin
from django.conf import settings
from settings import MEDIA_ROOT, STATIC_ROOT
from configuracion.models import *
from django.utils.translation import ugettext as _ 
from configuracion.forms import Configuracion_Admin_Form

from django.contrib.contenttypes import generic
from sorl.thumbnail import default
from sorl.thumbnail.admin import AdminImageMixin

ADMIN_THUMBS_SIZE = '60x60'

############################################################################################################################
class Idiomas_Inline(admin.StackedInline):
	model = Idioma_configuracion
	extra = 1
	max_num = 5
	
	def get_extra(self, request, obj=None, **kwargs):
		extra = 1
		if obj:
			extra = 0
			return extra
		return extra
	verbose_name = _(u'idioma')
	verbose_name = _(u'idioma')

	
############################################################################################################################
	
class ConfiguracionAdmin(admin.ModelAdmin):
		
	list_display = ('logo_thumb','nombre','idiomas','creado','creado_por','modificado','modificado_por')
	list_display_links = ('logo_thumb','nombre')
	exclude = ('metatags',)
	
	inlines = [
		Idiomas_Inline,
	]

	def queryset(self, request):
		qs = super(ConfiguracionAdmin, self).queryset(request)
		numero = qs.filter(usuario=request.user).count()
		
		if numero == 1:
			mensaje = _(u"Ya ha completado este campo. Solo puede editarlo, no añadir nuevos")
			self.message_user(request, mensaje)
			
		if request.user.is_superuser:
			return qs
		else:
			return qs.filter(usuario=request.user)

	def has_add_permission(self, request):
		qs = super(ConfiguracionAdmin, self).queryset(request)
		numero = qs.filter(usuario=request.user).count()

		if numero >= 1:
			return False
		else:
			return True
			
	def logo_thumb(self, obj):
		if obj.logo:
			thumb = default.backend.get_thumbnail(obj.logo.file, ADMIN_THUMBS_SIZE)
			return u'<img width="%s" src="%s" />' % (thumb.width, thumb.url)
		else:
			return "No Image" 
	logo_thumb.short_description = 'Logo'
	logo_thumb.allow_tags = True
					
	def save_model(self, request, obj, form, change): 
	
		try:
			conf = Configuracion.objects.get(creado_por=request.user)
			pass
		except Configuracion.DoesNotExist:
			obj.usuario = request.user
			obj.creado_por = request.user

		obj.modificado_por = request.user
		obj.save()

############################################################################################################################
				
class Banner_General_Admin(admin.ModelAdmin):
	list_display = ('thumb_banner','titulo','url','tipo','visibilidad','dimensiones','activo','orden','creado','creado_por','modificado','modificado_por')
	list_filter = ('tipo','visibilidad')

	def thumb_banner(self, obj):
		thumb = default.backend.get_thumbnail(obj.banner.file, ADMIN_THUMBS_SIZE)
		return u'<img width="%s" src="%s" />' % (thumb.width, thumb.url)
	thumb_banner.short_description = 'Banner'
	thumb_banner.allow_tags = True

	def queryset(self, request):
		qs = super(Banner_General_Admin, self).queryset(request)
		#Si es superusuario lo ve todo
		if request.user.is_superuser:
			return qs
		else:
			return qs.filter(usuario=request.user)
			
	def save_model(self, request, obj, form, change):
		
		try:
			b = Banner_general.objects.get(pk=obj.pk)
		except Banner_general.DoesNotExist:
			obj.usuario = request.user
			obj.creado_por = request.user
			
		obj.modificado_por = request.user	
		obj.save()


admin.site.register(Configuracion,ConfiguracionAdmin)
admin.site.register(Banner_general,Banner_General_Admin)

