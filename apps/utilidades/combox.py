# -*- coding: utf-8 -*-

# Copyright (C) 2014 by Víctor Romero Blanco <info at playcircular dot com>.
# http://playcircular.com/
# It's licensed under the AFFERO GENERAL PUBLIC LICENSE unless stated otherwise.
# You can get copies of the licenses here: http://www.affero.org/oagpl.html
# AFFERO GENERAL PUBLIC LICENSE is also included in the file called "LICENSE".

from django.contrib.sites.models import Site
from django.conf import settings
from django.utils.translation import ugettext as _


PROVINCIAS = (
	('Alava', 'Alava'),
	('Albacete', 'Albacete'),
	('Alicante', 'Alicante'),
	(u'Almería', u'Almería'),
	('Ávila', 'Ávila'),
	('Badajoz', 'Badajoz'),
	('Baleares', 'Baleares'),
	('Barcelona', 'Barcelona'),
	('Burgos', 'Burgos'),
	('Cáceres', 'Cáceres'),
	('Cádiz', 'Cádiz'),
	('Castellón', 'Castellón'),
	('Ciudad Real', 'Ciudad Real'),
	('Córdoba', 'Córdoba'),
	('A Coruña', 'A Coruña'),
	('Cuenca', 'Cuenca'),
	('Girona', 'Girona'),
	('Granada', 'Granada'),
	('Guadalajara', 'Guadalajara'),
	('Guipúzcoa', 'Guipúzcoa'),
	('Huelva', 'Huelva'),
	('Huesca', 'Huesca'),
	('Jaén', 'Jaén'),
	('León', 'León'),
	('Lleida', 'Lleida'),
	('La Rioja', 'La Rioja'),
	('Lugo', 'Lugo'),
	('Madrid', 'Madrid'),
	('Málaga', 'Málaga'),
	('Murcia', 'Murcia'),
	('Navarra', 'Navarra'),
	('Ourense', 'Ourense'),
	('Asturias', 'Asturias'),
	('Palencia', 'Palencia'),
	('Las Palmas', 'Las Palmas'),
	('Pontevedra', 'Pontevedra'),
	('Salamanca', 'Salamanca'),
	('S.C.Tenerife', 'S.C.Tenerife'),
	('Cantabria', 'Cantabria'),
	('Segovia', 'Segovia'),
	('Sevilla', 'Sevilla'),
	('Soria', 'Soria'),
	('Tarragona', 'Tarragona'),
	('Teruel', 'Teruel'),
	('Toledo', 'Toledo'),
	('Valencia', 'Valencia'),
	('Valladolid', 'Valladolid'),
	('Vizcaya', 'Vizcaya'),
	('Zamora', 'Zamora'),
	('Zaragoza', 'Zaragoza'),
	('Ceuta', 'Ceuta'),
	('Melilla', 'Melilla'),
)

TIPO_PAGINA = (
	('p_principal', _(u'Página principal')),
	('p_grupo', _(u'Página de grupo')),
)

TIPO_ENTRADA = (
	('e_general', _(u'Entrada general')),
	('e_grupo', _(u'Entrada de grupo')),
	('propuesta_general', _(u'Propuesta general')),
	('propuesta_grupo', _(u'Propuesta de grupo')),
)
ROBOTS_CHOICES = (
    ('index, follow', 'index, follow'),
    ('noindex, follow', 'noindex, follow'),
)

TIPO_BANNER = (
	('superior', _(u'Superior')),
	('laterial', _(u'Lateral')),
)

VISIBILIDAD_PAGINA = (
	('publica', _(u'Pública')),
	('privada', _(u'Privada')),
)
ESTADO_PAGINA = (
	('publicada', _(u'Publicada')),
	('borrador', _(u'Borrador')),
)

PAISES = (
	(_(u'España'), _(u'España')),
	(_(u'Francia'), _(u'Francia')),
	(_(u'Inglaterra'), _(u'Inglaterra')),
	(_(u'Alemania'), _(u'Alemania')),
)

IDIOMAS = (
	(_(u'es'), _(u'Español')),
	(_(u'en'), _(u'Inglés')),
	(_(u'fr'), _(u'Frances')),
	(_(u'ge'), _(u'Aleman')),
	(_(u'gr'), _(u'Griego')),
	(_(u'it'), _(u'Italiano')),
	(_(u'po'), _(u'Portugués')),
	(_(u'ca'), _(u'Catalán')),
)

CONDICION = (
	('', '------'),
	(_(u'Persona'), _(u'Persona')),
	(_(u'Empresa'), _(u'Empresa')),
	(_(u'Organización'), _(u'Organización')),
)

