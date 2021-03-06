#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Author: Eric Vandecasteele 2018
# http://blog.onlinux.fr
#
# Import required Python libraries
import os
import requests
import settings
from Zapi import ZiBase
import logging
import logging.config
import paho.mqtt.publish as publish
from hermes_python.hermes import Hermes
from snipshelpers.config_parser import SnipsConfigParser

# Fixing utf-8 issues when sending Snips intents in French with accents
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

CONFIG_INI = "config.ini"
MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))
SITE = "default"
SOUNDFILE = "./test/ia_ora-notification.wav"
binaryFile = open(SOUNDFILE, mode='rb')
wav = bytearray(binaryFile.read())


GESTION_VOLETS = 'ericvde31830:gestionVolets'
LIGHTSOFF = 'ericvde31830:lightsTurnOff'
LIGHTSSET = 'ericvde31830:lightsSet'
ASKTEMP = 'ericvde31830:ask4TempHum'
ALL_INTENTS = [GESTION_VOLETS, LIGHTSOFF, LIGHTSSET]

# os.path.realpath returns the canonical path of the specified filename,
# eliminating any symbolic links encountered in the path.
path = os.path.dirname(os.path.realpath(sys.argv[0]))
configPath = path + '/' + CONFIG_INI

logging.config.fileConfig(configPath)
logger = logging.getLogger(__name__)


