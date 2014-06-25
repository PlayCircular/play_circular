# coding=utf-8

# Copyright (C) 2014 by Víctor Romero Blanco <info at playcircular dot com>.
# http://playcircular.com/
# It's licensed under the AFFERO GENERAL PUBLIC LICENSE unless stated otherwise.
# You can get copies of the licenses here: http://www.affero.org/oagpl.html
# AFFERO GENERAL PUBLIC LICENSE is also included in the file called "LICENSE".

from django import forms
from django.forms.fields import ChoiceField, MultipleChoiceField
from django.forms import ModelForm
from django.utils.translation import ugettext as _
from utilidades.combox import *
from paginas.models import *
from django.utils.encoding import smart_str
from django.shortcuts import get_object_or_404
from django.forms.models import BaseInlineFormSet
from django.db.models import Q



############################################################################################################################

class Form_Pagina_Admin(forms.ModelForm):

	"""Cargo en los select solo los datos relativos a los grupos de los que el usuario registrado en el sistema es administrador"""
	class Meta:
		model = Pagina
		
	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop('request', None) # Now you can access request anywhere in your form methods by using self.request. 
		user = kwargs.pop('user', None)
		super(Form_Pagina_Admin, self).__init__(*args, **kwargs)

		if user.is_superuser:
			self.fields['parent'].queryset = Pagina.objects.all()
			self.fields['grupo'].queryset = Grupo.objects.all()
		else:
			grupos_administrados = Miembro.objects.filter(usuario=user,nivel=u'Administrador').values_list('grupo', flat=True)
			if len(grupos_administrados) > 0:
				self.fields['grupo'].queryset = Grupo.objects.filter(pk__in=grupos_administrados)
				self.fields['parent'].queryset = Pagina.objects.filter(grupo__in=grupos_administrados,superadmin=False)
			else:
				self.fields['grupo'].queryset = Grupo.objects.none()
				self.fields['parent'].queryset = Pagina.objects.none()
				
	def clean(self):
		try:
			grupos = self.cleaned_data['grupo']
			usuario = self.request.user

			#----- Grupos --------
			n_grupos = len(grupos)
			if n_grupos == 0 and not usuario.is_superuser:
				#El Superadmin puede publicar sin que pernezca a ningún grupo para que no lo controlen los Admin de los grupos
				raise forms.ValidationError(_(u"El campo grupo es obligatorio."))
			return self.cleaned_data
		except KeyError:
			raise forms.ValidationError(_("Soluciona estos problemas"), code='invalid')
				
############################################################################################################################

class Form_Banner_Admin(forms.ModelForm):

	"""Cargo en los select solo los datos relativos a los grupos de los que el usuario registrado en el sistema es administrador"""
	class Meta:
		model = Banner
		
	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop('request', None) # Now you can access request anywhere in your form methods by using self.request. 
		user = kwargs.pop('user', None)
		super(Form_Banner_Admin, self).__init__(*args, **kwargs)
		if user.is_superuser:
			self.fields['grupo'].queryset = Grupo.objects.all()
		else:
			grupos_administrados = Miembro.objects.filter(usuario=user,nivel=u'Administrador').values_list('grupo', flat=True)
			if len(grupos_administrados) > 0:
				self.fields['grupo'].queryset = Grupo.objects.filter(pk__in=grupos_administrados)
			else:
				self.fields['grupo'].queryset = Grupo.objects.none()
				
	def clean(self):
		try:
			grupos = self.cleaned_data['grupo']
			usuario = self.request.user

			#----- Grupos --------
			n_grupos = len(grupos)
			if n_grupos == 0 and not usuario.is_superuser:
				#El Superadmin puede publicar sin que pernezca a ningún grupo para que no lo controlen los Admin de los grupos
				raise forms.ValidationError(_(u"El campo grupo es obligatorio."))
			return self.cleaned_data
		except KeyError:
			raise forms.ValidationError(_("Soluciona estos problemas"), code='invalid')
				
				
############################################################################################################################

class Form_Categoria_Entrada_Admin(forms.ModelForm):

	"""Cargo en los select solo los datos relativos a los grupos de los que el usuario registrado en el sistema es administrador"""
	class Meta:
		model = Categoria_Entrada
		
	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop('request', None) # Now you can access request anywhere in your form methods by using self.request. 
		user = kwargs.pop('user', None)
		super(Form_Categoria_Entrada_Admin, self).__init__(*args, **kwargs)
		if user.is_superuser:
			self.fields['grupo'].queryset = Grupo.objects.all()
		else:
			grupos_administrados = Miembro.objects.filter(usuario=user,nivel=u'Administrador').values_list('grupo', flat=True)
			if len(grupos_administrados) > 0:
				self.fields['grupo'].queryset = Grupo.objects.filter(pk__in=grupos_administrados)
			else:
				mis_grupos_qs = Miembro.objects.filter(usuario=user).values_list('grupo', flat=True)
				self.fields['grupo'].queryset = Grupo.objects.filter(pk__in=mis_grupos_qs)
				
	def clean(self):
		try:
			grupos = self.cleaned_data['grupo']
			usuario = self.request.user

			#----- Grupos --------
			n_grupos = len(grupos)
			if n_grupos == 0 and not usuario.is_superuser:
				#El Superadmin puede publicar sin que pernezca a ningún grupo para que no lo controlen los Admin de los grupos
				raise forms.ValidationError(_(u"El campo grupo es obligatorio."))
			return self.cleaned_data
		except KeyError:
			raise forms.ValidationError(_("Soluciona estos problemas"), code='invalid')
				
				
