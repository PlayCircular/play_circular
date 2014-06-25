# coding=UTF-8


# Copyright (C) 2014 by Víctor Romero Blanco <info at playcircular dot com>.
# http://playcircular.com/
# It's licensed under the AFFERO GENERAL PUBLIC LICENSE unless stated otherwise.
# You can get copies of the licenses here: http://www.affero.org/oagpl.html
# AFFERO GENERAL PUBLIC LICENSE is also included in the file called "LICENSE".

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

ROBOTS_CHOICES = (
    ('index, follow', 'index, follow'),
    ('noindex, follow', 'noindex, follow'),
)

class Metatag(models.Model):
    """
    Meta Tags para SEO
    """
    robots      = models.CharField(max_length=32, choices=ROBOTS_CHOICES, default='index, follow', verbose_name=_(u'meta robots'),help_text=_(u'Por defecto \"index, follow\"'))
    titulo      = models.CharField(max_length=70, blank=True, null=True, verbose_name=_(u'meta titulo'), help_text=_(u'Titulo de la pagina. Máx. 70 car.'))
    descripcion = models.CharField(max_length=150, blank=True, null=True, verbose_name=_(u'meta description'), help_text=_(u'Breve descripción. Relacionado con el texto. Máx. 150 car.'))
    palabras_clave  = models.CharField(max_length=150, blank=True, null=True, verbose_name=_(u'meta keyword'), help_text=_(u'Palabras clave separadas por comas. Relacionado con el texto. Máx. 150 car.'))
    content_type= models.ForeignKey(ContentType)
    object_id   = models.PositiveIntegerField()
    content_object  = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
       return self.titulo
