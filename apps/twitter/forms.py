# coding=utf-8
from django import forms
#from django.contrib.localflavor.es.forms import *
from django.utils.translation import ugettext as _
from twitter.models import *
#from utilidades.combox import *
from django.forms.extras.widgets import *


############################################################################################################################

class Form_seguir(forms.Form):
	
   usu = forms.IntegerField(widget=forms.HiddenInput())
   accion = forms.IntegerField(widget=forms.HiddenInput())

############################################################################################################################

#class Form_escribir(forms.ModelForm):
	
	#class Meta:
		#model = Mensaje
		#fields = ('usuario', 'contenido')
		#widgets = {
			#'usuario': forms.HiddenInput(),
			#}


############################################################################################################################
class Form_escribir(forms.Form):
	
	usu = forms.IntegerField(widget=forms.HiddenInput())
	respuesta = forms.IntegerField(widget=forms.HiddenInput())
	contenido = forms.CharField(max_length=255, widget=forms.Textarea())
	
	"""El clean me lanza un error que no sé que hacer
	Exception Type:	KeyError
	Exception Value:'contenido'
	Exception Location:	/home/mene/www/virtualenv/market/apps/social/forms.py in clean, line 45

	/home/mene/www/virtualenv/market/apps/social/views.py in escribir
	line 63:  if form.is_valid(): 
	"""
	
	#def clean(self):
		
		#if self.cleaned_data['contenido'] == u'':
			#raise forms.ValidationError(_(u'Debes escribir algo.'))
		#else:
			#return self.cleaned_data