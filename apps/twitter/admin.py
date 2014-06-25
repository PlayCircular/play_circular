#coding=utf-8

from django.contrib import admin
from django.conf import settings
from settings import MEDIA_ROOT, STATIC_ROOT

from django.utils.translation import ugettext as _
#from django.core.mail import send_mail, send_mass_mail, BadHeaderError
#from django.db import connection
#from datetime import datetime, date, time

from twitter.models import *

############################################################################################################################
class Mensaje_Admin(admin.ModelAdmin):
	
	list_display = ('usuario','activo','creado')

	def queryset(self, request):
		qs = super(Mensaje_Admin, self).queryset(request)
		return qs.filter(usuario=request.user)

	def save_model(self, request, obj, form, change):
		obj.usuario = request.user
		#obj.modificado = datetime.now()
		obj.save()
		
	#class Media:
		#js = ('js/tiny_mce/tiny_mce.js',
		#'js/editores.js',)


############################################################################################################################
				
class Seguimiento_Admin(admin.ModelAdmin):
	
	list_display = ('seguidor','seguido','activo','creado')

	def queryset(self, request):
		qs = super(Seguimiento_Admin, self).queryset(request)
		return qs.filter(seguidor=request.user)

	def save_model(self, request, obj, form, change):
		obj.seguidor = request.user
		#obj.modificado = datetime.now()
		obj.save()
		
	#class Media:
		#js = ('js/tiny_mce/tiny_mce.js',
		#'js/editores.js',)


############################################################################################################################

admin.site.register(Mensaje,Mensaje_Admin)
admin.site.register(Seguimiento,Seguimiento_Admin)






