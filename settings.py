#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author: Eric Vandecasteele 2018
# http://blog.onlinux.fr
#


ROLLERSHUTTERID = {
    'rez-de-chaussée':      ['C3','C2', 'C1'],
    'du bas':               ['C3','C2', 'C1'],
    'salon':                ['C3','C2'],
    'salle à manger':       ['C3','C2'],
    'premier étage':        ['C6', 'C4', 'C5', 'C7'],
    'du haut':              ['C6', 'C4', 'C5', 'C7'],
    'chambre':              ['C7'],
    'gauche' :              ['C3'], # salon gauche
    'droit'  :              ['C2'], # salon droit
    'cuisine':              ['C1'],
    'chambre de Gaby':      ['C6'],
    'chambre de Caroline':  ['C4'],
    'salle de bains':       ['C5']
}

SONOFFID = {
    'tableau':          ['sonoff1-3395'],
    'salon' :           ['sonoff2-6546','sonoff1-3395'],
    'lampe' :           ['sonoff2-6546']
}

LIGHTID = {
    'du bas':               ['G4','G5','G2'],
    'rez de chaussée':      ['G4','G5','G2'],
    'prise camera cuisine': ['G3'],
    'prise camera foscam':  ['G10'],
    'salle à manger':       ['G4'],
    'patio'     :           ['G5'],
    'extérieur' :           ['G5'],
    'cuisine'   :           ['G2'],
    'buanderie' :           ['G6']
}

PROBEID = {
    'salon':                'OS439158532',
    'salle à manger':       'OS439158532',
    'congélateur':          'OS439204611',
    'patio':                'OS3391881217',
    'auriol':               'OS439204622',
    'chambre de Caroline':  'OS439183105',
    'salle de bain':      'OS439219713',
    'chambre parentale':    'OS439195137',
    'chambre':              'OS439195905',
}
