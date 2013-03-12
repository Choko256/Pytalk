#-*- coding:utf-8 -*-

import settings
import socket, ssl
import threading
import debug

"""
	Module for IRC network protocol intelligence
	Respect for IRC RFC 1459 and its extensions
"""

# Represents a IRC user
# Extracts nickname, ident and hostname from complete prefix user mask
class User:
	def __init__(self, usermask):
		self.nickname = ''
		self.ident = ''
		self.hostname = ''
		self.__usermask = usermask[1:]
		
		if self.__usermask.find('!') != -1:
			self.nickname = self.__usermask.split('!')[0]
			self.ident = self.__usermask.split('!')[1].split('@')[0]
			self.hostname = self.__usermask.split('@')[1]
		else:
			self.hostname = self.__usermask
			
	def get_mask(self):
		return self.__usermask
		
	def __str__(self):
		debug.info('Usermask: ' + self.__usermask)
		return self.get_mask()

# Represents an IRC message
# Removes the trailing end.
class Message:
	def __init__(self, line, autoparse = True):
		debug.info('Incoming data : ' + line)
		self._incoming = line
		for c in settings.SEPARATOR:
			self._incoming = self._incoming.replace(c, '')
			
		self.message_type = ''
		self.source = None
		self.target = ''
		self.arguments = []
		self.__command = ''
		
		if autoparse:
			self.parse()
			
	def get_command(self):
		return self.__command
		
	def __str__(self):
		if self.source is None:
			src = "None"
		else:
			src = self.source
		return "[Message object instance] Type: " + str(self.message_type) + " / Source: " + str(src) + " / Target: " + self.target + " / Args: " + str(len(self.arguments))
		
	# Parses the message
	def parse(self):
		if len(self._incoming) > 0:
			idx = 0
			parts = self._incoming.split()
			# Tests if first part is the command or the source (PING has no source...)
			debug.info("Message parsing..." + str(parts))
			if parts[idx].startswith(':'):
				self.source = User(parts[idx])
				idx = idx + 1
			debug.info("Source : " + str(self.source))
			self.__command = parts[idx]
			debug.info("Command: " + str(self.__command))
			idx = idx + 1
			if not parts[idx].startswith(':'):
				self.target = parts[idx]
				idx = idx + 1
			rest = parts[idx:]
			
			debug.info("Target: " + str(self.target))
			debug.info("Rest: " + str(rest))
			idx = 0
			for p in rest:
				if p.startswith(':'):
					self.arguments.append(' '.join(rest[idx:])[1:])
					break
				else:
					self.arguments.append(p)
					idx = idx + 1
			debug.info("Arguments: " + str(self.arguments))
					
# Represents the main connected socket
# Contains mainstream and bufferized input from network
# Beware of multi-packets messages

class IRCConnector(threading.Thread):
	def __init__(self, host, port, nickname, password, username, realname, ident, ssl = False):
		threading.Thread.__init__(self)
		self.__host = host
		self.__port = port
		self.__nickname = nickname
		self.__password = password
		self.__username = username
		self.__realname = realname
		self.__ident = ident
		self.__ssl = ssl
		self.Terminated = False
		
		self.__current_nickname = nickname
		
		self.on_incoming = None
		self.__socket = None
	
	def servername(self):
		return self.__host
		
	def connect(self):
		self.__socket = socket.create_connection((self.__host, self.__port))
		
	def run(self):
		debug.info("Connecting to " + self.__host + " on port " + str(self.__port))
		try:
			self.connect()
			debug.info("Connected.")
			self._init_ident()
			debug.info("Registering...")
			while not self.Terminated:
				buffer = ''
				while not buffer.endswith(settings.SEPARATOR):
					buffer = buffer + self.__socket.recv(settings.BUFFER_SIZE)
				for line in buffer.split(settings.SEPARATOR):
					ln = line.strip()
					if ln != '':
						m = Message(ln)
						debug.debug(str(m))
						if self.on_incoming:
							self.on_incoming(m)
		except Exception, e:
			debug.error("Disconnected from host. Reason : " + str(e))
			raise e
			
	def send_raw(self, raw):
		debug.debug("Sending " + raw)
		self.__socket.send(raw + settings.SEPARATOR)
		
	def get_current_nickname(self):
		return self.__current_nickname
		
	def _init_ident(self, usednick = None):
		if usednick is None:
			nickname = self.__nickname
		else:
			nickname = usednick
			
		self.__current_nickname = nickname
		debug.info("Sending authentication information...")
		if self.__password != '':
			self.send_raw("PASS " + self.__password)
		self.send_raw("NICK " + nickname)
		self.send_raw("USER " + nickname + " " + self.__username + " 0 " + self.__realname)
		
	def stop(self):
		self.Terminated = True
		
