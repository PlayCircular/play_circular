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
from grupos.models import *
from grupos.forms import *
from usuarios.models import *
from economia.models import *
from django.contrib.contenttypes import generic
from sorl.thumbnail import default
from sorl.thumbnail.admin import AdminImageMixin
import random
from django.core.mail import send_mail, send_mass_mail, BadHeaderError,EmailMultiAlternatives
from django.contrib.auth.models import User
from grupos.views import *
from django.contrib.sites.models import get_current_site

ADMIN_THUMBS_SIZE = '60x60'

	
############################################################################################################################
class Margenes_Inline(admin.TabularInline):
	model = Margenes
	formset = Margen_requerido_formset
	extra = 1
	
	
############################################################################################################################
class Social_Inline(admin.TabularInline):
	model = Social_grupo
	extra = 1

############################################################################################################################
class Mas_fotos_Inline(admin.TabularInline):
	model = Mas_fotos

	template ="admin/tabular.html" 
	extra = 2
	max_num = 6
	verbose_name = _(u'foto del grupo')
	
	
############################################################################################################################
class Idiomas_Inline(admin.StackedInline):
	model = Idiomas_grupo
	extra = 1
	formset = Idioma_requerido_formset
	
	def get_extra(self, request, obj=None, **kwargs):
		extra = 1
		if obj:
			extra = 0
			return extra
		return extra


############################################################################################################################
   