############################################################################################################################

class Form_Entrada_Admin(forms.ModelForm):

	"""Cargo en los select solo los datos relativos a los grupos de los que el usuario registrado en el sistema es administrador"""
	class Meta:
		model = Entrada
		
	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop('request', None) # Now you can access request anywhere in your form methods by using self.request. 
		user = kwargs.pop('user', None)
		super(Form_Entrada_Admin, self).__init__(*args, **kwargs)
		if user.is_superuser:
			self.fields['usuario'].queryset = User.objects.all()
			self.fields['grupo'].queryset = Grupo.objects.all()
			self.fields['categoria'].queryset = Categoria_Entrada.objects.all()
			self.fields['entradas_relacionadas'].queryset = Entrada.objects.all()
		else:
			grupos_administrados = Miembro.objects.filter(usuario=user,nivel=u'Administrador').values_list('grupo', flat=True)
			if len(grupos_administrados) > 0:
				miembros_administrados = Miembro.objects.filter(grupo__in=grupos_administrados).values_list('usuario', flat=True)
				self.fields['usuario'].queryset = User.objects.filter(pk__in=miembros_administrados)
				self.fields['grupo'].queryset = Grupo.objects.filter(pk__in=grupos_administrados)
				self.fields['categoria'].queryset = Categoria_Entrada.objects.filter(Q(grupo__in=grupos_administrados) | Q(superadmin=True))
				self.fields['entradas_relacionadas'].queryset = Entrada.objects.filter(Q(grupo__in=grupos_administrados) | Q(superadmin=True))
			else:
				mis_grupos_qs = Miembro.objects.filter(usuario=user).values_list('grupo', flat=True)
				self.fields['usuario'].queryset = User.objects.filter(pk=user.pk)
				self.fields['grupo'].queryset = Grupo.objects.filter(pk__in=mis_grupos_qs)
				self.fields['categoria'].queryset = Categoria_Entrada.objects.filter(Q(grupo__in=mis_grupos_qs) | Q(superadmin=True))
				self.fields['entradas_relacionadas'].queryset = Entrada.objects.filter(Q(grupo__in=mis_grupos_qs) | Q(superadmin=True))

	def clean(self):
		try:
			grupos = self.cleaned_data['grupo']
			usuario = self.cleaned_data['usuario']
			tipo = self.cleaned_data['tipo']
			
			#----- Grupos --------
			n_grupos = len(grupos)
			if n_grupos == 0 and not usuario.is_superuser:
				#El Superadmin puede publicar sin que pernezca a ningún grupo para que no lo controlen los Admin de los grupos
				raise forms.ValidationError(_(u"El campo grupo es obligatorio."))
			#----- Usuario --------
			n_usuario = Miembro.objects.filter(grupo__in=grupos,usuario=usuario,activo=True).count()
			if n_usuario == 0 and not usuario.is_superuser:
				#El Superadmin puede publicar sin que pernezca a ningún grupo para que no lo controlen los Admin de los grupos
				raise forms.ValidationError(_(u"El usuario elegido no pertenece a ninguno de los grupos seleccionados."))
			#----- Tipo --------
			if n_grupos == 0 and tipo == u'e_grupo':
				#Una entrada de grupo sin grupo no se vería
				raise forms.ValidationError(_(u"Una entrada de grupo sin grupos no se vería."))
			
			return self.cleaned_data
		except KeyError:
			raise forms.ValidationError(_("Soluciona estos problemas"), code='invalid')

############################################################################################################################
				
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

############################################################################################################################

class Form_Comentario(forms.ModelForm):

	class Meta:
		model = Comentario
		fields = ('comentario','notificaciones','content_type','object_id')
		widgets = {'comentario': forms.Textarea(),
					'content_type':forms.HiddenInput(),
					'object_id':forms.HiddenInput()}

############################################################################################################################

class Form_Rating_Entrada(forms.ModelForm):

	class Meta:
		model = Rating_entrada
		fields = ('usuario','entrada','a_favor','valor')
		widgets = {'usuario':forms.HiddenInput(),
					'entrada':forms.HiddenInput()}
		
############################################################################################################################

class Form_Opinion_Comentario(forms.ModelForm):

	class Meta:
		model = Opinion_comentario
		fields = ('comentario','a_favor')
		widgets = {'comentario':forms.HiddenInput()}
		
		
		
		
		
		