def intent_received(hermes, intent_message):
    intentName = intent_message.intent.intent_name
    sentence = 'Voilà c\'est fait.'
    logger.debug(" Session started, intentName = {}".format(intentName))
    logger.debug(" sessionID: {}".format(intent_message.session_id))
    logger.debug(" session site ID: {}".format(intent_message.site_id))
    logger.debug(" custumData: {}".format(intent_message.custom_data))

    for (slot_value, slot) in intent_message.slots.items():
        print('Slot {} -> \n\tRaw: {} \tValue: {}'
              .format(slot_value, slot[0].raw_value, slot[0].slot_value.value.value))

    if intentName == ASKTEMP:
        arg = None
        if intent_message.slots.house_room:
            room_slot = intent_message.slots.house_room.first()
            room = room_slot.value.encode('utf-8')
        elif intent_message.slots.device:
            room_slot = intent_message.slots.device.first()
            room = room_slot.value.encode('utf-8')
        else:
            room = 'salon'

        logger.debug(room)

        if room is not None and room in settings.PROBEID:
            arg = settings.PROBEID.get(room)
            logger.debug("ProbeId {}".format(arg))
        else:
            sentence = 'Il n\'y a pas de sonde dans la pièce {}'.format(room)
            hermes.publish_end_session(intent_message.session_id, sentence)
            return

        if zibase is not None and arg is not None:

            """ Retourne les valeurs v1 et v2 du capteur spécifié
            ainsi que la date heure du relevé.
            Pour les sondes Oregon et TS10, il faut diviser v1 par 10.
            Tableau en retour :
            index 0 => date du relevé
            index 1 => v1
            index 2 => v2
            """
            probeValues = zibase.getSensorInfo(arg)

            if probeValues is None:
                # Probably, probeId value is wrong withing setting.py!
                logger.warning("exception while retrieving sensor info!")
                sentence = 'Désolé mais la zibase indique une erreur dans le retour de la sonde'
                hermes.publish_end_session(intent_message.session_id, sentence)
                return

            else:
                temp = str(float(probeValues[1]) / 10).replace('.', ',')

                if probeValues[2] > 0:
                    hum = probeValues[2]
                    sentence = "Il y fait {} degrés pour une humidité de {}% .".format(
                        temp, hum)
                else:
                    sentence = "Il y fait {} degrés.".format(temp)

        else:
            sentence = 'Désolé mais je n\'arrive pas à communiquer avec la zibase.'

        hermes.publish_end_session(intent_message.session_id, sentence)
        return

    if intentName == LIGHTSOFF:
        arg = None

        if intent_message.slots.house_room:
            room_slot = intent_message.slots.house_room.first()
            room = room_slot.value.encode('utf-8')
            logger.debug(room)
            if room not in settings.LIGHTID and room not in settings.SONOFFID:
                sentence = 'Désolée, mais je ne peux pas agir dans la pièce nommée {}'.format(
                    room)
                hermes.publish_end_session(intent_message.session_id, sentence)
                logger.debug(" " + sentence)
                logger.debug(
                    " Session started, intentName = {}".format(intentName))
                return
        else:
            room = None
            sentence = 'Je n\'ai pas saisi la pièce . Répétez s\'il vous plaît.'
            hermes.publish_continue_session(
                intent_message.session_id, sentence, ALL_INTENTS)
            return

        if room is not None and room in settings.LIGHTID:
            arg = settings.LIGHTID.get(room)
            logger.debug(arg)

            if arg is not None:
                for i, item in enumerate(arg):
                    logger.debug(item)
                    url = "http://{}/cgi-bin/domo.cgi?cmd=OFF {}".format(
                        ip, item)
                    logger.debug(url)
                    try:
                        resp = requests.get(url)
                        logger.debug(resp.text)
                    except requests.ConnectionError, e:
                        # Trick to bypass the wrong return status of zibase
                        # Even if request is ok, zibase returns ('Connection aborted.', BadStatusLine('OK\r\n',))
                        if 'OK' not in str(e):
                            sentence = 'Désolé mais çà n\'a pas marché. Peut être un problème de connexion à la zibase.'
                            logger.warning(e)
                            hermes.publish_end_session(
                                intent_message.session_id, sentence)
                        else:
                            sentence = "Ok, c'est fait"
                            hermes.publish_end_session(
                                intent_message.session_id, sentence)
                            logger.debug(sentence)
                            return

        elif room is not None and room in settings.SONOFFID:
            arg = settings.SONOFFID.get(room)
            logger.debug(arg)

            if arg is not None:
                for i, item in enumerate(arg):
                    logger.debug(item)
                    logger.debug(i)

                    url = "http://{}/cm?user={}&password={}&cmnd=Power%20off".format(
                        item, sonoffUser, sonoffPassword)
                    logger.debug(url)
                    try:
                        resp = requests.get(url)
                        logger.debug(resp.text)

                    except requests.ConnectionError, e:
                        sentence = 'Désolé mais çà n\'a pas marché. Peut être un problème avec le sonoff.'
                        logger.warning(e)

                logger.debug(sentence)
                hermes.publish_end_session(intent_message.session_id, sentence)

        else:
            sentence = 'Désolé mais je ne connais pas cette pièce. S\'il vout plaît, indiquez la pièce plus clairement.'
            logger.debug(sentence)
            hermes.publish_end_session(intent_message.session_id, sentence)

    if intentName == LIGHTSSET:
        arg = None
        percentage = None

        if intent_message.slots.house_room:
            room_slot = intent_message.slots.house_room.first()
            room = room_slot.value.encode('utf-8')
            logger.debug("Room: {}".format(room))
            if room not in settings.LIGHTID and room not in settings.SONOFFID:
                sentence = 'Désolée, mais je ne peux pas agir dans la pièce nommée {}'.format(
                    room)
                hermes.publish_end_session(intent_message.session_id, sentence)
                logger.debug(" " + sentence)
                logger.debug(
                    " Session started, intentName = {}".format(intentName))
                return

        else:
            room = None
            sentence = 'Désolée mais je n\'ai pas bien saisi la pièce . Répétez s\'il vous plaît.'
            hermes.publish_continue_session(
                intent_message.session_id, sentence, ALL_INTENTS)
            return

        if room is not None and room in settings.LIGHTID:
            # Devices driven by ZiBase
            arg = settings.LIGHTID.get(room)
            logger.debug("LIGHTID: {}".format(arg))

            if intent_message.slots.intensity_percent:
                percentage = intent_message.slots.intensity_percent.first().value
                logger.debug(percentage)

            if arg is not None:
                for i, item in enumerate(arg):
                    logger.debug(item)
                    if percentage is not None:
                        url = "http://{}/cgi-bin/domo.cgi?cmd=DIM {} P3 {}".format(
                            ip, item, percentage)
                    # Start scenario 49. Turns on light for 5 minutes.
                    elif item == 'G6':
                        url = "http://{}/cgi-bin/domo.cgi?cmd=LM49".format(ip)
                    else:
                        url = "http://{}/cgi-bin/domo.cgi?cmd=ON {}".format(
                            ip, item)
                    try:
                        logger.debug(url)
                        resp = requests.get(url)
                        logger.debug(resp.text)
                    except requests.ConnectionError, e:
                        # Trick to bypass the wrong return status of zibase
                        # Even if request is ok, zibase returns ('Connection aborted.', BadStatusLine('OK\r\n',))
                        if 'OK' not in str(e):
                            logger.warning(e)
                            sentence = 'Désolé mais çà n\'a pas marché. Peut être un problème de connexion à la zibase.'

                    hermes.publish_end_session(
                        intent_message.session_id, sentence)
                    return

        elif room is not None and room in settings.SONOFFID:
            # Devices driven by sonoff
            arg = settings.SONOFFID.get(room)
            logger.debug(arg)

            if arg is not None:
                for i, item in enumerate(arg):
                    logger.debug(item)
                    url = "http://{}/cm?user={}&password={}&cmnd=Power%20on".format(
                        item, sonoffUser, sonoffPassword)
                    logger.debug(url)
                    try:
                        resp = requests.get(url)
                        logger.debug(resp.text)
                    except requests.ConnectionError, e:
                        sentence = 'Désolé mais çà n\'a pas marché. Peut être un problème de connexion au sonoff.'
                        logger.warning(e)

                logger.debug(sentence)
                publish.single("hermes/audioServer/{}/playBytes/whateidver".format(SITE),
                               payload=wav, hostname=MQTT_IP_ADDR, client_id="")
                hermes.publish_end_session(intent_message.session_id, sentence)

        else:
            sentence = 'Désolé mais je ne reconnais pas cette pièce. Indiquez l\'endroit plus clairement, merci!'
            logger.debug(sentence)
            hermes.publish_end_session(intent_message.session_id, sentence)

    if intentName == GESTION_VOLETS:
        arg = None
        action = None
        url = None
        sentence = "Ok, j'ai bien envoyé l'ordre aux volets"

        if intent_message.slots.house_room:
            room_slot = intent_message.slots.house_room.first()
            room = room_slot.value.encode('utf-8')
            logger.debug(room)

            if room not in settings.ROLLERSHUTTERID:
                sentence = 'Désolée, mais je ne peux pas agir sur les volets de la pièce nommée {}'.format(
                    room)
                hermes.publish_end_session(intent_message.session_id, sentence)
                logger.debug(" " + sentence)
                logger.debug(
                    " Session started, intentName = {}".format(intentName))
                return

        else:
            # Slot room not present
            room = None
            sentence = 'Je n\'ai pas saisi la pièce . Répétez s\'il vous plaît.'
            hermes.publish_continue_session(
                intent_message.session_id, sentence, GESTION_VOLETS)
            return

        if room is not None and room in settings.ROLLERSHUTTERID:
            arg = settings.ROLLERSHUTTERID[room]
            logger.debug(arg)

            if intent_message.slots.action:
                action_slot = intent_message.slots.action.first()
                action = action_slot.value

                if action is not None and arg is not None:
                    for i, item in enumerate(arg):
                        logger.debug(item)
                        if action == 'lever':
                            url = "http://{}/cgi-bin/domo.cgi?cmd=ON {} P10".format(
                                ip, item)
                        elif action == 'entre-ouvrir':
                            url = "http://{}/cgi-bin/domo.cgi?cmd=DIM {} P10 100".format(
                                ip, item)
                        elif action == 'baisser':
                            url = "http://{}/cgi-bin/domo.cgi?cmd=off {} P10".format(
                                ip, item)
                        else:
                            sentence = 'Désolé mais je n\'ai pas compris.'
                            url = None

                        if url is not None:
                            logger.debug(url)
                            try:
                                resp = requests.get(url)
                                logger.debug(resp.text)
                            except requests.ConnectionError, e:
                                # Trick to bypass the wrong return status of zibase
                                # Even if request is ok, zibase returns ('Connection aborted.', BadStatusLine('OK\r\n',))
                                if 'OK' not in str(e):
                                    sentence = 'Désolé mais çà n\'a pas marché. Peut être un problème de connexion à la zibase.'
                                    logger.warning(e)

                                else:
                                    sentence = "Ok, c'est fait"
                                    logger.debug(sentence)

                logger.debug(sentence)
                hermes.publish_end_session(intent_message.session_id, sentence)
        else:
            sentence = 'Désolé mais je ne connais pas cette pièce '
            logger.debug(sentence)
            hermes.publish_end_session(intent_message.session_id, sentence)