class GrupoAdmin(admin.ModelAdmin):
	list_display = ('logo_thumb','nombre','simbolo','idiomas','unidad_s','provincia','poblacion','telefono','email','activo','creado','creado_por','modificado','modificado_por')
	list_display_links = ('logo_thumb', 'nombre',)
	exclude = ('metatags',)
	inlines = [
		Idiomas_Inline,
		Social_Inline,
		Mas_fotos_Inline,
	]
	
	def logo_thumb(self, obj):
		if obj.logo:
			thumb = default.backend.get_thumbnail(obj.logo.file, ADMIN_THUMBS_SIZE)
			return u'<img width="%s" src="%s" />' % (thumb.width, thumb.url)
		else:
			return _(u"Sin imagen")
	logo_thumb.short_description = 'Logo'
	logo_thumb.allow_tags = True

	def queryset(self, request):

		"""Pueden ver el grupo los usuarios que sean administradores o el superadministrador"""
		qs = super(GrupoAdmin, self).queryset(request)
		if request.user.is_superuser:
			return qs
		else:
			grupos_administrados = Miembro.objects.filter(usuario=request.user,nivel=u'Administrador').values_list('grupo', flat=True).order_by('grupo')
			qs_1 = qs.filter(id__in=grupos_administrados)
			return qs_1

	def save_model(self, request, obj, form, change):
		"""Cada grupo debe permanecer siempre con al menos un usuario administrador. Lo creo al crear el grupo y no dejo que se eliminen todos luego.
		   Y compruebo si el grupo se crea o se actualiza. Si se crea le aplico una configuración por defecto.
		   Se crean tres cuentas: intergrupos, administrador y normal. Aunque está soportado que una cuenta pueda tener muchos titulares, voy a crear
		   un usuario nuevo para la administración del grupo por si lo utiliza mucha gente para gestionar el grupo. Al usuario creador del grupo le asigno
		   una cuenta normal. Así todas las cuentas tienen un único titular."""
		
		n_admin = Miembro.objects.filter(grupo=obj,nivel=u'Administrador').count()
		
		if n_admin == 0:
			obj.creado_por = request.user
		obj.modificado_por = request.user
		obj.save()
		
		if n_admin == 0:
			
			config = Config_grupo()
			config.grupo = obj
			config.creado_por = request.user
			config.modificado_por = request.user
			config.save()
			
			margen_defecto = Margenes()
			margen_defecto.config_grupo = config
			margen_defecto.nombre = _(u'Nivel 1 (+100/-100)')
			margen_defecto.superior = 100
			margen_defecto.inferior = -100
			margen_defecto.default = True
			margen_defecto.creado_por = request.user
			margen_defecto.save()
			
			
			""" Creo un nuevo usuario para manejar la cuenta administración"""
			new_username = str(obj.simbolo) + u'-Admin'
			randon_1 = random.randint(1, 10000)
			
			qs_busqueda = User.objects.filter(username=new_username).count()
			#Pruebo si existe el usuario adminSIMBOLO
			if qs_busqueda > 0:
				randon_2 = random.randint(1, 10000)
				new_username = str(obj.simbolo) + u'-Admin-' + str(randon_2)
				qs_busqueda = User.objects.filter(username=new_username).count()
				#Pruebo otra vez por si acaso el usuario aleatorio existe. No creo que exista más.
				if qs_busqueda > 0:
					randon_3 = random.randint(1, 1000000)
					new_username = str(obj.simbolo) + u'-Admin-' + str(randon_3)
				
			new_usu = User.objects.create_user(new_username,request.user.email,randon_1)
			new_usu.is_active = True
			new_usu.is_staff = True
			new_usu.is_superuser = False
			new_usu.save()

			""" Y completo su perfil básico y su configuración para que pueda editarlos"""
			
			perfil_creador = Perfil.objects.get(usuario=request.user)
			perfil = Perfil()
			perfil.usuario = new_usu
			perfil.telefono = perfil_creador.telefono
			perfil.mi_email = perfil_creador.mi_email
			perfil.creado_por = request.user
			perfil.modificado_por = request.user
			perfil.save()
			
			config_perfil = Config_perfil()
			config_perfil.usuario = new_usu
			config_perfil.creado_por = request.user
			config_perfil.modificado_por = request.user
			config_perfil.save()
			
			"""El nuevo usuario será administrador"""
			grupo_admin = grupo_administrador()
			new_usu.groups.add(grupo_admin)
			new_usu.save()
			
			"""Al usuario actual le paso del grupo visitante al grupo normal"""
			grupo = grupo_normal()
			request.user.groups.clear()
			request.user.groups.add(grupo)
			request.user.save()
			
			cuenta_admin = Cuenta()
			cuenta_admin.grupo = obj
			cuenta_admin.tipo = 'Administrador'
			cuenta_admin.alias = _(u"Admistración ") + str(obj.simbolo)
			cuenta_admin.cuenta = str(obj.simbolo) + u'-Admin'
			cuenta_admin.margen = margen_defecto
			cuenta_admin.creado_por = request.user
			cuenta_admin.modificado_por = request.user
			cuenta_admin.save()
			cuenta_admin.titulares.add(new_usu)
			
			miembro_1 = Miembro()
			miembro_1.grupo = obj
			miembro_1.usuario = new_usu
			miembro_1.clave = str(obj.simbolo) + u'0000'
			miembro_1.activo = True
			miembro_1.pendiente = False
			miembro_1.nivel = 'Administrador'
			miembro_1.creado_por = request.user
			miembro_1.modificado_por = request.user
			miembro_1.save()
			
			"""Se crea una cuenta intergrupos cuyo titular es el admin pero que sólo lo maneja el sistema en las transacciones intergrupos."""
			cuenta_intergrupos = Cuenta()
			cuenta_intergrupos.grupo = obj
			cuenta_intergrupos.tipo = 'Intergrupos'
			cuenta_intergrupos.alias = _(u"Cuenta intergrupos ") + str(obj.simbolo)
			cuenta_intergrupos.cuenta = str(obj.simbolo) + u'-Intergrupos'
			cuenta_intergrupos.margen = margen_defecto
			cuenta_intergrupos.creado_por = request.user
			cuenta_intergrupos.modificado_por = request.user
			cuenta_intergrupos.save()
			cuenta_intergrupos.titulares.add(new_usu)
			
			cuenta_normal = Cuenta()
			cuenta_normal.grupo = obj
			cuenta_normal.tipo = 'Normal'
			cuenta_normal.alias = _(u"Cuenta de usuario ") + str(request.user.username) + ' en '+ str(obj.simbolo)
			cuenta_normal.cuenta = str(obj.simbolo) + u'1'
			cuenta_normal.margen = margen_defecto
			cuenta_normal.creado_por = request.user
			cuenta_normal.modificado_por = request.user
			cuenta_normal.save()
			cuenta_normal.titulares.add(request.user)

			miembro_2 = Miembro()
			miembro_2.grupo = obj
			miembro_2.usuario = request.user
			miembro_2.clave = str(obj.simbolo) + u'1'
			miembro_2.activo = True
			miembro_2.pendiente = False
			miembro_2.nivel = 'Normal'
			miembro_2.creado_por = request.user
			miembro_2.modificado_por = request.user
			miembro_2.save()
			
			#Ahora creo un contador en para llevar el autoincremento de los usuarios en el grupo.
			#Pongo el marcador a 2 porque ya hay dos usuarios: el admin y la cuenta normal del creador. Indica el numero del siguiente usuario en el grupo.
			#Cuando haya nuevas altas busco el número por donde va y le incremento 1.
			
			contador = Contador()
			contador.grupo = obj
			contador.numero = 2
			contador.save()
			
			asunto = _(u'Creación del grupo ') + str(obj)
			
			current_site = get_current_site(request)
			sitio = current_site.domain
			idioma=request.LANGUAGE_CODE

			
			mensaje_1 = _(u"""Se ha creado el grupo solicitado. Además se ha creado un nuevo usuario administrador del grupo distinto al suyo. 
							  Para gestionar el grupo utilize el siguiente usuario:""")
			mensaje_2 = _(u"""Es recomendable que cambie la contraseña nada más acceder por otra que solo usted conozca. Por otro lado también se 
							  ha creado otra cuenta normal vinculada a su usuario actual: """)
			
			html = u"""<p>&nbsp;</p>
					<table width="500" border="0" align="center" cellpadding="8" cellspacing="0" style="border: 2px solid #000000;">
					<tr>
						<td colspan="2"><div align="center">
						<img src="%s/media/%s" width="48px" alt="%s"/> 
						</div></td>
					</tr>
					<tr>
						<td>Asunto:</td><td>%s</td>
					</tr>
					<tr>
						<td>Grupo:</td><td>%s</td>
					</tr>
					<tr>
						<td colspan="2">%s</td>
					</tr>
					<tr>
						<td>Usuario:</td><td>%s</td>
					</tr>
					<tr>
						<td>Contraseña a cambiar:</td><td>%s</td>
					</tr>
					<tr>
						<td colspan="2">%s %s</td>
					</tr>
				</table>
				<p>&nbsp;</p>""" % (sitio,obj.logo.name, obj.logo.name, asunto, obj.nombre, mensaje_1, new_usu.username, randon_1,mensaje_2, request.user.username)

			
			from_email = 'info@playcircular.com'
			to = request.user.email
			
			msg = EmailMultiAlternatives(asunto, mensaje_1, from_email, [to])
			msg.attach_alternative(html, "text/html")
			try:
				msg.send()
			except:
				pass
			
			correspondencia = Correspondencia()
			correspondencia.destinatario = request.user
			correspondencia.id_remitente = request.user.pk
			correspondencia.remitente = request.user.username
			correspondencia.email_remitente = request.user.email			
			correspondencia.asunto = asunto
			correspondencia.mensaje = html
			correspondencia.save()
			
			#try:
				#send_mass_mail(mensajes, fail_silently=False)
			#except BadHeaderError:
				#return HttpResponse('Invalid header found.')
	
