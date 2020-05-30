#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import gettext
import traceback
import sys
from ikabot.config import *
from ikabot.helpers.botComm import *
from ikabot.helpers.gui import enter
from ikabot.helpers.varios import esperar
from ikabot.helpers.signals import setInfoSignal
from ikabot.helpers.pedirInfo import getIdsdeIslas
from ikabot.helpers.getJson import getIsla
from ikabot.helpers.process import forkear

t = gettext.translation('buscarEspacios', 
                        localedir, 
                        languages=idiomas,
                        fallback=True)
_ = t.gettext

def buscarEspacios(s,e,fd):
	sys.stdin = os.fdopen(fd)
	if botValido(s) is False:
		e.set()
		return
	print(_('Se buscarán espacios nuevos cada hora.'))
	read()

	forkear(s)
	if s.padre is True:
		return

	e.set()

	info = _('\nBusco espacios nuevos en las islas cada 1 hora\n')
	setInfoSignal(s, info)
	try:
		do_it(s)
	except:
		msg = _('Error en:\n{}\nCausa:\n{}').format(info, traceback.format_exc())
		sendToBot(s, msg)
	finally:
		s.logout()

def do_it(s):
	isla_ciudades = {}
	while True:
		idIslas = getIdsdeIslas(s) #gets the ids of the islands
		for idIsla in idIslas: #for each island id
			html = s.get(urlIsla + idIsla) #get html
			isla = getIsla(html) #parse html into island object
			ciudades = [ciudad for ciudad in isla['cities'] if ciudad['type'] != 'empty'] #loads the islands non empty cities into ciudades

			if idIsla in isla_ciudades: #for each island
				ciudadesAntes = isla_ciudades[idIsla] #loads into ciudadesAntes the current islands cities

				# alguien desaparecio - someone disappeared
				for cityAntes in ciudadesAntes: #for each beforecity on the island
					for ciudad in ciudades: #for each city
						if ciudad['id'] == cityAntes['id']: #compare current city's id with beforecity's id
							break
					else:
						msg = _('la ciudad {} del jugador {} desapareció en {} {}:{} {}').format(cityAntes['name'], cityAntes['Name'], tipoDeBien[int(isla['good'])], isla['x'], isla['y'], isla['name'])
						sendToBot(s, msg)

				# alguien fundo - someone colonised
				for ciudad in ciudades: #for each city on the island
					for cityAntes in ciudadesAntes: #for each beforecity
						if ciudad['id'] == cityAntes['id']: #compare current city's id with beforecity's id
							break
					else:
						msg = _('{} fundó {} en {} {}:{} {}').format(ciudad['Name'], ciudad['name'], tipoDeBien[int(isla['good'])], isla['x'], isla['y'], isla['name'])
						sendToBot(s, msg)

			isla_ciudades[idIsla] = ciudades.copy() #copies non empty cities into current islands cities (isla_ciudades)
		esperar(1*60*60) #wait
