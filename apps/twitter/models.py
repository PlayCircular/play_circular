# coding=utf-8

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import re
from urllib import urlencode
from django.utils.translation import ugettext as _

############################################################################################################################

class Mensaje(models.Model):

	usuario = models.ForeignKey(User, related_name='usu_mensaje',editable=False)
	contenido = models.TextField(_(u"Contenido"),max_length = 500)
	reescrito = models.BooleanField(_(u"Reenviar"), default=False, blank=True)
	respuesta = models.IntegerField(_(u"Respuesta"), null=True, blank=True)
	activo = models.BooleanField(_(u"Activo"), default=True)
	creado = models.DateTimeField(_(u"Creado"),auto_now_add=True)
	modificado = models.DateTimeField(_(u"Modificado"),auto_now=True)

	def __unicode__(self):
		return self.contenido
		
	def filtrar(self):
		"""Filtra XSS enlaza hashtags, menciones y enlaces """
		t = self.contenido

		#Anti XSS
		t = t.replace('&','&amp;')
		t = t.replace('<','&lt;')
		t = t.replace('>','&gt;')
		t = t.replace('\'','&#39;')
		t = t.replace('"','&quot;')

		hashtags = re.findall('#[a-zA-Z][a-zA-Z0-9_-]*', t)
		for hashtag in hashtags:
			"""El simbolo '#' no puedo mandarlo en las variables de expresion regular por url así que lo quito."""
			v = hashtag.replace('#','')
			t = t.replace(hashtag, '<a href="/social/buscar/%s/1">%s</a>' % (v, hashtag))

		links = re.findall('http\\:\\/\\/[^ ]+', t)
		for link in links:
			t = t.replace(link, '<a href="%s">%s</a>' % (link, link))

		menciones = re.findall('\\@[a-zA-Z0-9_]+', t)
		for mencion in menciones:
			t = t.replace(mencion, '<a href="/social/perfil_social/%s/">%s</a>' % (mencion[1:], mencion))

		return t

############################################################################################################################

class Votos_mensaje(models.Model):

	usuario = models.ForeignKey(User, related_name='usu_voto_mensaje')
	mensaje = models.ForeignKey(Mensaje, related_name='votos_mensaje')
	puntuacion = models.PositiveIntegerField(_(u"Valoración"),default=0,editable=False)
	creado = models.DateTimeField(_(u"Creado"),auto_now_add=True)
	modificado = models.DateTimeField(_(u"Modificado"),auto_now=True)

	class Meta:
		verbose_name = _(u'voto del mensaje')
		verbose_name_plural = _(u'votos de los mensajes')
		
############################################################################################################################


class Seguimiento(models.Model):
	seguidor = models.ForeignKey(User, related_name='seguidor',editable=False)
	seguido = models.ForeignKey(User, related_name='seguidos')
	activo = models.BooleanField(_(u"Activo"), default=True)
	creado = models.DateTimeField(_(u"Creado"),auto_now_add=True)
	modificado = models.DateTimeField(_(u"Modificado"),auto_now=True)

############################################################################################################################



