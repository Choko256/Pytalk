#-*- coding:utf-8 -*-

# import irclib
import settings
import net
import debug
import log
# CS IRC Core Module

"""
	Represents a basic IRC User with its information
"""
class User:
	def __init__(self, nick, ident, host, mode = '', away = False):
		self._nick = nick
		self._ident = ident
		self._host = host
		self._mode = mode
		self._away = away
	
	def change_nick(self, newnick):
		self._nick = newnick
		
	def add_mode(self, mode):
		self._mode = self._mode + mode
	
	def remove_mode(self, mode):
		if mode in self._mode:
			self._mode = self._mode.replace(mode, '')
			
	def set_away(self, away):
		self._away = away

"""
	Represents a channel data with users list and current active modes
"""
class Channel:
	def __init__(self, srv, name, key):
		self._name = name
		self._key = key
		self._users = {}
		self._mode = ''
		
	def add_mode(self, mode):
		if not mode in self._mode:
			self._mode = self._mode + mode
			
	def remove_mode(self, mode):
		if mode in self._mode:
			self._mode = self._mode.replace(mode, '')
		
	def add_user(self, nick, ident, host, mode = ""):
		debug.debug('Adding new user to channel ' + self._name + ' : ' + nick + '!~' + ident + '@' + host)
		self._users[nick] = User(nick, ident, host, mode)
		
	def remove_user(self, nick):
		if nick in self._users:
			del self._users[nick]
			
	def is_user_present(self, nick):
		return nick in self._users
			
	def clear_users(self):
		self._users = {}
			
	def change_user_nick(self, oldnick, nick):
		if oldnick in self._users:
			self._users[nick] = self._users[oldnick]
			del self._users[oldnick]
			self._users[nick].change_nick(nick)
			
	def add_user_mode(self, nick, mode):
		if nick in self._users:
			self._users[nick].add_mode(mode)
			
	def remove_user_mode(self, nick, mode):
		if nick in self._users:
			self._users[nick].remove_mode(mode)

"""
	Represents a server configuration
"""
class Server:
	def __init__(self, host, port, password, encoding, nickname, alternative, username, realname, ident, nickserv, welcomemsg):
		self._host = host
		self._name = host
		self._port = port
		self._password = password
		self._encoding = encoding
		self._nickname = nickname
		self._alternative = alternative
		self._current_nickname = nickname
		self._username = username
		self._realname = realname
		self._nickserv = nickserv
		self._ident = ident
		self._welcome_msg = welcomemsg
		self._channels = {}
		
	def add_channel(self, name, key):
		self._channels[name] = Channel(self._host, name, key)
		
	def remove_channel(self, name):
		if name in self._channels:
			del self._channels[name]
			
	def get_channel_by_name(self, name):
		debug.debug('Searching for channel ' + name + '...')
		if name in self._channels:
			debug.debug("Channel found " + name)
			return self._channels[name]
		else:
			debug.warn("Channel " + name + " not found !")
			return None
			
	def is_user_on_channel(self, nickname, channel):
		if channel in self._channels:
			return self._channels[channel].is_user_present(nickname)
			
	def quit_user(self, name):
		for c in self._channels:
			self._channels[c].remove_user(name)
			
	def nick_user(self, old, new):
		for c in self._channels:
			self._channels[c].change_user_nick(old, new)
			
	def add_channel_mode(self, channel, mode):
		if channel in self._channels:
			self._channels[channel].add_mode(mode)
			
	def remove_channel_mode(self, channel, mode):
		if channel in self._channels:
			self._channels[channel].remove_mode(mode)
			
	def __str__(self):
		return self._name
		
	def get_user_list_of(self, channel, withmode = False):
		if channel in self._channels:
			result = []
			for u in self._channels[channel]._users:
				s = self._channels[channel]._users[u]._nick
				if withmode:
					s = s + " ( Modes: " + self._channels[channel]._users[u]._mode + " )"
				result.append(s)
			return result
			# return self._channels[channel]._users.keys()
		else:
			return None
			
