#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
from google.appengine.ext.webapp import template
from google.appengine.ext import ndb
from google.appengine.api import memcache

import os
import logging
import json
from datetime import datetime

from twilio.rest import TwilioRestClient

ACCOUNT_SID = "ACfdbf4dbda86dda79e8ccdf84c5274d49"
AUTH_TOKEN = "7197db58d257ae8d30b1225192361b33"

_DEBUG = True


class Greeting(ndb.Model):
    user = ndb.StringProperty()
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)


class Session(ndb.Model):
    server_number = ndb.StringProperty(indexed=False)
    start_time = ndb.DateTimeProperty(auto_now_add=True)
    last_active_time = ndb.DateTimeProperty(auto_now=True)


class Client(ndb.Model):
    name = ndb.StringProperty()
    host = ndb.StringProperty()
    server_numbers = ndb.StringProperty(repeated=True)
    phone_number = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)


class BaseRequestHandler(webapp2.RequestHandler):
    def _get_path(self, template_name):
        directory = os.path.dirname(__file__)
        return os.path.join(directory, 'templates', template_name)

    def render(self, template_name, template_values={}):
        self.response.out.write(
            template.render(self._get_path(template_name),
                            template_values, debug=_DEBUG))

    def generate(self, template_name, template_values={}):
        return template.render(
            self._get_path(template_name), template_values, debug=_DEBUG)

    def renderChatJSON(self, session_key):
        greeting_query = Greeting.query(
            ancestor=session_key).order(Greeting.date)
        greetings = greeting_query.fetch(100)
        ret = []
        for g in greetings:
            ret.append(
                {'user': g.user, 'msg': g.content,
                 'date': g.date.strftime('%s')})
        return ret

    def getChatsJSON(self, session_key, useCache=True):
        self.updateSession(session_key)
        if useCache is False:
            greetings = self.renderChatJSON(session_key)
            if not memcache.set(session_key.urlsafe(), greetings, 1000):
                logging.error('Memcache set in getChatJSON failed:')
            return self.response.out.write(json.dumps(greetings))
        greetings = memcache.get(session_key.urlsafe())
        if greetings is not None:
            return self.response.out.write(json.dumps(greetings))
        else:
            greetings = self.renderChatJSON(session_key)
            if not memcache.set(session_key.urlsafe(), greetings, 1000):
                logging.error('Memcache set in getChatJSON failed:')
            return self.response.out.write(json.dumps(greetings))

    def getAvailablePhoneNumber(self, client):
        number_list = client.server_numbers
        logging.error('checking numbers'+str(number_list))
        for n in number_list:
            session_url = memcache.get(n)
            logging.error('checking memcache for number '+n)
            if session_url is None:
                return n
            else:
                session = ndb.Key(urlsafe=session_url).get()
                # release this phone number is session is inactive for 15 sec
                if (datetime.now() - session.last_active_time).seconds > 15:
                    memcache.delete(n)
                    logging.info('server number '+n+' is released!')
                    return n
        return None

    def updateSession(self, session_key):
        s = session_key.get()
        s.last_update_time = datetime.now()
        s.put()


class MainHandler(BaseRequestHandler):
    def getSession(self, host):
        try:
            client_key = Client.query(Client.host == host).fetch(1)[0].key
        except IndexError:
            # Create a placeholder client
            temp_client = Client(
                name="Client Placeholder",
                host=host,
                server_numbers=['+17788001265'],
                phone_number='+17789971987'
            )
            temp_client.put()
            client_key = temp_client.key
        client = client_key.get()
        # register server phone number and session mapping
        server_number = self.getAvailablePhoneNumber(client)
        if server_number is not None:
            session = Session(parent=client_key)
            session.server_number = server_number
            session_key = session.put()
            logging.info('allocated session with '+server_number)
            if not memcache.set(server_number, session_key.urlsafe(), 1000):
                logging.error("Memcache in getSession failed:")
            return session_key
        else:
            return None

    def get(self):
        #ip = self.request.remote_addr
        host = self.request.host
        session_key = self.getSession(host)
        if session_key is None:
            template_values = {'wait': 'true'}
        else:
            template_values = {'wait': 'false',
                               'session': session_key.urlsafe()}
        self.render('index.html', template_values)

class ServiceHandler(BaseRequestHandler):
    def get(self):
        self.render('services.html', {})



