#!/usr/bin/python
from googlevoice import Voice
from googlevoice.util import input

# Robot Framework Google Voice test library. Use it to make calls, download
# voicemail, send SMS/text messages, etc.

# From http://code.google.com/p/telcotools4robotframework/
# @author David Luu

# This test library makes use of Google Voice Python library,
# http://code.google.com/p/pygooglevoice, which is licensed under
# the BSD license: http://www.opensource.org/licenses/bsd-license.php

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 or version 3 of the
# License.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

__all__ = ['send_sms', 'place_call', 'download_voicemails', 'download_call_recordings', 'get_list_of_google_voice_phones', 'get_list_of_missed_calls', 'get_list_of_received_calls', 'delete_sms_messages', 'delete_voicemails', 'delete_call_recordings', 'delete_missed_calls_list', 'delete_received_calls_list', 'delete_placed_calls_list', 'get_list_of_sms_messages']

class GoogleVoiceLibrary:
	"""Robot Framework Google Voice test library. Use it to make calls, download voicemail, send SMS/text messages, etc.
	
	This test library makes use of Google Voice Python library, get it at http://code.google.com/p/pygooglevoice
	
	Requires Google Voice Python library to be pre-installed to work. This Robot Framework test library does not include or install that library.
	
	"""
	
	__version__ = '1.0'
	ROBOT_LIBRARY_SCOPE = 'GLOBAL'
	
	def __init__(self, pUsername, pPassword):
		self._gv = Voice()
		self._gv.login(pUsername,pPassword)
		
	def send_sms(self, toNumber, message):
		"""Send an SMS text message to given phone number.
		
		"""
		self._gv.send_sms(toNumber, message)
	
	def place_call(self, toNumber, fromNumber=None):
		"""Place a call to given phone number from optionally selected phone (number) registered with Google Voice (GV) account. If GV phone not specified, it will use the default one associated with GV.
		
		Invoking this keyword will ring the selected registered GV phone, and on answer, will then proceed to call the given phone number. For test automation, we assume you have a method to automate answering the GV phone after invoking this keyword. We also assume you automate answering the call at the called party, and perhaps also do some tone, DTMF, and/or caller ID validation in the test automation.
		
		"""
		try:
			self._gv.call(toNumber, fromNumber)
		except err:
			print "Failed to place call to %s from %s. %s" % (toNumber,fromNumber,err)
	
	def download_voicemails(self, downloadPath):
		"""Downloads all voicemails in Google Voice account to given path location as MP3 files.
		
		One can then further process the MP3s for testing purposes (e.g. analyze for tone, DTMF, specific audio; convert MP3 to proper wave audio format, etc. then do analysis as mentioned).
		
		"""
		try:
			for message in self._gv.voicemail().messages:
				message.download(downloadPath)
				message.mark(1) #mark as read
		except IOError, err:
			print "Failed to download one or more voicemails as an MP3 to %s. %s" % (downloadPath, err)
			
	def download_call_recordings(self, downloadPath):
		"""Downloads all call recordings in Google Voice account to given path location as MP3 files.
		
		One can then further process the MP3s for testing purposes (e.g. analyze for tone, DTMF, specific audio; convert MP3 to proper wave audio format, etc. then do analysis as mentioned).
		
		"""
		try:
			for message in self._gv.recorded().messages:
				message.download(downloadPath)
				message.mark(1) #mark as read
		except IOError, err:
			print "Failed to download one or more call recordings as an MP3 to %s. %s" % (downloadPath, err)
			
	def get_list_of_google_voice_phones(self):
		"""Get a list of registered phone (numbers) for the Google Voice account.
		
		"""
		util.pprint(self._gv.phones)
		return self._gv.phones
		
	def get_list_of_missed_calls(self):
		"""Get a list of missed calls to Google Voice number. List is of phone numbers of calling party that didn't leave any messages, otherwise call would end up in voicemail/inbox rather than here.
		"""
		missed_calls = () # (array) list of missed calls
		for message in self._gv.missed().messages:
			missed_calls.append(message.phoneNumber) #or msg.displayNumber
			
	def get_list_of_received_calls(self):
		"""Get a list of received/answered calls to Google Voice number. List is of phone numbers of calling party.
		"""
		received_calls = () # (array) list of received calls
		for message in self._gv.received().messages:
			missed_calls.append(message.phoneNumber) #or msg.displayNumber
		
	def delete_sms_messages(self,readFlag=False):
		"""Delete SMS text messages in Google voice account. 
		
		Optionally specify readFlag to delete only messages that are read. Otherwise, will default to deleting all messages regardless.
		
		"""
		for message in self._gv.sms().messages:
			if readFlag:
				if message.isRead:
					message.delete()
			else:
				message.delete()
				
	def delete_voicemails(self,readFlag=False):
		"""Delete voicemail messages in Google voice account. 
		
		Optionally specify readFlag to delete only messages that are read. Otherwise, will default to deleting all messages regardless.
		
		"""
		for message in self._gv.voicemail().messages:
			if readFlag:
				if message.isRead:
					message.delete()
			else:
				message.delete()
				
	def delete_call_recordings(self,readFlag=False):
		"""Delete recorded calls in Google voice account. 
		
		Optionally specify readFlag to delete only messages that are read. Otherwise, will default to deleting all messages regardless.
		
		"""
		for message in self._gv.recorded().messages:
			if readFlag:
				if message.isRead:
					message.delete()
			else:
				message.delete()
				
	def delete_missed_calls_list(self,readFlag=False):
		"""Delete list of missed calls in Google voice account.
		
		Optionally specify readFlag to delete only messages that are read. Otherwise, will default to deleting all messages regardless.
		
		"""
		for message in self._gv.missed().messages:
			if readFlag:
				if message.isRead:
					message.delete()
			else:
				message.delete()
				
	def delete_received_calls_list(self):
		"""Delete list of received (i.e. answered) calls in Google voice account."""
		for message in self._gv.received().messages:
			message.delete()
			
	def delete_placed_calls_list(self):
		"""Delete list of placed/outbound calls in Google voice account."""
		for message in self._gv.placed().messages:
			message.delete()
			
	def get_list_of_sms_messages(self):
		"""Get a list of SMS text messages with their complete message thread/history in Google Voice account.
		
		"""
		#self._gv.sms()
		msgs = extractsms(self._gv.sms.html)
		for message in self._gv.sms().messages:
			message.mark(1) #mark as read
		for msg in msgs:
			print str(msg)
		return msgs
	
	def extractsms(htmlsms) :
		"""extractsms  --  extract SMS messages from BeautifulSoup tree of Google Voice SMS HTML.
		
		Output is a list of dictionaries, one per message.
		"""
		msgitems = [] # accum message items here
		# Extract all conversations by searching for a DIV with an ID at top level.
		tree = BeautifulSoup.BeautifulSoup(htmlsms) # parse HTML into tree
		conversations = tree.findAll("div",attrs={"id" : True},recursive=False)
		for conversation in conversations :
			# For each conversation, extract each row, which is one SMS message.
			rows = conversation.findAll(attrs={"class" : "gc-message-sms-row"})
			for row in rows : # for all rows
				# For each row, which is one message, extract all the fields.
				msgitem = {"id" : conversation["id"]}		# tag this message with conversation ID
				spans = row.findAll("span",attrs={"class" : True}, recursive=False)
				for span in spans : # for all spans in row
					cl = span["class"].replace('gc-message-sms-', '')
			msgitem[cl] = (" ".join(span.findAll(text=True))).strip() # put text in dict
			msgitems.append(msgitem) # add msg dictionary to list
		return msgitems
		
	