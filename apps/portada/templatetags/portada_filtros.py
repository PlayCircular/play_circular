# -*- coding: utf-8 -*-


from django import template
#from django.contrib.auth.models import User
#from utilidades.views import *
#from grupos.models import *
from paginas.models import *
#from paginas.models import Paginas, Idiomas_pagina


register = template.Library()

@register.filter(name='get_titulo_idioma')
def get_titulo_idioma(pk,value):
	try:
		idioma = Idiomas_pagina.objects.get(pagina=pk, idioma=value)
	except Idiomas_pagina.DoesNotExist:
		idiomas_qs = Idiomas_pagina.objects.filter(pagina=pk).order_by('-idioma_default')
		idioma = idiomas_qs[0]
		
	return unicode(idioma)
		
	#try:
		#idioma = Paginas.objects.get(pk=pk)
	#except Paginas.DoesNotExist:
		#idiomas_qs = Paginas.objects.filter(pk=pk)
		#idioma = idiomas_qs[0]
	#return unicode(idioma.estado)