ProjectTemplateValues = {
    'liquid': {
        'template': 'project.html',
        'title': 'Liquid Urethane Membrane',
        'info': 'This is a text placeholder. Lorem ipsum dolor sit amet, consectetur adipiscing elit. In congue sed risus vitae efficitur. Sed dapibus dictum risus, nec pellentesque libero dignissim sed. Praesent blandit velit nulla, in tempus nisi ornare sed. Maecenas sagittis tortor in nibh tristique iaculis. Interdum et malesuada fames ac ante ipsum primis in faucibus. Phasellus sit amet magna vitae nulla blandit commodo. Sed ornare hendrerit ultrices. Morbi bibendum massa a quam egestas tempus. Etiam aliquet neque et leo ornare pharetra. Cras odio orci, feugiat eu dapibus vitae, laoreet quis ante. Nulla convallis lorem ante, eu sodales erat dictum quis. Nullam vehicula scelerisque nulla ornare rhoncus. Nullam ultricies et neque sed iaculis.',
        'detail': 'This is a text placeholder. Lorem ipsum dolor sit amet, consectetur adipiscing elit. In congue sed risus vitae efficitur. Sed dapibus dictum risus, nec pellentesque libero dignissim sed. Praesent blandit velit nulla, in tempus nisi ornare sed. Maecenas sagittis tortor in nibh tristique iaculis. Interdum et malesuada fames ac ante ipsum primis in faucibus. Phasellus sit amet magna vitae nulla blandit commodo. Sed ornare hendrerit ultrices. Morbi bibendum massa a quam egestas tempus. Etiam aliquet neque et leo ornare pharetra. Cras odio orci, feugiat eu dapibus vitae, laoreet quis ante. Nulla convallis lorem ante, eu sodales erat dictum quis. Nullam vehicula scelerisque nulla ornare rhoncus. Nullam ultricies et neque sed iaculis.',
        'img0': '/static/img/projects/Helios_projects_Liquid Urethane Membrane5.jpg',
        'img1': '/static/img/projects/Helios_projects_Liquid Urethane Membrane4.jpg',
        'img2': '/static/img/projects/Helios_projects_Liquid Urethane Membrane3.jpg',
        'img3': '/static/img/projects/Helios_projects_Liquid Urethane Membrane1.jpg',
        'img4': '/static/img/projects/Helios_projects_Liquid Urethane Membrane7.jpg',
        'img5': '/static/img/projects/Helios_projects_Liquid Urethane Membrane2.jpg',
        'img6': '/static/img/projects/Helios_projects_Liquid Urethane Membrane6.jpg',
    },
    'shingle': {
        'template': 'project.html',
        'title': 'Shingle',
        'info': 'This is a text placeholder. Lorem ipsum dolor sit amet, consectetur adipiscing elit. In congue sed risus vitae efficitur. Sed dapibus dictum risus, nec pellentesque libero dignissim sed. Praesent blandit velit nulla, in tempus nisi ornare sed. Maecenas sagittis tortor in nibh tristique iaculis. Interdum et malesuada fames ac ante ipsum primis in faucibus. Phasellus sit amet magna vitae nulla blandit commodo. Sed ornare hendrerit ultrices. Morbi bibendum massa a quam egestas tempus. Etiam aliquet neque et leo ornare pharetra. Cras odio orci, feugiat eu dapibus vitae, laoreet quis ante. Nulla convallis lorem ante, eu sodales erat dictum quis. Nullam vehicula scelerisque nulla ornare rhoncus. Nullam ultricies et neque sed iaculis.',
        'detail': 'This is a text placeholder. Lorem ipsum dolor sit amet, consectetur adipiscing elit. In congue sed risus vitae efficitur. Sed dapibus dictum risus, nec pellentesque libero dignissim sed. Praesent blandit velit nulla, in tempus nisi ornare sed. Maecenas sagittis tortor in nibh tristique iaculis. Interdum et malesuada fames ac ante ipsum primis in faucibus. Phasellus sit amet magna vitae nulla blandit commodo. Sed ornare hendrerit ultrices. Morbi bibendum massa a quam egestas tempus. Etiam aliquet neque et leo ornare pharetra. Cras odio orci, feugiat eu dapibus vitae, laoreet quis ante. Nulla convallis lorem ante, eu sodales erat dictum quis. Nullam vehicula scelerisque nulla ornare rhoncus. Nullam ultricies et neque sed iaculis.',
        'img0': '/static/img/projects/Helios_projects_shigle1_7.jpg',
        'img1': '/static/img/projects/Helios_projects_shigle1_2.jpg',
        'img2': '/static/img/projects/Helios_projects_shigle1_3.jpg',
        'img3': '/static/img/projects/Helios_projects_shigle1_4.jpg',
        'img4': '/static/img/projects/Helios_projects_shigle1_1.jpg',
        'img5': '/static/img/projects/Helios_projects_shigle1_5.jpg',
        'img6': '/static/img/projects/Helios_projects_shigle1_6.jpg',
    },
    'insulation': {
        'template': 'project.html',
        'title': 'Insulation',
        'info': 'This is a text placeholder. Lorem ipsum dolor sit amet, consectetur adipiscing elit. In congue sed risus vitae efficitur. Sed dapibus dictum risus, nec pellentesque libero dignissim sed. Praesent blandit velit nulla, in tempus nisi ornare sed. Maecenas sagittis tortor in nibh tristique iaculis. Interdum et malesuada fames ac ante ipsum primis in faucibus. Phasellus sit amet magna vitae nulla blandit commodo. Sed ornare hendrerit ultrices. Morbi bibendum massa a quam egestas tempus. Etiam aliquet neque et leo ornare pharetra. Cras odio orci, feugiat eu dapibus vitae, laoreet quis ante. Nulla convallis lorem ante, eu sodales erat dictum quis. Nullam vehicula scelerisque nulla ornare rhoncus. Nullam ultricies et neque sed iaculis.',
        'detail': 'This is a text placeholder. Lorem ipsum dolor sit amet, consectetur adipiscing elit. In congue sed risus vitae efficitur. Sed dapibus dictum risus, nec pellentesque libero dignissim sed. Praesent blandit velit nulla, in tempus nisi ornare sed. Maecenas sagittis tortor in nibh tristique iaculis. Interdum et malesuada fames ac ante ipsum primis in faucibus. Phasellus sit amet magna vitae nulla blandit commodo. Sed ornare hendrerit ultrices. Morbi bibendum massa a quam egestas tempus. Etiam aliquet neque et leo ornare pharetra. Cras odio orci, feugiat eu dapibus vitae, laoreet quis ante. Nulla convallis lorem ante, eu sodales erat dictum quis. Nullam vehicula scelerisque nulla ornare rhoncus. Nullam ultricies et neque sed iaculis.',
        'img0': '/static/img/projects/Helios_projects_Insulation3.jpg',
        'img1': '/static/img/projects/Helios_projects_Insulation2.jpg',
        'img2': '/static/img/projects/Helios_projects_Insulation5.jpg',
        'img3': '/static/img/projects/Helios_projects_Insulation7.jpg',
        'img4': '/static/img/projects/Helios_projects_Insulation6.jpg',
        'img5': '/static/img/projects/Helios_projects_Insulation1.jpg',
        'img6': '/static/img/projects/Helios_projects_Insulation4.jpg',
    },
     'richmond': {
        'template': 'project.html',
        'title': 'Bridgeport Road',
        'info': 'This is a text placeholder. Lorem ipsum dolor sit amet, consectetur adipiscing elit. In congue sed risus vitae efficitur. Sed dapibus dictum risus, nec pellentesque libero dignissim sed. Praesent blandit velit nulla, in tempus nisi ornare sed. Maecenas sagittis tortor in nibh tristique iaculis. Interdum et malesuada fames ac ante ipsum primis in faucibus. Phasellus sit amet magna vitae nulla blandit commodo. Sed ornare hendrerit ultrices. Morbi bibendum massa a quam egestas tempus. Etiam aliquet neque et leo ornare pharetra. Cras odio orci, feugiat eu dapibus vitae, laoreet quis ante. Nulla convallis lorem ante, eu sodales erat dictum quis. Nullam vehicula scelerisque nulla ornare rhoncus. Nullam ultricies et neque sed iaculis.',
        'detail': 'This is a text placeholder. Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
        'img0': '/static/img/projects/Helios_projects_BridgeportRoadRichmond2.jpg',
        'img1': '/static/img/projects/Helios_projects_BridgeportRoadRichmond4.jpg',
        'img2': '/static/img/projects/Helios_projects_BridgeportRoadRichmond5.jpg',
        'img3': '/static/img/projects/Helios_projects_BridgeportRoadRichmond6.jpg',
        'img4': '/static/img/projects/Helios_projects_BridgeportRoadRichmond3.jpg',
        'img5': '/static/img/projects/Helios_projects_BridgeportRoadRichmond7.jpg',
        'img6': '/static/img/projects/Helios_projects_BridgeportRoadRichmond1.jpg',
    },
}

