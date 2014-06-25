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
from django.core.mail import send_mail, send_mass_mail, BadHeaderError
from django.db import connection

from django.contrib.auth.models import User
from usuarios.models import *
from grupos.models import *
from configuracion.models import *

############################################################################################################################
class Social_Inline(admin.TabularInline):
	model = Social_usu
	extra = 1	
	max_num = 6
	verbose_name = _(u'dato social')
	verbose_name_plural = _(u'datos sociales')
	
############################################################################################################################
class FotosPersonalesInline(admin.TabularInline):
    model = Fotos_personales
    template ="admin/tabular.html" 
    extra = 2
    max_num = 3
    verbose_name = _(u'fotos personales')

############################################################################################################################

class IncidenciasUsuariosInline(admin.TabularInline):
    model = Incidencias_usuario
    extra = 1
    max_num = 6
    verbose_name = _(u'Incidencia del usuario')
    verbose_name_plural = _(u'Incidencias del usuario')
    
############################################################################################################################
   
class Perfil_Admin(admin.ModelAdmin):
	list_display = ('usuario','fotos','nombre_completo', 'email','ultima_visita','creado','creado_por','modificado','modificado_por')

	inlines = [
		Social_Inline,
		FotosPersonalesInline,
	]
	
	fieldsets = (
	(None, {
		'fields': (
					('nombre', 'ocultar_nombre'),
					('apellidos', 'ocultar_apellidos'),
					('pais'),
					('provincia'),
					('poblacion'),
					('direccion', 'ocultar_direccion'),
					('codigo_postal'),
					('coordenadas'),
					('telefono', 'ocultar_telefono'),
					('mi_email', 'ocultar_email'),
					('descripcion'),
				)
		}),
	)

	def queryset(self, request):
		qs = super(Perfil_Admin, self).queryset(request)
		numero = qs.filter(usuario=request.user).count()

		if numero == 1:
			mensaje = _(u"Ya ha completado este campo. Solo puede editarlo, no añadir nuevos")
			self.message_user(request, mensaje)
		
		#Si es superusuario lo ve todo
		if request.user.is_superuser:
			return qs
		else:
			# Si no es superusuario pero es administrador de grupo, ve todos los de su grupo.
			grupos_administrados = Miembro.objects.filter(usuario=request.user,nivel=u'Administrador').values_list('grupo', flat=True).order_by('grupo')
			
			if len(grupos_administrados) > 0:
				miembros_administrados = Miembro.objects.filter(grupo__in=grupos_administrados).values_list('usuario', flat=True).order_by('usuario')
				perfil_qs = Perfil.objects.filter(usuario__in=miembros_administrados).values_list('id', flat=True).order_by('id')
				return qs.filter(usuario__in=perfil_qs)
			else:
				return qs.filter(usuario=request.user)
		

	def has_add_permission(self, request):
		qs = super(Perfil_Admin, self).queryset(request)
		numero = qs.filter(usuario=request.user).count()

		if numero >= 1:
			return False
		else:
			return True

	def save_model(self, request, obj, form, change):
		
		try:
			datos = Perfil.objects.get(usuario=request.user)
			pass
		except Perfil.DoesNotExist:
			obj.usuario = request.user
			obj.creado_por = request.user
			
		obj.modificado_por = request.user
		obj.save()
		
		u = User.objects.get(pk=obj.usuario.pk)
		u.first_name = obj.nombre
		u.last_name = obj.apellidos
		u.email = obj.mi_email
		u.save()

############################################################################################################################

class Correspondencia_Admin(admin.ModelAdmin):
	list_display = ('destinatario', 'remitente', 'asunto','leido','creado')

	def queryset(self, request):
		qs = super(Correspondencia_Admin, self).queryset(request)
		numero = qs.filter(destinatario=request.user).count()

		if numero == 1:
			mensaje = _(u"Ya ha completado este campo. Solo puede editarlo, no añadir nuevos")
			self.message_user(request, mensaje)
		
		if request.user.is_superuser:
			return qs
		else:
			return qs.filter(destinatario=request.user)

	def has_add_permission(self, request):
		#qs = super(Mensajes_sistema_Admin, self).queryset(request)
		#numero = qs.filter(usuario=request.user).count()

		#if numero >= 1:
		return False
		#else:
			#return True

	def save_model(self, request, obj, form, change):
		obj.destinatario = request.user
		obj.save()

		
############################################################################################################################


class Config_Perfil_Admin(admin.ModelAdmin):
	list_display = ('usuario', 'idioma', 'valorar_actividades','intercambios_publicos','creado','creado_por','modificado','modificado_por')

	def queryset(self, request):
		qs = super(Config_Perfil_Admin, self).queryset(request)
		numero = qs.filter(usuario=request.user).count()

		if numero == 1:
			mensaje = _(u"Ya ha completado este campo. Solo puede editarlo, no añadir nuevos")
			self.message_user(request, mensaje)
		
		#Si es superusuario lo ve todo
		if request.user.is_superuser:
			return qs
		else:
			# Si no es superusuario pero es administrador de grupo, ve todos los de su grupo.
			grupos_administrados = Miembro.objects.filter(usuario=request.user,nivel=u'Administrador').values_list('grupo', flat=True).order_by('grupo')
			
			if len(grupos_administrados) > 0:
				miembros_administrados = Miembro.objects.filter(grupo__in=grupos_administrados).values_list('usuario', flat=True).order_by('usuario')
				return qs.filter(usuario__in=miembros_administrados)
			else:
				return qs.filter(usuario=request.user)

	def has_add_permission(self, request):

		if request.user.is_superuser:
			qs = super(Config_Perfil_Admin, self).queryset(request)
			numero = qs.filter(usuario=request.user).count()
			if numero == 1:
				mensaje = _(u"Ya ha completado este campo. Solo puede editarlo, no añadir nuevos")
				return False
			else:
				return True
		else:
			return False
		
	def save_model(self, request, obj, form, change):
		obj.usuario = request.user
		obj.modificado_por = request.user
		obj.save()



############################################################################################################################

admin.site.register(Perfil,Perfil_Admin)
admin.site.register(Correspondencia,Correspondencia_Admin)
admin.site.register(Config_perfil,Config_Perfil_Admin)

