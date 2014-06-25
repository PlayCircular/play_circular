#coding=utf-8

# Copyright (C) 2014 by Víctor Romero Blanco <info at playcircular dot com>.
# http://playcircular.com/
# It's licensed under the AFFERO GENERAL PUBLIC LICENSE unless stated otherwise.
# You can get copies of the licenses here: http://www.affero.org/oagpl.html
# AFFERO GENERAL PUBLIC LICENSE is also included in the file called "LICENSE".

from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib.sitemaps import GenericSitemap
from actividades.models import *
from paginas.models import *
from paginas.feeds import *
from actividades.feeds import *

# añadido por las modificaciones en el django-registration
from django.contrib.auth import views as auth_views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

actividades_dict = {
    'queryset': Idiomas_actividad.objects.all(),
    'date_field': 'creado',
}

paginas_dict = {
    'queryset': Idiomas_pagina.objects.filter(pagina__estado='publicada',pagina__visibilidad='publica'),
    'date_field': 'creado',
}

entradas_dict = {
    'queryset': Idiomas_entrada.objects.filter(entrada__estado='publicada',entrada__visibilidad='publica'),
    'date_field': 'creado',
}


sitemap = {
    'paginas': GenericSitemap(paginas_dict, priority=0.5, changefreq='weekly'),
    'entradas': GenericSitemap(entradas_dict, priority=0.5, changefreq='weekly'), 
    'actividades': GenericSitemap(actividades_dict, priority=0.5, changefreq='weekly'), 
}

urlpatterns = patterns('',


	########## PERSONALIZACION DE LA ADMINISTRACIÓN ###########
	########## ACTIVIDADES #########
	url(r'^admin/recarga_miembros_actividad/$', 'actividades.admin_views.recarga_actividad', name='admin-recarga-actividad'),
	########## GRUPO #########
	url(r'^admin/recarga_miembros_grupo/$', 'grupos.admin_views.grupos_miembros_dependientes', name='admin-grupos-recarga-miembros-grupo'),
	
	########## PAGINAS #########
	url(r'^admin/recarga_entrada/$', 'paginas.admin_views.recarga_entrada', name='admin-entrada-recarga'),
	url(r'^admin/recarga_pagina/$', 'paginas.admin_views.recarga_pagina', name='admin-pagina-recarga'),

	########## ECONOMIA #########
	url(r'^admin/recarga_form_cuenta/$', 'economia.admin_views.eco_cuenta_codas_dependientes', name='admin-eco-recarga-form-cuenta'),
	url(r'^admin/recarga_form_intercambio_1/$', 'economia.admin_views.eco_cosas_dependientes_1', name='admin-eco-recarga-form-intercambio-1'),
	url(r'^admin/recarga_form_intercambio_2/$', 'economia.admin_views.eco_cosas_dependientes_2', name='admin-eco-recarga-form-intercambio-2'),
	url(r'^admin/recarga_form_intercambio_3/$', 'economia.admin_views.eco_cosas_dependientes_3', name='admin-eco-recarga-form-intercambio-3'),
	url(r'^admin/recarga_form_intercambio_4/$', 'economia.admin_views.eco_cosas_dependientes_4', name='admin-eco-recarga-form-intercambio-4'),
	
	url(r'^admin/', include(admin.site.urls)),

	########## INTERNALIZACION ###################################
	(r'^trans/', include('datatrans.urls')), #django-datatrans
	(r'^i18n/', include('django.conf.urls.i18n')),
	url(r'^rosetta/', include('rosetta.urls')),
	(r'^set_lang/(?P<lang>\w{2})/$','utilidades.views.set_lang'),

	########## PORTADA ###################################
	url(r'^$', 'portada.views.portada', name = "portada"),
	url(r'', include('portada.urls')),

	########## ACTIVIDADES ###################################
	(r'^actividad/', include('actividades.urls')),

	########## ECONOMIA ###################################
	(r'^economia/', include('economia.urls')),
	
	########## USUARIOS ###################################
	(r'^usuarios/', include('usuarios.urls')),
	
	########## DJANGO-ALLAUTH ###################################
	(r'^accounts/', include('allauth.urls')),
	
	########## Python Social Auth ###################################
	#url('', include('social.apps.django_app.urls', namespace='social')),
	#url('', include('django.contrib.auth.urls', namespace='auth')),
	
	########### LOGIN ###################################
	#url(r'^accounts/login/$', 'django.contrib.auth.views.login', name = "login"),
	#url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', kwargs=dict(next_page='/') , name = "logout"),
	#(r'^accounts/', include('registration.backends.default.urls')),

	########## twitter ###################################
	(r'^twitter/', include('twitter.urls')),

	########## GRUPOS ###################################
	(r'^grupos/', include('grupos.urls')),
	
	########## PAGINAS ###################################
	
	(r'^p/', include('paginas.urls')),
	
	########## PAGINAS ###################################
	
	(r'^ces/', include('ces.urls')),
	
	########## TINYMCE ###################################
	
	(r'^tinymce/', include('tinymce.urls')),
	
	########## SITEMAPS ###################################

	url(r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemap}),
	
	########## RSS ###################################
	
	url(r'^rss/entradas/$', Entradas_Generales_Feed(), name="rss-entradas-general"),
	url(r'^rss/entradas/(?P<simbolo>([^/]+))/$', Entradas_Grupo_Feed(), name="rss-entradas-grupo"),
	url(r'^rss/actividades/$', Actividades_Generales_Feed(), name="rss-actividades-general"),
	url(r'^rss/actividades/(?P<simbolo>([^/]+))/$', Actividades_Grupo_Feed(), name="rss-actividades-grupo"),
	
	########## CONFIGURACION ###################################
	

	(r'^%s/(?P<path>.*)$' % settings.MEDIA_URL[1:-1], 'django.views.static.serve',
	{'document_root': settings.MEDIA_ROOT}),
	
	# añadido por las modificaciones en el django-registration
	#override the default urls
	#url(r'^password/change/$',
				#auth_views.password_change,
				#name='password_change'),
	#url(r'^password/change/done/$',
				#auth_views.password_change_done,
				#name='password_change_done'),
	#url(r'^password/reset/$',
				#auth_views.password_reset,
				#name='password_reset'),
	#url(r'^password/reset/done/$',
				#auth_views.password_reset_done,
				#name='password_reset_done'),
	#url(r'^password/reset/complete/$',
				#auth_views.password_reset_complete,
				#name='password_reset_complete'),
	#url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
				#auth_views.password_reset_confirm,
				#name='password_reset_confirm'),

	##and now add the registration urls
	#url(r'', include('registration.backends.default.urls')),
)

#if 'rosetta' in settings.INSTALLED_APPS:
	#urlpatterns += patterns('',
		#url(r'^rosetta/', include('rosetta.urls')),
	#)

	
if settings.DEBUG:
	#urlpatterns += staticfiles_urlpatterns()
	urlpatterns += patterns('',
		#(r'^' + settings.STATIC_URL.lstrip('/'), include('appmedia.urls')),
		url(r'static/(?P<path>.*)$', 'django.views.static.serve', {
		'document_root': settings.STATIC_ROOT,
	}),
)
			