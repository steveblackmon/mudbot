
from datetime import timedelta
from pprintpp import pprint
from pyhocon import ConfigFactory
from pyhocon import ConfigTree

class AppConfig:

    config_path : str = None
    typesafe_conf : ConfigTree = None 
    
    bbs_protocol : str = None
    bbs_host : str = None
    bbs_port : int = None
    bbs_timeout : timedelta = None
    bbs_realm = str = None
    bbs_loginsteps : dict = None
    
    player_username : str = None
    player_password : str = None

    server_bind : str = None
    server_port : int = None

    terminal_numrows : int = None
    terminal_numcols : int = None

    def __init__(self, config_path):

        self.config_path = config_path
        pprint(self.config_path)
        
        self.typesafe_conf = ConfigFactory.parse_file(self.config_path)
        pprint(self.typesafe_conf)
        
        self.bbs_protocol = self.typesafe_conf.get('bbs.protocol')
        self.bbs_host = self.typesafe_conf.get('bbs.host')
        self.bbs_port = self.typesafe_conf.get('bbs.port')
        self.bbs_timeout = self.typesafe_conf.get('bbs.timeout')
        self.bbs_realm = self.typesafe_conf.get('bbs.realm')
        self.bbs_logon_sequence = self.typesafe_conf.get('bbs.logon.sequence')

        self.player_username = self.typesafe_conf.get('player.username')
        self.player_password = self.typesafe_conf.get('player.password')

        self.server_bind = self.typesafe_conf.get('server.bind')
        self.server_port = self.typesafe_conf.get('server.port')

        self.terminal_numrows = self.typesafe_conf.get('terminal.numrows')
        self.terminal_numcols = self.typesafe_conf.get('terminal.numcols')

    