COMO_CONOCISTE = (
	(_(u'Internet'), _(u'Internet')),
	(_(u'Un amigo'), _(u'Un amigo')),
	(_(u'Por un mercadillo'), _(u'Por un mercadillo')),
	(_(u'Por publicidad'), _(u'Por publicidad')),
	(_(u'Otros'), _(u'Otros'))
)

TIPO_INTERCAMBIO = (
	(u'Normal', _(u'Normal')),
	(u'Intergrupos', _(u'Intergrupos')),
	(u'Imp_interno', _(u'Impuesto interno')),
	(u'Imp_externo', _(u'Impuesto externo')),
)

TIPO_ALTA = (
	('Online', _(u'Directamente online')),
	('Revisada', _(u'Online pero revisada por un administrador')),
	('Presencial', _(u'Presencial')),
)

CLASES_ENTIDADES = (
	(_(u'Asociación'), _(u'Asociación')),
	(_(u'Empresa privada'), _(u'Empresa privada')),
	(_(u'Cooperativa'), _(u'Cooperativa')),
	(_(u'Gobierno regional'), _(u'Gobierno regional')),
	(_(u'Institución educativa'), _(u'Institución educativa')),
)

NIVEL = (
	(_(u'Baja'), _(u'Baja')),
	(_(u'Media'), _(u'Media')),
	(_(u'Alta'), _(u'Alta')),
	(_(u'Muy alta'), _(u'Muy alta')),
)


GRADO = (
	(u'Visitante', _(u'Visitante')),
	(u'Normal', _(u'Normal')),
	(u'Editor', _(u'Editor')),
	(u'Administrador', _(u'Administrador')),
)

TIPOS_CUENTA = (
	(u'Normal', _(u'Normal')),
	(u'Administrador', _(u'Administrador')),
	(u'Renta Básica', _(u'Renta Básica')),
	(u'Intergrupos', _(u'Intergrupos')),
)

PROGRESO = (
	(_(u'Enviado'), _(u'Enviado')),
	(_(u'En estudio'), _(u'En estudio')),
	(_(u'Concluida'), _(u'Concluida')),
)

SINO = (
	(1, _(u'Si')),
	(0, _(u'No')),
)

TRUE_FALSE = (
	(0, 0),
	(1, 1),
)

ESTADO = (
	(_(u'Pendiente'), _(u'Pendiente')),
	(_(u'Concluído'), _(u'Concluído')),
	(_(u'Error'), _(u'Error')),
)
# el -2 es la opción vacía. Con jquery compruebo que tiene que ser mayor que -2
RATING = (
	(-2,''),
	(-1,-1),
	(0,0),
	(1,1),
	(2,2),
	(3,3),
	(4,4),
	(5,5),
	(6,6),
	(7,7),
	(8,8),
	(9,9),
	(10,10)
)

RATING_ENTRADA = (
	(0,0),
	(1,1),
	(2,2),
	(3,3),
	(4,4),
	(5,5),
	(6,6),
	(7,7),
	(8,8),
	(9,9),
	(10,10)
)

PERIODICIDAD_INTERES = (
	(_(u'Ninguna'), _(u'Ninguna')),
	(_(u'Cada semana'), _(u'Cada semana')),
	(_(u'Cada dos semanas'), _(u'Cada dos semanas')),
	(_(u'Cada tres semanas'), _(u'Cada tres semanas')),
	(_(u'Cada mes'), _(u'Cada mes')),
	(_(u'Cada dos meses'), _(u'Cada dos meses')),
	(_(u'Cada tres meses'), _(u'Cada tres meses')),
	(_(u'Cada cuatro meses'), _(u'Cada cuatro meses')),
	(_(u'Cada seis meses'), _(u'Cada seis meses')),
)

FUNCION = (
	(_(u'Moneda'), _(u'Moneda')),
	(_(u'Tiempo'), _(u'Tiempo')),
)


CLASE_ACTIVIDAD = (
	(_(u'bienes'), _(u'Bienes')),
	(_(u'servicios'), _(u'Servicios')),
)

TIPO_ACTIVIDAD = (
	(_(u'oferta'), _(u'Oferta')),
	(_(u'demanda'), _(u'Demanda')),
)

GRUPOS_BUSQUEDA = (
	(_(u'Mis grupos'), _(u'Mis grupos')),
	(_(u'Todos los grupos'), _(u'Todos los grupos')),
)

ORDEN = (
	(_(u'clase'), _(u'clase')),
	(_(u'tipo'), _(u'tipo')),
)

ORDEN_USU = (
	(_(u'fecha de alta'), _(u'fecha de alta')),
	(_(u'último acceso'), _(u'último acceso')),
)

MENSAJES_EN_PAGINA = 8
MENSAJES_EN_PERFIL = 8