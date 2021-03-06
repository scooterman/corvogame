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
from json_handler import Handler
import logging

class WebsocketHandler(Handler):
    NAME = 'json_websocket'

    def __init__(self):
        Handler.__init__(self, '\xff')

    def from_string(self, raw_message):
        raw_message= raw_message[1:]
        logging.debug("Raw message is {0}".format(raw_message))
        Handler.from_string(self, raw_message)

    def to_string(self, message):
        encoded_msg = Handler.to_string(self, message)
        return '\x00' + encoded_msg.encode('utf-8')
