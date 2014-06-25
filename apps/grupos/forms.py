# coding=utf-8

# Copyright (C) 2014 by Víctor Romero Blanco <info at playcircular dot com>.
# http://playcircular.com/
# It's licensed under the AFFERO GENERAL PUBLIC LICENSE unless stated otherwise.
# You can get copies of the licenses here: http://www.affero.org/oagpl.html
# AFFERO GENERAL PUBLIC LICENSE is also included in the file called "LICENSE".

from django import forms
from django.forms import ModelForm
from grupos.models import *
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.forms.models import BaseInlineFormSet

#######################################################################################################################################################

class Idioma_requerido_formset(BaseInlineFormSet):

	def clean(self):
		"""Check that at least one form has been completed."""
		super(Idioma_requerido_formset, self).clean()
		for error in self.errors:
			if error:
				return
			completed = 0
		for cleaned_data in self.cleaned_data:
			# form has data and we aren't deleting it.
			if cleaned_data and not cleaned_data.get('DELETE', False):
				completed += 1

		if completed < 1:
			raise forms.ValidationError(_("Es necesario introducir al menos un idioma."))
		
#######################################################################################################################################################

class Admin_requerido_formset(BaseInlineFormSet):
	"""
	Generates an inline formset that is required
	"""
	def _construct_form(self, i, **kwargs):
		"""
		Override the method to change the form attribute empty_permitted
		"""
		form = super(Admin_requerido_formset, self)._construct_form(i, **kwargs)
		form.empty_permitted = False
		return form
		
		
#######################################################################################################################################################

class Margen_requerido_formset(BaseInlineFormSet):

	#"""
	#Generates an inline formset that is required
	#"""
	#def _construct_form(self, i, **kwargs):
		#"""
		#Override the method to change the form attribute empty_permitted
		#"""
		#form = super(Margen_requerido_formset, self)._construct_form(i, **kwargs)
		#form.empty_permitted = False
		#return form

	"""Esta formula de arriba me obliga a no dejar ningún tabular inline vacío ( y se crean tabularinline automaticamente con un extra cada vez que lo edito)
	La fórmula de abajo me obliga solo a que haya al menos un margen perteneciente al grupo."""

	def clean(self):
		"""Check that at least one form has been completed."""
		super(Margen_requerido_formset, self).clean()
		for error in self.errors:
			if error:
				return
			completed = 0
		for cleaned_data in self.cleaned_data:
			# form has data and we aren't deleting it.
			if cleaned_data and not cleaned_data.get('DELETE', False):
				completed += 1

		if completed < 1:
			raise forms.ValidationError(_("Es necesario introducir al menos un margen en el grupo."))


########################################################################################################################################################


class Form_solicitud_miembro(forms.Form):

	condiciones = forms.BooleanField(label=_(u"Acepta las condiciones del grupo"))
	
	def clean(self):
		try:
			if self.cleaned_data['condiciones']:
				return self.cleaned_data	
			else:
				raise forms.ValidationError(_(u'Es necesario aceptar las condiciones del grupo para unirse a él.'))
		except KeyError:
			raise forms.ValidationError(_(u'Es necesario aceptar las condiciones del grupo para unirse a él.'))
			
	
#######################################################################################################################################################

class Form_miembros(forms.ModelForm):

	"""Cargo en los select solo los datos relativos a los grupos de los que el usuario registrado en el sistema es administrador"""
	class Meta:
		model = Miembro

	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop('request', None) # Now you can access request anywhere in your form methods by using self.request. 
		user = kwargs.pop('user', None)
		super(Form_miembros, self).__init__(*args, **kwargs)

		if user.is_superuser:
			self.fields['grupo'].queryset = Grupo.objects.all()
			self.fields['usuario'].queryset = User.objects.all()
		else:
			grupos_administrados = Miembro.objects.filter(usuario=user,nivel=u'Administrador').values_list('grupo', flat=True)
			if len(grupos_administrados) > 0:
				miembros_administrados = Miembro.objects.filter(grupo__in=grupos_administrados).values_list('usuario', flat=True)
				self.fields['grupo'].queryset = Grupo.objects.filter(pk__in=grupos_administrados)
				self.fields['usuario'].queryset = User.objects.filter(pk__in=miembros_administrados)
			else:
				self.fields['grupo'].queryset = Grupo.objects.none()
				self.fields['usuario'].queryset = User.objects.none()

