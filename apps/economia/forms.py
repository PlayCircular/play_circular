# coding=utf-8

# Copyright (C) 2014 by Víctor Romero Blanco <info at playcircular dot com>.
# http://playcircular.com/
# It's licensed under the AFFERO GENERAL PUBLIC LICENSE unless stated otherwise.
# You can get copies of the licenses here: http://www.affero.org/oagpl.html
# AFFERO GENERAL PUBLIC LICENSE is also included in the file called "LICENSE".

from django import forms
from django.forms.fields import ChoiceField, MultipleChoiceField
from django.forms import ModelForm
from economia.models import *
from grupos.models import *
from actividades.models import *
from django.utils.translation import ugettext as _
from utilidades.combox import *
from django.utils.encoding import smart_str
from django.shortcuts import get_object_or_404

############################################################################################################################

class Form_Cuenta_Admin(forms.ModelForm):

	"""Cargo en los select solo los datos relativos a los grupos de los que el usuario registrado en el sistema es administrador"""
	class Meta:
		model = Cuenta
		
	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop('request', None) # Now you can access request anywhere in your form methods by using self.request. 
		user = kwargs.pop('user', None)
		super(Form_Cuenta_Admin, self).__init__(*args, **kwargs)
		if user.is_superuser:
			self.fields['grupo'].queryset = Grupo.objects.all()
			self.fields['titulares'].queryset = User.objects.all()
			self.fields['margen'].queryset = Margenes.objects.all()
		else:
			grupos_administrados = Miembro.objects.filter(usuario=user,nivel=u'Administrador').values_list('grupo', flat=True)
			if len(grupos_administrados) > 0:
				config_grupos_administrados = Config_grupo.objects.filter(grupo__in=grupos_administrados).values_list('pk', flat=True)
				miembros_administrados = Miembro.objects.filter(grupo__in=grupos_administrados).values_list('usuario', flat=True)
				self.fields['grupo'].queryset = Grupo.objects.filter(pk__in=grupos_administrados)
				self.fields['titulares'].queryset = User.objects.filter(pk__in=miembros_administrados)
				self.fields['margen'].queryset = Margenes.objects.filter(config_grupo__in=config_grupos_administrados)
			else:
				self.fields['grupo'].queryset = Grupo.objects.none()
				self.fields['titulares'].queryset = User.objects.none()
				self.fields['margen'].queryset = Margenes.objects.none()
				
############################################################################################################################

