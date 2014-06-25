# coding=utf-8

# Copyright (C) 2014 by Víctor Romero Blanco <info at playcircular dot com>.
# http://playcircular.com/
# It's licensed under the AFFERO GENERAL PUBLIC LICENSE unless stated otherwise.
# You can get copies of the licenses here: http://www.affero.org/oagpl.html
# AFFERO GENERAL PUBLIC LICENSE is also included in the file called "LICENSE".

from django import forms
from actividades.models import *
from django.utils.translation import ugettext as _
from utilidades.combox import *
from actividades.models import *
from grupos.models import *
from django.forms import ModelMultipleChoiceField
from django.forms.models import BaseInlineFormSet
from django.db.models import Q



############################################################################################################################

class Form_valorar_actividad(forms.Form):
	
   objeto = forms.IntegerField(widget=forms.HiddenInput())
   pagina = forms.IntegerField(widget=forms.HiddenInput())
   n_paginas = forms.IntegerField(widget=forms.HiddenInput())
   retorno = forms.IntegerField(widget=forms.HiddenInput())
   me_gusta_para_mi = forms.IntegerField()
   rating_para_mi = forms.IntegerField()
   bien_comun = forms.IntegerField()
   rating_para_bien_comun = forms.IntegerField()
   comentario = forms.CharField(widget=forms.Textarea(), label=_(u"Comentario"),max_length=400,required=False)

############################################################################################################################
class Form_busqueda(forms.Form):
	
	busqueda = forms.CharField(max_length=100, label=_(u"Búsqueda"),required=False)
	clase = forms.ChoiceField(choices=CLASE_ACTIVIDAD, label=_(u"Clase"),required=False)
	tipo = forms.ChoiceField(choices=TIPO_ACTIVIDAD, label=_(u"Tipo"),required=False)
	grupos = forms.ChoiceField(choices=GRUPOS_BUSQUEDA, label=_(u"En qué grupos"),required=False)
	orden = forms.ChoiceField(choices=ORDEN, label=_(u"Ordenar por"),required=False)
	
############################################################################################################################
	
class Form_categoria_actividad_admin(forms.ModelForm):

	"""Cargo en los select solo los datos relativos a los grupos de los que el usuario registrado en el sistema es administrador"""
	class Meta:
		model = Categoria
		
	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop('request', None) # Now you can access request anywhere in your form methods by using self.request. 
		user = kwargs.pop('user', None)
		super(Form_categoria_actividad_admin, self).__init__(*args, **kwargs)
		if user.is_superuser:
			self.fields['grupo'].queryset = Grupo.objects.all()
		else:
			qs_grupos_administrados = Miembro.objects.filter(usuario=user,activo=True,nivel=u'Administrador').values_list('grupo', flat=True)
			if len(qs_grupos_administrados)>0:
				self.fields['grupo'].queryset = Grupo.objects.filter(pk__in=qs_grupos_administrados,activo=True)
			else:
				qs_grupos = Miembro.objects.filter(usuario=user).values_list('grupo', flat=True)
				
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
	
class Form_actividad_admin(forms.ModelForm):

	"""Cargo en los select solo los datos relativos a los grupos de los que el usuario registrado en el sistema es administrador"""
	class Meta:
		model = Actividad
		fields = ('grupo','superadmin','usuario','clase','tipo','categoria','precio_moneda_social','activo')
		
	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop('request', None) # Now you can access request anywhere in your form methods by using self.request. 
		user = kwargs.pop('user', None)
		super(Form_actividad_admin, self).__init__(*args, **kwargs)

		if user.is_superuser:
			self.fields['grupo'].queryset = Grupo.objects.all()
			self.fields['usuario'].queryset = User.objects.all()
			self.fields['categoria'].queryset = Categoria.objects.all()
		else:
			qs_grupos_administrados = Miembro.objects.filter(usuario=user,activo=True,nivel=u'Administrador').values_list('grupo', flat=True)
			if len(qs_grupos_administrados)>0:
				qs_miembros_administrados = Miembro.objects.filter(grupo__in=qs_grupos_administrados,activo=True).values_list('usuario', flat=True)
				self.fields['grupo'].queryset = Grupo.objects.filter(pk__in=qs_grupos_administrados,activo=True)
				self.fields['usuario'].queryset = User.objects.filter(pk__in=qs_miembros_administrados)
				self.fields['categoria'].queryset = Categoria.objects.filter(Q(grupo__in=qs_grupos_administrados) | Q(superadmin=True))
			else:
				qs_grupos = Miembro.objects.filter(usuario=user).values_list('grupo', flat=True)
				self.fields['grupo'].queryset = Grupo.objects.filter(pk__in=qs_grupos,activo=True)
				self.fields['usuario'].queryset = User.objects.filter(pk=user.pk)
				self.fields['categoria'].queryset = Categoria.objects.filter(Q(grupo__in=qs_grupos) | Q(superadmin=True))
				
	def clean_precio_moneda_social(self):
		precio_moneda_social = self.cleaned_data['precio_moneda_social']
		if precio_moneda_social <= 0:
			raise forms.ValidationError(_(u"Introduce una cantidad positiva."))
		return self.cleaned_data['precio_moneda_social']
	

	def clean(self):
		try:
			grupos = self.cleaned_data['grupo']
			usuario = self.cleaned_data['usuario']
			categoria = self.cleaned_data['categoria']
			
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
			#------ Categoria ---------
			if categoria and categoria.superadmin == False:
				# Al superadmin que puede publicar sin grupos no se le controla.
				if n_grupos > 0:
					n_categoria = Categoria.objects.filter(pk=categoria.pk,grupo__in=grupos).count()
					if n_categoria == 0:
						raise forms.ValidationError(_(u"La categoria elegida no pertenece a ninuno de los grupos selecionados"))
			
			return self.cleaned_data
		except KeyError:
			raise forms.ValidationError(_("Soluciona estos problemas"), code='invalid')


############################################################################################################################	
class Form_Actividad(forms.ModelForm):

	class Meta:
		model = Actividad

	def __init__(self, *args, **kwargs):
		user = kwargs.pop('user', None)
		super(Form_Actividad, self).__init__(*args, **kwargs)
		self.fields['grupo'].queryset = Miembro.objects.filter(usuario=user).values('grupo')

		

#######################################################################################################################################################

class Idioma_requerido_formset(BaseInlineFormSet):

	def clean(self):
		super(Idioma_requerido_formset, self).clean()
		for error in self.errors:
			if error:
				return
			completed = 0
		for cleaned_data in self.cleaned_data:
			if cleaned_data and not cleaned_data.get('DELETE', False):
				completed += 1

		if completed < 1:
			raise forms.ValidationError(_("Es necesario introducir al menos un idioma para la actividad."))

		
############################################################################################################################




