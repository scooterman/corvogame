# -*- coding: utf-8 -*-
import json

def read(raw_message):
  ''' Basic reader. Searches for endlines, strip unused character's and tries to parse them as json objects '''
  assert type(raw_message) == str
  output = []
  errors = []
  if raw_message.rfind("\n") >= 0:
    messages = raw_message.strip().split('\n')
    
    for message in messages:
      print "trying to decode", message
      try:
	msg = json.loads(message)
	output.append(msg)
      except Exception, e:
	print e
	errors.append({ "error" : "Malformed input" })    

  return output, errors