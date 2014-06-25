# coding=utf-8

# Copyright (C) 2014 by Víctor Romero Blanco <info at playcircular dot com>.
# http://playcircular.com/
# It's licensed under the AFFERO GENERAL PUBLIC LICENSE unless stated otherwise.
# You can get copies of the licenses here: http://www.affero.org/oagpl.html
# AFFERO GENERAL PUBLIC LICENSE is also included in the file called "LICENSE".

from django import forms
from usuarios.models import *
from grupos.models import *
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

#######################################################################################################################################################
class Form_User(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'email')

	def clean_username(self):
		username = self.cleaned_data["username"]
		try:
			User.objects.get(username=username, is_active=True)
			raise forms.ValidationError(_(u'Ese nombre de usuario ya existe. Elige otro único.'))
		except User.DoesNotExist:
			return self.cleaned_data
			
	def clean_email(self):
		email = self.cleaned_data["email"]
		try:
			User.objects.get(email=email, is_active=True)
			raise forms.ValidationError(_(u'Ese email ya exite vinculado a un usuario registrado. Elige otro único.'))
		except User.DoesNotExist:
			return self.cleaned_data

#######################################################################################################################################################

class Form_busqueda_usuarios(forms.Form):

	grupo = forms.ModelChoiceField(queryset=Grupo.objects.none(),label=_(u"Grupo"),required=True)
	usuario = forms.CharField(max_length=100, label=_(u"Usuario"),required=False)
	nombre = forms.CharField(max_length=100, label=_(u"Nombre"),required=False)
	apellidos = forms.CharField(max_length=100, label=_(u"Apellidos"),required=False)
	poblacion = forms.CharField(max_length=100, label=_(u"Población"),required=False)
	telefono = forms.IntegerField(label=_(u"Teléfono"),required=False)
	email = forms.CharField(max_length=100, label=_(u"Email"),required=False)
	miembro = forms.CharField(max_length=100, label=_(u"Miembro"),required=False)
	cuenta = forms.CharField(max_length=100, label=_(u"Cuenta"),required=False)
	orden = forms.ChoiceField(choices=ORDEN_USU, label=_(u"Ordenar por"),required=False)

	def __init__(self, *args, **kwargs):
		super(Form_busqueda_usuarios, self).__init__(*args, **kwargs)
		self.fields['grupo'].queryset = Grupo.objects.filter(activo=True)

#######################################################################################################################################################









