# coding=utf-8

# Copyright (C) 2014 by Víctor Romero <info at playcircular dot com>.
# http://playcircular.com/
# It's licensed under the AFFERO GENERAL PUBLIC LICENSE unless stated otherwise.
# You can get copies of the licenses here: http://www.affero.org/oagpl.html
# AFFERO GENERAL PUBLIC LICENSE is also included in the file called "LICENSE".

from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, render_to_response
from django.core.urlresolvers import reverse
from usuarios.models import *
from grupos.models import *
from actividades.models import *
from economia.models import *
from economia.views import *
from utilidades.views import *
from django.contrib.sites.models import Site,get_current_site
from django.utils.translation import ugettext as _
from django.core.mail import send_mail, send_mass_mail, BadHeaderError
from settings import MEDIA_ROOT, MEDIA_URL
from django.template import RequestContext, loader
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib.auth.decorators import login_required

#######################################################################################################################################################
@login_required
def importar_1(request):

	situacion = _(u'Importar datos del CES')

	datos = {'situacion':situacion}


	return render_to_response("ces/importar_1.html",datos,context_instance=RequestContext(request, processors=[custom_proc])) 

#######################################################################################################################################################