"""
	Basic IRC Client
	Basic command mapping
	Could be overrided to map more commands.
"""
class Client(net.IRCClient):
	def __init__(self, config):
		net.IRCClient.__init__(self)
		debug.debug("Server configuration: " + str(config))	
		self.server = Server(
			config['host'],
			int(config['port']),
			config['password'],
			config['encoding'],
			config['userinfo']['nickname'],
			config['userinfo']['alternative'],
			config['userinfo']['username'],
			config['userinfo']['realname'],
			config['userinfo']['ident'],
			config['userinfo']['nickserv'],
			config['welcome_msg']
		)
		self.server._name = config['name']
		for c in config['autojoin']:
			self.server.add_channel(c[0], c[1])
			
		self.version = config['version'].replace('{% APPLICATION_NAME %}', settings.APPLICATION_NAME).replace('{% APPLICATION_VERSION %}', settings.APPLICATION_VERSION).	replace('{% APPLICATION_COPYRIGHT %}', settings.APPLICATION_COPYRIGHT).replace('{% APPLICATION_RELEASE_DATE %}', settings.APPLICATION_RELEASE_DATE)
		
		self.events = {
			'welcome': None,
			'pubmsg': None,
			'privmsg': None,
			'pubnotice': None,
			'privnotice': None,
			'quit': None,
			'kick': None,
			'mode': None,
			'part': None,
			'join': None,
			'nick': None,
			'action': None,
			'ping': None
		}
		
		self.plugins = {}
		
		self.ignorelist = []
		
		self._connect(self.server._host, self.server._port, self.server._nickname, self.server._password, self.server._username, self.server._realname, self.server._ident, ssl = config['ssl'])
		
	def associate_plugin(self, name, plugin, active = True):
		if name in self.plugins:
			self.plugins[name]['active'] = active
		else:
			self.plugins[name] = {
				'plugin': plugin,
				'active': active
			}
			
	def dissociate_plugin(self, name):
		if name in self.plugins:
			del self.plugins[name]
	
	def get_plugin(self, name):
		return self.plugins.get(name)
		
	def bind_event(self, event, callback):
		debug.info('Binding event ' + event + ' on ' + str(callback))
		self.events[event] = callback
			
	def unbind_event(self, event):
		self.events[event] = None
		
	def get_user_list(self, chan, withmode = False):
		return self.server.get_user_list_of(chan, withmode)
		
	def get_welcome_message(self, nick, chan):
		return self.server._welcome_msg.replace("{% channel %}", chan).replace("{% nickname %}", nick)
			
	def dispatch_event(self, ev):
		eventtype = ev.eventtype()
		debug.debug("Dispatching event %s..." % (eventtype,))
		if eventtype in self.events:
			if not self.events[eventtype] is None:
				debug.debug("Raising Event for '%s' found: %s" % (eventtype, self.events[eventtype]))
				self.events[eventtype](self, ev.source(), ev.target(), ev.arguments())
				
	def nickname(self):
		return self.server._current_nickname
		
	def ident(self):
		return self.server._ident
		
	def realname(self):
		return self.server._realname
				
	def is_ignored(self, source):
		# return irclib.nm_to_n(source) in self.ignorelist
		return source.nickname in self.ignorelist
		
	def get_mode_by_symbol(self, symbol):
		if symbol == '@':
			return 'o'
		elif symbol == '%':
			return 'h'
		elif symbol == '+':
			return 'v'
		elif symbol == '&':
			return 'q'
			
	""" Event Triggered on Special Message VERSION """
	def on_version(self, serv, ev):
		self.notice(ev.source().nickname, self.version)
	
	""" Event Triggered when Message 001 is received (RPL_WELCOME 001)
	# 	Description of Event:
	#		eventtype: 	'welcome'
	#		source:		IRC Server Relay hostname which client is connected on
	#		target:		Nickname of the user
	#		arguments:	[0] Welcome message
	"""
	def on_welcome(self, serv, ev):
		if len(self.server._nickserv) > 0:
			self.privmsg('NickServ', 'identify ' + self.server._nickserv)
		for c in self.server._channels:
			chan = self.server._channels[c]
			self.join(chan._name, chan._key)
		self.dispatch_event(ev)
	
	# Pong response is now automatic
	# Dispatches only the event
	""" Event Triggered when a PING request is sent by the server
		Ping Identifier can be in target or in arguments parameter
	"""
	def on_ping(self, serv, ev):
		self.dispatch_event(ev)
			
	""" Event Triggered when Message PRIVMSG is received on a channel (Public Message)
	# If sender is in ignore list, event does nothing
	# 	Description of Event:
	#		eventtype:	'pubmsg'
	#		source:		Complete mask of sender (nick!~ident@host)
	#		target:		Target channel
	#		arguments:	[0] Message
	"""
	def on_pubmsg(self, serv, ev):
		if settings.LOG:
			log.statify(serv.servername(), ev.target(), ev.source(), ev.eventtype(), ev.arguments()[0])
		if not self.is_ignored(ev.source()):
			self.dispatch_event(ev)
			
	""" Event Triggered when Private Message is sent to the bot
	# If sender is in ignore list, event does nothing
	# 	Description of Event:
	#		eventtype:	'privmsg'
	#		source:		Complete mask of sender (nick!~ident@host)
	#		target:		The bot itself
	#		arguments:	[0] Message
	"""
	def on_privmsg(self, serv, ev):
		if not self.is_ignored(ev.source()):
			self.dispatch_event(ev)
			
	""" Event Triggered when Notice is sent to the bot
	# If sender is in ignore list, event does nothing
	# 	Description of Event:
	#		eventtype:	'privnotice'
	#		source:		Complete mask of sender (nick!~ident@host)
	#		target:		The bot itself
	#		arguments:	[0] Message
	"""
	def on_privnotice(self, serv, ev):
		if not self.is_ignored(ev.source()):
			self.dispatch_event(ev)
			
	""" Event Triggered when Notice is sent to a channel
	# If sender is in ignore list, event does nothing
	# 	Description of Event:
	#		eventtype:	'pubnotice'
	#		source:		Complete mask of sender (nick!~ident@host)
	#		target:		The destination channel
	#		arguments:	[0] Message
	"""
	def on_pubnotice(self, serv, ev):
		if not self.is_ignored(ev.source()):
			self.dispatch_event(ev)
			
	""" Event Triggered when a user Joined one of the bot channels
	# 	Description of Event:
	#		eventtype:	'join'
	#		source:		Complete mask of user (nick!~ident@host)
	#		target:		Channel user has just joined
	#		arguments:	None
	"""
	def on_join(self, serv, ev):
		if settings.LOG:
			log.statify(serv.servername(), ev.arguments()[0], ev.source(), ev.eventtype(), '')
		if ev.source().nickname == self.server._current_nickname:
			debug.debug('New channel: ' + ev.target())
			self.server.add_channel(ev.target(), '')
		else:
			debug.debug('Received Join Event: ' + str(ev.source()) + ' on ' + ev.arguments()[0])
			self.server.get_channel_by_name(ev.arguments()[0]).add_user(ev.source().nickname, ev.source().ident, ev.source().hostname)
		self.dispatch_event(ev)
			
	""" Event Triggered when bot receives user list after join
	# 	Description of Event:
	#		eventtype:	'namreply'
	#		source:		IRC Server which has sent the list
	#		target:		The bot itself
	#		arguments:	[0] Status on channel (@, &, =) [1] Channel name [2] User list (separated with spaces)
	"""
	def on_namreply(self, serv, ev):
		channel = ev.arguments()[1]
		userlist = ev.arguments()[2].strip().split()
		for user in userlist:
			if user[0] == '@' or user[0] == '&' or user[0] == '%' or user[0] == '+':
				self.server.get_channel_by_name(channel).add_user(user[1:], user[1:], user[1:], self.get_mode_by_symbol(user[0]))
			else:
				self.server.get_channel_by_name(channel).add_user(user, user, user, '')
				
	""" Event Triggered when a user parts from one of the bot channels
	# 	Description of Event:
	#		eventtype:	'part'
	#		source:		Complete mask of user (nick!~ident@host)
	#		target:		Channel user has just parted from
	#		arguments:	[Not Mandatory][0] Part message
	"""
	def on_part(self, serv, ev):
		# self.server.get_channel_by_name(ev.target()).remove_user(irclib.nm_to_n(ev.source()))
		if settings.LOG:
			if len(ev.arguments()) == 0:
				arg = ''
			else:
				arg = ev.arguments()[0]
			log.statify(serv.servername(), ev.target(), ev.source(), ev.eventtype(), arg)
		self.server.get_channel_by_name(ev.target()).remove_user(ev.source().nickname)
		self.dispatch_event(ev)
		
	""" Event Triggered when a user quits IRC
	#   Make the users list empty and asks for all names
	# 	Description of Event:
	#		eventtype:	'quit'
	#		source:		Complete mask of user (nick!~ident@host)
	#		target:		None
	#		arguments:	[Not Mandatory][0] Quit message
	"""
	def on_quit(self, serv, ev):
		# self.server.quit_user(irclib.nm_to_n(ev.source()))
		debug.info(ev.source().nickname + " has quit.")
		if settings.LOG:
			if len(ev.arguments()) == 0:
				arg = 'Quit.'
			else:
				arg = ev.arguments()[0]
			for c in self.server._channels:
				if self.server.is_user_on_channel(ev.source().nickname, c):
					debug.debug("Statify quit of " + ev.source().nickname + " for channel " + c + "...")
					log.statify(serv.servername(), c, ev.source(), ev.eventtype(), arg)
		self.server.quit_user(ev.source().nickname)
		self.dispatch_event(ev)
		
	""" Event Triggered when a user invites the bot on a channel
	# 	Description of Event:
	#		eventtype:	'invite'
	#		source:		Complete mask of user (nick!~ident@host)
	#		target:		The bot itself / Destination
	#		arguments:	[0] Channel where the bot is invited
	"""
	def on_invite(self, serv, ev):
		self.dispatch_event(ev)
		
	""" Event Triggered when a user changes his nickname
	# 	Description of Event:
	#		eventtype:	'nick'
	#		source:		Complete mask of user (nick!~ident@host) BEFORE nick has been changed
	#		target:		None
	#		arguments:	New user nickname
	"""
	def on_nick(self, serv, ev):
		if settings.LOG:
			for c in self.server._channels:
				if self.server.is_user_on_channel(ev.source().nickname, c):
					log.statify(serv.servername(), c, ev.source(), ev.eventtype(), ev.arguments()[0])
		self.server.nick_user(ev.source().nickname, ev.arguments()[0])
		self.dispatch_event(ev)
		
	""" Event Triggered when a user is kicked from a channel
	# 	Description of Event:
	#		eventtype:	'kick'
	#		source:		Complete mask of kicker (nick!~ident@host)
	#		target:		Channel where the user has been kicked from
	#		arguments:	[0] Nickname of the kicked user [Not Mandatory][1] Reason
	"""
	def on_kick(self, serv, ev):
		if ev.arguments()[0].lower() != self.server._current_nickname.lower():
			self.server.get_channel_by_name(ev.target()).remove_user(ev.arguments()[0])
			if settings.LOG:
				log.statify(serv.servername(), ev.target(), ev.source(), ev.eventtype(), ev.arguments()[0])
		self.dispatch_event(ev)
		
	""" Event triggered when a user makes an ACTION message (/me)
		No distinction between Private and Public ACTION messages
	#	Description of Event:
	#		eventtype: 'pubaction'
	#		source:		Complete mask of user (nick!~ident@host)
	#		target:		Channel where the users sends the message / Nickname of the target
	#		arguments:	[0] Message
	"""
	def on_pubaction(self, serv, ev):
		actionmsg = ev.arguments()[0][len('\x01ACTION '):-1]
		if settings.LOG:
			log.statify(serv.servername(), ev.target(), ev.source(), ev.eventtype(), actionmsg)
		self.dispatch_event(ev)
		
	""" Event triggered when a user changes a MODE
		Target can be a user or a user on a channel or an entire channel
	#	Description of Event:
	#		eventtype:	'mode'
	#		source:		Complete mask of user (nick!~ident@host)
	#		target:		Channel + Mode [ + __SPACE__ + User Target ]
	#		arguments:	[0] // [1] //
	"""
	def on_mode(self, serv, ev):
		channel = ev.target()
		if net.ProtocolMgr._is_a_channel(channel):
			modes = ev.arguments()[0]
			if len(ev.arguments()) > 1:
				targets = ev.arguments()[1:]
			else:
				targets = None
			
			current_md = ''
			idx = 0
			for m in modes:
				if m == '+' or m == '-':
					current_md = m
				else:
					if targets is None:
						if current_md == '+':
							self.server.add_channel_mode(channel, m)
						elif current_md == '-':
							self.server.remove_channel_mode(channel, m)
					else:
						if current_md == '+':
							self.server.get_channel_by_name(channel).add_user_mode(targets[idx], m)
						elif current_md == '-':
							self.server.get_channel_by_name(channel).remove_user_mode(targets[idx], m)
					idx = idx + 1
			if settings.LOG:
				log.statify(serv.servername(), ev.target(), ev.source(), ev.eventtype(), ' '.join(ev.arguments()))
		
		self.dispatch_event(ev)
		
	""" Event triggered after USER command when used nickname is already taken
		Retrigger a new NICK/USER command for a new authentication on server with Alternative Nickname
	#	Description of Event:
	#		eventtype:	'nicknameinuse'
	#		source:		Server URL
	#		target:		*
	#		arguments:	[0] Chosen nickname [1] Message "Nickname is already in use"
	"""
	def on_nicknameinuse(self, serv, ev):
		self.connection._init_ident(usednick = self.server._alternative)
		self.dispatch_event(ev)
		
	"""
		Shutdown script
	"""
	def shutdown(self):
		self.connection.disconnect(self.config.misc['quitmsg'])
		sys.exit(0)

	"""
		Identify the user with his nickserv password
	"""
	def ident(self, pwd = None):
		if pwd is None:
			if len(self.config.ident['passwd']) != 0:
				self.privmsg('NickServ', 'identify ' + self.config.ident['passwd'])
		else:
			self.privmsg("NickServ", 'identify ' + pwd)
		
