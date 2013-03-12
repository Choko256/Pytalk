#-*- coding:utf-8 -*-

# Version Notes
APPLICATION_NAME = 'ChokoBot'
APPLICATION_VERSION = '3.0a'
APPLICATION_COPYRIGHT = 'ChakSoft Computing'
APPLICATION_RELEASE_DATE = '19/02/2013'

# Set DEBUG to True to activate debug lines in console output
DEBUG = True

# Set LOG to True to activate dynamic logging.
# Logs are stored as CSV files
LOG = False
# PostgreSQL database information
LOG_DB = {
	'HOST' : 'localhost',
	'USER' : 'chaksoft',
	'PASSWORD' : 'bMfHOKqw3XmK',
	'DATABASE' : 'botlog',
	'PORT' : '5432'
}

# Buffer size for network socket input
BUFFER_SIZE = 2048

# Message separator on IRC (do not change)
SEPARATOR = "\r\n"

# Default quit message
QUIT_MESSAGE = "Bwah !"
# Default part message
PART_MESSAGE = "Au revoir ! (part)"

# Automatic join on kick
# Set to True to force a new JOIN message after being kicked from a channel
AUTO_JOIN_KICK = False

# Administrators (can run special commands for robots)
ADMINS = [
	'Choko',
	'Chokaw',
	'miam',
	'DieuLePere',
	'LapinCretin',
	'Krevett`',
	'Quarante-Deux',
	'Marlitaa',
	'Rubiana',
	'Rubianaway'
]

# Game Statistics Files, with differents paths
GAMESTAT_DB = (
	# 'C:/Dev/ChokoBot/V2/game/stat/stat.db',
	# '/home/mchoko/dev/chokobot/V2/game/stat/stat.db',
	# '/home/choko/chokobot/V2/game/stat/stat.db',
	'C:/Users/Choko/Documents/CHOKOBOT/V3/game/stat/stat.db',
)

# Numeric commands dictionary
# Used for translating command into event type
#!!# Please do not change this dictionary #!!#
NUMERIC_COMMANDS = {
	'001': 'welcome',
	'002': 'serververinfo',
	'003': 'servercreatdate',
	'004': 'servermodes',
	'200': 'tracelink',
	'201': 'traceconnecting',
	'202': 'tracehandshake',
	'203': 'traceunknown',
	'204': 'traceoperator',
	'205': 'traceuser',
	'206': 'traceserver',
	'208': 'tracenewtype',
	'261': 'tracelog',
	'211': 'statslinkinfo',
	'212': 'statscommands',
	'213': 'statscline',
	'214': 'statsnline',
	'215': 'statsiline',
	'216': 'statskline',
	'218': 'statsyline',
	'219': 'endofstats',
	'241': 'statssline',
	'242': 'statsuptime',
	'243': 'statsoline',
	'244': 'statshline',
	'221': 'umodels',
	'251': 'luserclient',
	'252': 'luserop',
	'253': 'luserunknown',
	'254': 'luserchannels',
	'255': 'luserme',
	'256': 'adminme',
	'257': 'adminloc1',
	'258': 'adminloc2',
	'259': 'adminemail',
	'300': 'none',
	'301': 'away',
	'302': 'userhost',
	'303': 'ison',
	'305': 'unaway',
	'306': 'noaway',
	'311': 'whoisuser',
	'312': 'whoisserver',
	'313': 'whoisoperator',
	'317': 'whoisidle',
	'318': 'endofwhois',
	'319': 'whoischannels',
	'314': 'whowasuser',
	'369': 'endofwhowas',
	'321': 'liststart',
	'322': 'list',
	'323': 'listend',
	'324': 'channelmodeis',
	'331': 'notopic',
	'332': 'topic',
	'341': 'inviting',
	'342': 'summoning',
	'351': 'version',
	'352': 'whoreply',
	'315': 'endofwho',
	'353': 'namreply',
	'366': 'endofnames',
	'364': 'links',
	'365': 'endoflinks',
	'367': 'banlist',
	'368': 'endofbanlist',
	'371': 'info',
	'374': 'endofinfo',
	'375': 'motdstart',
	'372': 'motd',
	'376': 'endofmotd',
	'381': 'youreoper',
	'382': 'rehashing',
	'391': 'time',
	'392': 'usersstart',
	'393': 'users',
	'394': 'endofusers',
	'395': 'nousers',
	'401': 'nosuchnick',
	'402': 'nosuchserver',
	'403': 'nosuchchannel',
	'404': 'cannotsendtochan',
	'405': 'toomanychannels',
	'406': 'wasnosuchnick',
	'407': 'toomanytargets',
	'409': 'noorigin',
	'411': 'norecipient',
	'412': 'notexttosend',
	'413': 'notoplevel',
	'414': 'wildtoplevel',
	'421': 'unknowncommand',
	'422': 'nomotd',
	'423': 'noadmininfo',
	'424': 'fileerror',
	'431': 'nonicknamegiven',
	'432': 'erroneusnickname',
	'433': 'nicknameinuse',
	'436': 'nickcollision',
	'441': 'usernotinchannel',
	'442': 'notonchannel',
	'443': 'useronchannel',
	'444': 'nologin',
	'445': 'summondisabled',
	'446': 'usersdisabled',
	'451': 'notregistered',
	'461': 'needmoreparams',
	'462': 'alreadyregistered',
	'463': 'nopermforhost',
	'464': 'passwdmismatch',
	'465': 'yourebannedcreep',
	'467': 'keyset',
	'471': 'channelisfull',
	'472': 'unknownmode',
	'473': 'inviteonlychan',
	'474': 'bannedfromchan',
	'475': 'badchannelkey',
	'481': 'noprivileges',
	'482': 'chanoprivsneeded',
	'483': 'cantkillserver',
	'491': 'nooperhost',
	'501': 'umodeunknownflag',
	'502': 'usersdontmatch',
	'209': 'traceclass',
	'217': 'statsqline',
	'231': 'serviceinfo',
	'232': 'endofservices',
	'233': 'service',
	'235': 'servlistend',
	'316': 'whoischanop',
	'361': 'killdone',
	'362': 'closing',
	'363': 'closeend',
	'373': 'infostart',
	'384': 'myportis',
	'466': 'youwillbebanned',
	'476': 'badchanmask',
	'492': 'noservicehost'
}