class Form_Intercambio_Admin(forms.ModelForm):

	"""Cargo en los select solo los datos relativos a los grupos de los que el usuario registrado en el sistema es administrador"""
	class Meta:
		model = Intercambio
		
	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop('request', None) # Now you can access request anywhere in your form methods by using self.request. 
		user = kwargs.pop('user', None)
		super(Form_Intercambio_Admin, self).__init__(*args, **kwargs)
		if user.is_superuser:
			self.fields['origen'].queryset = User.objects.all()
			self.fields['cuenta_origen'].queryset = Cuenta.objects.all().exclude(tipo='Intergrupos').distinct()
			self.fields['grupo_origen'].queryset = Grupo.objects.all()
			self.fields['grupo_destino'].queryset = Grupo.objects.all()
			self.fields['destino'].queryset = User.objects.all()
			self.fields['cuenta_destino'].queryset = Cuenta.objects.all().exclude(tipo='Intergrupos').distinct()
			
			self.fields['actividad'].queryset = Actividad.objects.all()
		else:
			grupos_administrados = Miembro.objects.filter(usuario=user,nivel=u'Administrador').values_list('grupo', flat=True)
			if len(grupos_administrados) > 0:
				#Puede hacer un intercambio desde algún miembro de su grupo a cualquier otro miembro de la plataforma ( otros grupos.)
				miembros_administrados = Miembro.objects.filter(grupo__in=grupos_administrados).values_list('usuario', flat=True)
				self.fields['origen'].queryset = User.objects.filter(pk__in=miembros_administrados)
				qs_cuenta_origen = Cuenta.objects.filter(titulares__in=miembros_administrados, grupo__in=grupos_administrados).distinct()
				qs_cuenta_origen = qs_cuenta_origen.exclude(tipo='Intergrupos').distinct()
				self.fields['cuenta_origen'].queryset = qs_cuenta_origen
				self.fields['grupo_origen'].queryset = Grupo.objects.filter(pk__in=grupos_administrados)
				self.fields['grupo_destino'].queryset = Grupo.objects.all()
				self.fields['destino'].queryset = User.objects.all()
				self.fields['cuenta_destino'].queryset = Cuenta.objects.all().exclude(tipo='Intergrupos').distinct()
				self.fields['actividad'].queryset = Actividad.objects.all()
			else:
				self.fields['origen'].queryset = User.objects.none()
				self.fields['cuenta_origen'].queryset = Cuenta.objects.none()
				self.fields['grupo_origen'].queryset = Grupo.objects.none()
				self.fields['destino'].queryset = User.objects.none()
				self.fields['cuenta_destino'].queryset = Cuenta.objects.none()
				self.fields['grupo_destino'].queryset = Grupo.objects.none()
				self.fields['actividad'].queryset = Actividad.objects.none()
				
	def clean_cuenta_origen(self):
		origen = self.cleaned_data['origen']
		cuenta_origen = self.cleaned_data['cuenta_origen']
		n_cuenta_origen = Cuenta.objects.filter(pk=cuenta_origen.pk,titulares=origen,activo=True).count()
		if n_cuenta_origen == 0:
			raise forms.ValidationError(_(u"La cuenta elegida no pertenece al usuario de origen"))
		return self.cleaned_data['cuenta_origen']
	
	def clean_grupo_origen(self):
		origen = self.cleaned_data['origen']
		grupo_origen = self.cleaned_data['grupo_origen']
		n_mis_grupos = Miembro.objects.filter(usuario=origen,activo=True,grupo=grupo_origen).count()
		if n_mis_grupos == 0:
			raise forms.ValidationError(_(u"El grupo elegido no pertenece al usuario de origen"))
		return self.cleaned_data['grupo_origen']
	
	def clean_destino(self):
		grupo_destino = self.cleaned_data['grupo_destino']
		destino = self.cleaned_data['destino']
		n_mis_grupos = Miembro.objects.filter(usuario=destino,activo=True,grupo=grupo_destino).count()
		if n_mis_grupos == 0:
			raise forms.ValidationError(_(u"El usuario elegido no pertenece al grupo destino"))
		return self.cleaned_data['destino']
	
	def clean_cuenta_destino(self):
		cuenta_destino = self.cleaned_data['cuenta_destino']
		#hago esto porque aquí no llega a veces el self.cleaned_data['destino'] y da un fallo de KeyError. Solo llegan algunos self.cleaned_data
		try:
			destino = self.cleaned_data['destino']
			n_cuenta_destino = Cuenta.objects.filter(pk=cuenta_destino.pk,activo=True,titulares=destino).count()
		except:
			try:
				grupo_destino = self.cleaned_data['grupo_destino']
				n_cuenta_destino = Cuenta.objects.filter(pk=cuenta_destino.pk,activo=True,grupo=grupo_destino).count()
			except:
				n_cuenta_destino = Cuenta.objects.filter(pk=cuenta_destino.pk,activo=True).count()
		if n_cuenta_destino == 0:
			raise forms.ValidationError(_(u"La cuenta destino elegida no pertenece al usuario de destino"))
		return self.cleaned_data['cuenta_destino']
	
	def clean_actividad(self):
		actividad = self.cleaned_data['actividad']
		#No es un campo obligatorio. Podría ser vacío.
		if self.cleaned_data['actividad']:
			try:
				#hago esto porque aquí no llega a veces el self.cleaned_data['destino'] y da un fallo de KeyError. Solo llegan algunos self.cleaned_data
				destino = self.cleaned_data['destino']
				perfil_destino = Perfil.objects.get(usuario=destino)
				n_actividad = Actividad.objects.filter(pk=actividad.pk,perfil=perfil_destino,activo=True).count()
			except:
				try:
					grupo_destino = self.cleaned_data['grupo_destino']
					n_actividad = Actividad.objects.filter(pk=actividad.pk,activo=True,grupo__in=grupo_destino).count()
				except:
					n_actividad = Actividad.objects.filter(pk=actividad.pk,activo=True).count()
			if n_actividad == 0:
				raise forms.ValidationError(_(u"La actividad elegida no pertenece al usuario destino"))

		return self.cleaned_data['actividad']
	
	def clean(self):
		try:
			#vuelvo a hacer aquí comprobaciones porque algunas veces en los campos clean no llega toda la información y se pueden escapar cosas
			origen = self.cleaned_data['origen']
			destino = self.cleaned_data['destino']
			cuenta_origen = self.cleaned_data['cuenta_origen']
			cuenta_destino = self.cleaned_data['cuenta_destino']
			grupo_origen = self.cleaned_data['grupo_origen']
			grupo_destino = self.cleaned_data['grupo_destino']
			actividad = self.cleaned_data['actividad']
			
			#----- Cuenta origen --------
			n_cuenta_origen = Cuenta.objects.filter(pk=cuenta_origen.pk,titulares=origen,activo=True).count()
			if n_cuenta_origen == 0:
				raise forms.ValidationError(_(u"La cuenta elegida no pertenece al usuario de origen"))
			#------ Grupo origen ---------
			n_grupo_origen = Miembro.objects.filter(usuario=origen,activo=True,grupo=grupo_origen).count()
			if n_grupo_origen == 0:
				raise forms.ValidationError(_(u"El grupo elegido no pertenece al usuario de origen"))
			#------ Grupo destino ---------
			n_mis_grupos = Miembro.objects.filter(usuario=destino,activo=True,grupo=grupo_destino).count()
			if n_mis_grupos == 0:
				raise forms.ValidationError(_(u"El usuario elegido no pertenece al grupo destino"))
			#------ Grupo cuenta_destino ---------
			n_cuenta_destino = Cuenta.objects.filter(pk=cuenta_destino.pk,activo=True,titulares=destino).count()
			if n_cuenta_destino == 0:
				raise forms.ValidationError(_(u"La cuenta destino elegida no pertenece al usuario de destino"))
			#------ actividad---------
			#No es un campo obligatorio. Podría ser vacío.
			if self.cleaned_data['actividad']:
				perfil_destino = Perfil.objects.get(usuario=destino)
				n_actividad = Actividad.objects.filter(pk=actividad.pk,perfil=perfil_destino,activo=True).count()
				if n_actividad == 0:
					raise forms.ValidationError(_(u"La actividad elegida no pertenece al usuario destino"))
				
			#------ Otras comprobaciones ---------
			#------ No mismos titulares en cuentas de origen y destino ---------
			
			titulares_origen = []
			for titular in cuenta_origen.titulares.all():
				titulares_origen.append(titular)
				
			titulares_destino = []
			for titular in cuenta_destino.titulares.all():
				titulares_destino.append(titular)

			titulares_comunes = False
			for item in titulares_destino:
				if titulares_origen.count(item) >= 1:
					titulares_comunes = True
					
			if titulares_comunes:
				raise forms.ValidationError(_("Las cuentas seleccionadas tienen titulares comunes. No se puede procesar."), code='invalid')
			
			return self.cleaned_data
		except KeyError:
			raise forms.ValidationError(_("Soluciona estos problemas"), code='invalid')