############################################################################################################################
   
class ConfigGrupoAdmin(admin.ModelAdmin):
	list_display = ('grupo',
					'impuestos_transaccion',
					'oxidacion',
					'comercio_intergrupos',
					'impuestos_intergrupos',
					'tipo_alta',
					'cuenta_x_miembro',
					'creado','creado_por','modificado','modificado_por')
	inlines = [
		Margenes_Inline,
	]
	
	def queryset(self, request):

		"""Pueden ver el grupo los usuarios que sean administradores o el superadministrador"""
		qs = super(ConfigGrupoAdmin, self).queryset(request)
		if request.user.is_superuser:
			return qs
		else:
			grupos_administrados = Miembro.objects.filter(usuario=request.user,nivel=u'Administrador').values_list('grupo', flat=True).order_by('grupo')
			qs_1 = qs.filter(id__in=grupos_administrados)
			return qs_1
	
	def has_add_permission(self, request):
		return False
	
	def has_delete_permission(self, request, obj=None):
		return False
	
	def save_model(self, request, obj, form, change):
		"""Cada grupo debe permanecer siempre con al menos un usuario administrador. Lo creo al crear el grupo y no dejo que se eliminen todos luego."""
		#admin = request.user
		try:
			config = Config_grupo.objects.get(creado_por=request.user)
			pass
		except Config_grupo.DoesNotExist:
			obj.creado_por = request.user

		obj.modificado_por = request.user
		obj.save()
		
		if obj.activo == True:
			grupo = Grupo.objects.get(pk=obj.grupo.pk)
			grupo.activo = True
			grupo.save()