class ProjectHandler(BaseRequestHandler):
    def get(self, projectName):
        if projectName not in ProjectTemplateValues:
            projectName = 'summary'
            self.render('project_summary.html', {})
        else:
            self.render(ProjectTemplateValues[projectName]['template'], ProjectTemplateValues[projectName])


class ChatRequestHandler(BaseRequestHandler):
    def sendSms(self, from_number, to_number, msg):
        twilio_client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)
        message = twilio_client.messages.create(
            to=to_number, from_=from_number, body=msg)
        return message.sid

    def get(self):
        session_key = ndb.Key(urlsafe=self.request.get('session'))
        self.getChatsJSON(session_key)

    def post(self):
        session_key = ndb.Key(urlsafe=self.request.get('session'))
        greeting = Greeting(parent=session_key)
        greeting.content = self.request.get("msg")
        greeting.put()

        client = session_key.parent().get()
        session = session_key.get()
        logging.info(
            'sending sms to ' + client.phone_number +
            ' from number ' + session.server_number)

        """
        self.sendSms(
            session.server_number,
            client.phone_number,
            self.request.get("msg"))
        """

        self.getChatsJSON(session_key, False)


class SmsHandler(BaseRequestHandler):
    def get(self):
        pass

    def post(self):
        from_number = self.request.get('From')
        server_number = self.request.get('To')
        msg_body = self.request.get('Body')
        session_key_url = memcache.get(server_number)
        logging.info(session_key_url)
        session_key = ndb.Key(urlsafe=session_key_url)
        greeting = Greeting(parent=session_key)
        greeting.content = msg_body
        greeting.user = from_number
        greeting.put()

        self.getChatsJSON(session_key, False)


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/services', ServiceHandler),
    ('/projects/([^/]+)', ProjectHandler),
    ('/getchats', ChatRequestHandler),
    ('/sms', SmsHandler),
], debug=True)