############################################################################################################################

class Form_Margenes_Cuenta(forms.ModelForm):
	
	"""Cargo en los select solo los datos relativos a los grupos de los que el usuario registrado en el sistema es administrador"""
	class Meta:
		model = Cuenta

	# Restringo las opciones 
	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop('request', None) # Now you can access request anywhere in your form methods by using self.request.            
		super(Form_Margenes_Cuenta, self).__init__(*args, **kwargs)
		grupo = kwargs['instance'].grupo
		config = grupo.config_grupo
		self.fields['margen'].queryset = Margenes.objects.filter(config_grupo=config)

############################################################################################################################

class Form_pago(forms.ModelForm):

	class Meta:
		model = Intercambio
		fields = ('origen','cuenta_origen','actividad','cantidad','destino','cuenta_destino','concepto','publico','descripcion')
		widgets = {'descripcion': forms.Textarea(),
					'origen':forms.HiddenInput(),
					'destino':forms.HiddenInput()}

		
	def __init__(self, *args, **kwargs):
		diccionario = kwargs.pop('diccionario', None)
		super(Form_pago, self).__init__(*args, **kwargs)
		self.fields['cuenta_origen'].queryset = diccionario['cuentas_posibles_origen']
		self.fields['cuenta_destino'].queryset = diccionario['cuentas_posibles_destino']
		self.fields['actividad'].queryset = diccionario['actividades']
		
	def clean_cantidad(self):
		if self.cleaned_data['cantidad'] <= 0:
			raise forms.ValidationError(_("Tienes que introducir una cantidad positiva."))
		return self.cleaned_data['cantidad']
	
	def clean(self):
		try:
			
			cuenta_origen = self.cleaned_data['cuenta_origen']
			cuenta_destino = self.cleaned_data['cuenta_destino']
			
			titulares_origen = []
			for titular in cuenta_origen.titulares.all():
				titulares_origen.append(titular)
				
			titulares_destino = []
			for titular in cuenta_destino.titulares.all():
				titulares_destino.append(titular)

			titulares_comunes = False
			for item in titulares_destino:
				if titulares_origen.count(item) >= 1:
					titulares_comunes = True
				
			if titulares_comunes:
				raise forms.ValidationError(_("Las cuentas seleccionadas tienen titulares comunes. No se puede procesar."), code='invalid')
			else:
				return self.cleaned_data
		except KeyError:
			raise forms.ValidationError(_("Soluciona estos problemas"), code='invalid')

############################################################################################################################

class Form_pago_confirmacion(forms.ModelForm):
	
	permitido = forms.IntegerField(label=_(u"Permitido"),required=False,widget=forms.HiddenInput())

	class Meta:
		model = Intercambio
		fields = ('origen','cuenta_origen','actividad','cantidad','destino','cuenta_destino','concepto','publico','descripcion')
		widgets = {'origen': forms.HiddenInput(),
					'cuenta_origen': forms.HiddenInput(),
					'actividad':forms.HiddenInput(),
					'cantidad':forms.HiddenInput(),
					'destino':forms.HiddenInput(),
					'cuenta_destino':forms.HiddenInput(),
					'concepto':forms.HiddenInput(),
					'publico':forms.HiddenInput(),
					'descripcion':forms.HiddenInput()}


#############################################################################################################################