# Protocol Manager
class ProtocolMgr:
	@staticmethod
	def _is_a_channel(tgt):
		return tgt.startswith('&') or tgt.startswith('#')
		
	@staticmethod
	def get_type_from_command(cmd, tgt = '', msg = ''):
		#if settings.DEBUG:
		#	print "[Info] Parsing type from command :", cmd
		debug.debug("Parsing type from command : " + cmd)
		if cmd == 'privmsg':
			if ProtocolMgr._is_a_channel(tgt):
				if msg.startswith('\x01ACTION'):
					return 'pubaction'
				else:
					return 'pubmsg'
			else:
				if msg.startswith('\x01ACTION'):
					return 'privaction'
				elif msg.startswith('\x01VERSION'):
					return 'version'
				else:
					return 'privmsg'
				
		elif cmd == 'notice':
			if ProtocolMgr._is_a_channel(tgt):
				return 'pubnotice'
			else:
				return 'privnotice'
		elif cmd in settings.NUMERIC_COMMANDS:
			return settings.NUMERIC_COMMANDS[cmd]
		else:
			return cmd
			
# IRC Event
# Dispatched to linked client
class Event:
	def __init__(self, eventtype, source, target, arguments):
		self.__eventtype = eventtype
		self.__source = source
		self.__target = target
		self.__arguments = arguments
		
	def eventtype(self):
		return self.__eventtype

	def source(self):
		return self.__source
	
	def target(self):
		return self.__target
	
	def arguments(self):
		return self.__arguments

# Connector controller
# Intercepts message events from Connector object and dispatches them after protocol treatments
# This class MUST be OVERRIDED !
class IRCClient:
	def __init__(self):
		self.connection = None
	
	def _connect(self, host, port, nickname, password, username, realname, ident, ssl = False):
		self.connection = IRCConnector(host, port, nickname, password, username, realname, ident, ssl)
		self.connection.on_incoming = self._on_incoming_message
		
	def start(self):
		self.connection.start()
		
	def _on_incoming_message(self, message):
		if not isinstance(message, Message):
			raise Exception("[Error 001] Unable to parse incoming message. Invalid message type (Expected: csirc.lib.net.Message)")
		cmd = message.get_command().lower()
		tgt = message.target
		
		if len(message.arguments) > 0:
			result = ProtocolMgr.get_type_from_command(cmd, tgt, message.arguments[0])
		else:
			result = ProtocolMgr.get_type_from_command(cmd, tgt, '')
		message.message_type = result
		try:
			internal = getattr(self, '_on_' + result)
			debug.info("Entering internal event method _on_" + result + "...")
			internal(message.message_type, message.source, message.target, message.arguments)
		except AttributeError, e:
			debug.warn("Unable to find internal event method (_on_" + result + ") [" + str(e) + "]")
			
		try:
			event = getattr(self, 'on_' + result)
			debug.info("Entering event method on_" + result + "...")
			event(self.connection, Event(message.message_type, message.source, message.target, message.arguments))
		except AttributeError, e:
			debug.warn("Unable to find event method (on_" + result + ") [" + str(e) + "]")
			
	def _on_ping(self, mtype, source, target, args):
		pid = target
		if pid == '':
			pid = args[0]
		self.pong(pid)
		
	def _on_kick(self, mtype, source, target, args):
		if settings.AUTO_JOIN_KICK:
			if args[0] == self.connection.get_current_nickname():
				self.join(target)
			
	def privmsg(self, target, message):
		self._raw("PRIVMSG " + target + " :" + message)
	
	def join(self, channel, key = ""):
		to_send = "JOIN " + channel
		if key != "":
			to_send = to_send + " " + key
		self._raw(to_send)
		
	def notice(self, target, message):
		self._raw("NOTICE " + target + " :" + message)
		
	def quit(self, message = ""):
		msg = message
		if msg == "":
			msg = settings.QUIT_MESSAGE
		self._raw("QUIT :" + msg)
		self.connection.Terminated = True
		
	def invite(self, nick, channel):
		self._raw("INVITE " + nick + " :" + channel)
		
	def kick(self, channel, nick, reason):
		self._raw("KICK " + channel + " " + nick + " :" + reason)
		
	def mode(self, target, args = []):
		self._raw("MODE " + target + " " + " ".join(args))
		
	def nick(self, newnick):
		self._raw("NICK :" + newnick)
		
	def part(self, channel, message = ""):
		msg = message
		if msg == '':
			msg = settings.PART_MESSAGE
		self._raw("PART " + channel + " :" + msg)
		
	def pong(self, pid):
		self._raw("PONG :" + pid)
		
	def action(self, target, message):
		self.privmsg(target, "\x01ACTION " + message + "\x01")
		
	def _raw(self, message):
		self.connection.send_raw(message)
		
