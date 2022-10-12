import asyncio
from threading import Thread

from appconfig import AppConfig

from twisted.conch.telnet import TelnetTransport, StatefulTelnetProtocol
from twisted.internet import defer, reactor
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet.protocol import ClientFactory
from twisted.python import log

class MudClient(StatefulTelnetProtocol):
    
    appconfig : AppConfig = None
    
    def __init__(self, appconfig):
        
        self.appconfig = appconfig

        self.connected = False
        self.login_deferred = None
        self.command_deferred = None

        self.command = b''
        self.response = b''

        print(f"Connecting to %s:%s as %s" % (appconfig.bbs_host, appconfig.bbs_port, appconfig.player_username))        
        
        self.done_callback = None

    def connectionMade(self):
        """
        Set rawMode since we do not receive the login and password prompt in line mode.
        We return to default line mode when we detect the prompt in the received data stream.
        """
        self.setRawMode()

    def rawDataReceived(self, bytes):
        """
        The login and password prompt on some systems are not received in lineMode.
        Therefore we do the authentication in raw mode and switch back to line mode
        when we detect the shell prompt.
        TODO: Need to handle authentication failure
        """
        if self.factory.prompt.strip() == br'#':
            self.re_prompt = re.compile(br'\[.*\]')
        else:
            self.re_prompt = re.compile(self.factory.prompt.encode())

        print('Received raw telnet data: %s' % repr(bytes))

        while self.connected == False:
            for (pattern, response) in self.appconfig.bbs_logon_sequence:
                if pattern in bytes:
                    self.sendLine(response.encode())
                    break
                elif self.re_prompt.search(bytes):
                    print('Telnet client logged in. We are ready for commands')
                    self.setLineMode()
                    self.connected = True
                    # second deferred, fired to signal auth is done
                    self.login_deferred.callback(True)

    def lineReceived(self, line):
        # ignore data sent by server before command is sent
        # ignore command echo from server
        if not self.command or line == self.command:
            return

        # trim control characters
        if line.startswith(b'\x1b'):
            line = line[4:]

        print('Received telnet line: %s' % repr(line))

        self.response += line + b'\r\n'

        # start countdown to command done (when reached, consider the output was completely received and close)
        if not self.done_callback:
            self.done_callback = reactor.callLater(0.5, self.close)
        else:
            self.done_callback.reset(0.5)

    def send_command(self, command):
        """
        Sends a command via Telnet using line mode
        """
        self.command = command.encode()
        self.sendLine(self.command)

    def close(self):
        """
        Sends exit to the Telnet server and closes connection.
        Fires the deferred with the command's output.
        """
        self.sendLine(b'exit')
        self.factory.transport.loseConnection()

        # third deferred, to signal command's output was fully received
        self.command_deferred.callback(self.response)
        
    def __init__(self, appconfig):
        super().__init__()
        self.appconfig = appconfig
        self.coro = open_connection(
            host=appconfig.bbs_host,
            port=appconfig.bbs_port,
            encoding='utf-8',
            loop=self.loop,
            shell=self.shell,
            cols=appconfig.terminal_numcols,
            rows=appconfig.terminal_numrows,
            connect_maxwait=appconfig.bbs_timeout.total_seconds() * 1000
        )
        if self.coro != None:
            print("Connection established")
        else:
            print("Connection failed")
    
class TelnetFactory(ClientFactory):
    def __init__(self, username, password, prompt):
        self.username = username
        self.password = password
        self.prompt = prompt
        self.transport = None

    def buildProtocol(self, addr):
        self.transport = TelnetTransport(MudClient)
        self.transport.factory = self
        return self.transport

    def clientConnectionLost(self, connector, reason):
        print('Lost telnet connection.  Reason: %s ' % reason)

    def clientConnectionFailed(self, connector, reason):
        print('Telnet connection failed. Reason:%s ' % reason)

class TelnetClientCommand:
    def __init__(self, prompt, command):
        self.connection_deferred = None

        self.login_deferred = defer.Deferred()
        self.login_deferred.addCallback(self.send_command)

        self.command_deferred = defer.Deferred()
        self.command_deferred.addCallback(self.received_response)

        self.transport = None
        self.prompt = prompt
        self.command = command

    def connect(self, host, port, username, password):
        def check_connection_state(transport):
            """Since we can't use the telnet connection before we have
            logged in and the client is in line_mode 1
            we pause the connection_deferred here until the client is ready
            The client unpuase the defer when wee are logged in
            """
            if transport.protocol.line_mode == 1:
                return transport

            transport.protocol.connected_deferred = self.connection_deferred
            return transport

        def connection_failed(reason):
            print(reason)
            raise TelnetConnectionError(reason)

        # start connection to the Telnet server
        endpoint = TCP4ClientEndpoint(reactor, host, port, 30)
        telnetFactory = TelnetFactory(username, password, self.prompt)
        telnetFactory.protocol = MudClient
        self.connection_deferred = endpoint.connect(telnetFactory)

        # first deferred, fired on connection
        self.connection_deferred.addCallback(check_connection_state)
        self.connection_deferred.addErrback(connection_failed)
        self.connection_deferred.addCallback(self.start_protocol)

    def start_protocol(self, protocol):
        self.transport = protocol.protocol
        self.transport.login_deferred = self.login_deferred
        self.transport.command_deferred = self.command_deferred

    def send_command(self, _):
        self.transport.send_command(self.command)

    def received_response(self, _):
        print(_)