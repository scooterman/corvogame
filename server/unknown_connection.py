# -*- coding: utf-8 -*-
#    This file is part of corvogame.
#
#    corvogame is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    corvogame is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with corvogame.  If not, see <http://www.gnu.org/licenses/>.

from common import client_handler
import logging

class RawHandler(object):
    NAME = 'raw_string'

    def from_string(self, raw_string):
        data = raw_string.strip()
        return (True, [data], [], "")

    def to_string(self,message):
        pass

class UnknownConnectionHandler(client_handler.ClientHandler):
    ''' Class handler for an unknown source connection

    We define as unknown connection a client that has not made a initial handshake:
    before we determine the message protocol and authentication steps.
    '''

    def __init__(self, conn, server, addr):
        ''' Starts the handler and define the read method as 'not protocol enabled yet' '''
        logging.debug("Instantiating an unknown connection handler for connection {0}".format(addr))
        client_handler.ClientHandler.__init__(self, conn)
        self.server = server
        self.message_handler = None
        self.read_handler = self._unknown_protocol_message
        #self.write("Welcome to corvogame! Please input your protocol: ")
        self.message_handler = RawHandler()
        self.addr = addr

    def upgrade_protocol_handler(self, to_handler):
        logging.debug("Upgrading protocol to handler {0} and setting to auth mode".format(to_handler))
        self.read_handler = self._auth_handler
        self.message_handler = to_handler
        self.write(self.message_handler.to_string({ u'action' : 'connection_response', u'accepted' : 'yes', u'result_text' : u'Protocol accepted. Using {0}'.format(to_handler.NAME) }))

    def _unknown_protocol_message(self, data):
        ''' handshake handler. basically it checks if the client has inputted an
            valid protocol_handler. Otherwise, disconnects '''

        if data in self.server.message_handlers:
            logging.info("promoting {1} to {0} protocol: ".format(data, self.socket))
            self.upgrade_protocol_handler(self.server.message_handlers[data])

        else:
            logging.info("rejecting {1} due to invalid protocol: {0} ".format(data, self.socket))
            self.write("Invalid protocol type: {0}\r\n".format(data))
            self.shutdown()

    def _auth_handler(self, message):
        ''' after promoted as an protocol enabled connection, waits for an logon message,
            and give it to the auth_handler to check if something gone wrong. If yes,
            disconnects, otherwise notify the server to a new session '''

        try:
            assert message[u'action'] == 'login'
            username = message[u'username']
            password = message[u'password']

            logging.debug("Trying to authenticate [%s]" % username)

            if self.server.auth_handler(message):
                logging.debug("Authentication suceed, promoting to session")
                self.username = username
                logging.debug(self.message_handler.to_string)
                self.write(self.message_handler.to_string({ u'action' : 'logon_response', u'authenticated' : u'yes' , u'result_text' : u'Connected successfully.' }))
                self.read_handler = None
                self.server.promote_to_session(self, self.message_handler, self.addr)
            else:
                self.write(self.message_handler.to_string({ u'action' : 'logon_response', u'authenticated' : u'no' , u'result_text' : u'Invalid username or password.' }))
                #TODO shouldn't we terminate the connection after some tries?

        except KeyError,AssertionError:
            logging.debug("Invalid logon message. Rejecting")
            self.write(self.message_handler.to_string({ u'action' : 'logon_response', u'result' : u"Invalid logon message: {0}".format(readed[0]) }))
            self.shutdown()
