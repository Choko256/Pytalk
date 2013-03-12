#-*- coding:utf-8 -*-

"""
	IRC Module for protocol implementation into CS-IRC
"""

from xml.dom.minidom import parse
import os.path
# from lib import irc
from lib import irc
from lib import settings

import debug

class CsIrcConfig:
	def __init__(self):
		self.__filename = os.path.dirname(__file__) + '/conf/csirc.xml'
		self.__config = parse(self.__filename)

		self.profiles = {}		# List of Configuration profiles

		root = self.__config.getElementsByTagName('Profiles')[0]
		for profile in root.childNodes:
			if profile.nodeType == profile.ELEMENT_NODE:
				pid = profile.attributes['id'].value
				self.profiles[pid] = {
					'name': profile.getElementsByTagName('Name')[0].firstChild.data
				}
				cfg = profile.getElementsByTagName('Configuration')[0]
				self.profiles[pid]['cfg'] = {}
				srv = cfg.getElementsByTagName('Servers')[0]
				for s in srv.childNodes:
					if s.nodeType == s.ELEMENT_NODE:
						srvid = s.attributes['name'].value
						if len(s.getElementsByTagName("Password")[0].childNodes) > 0:
							pwd = s.getElementsByTagName('Password')[0].firstChild.data
						else:
							pwd = ''
						if len(s.getElementsByTagName('UserInfo')[0].getElementsByTagName('NickServ')[0].childNodes) > 0:
							nserv = s.getElementsByTagName('UserInfo')[0].getElementsByTagName('NickServ')[0].firstChild.data
						else:
							nserv = ''
						self.profiles[pid]['cfg'][srvid] = {
							'name': srvid,
							'host': s.getElementsByTagName('Host')[0].firstChild.data,
							'port': int(s.getElementsByTagName('Port')[0].firstChild.data),
							'encoding': s.getElementsByTagName('Encoding')[0].firstChild.data,
							'ssl': s.getElementsByTagName('SSL')[0].firstChild.data == u'True',
							'password': pwd,
							'welcome_msg': s.getElementsByTagName('WelcomeMessage')[0].firstChild.data,
							'userinfo': {
								'nickname': s.getElementsByTagName('UserInfo')[0].getElementsByTagName('Nickname')[0].firstChild.data,
								'alternative': s.getElementsByTagName('UserInfo')[0].getElementsByTagName('AlternativeNickname')[0].firstChild.data,
								'username': s.getElementsByTagName('UserInfo')[0].getElementsByTagName('Username')[0].firstChild.data,
								'realname': s.getElementsByTagName('UserInfo')[0].getElementsByTagName('Realname')[0].firstChild.data,
								'ident': s.getElementsByTagName('UserInfo')[0].getElementsByTagName('Ident')[0].firstChild.data,
								'nickserv': nserv
							},
							'autojoin': [],
							'version': profile.getElementsByTagName('Version')[0].firstChild.data
						}
						for c in s.getElementsByTagName('AutoJoin')[0].childNodes:
							if c.nodeType == c.ELEMENT_NODE:
								self.profiles[pid]['cfg'][srvid]['autojoin'].append([c.attributes['name'].value, c.attributes['key'].value])

	def get_info(self):
		return self.profiles

class CsIrcCore:
	def __init__(self, profile = 'default', classname = 'Client', modulename = 'irc'):
		self.profile = profile
		self.config = CsIrcConfig()
		self.connectors = {}
		self.params = {}
		
		exec 'import ' + modulename
		#if settings.DEBUG:
		#	print "[DEBUG] Importing Module [" + modulename + "] Class [" + classname + "]"
		debug.debug("Importing module [" + modulename + "] Class [" + classname + "]")
		
		pf = self.config.profiles.get(self.profile)
		if pf:
			for s in pf['cfg']:
				# self.connectors[s] = irc.Client(pf['cfg'][s])
				self.connectors[s] = getattr(locals()[modulename], classname)(pf['cfg'][s])
		
		self.on_server_added = None
		
	# TODO : Add connector to plugin event...
	def associate_to_all(self, plugin_name, modulename = '', classname = '', events = {}, active = True):
		for s in self.connectors:
			exec 'import ' + modulename
			p = getattr(locals()[modulename], classname)(events)
			p.add_property('connector', self.connectors[s])
			self.associate_plugin_to_server(s, plugin_name, p, active)
			
	def dissociate_from_all(self, plugin_name):
		for s in self.connectors:
			self.dissociate_plugin_from_server(s, plugin_name)
		
	def associate_plugin_to_server(self, server, plugin_name, plugin = None, active = True):
		if server in self.connectors:
			self.connectors[server].associate_plugin(plugin_name, plugin, active)
		
	def dissociate_plugin_from_server(self, server, plugin_name):
		if server in self.connectors:
			self.connectors[server].dissociate_plugin(plugin_name)
		
	def set_param(self, param, value):
		self.params[param] = value
		
	def bind_event(self, svname, eventname, callback):
		if svname in self.connectors:
			self.connectors[svname].bind_event(eventname, callback)
			
	def bind_events(self, kw = {}, svname = None):
		if svname is None:
			for sv in self.connectors:
				for k in kw:
					self.bind_event(sv, k, kw[k])
				#if settings.DEBUG:
				#	print "[DEBUG]", self.connectors[sv].events
				debug.debug(str(self.connectors[sv].events))
		else:
			if svname in self.connectors:
				for k in kw:
					self.bind_event(svname, k, kw[k])
				#if settings.DEBUG:
				#	print "[DEBUG]", self.connectors[svname].events
				debug.debug(str(self.connectors[svnname].events))
	
	def unbind_event(self, svname, eventname):
		if svname in self.connectors:
			self.connectors[svname].unbind_event(eventname, callback)
			
	def stop_all(self):
		for s in self.connectors:
			self.stop_bot(s)
		
	def stop_bot(self, svname):
		if svname in self.connectors:
			self.connectors[svname].quit()
		
	def start_bots(self):
		pf = self.config.profiles.get(self.profile)
		if pf:
			for s in pf['cfg']:
				self.connectors[s].start()
				if self.on_server_added:
					self.on_server_added(s)
