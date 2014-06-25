# coding=utf-8

# Copyright (C) 2014 by Víctor Romero Blanco <info at playcircular dot com>.
# http://playcircular.com/
# It's licensed under the AFFERO GENERAL PUBLIC LICENSE unless stated otherwise.
# You can get copies of the licenses here: http://www.affero.org/oagpl.html
# AFFERO GENERAL PUBLIC LICENSE is also included in the file called "LICENSE".

from django import forms
from configuracion.models import *
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.forms.util import ErrorList


class Configuracion_Admin_Form(forms.ModelForm):
    class Meta:
        model = Configuracion
        exclude = ("usuairo",)

                  
    def clean(self):
		config = Configuracion.objects.all()
		if config.exists() and not self.initial:
			self._errors.setdefault('__all__', ErrorList()).append("Ya existe una configuración. Para hacer cambios edite la existente.")
		return self.cleaned_data