############################################################################################################################

class Miembros_Admin(admin.ModelAdmin):

	form = Form_miembros
	list_display = ('grupo', 'usuario', 'clave','nombre_completo','nivel','email','activo', 'pendiente','creado','creado_por','modificado','modificado_por')
	readonly_fields = ('clave','creado_por',)
	model = Miembro
	fk_name = 'grupo'
	
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
			return False
	
	def get_actions(self, request):
		actions = super(Miembros_Admin, self).get_actions(request)
		if request.user.is_superuser:
			return actions
		else:
			if 'delete_selected' in actions:
				del actions['delete_selected']
			return actions
	
	#Esto es para que funcione el Form_miembros. Para pasarle el request
	def get_form(self, request, obj=None, **kwargs):
		AdminForm = super(Miembros_Admin, self).get_form(request, obj, **kwargs)
		class ModelFormMetaClass(AdminForm):
			def __new__(cls, *args, **kwargs):
				kwargs['request'] = request
				kwargs['user'] = request.user
				return AdminForm(*args, **kwargs)
		return ModelFormMetaClass

	def queryset(self, request):
		qs = super(Miembros_Admin, self).queryset(request)

		if request.user.is_superuser:
			return qs
		else:
			grupos_administrados = Miembro.objects.filter(usuario=request.user,nivel=u'Administrador').values_list('grupo', flat=True).order_by('grupo')
			return qs.filter(grupo__in=grupos_administrados)
		
	def save_model(self, request, obj, form, change):
		"""Registro quien crea y modifica cada cosa."""
		try:
			m = Miembro.objects.get(pk=obj.pk)
			pass
		except Miembro.DoesNotExist:
			obj.creado_por = request.user
			
		if obj.nivel == 'Normal' or obj.nivel == 'Editor':
			grupo = grupo_normal()
			obj.usuario.groups.clear()
			obj.usuario.groups.add(grupo)
			obj.usuario.save()
			
		if obj.nivel == 'Visitante':
			grupo = grupo_visitante()
			obj.usuario.groups.clear()
			obj.usuario.groups.add(grupo)
			obj.usuario.save()
			
		if obj.nivel == 'Administrador':
			grupo = grupo_administrador()
			obj.usuario.groups.clear()
			obj.usuario.groups.add(grupo)
			obj.usuario.save()
			
		obj.modificado_por = request.user
		obj.save()

############################################################################################################################

admin.site.register(Grupo,GrupoAdmin)
admin.site.register(Config_grupo,ConfigGrupoAdmin)
admin.site.register(Miembro,Miembros_Admin)