with Hermes(MQTT_ADDR) as h:

    try:
        config = SnipsConfigParser.read_configuration_file(CONFIG_INI)
    except:
        config = None

    zibase = None
    hostname = None
    ip = None
    sonoffUser = None
    sonoffPassword = None

    if config:
        sonoffUser = config.get(
            'secret', {
                "sonoffuser": "sonoffuser"}).get(
            'sonoffuser', 'sonoffuser')

        sonoffPassword = config.get(
            'secret', {
                "sonoffpassword": "sonoffpassword"}).get(
            'sonoffpassword', 'sonoffpassword')

    if config and config.get('secret', None) is not None:
        if config.get('secret').get('ip_zibase', None) is not None:
            ip = config.get('secret').get('ip_zibase')
            if ip == "":
                ip = None

        logger.info("Address ip ZiBase:{}".format(ip))

    if ip is not None:
        try:
            zibase = ZiBase.ZiBase(ip)
            logger.info('ZiBase initialization: OK')
        except Exception as e:
            zibase = None
            logger.error('Error Zapi {}'.format(e))

    h.subscribe_intent(LIGHTSOFF, intent_received) \
        .subscribe_intent(LIGHTSSET, intent_received) \
        .subscribe_intent(GESTION_VOLETS, intent_received) \
        .start()
