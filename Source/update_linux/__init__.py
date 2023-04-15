import sys
import datetime
import subprocess
import time
import socket
import platform
import tempfile
import json
from config_path import ConfigPath

VERSION = '2.1.1'

default_json_config_template = u'''{
    "group":
        {"all": []},
    "logdir":   "%(logdir)s"
}
'''


from pathlib import Path

from colour_text import ColourText
from ssh_wait import ssh_wait

class OptionError(Exception):
    pass

class Option:
    def __init__( self, name, default, value_type=None, value_name=None, description=None ):
        self.name = name
        self.default = default
        self.value_type = value_type
        self.value_name = value_name
        self.description = description

        self.is_present = False
        self.value = self.default

    def parse( self, arg ):
        # if is has a value type then there is a value to parse
        if self.value_type is not None:
            prefix = self.name + '='
            if arg.startswith( prefix ):
                self.is_present = True
                if self.value_type is not None:
                    try:
                        self.value = self.value_type( arg[len(prefix):] )

                    except ValueError as e:
                        raise OptionError( '%s type error %s' % (self.name, e) )

                else:
                    self.value = arg[len(name):]
                return True

            if arg == self.name:
                raise OptionError( '%s expects a value' % (self.name,) )

        else:
            if arg == self.name:
                self.is_present = True
                return True

        return False

    def __repr__( self ):
        return '<Option: %s present: %r value: %r>' % (self.name, self.is_present, self.value)

    def __bool__( self ):
        return self.is_present

    def __call__( self ):
        return self.value

    def help( self ):
        all_help = []
        if self.value_type is not None:
            all_help.append( '%s=%s default %s' %
                (self.name
                ,self.value_name
                ,{True: 'On', False: 'Off'}.get( self.default, self.default ) ))

        else:
            all_help.append( '%s default %s' %
                (self.name
                ,{True: 'On', False: 'Off'}.get( self.default, self.default ) ))

        if self.description:
            for line in self.description.split('\n'):
                all_help.append( '    %s' % (line,) )

        return all_help


def parseOptions( storage, positional_args, args, debug=False ):
    for arg in args:
        if debug: print( 'debug: arg %s' % (arg,) )
        if arg.startswith('-'):
            for name in dir(storage):
                value = getattr( storage, name )
                #print( 'debug: storage.%s: %r' % (name, value) )
                if isinstance( value, Option ):
                    #print( 'debug: Matching against %r' % (value,) )
                    if value.parse( arg ):
                        if debug: print( 'debug: %s present value %r' % (value.name, value()) )
                        break

            else: # no break
                raise OptionError( 'Unknown option %s' % (arg,) )
        else:
            if debug: print( 'debug: is positional arg' )
            positional_args.append( arg )

def printOptionsHelp( storage ):
    for name in dir( storage ):
        value = getattr( storage, name )
        if isinstance( value, Option ):
            for line in value.help():
                print( '        %s' % (line,) )
            print()

class UpdateFedora:
    def __init__( self ):
        self.all_hosts = []
        self.opt_help = Option( '--help', False,
                            description='print this help' )
        self.opt_debug = Option( '--debug', False,
                            description='print debug messages' )
        self.opt_check = Option( '--check', False,
                            description='check if update is required' )
        self.opt_exclude = Option( '--exclude', None, value_type=str, value_name='<host>',
                            description='exclude the <host> from being updated'  )
        self.opt_system_upgrade = Option( '--system-upgrade', None, value_type=int, value_name='<version>',
                            description='perform a system upgrade to version <version>' )
        self.opt_force_reboot = Option( '--force-reboot', False,
                            description='always reboot host even if no packages where updated' )
        self.opt_install_package = Option( '--install-package', None, value_type=str, value_name='<package>',
                            description='install <package> only' )
        self.opt_list_config = Option( '--list-config', False,
                            description='list the configuration from the JSON config file' )

        self.ct = ColourText()
        self.ct.initTerminal()
        self.ct.define( 'host', 'lightblue' )
        self.ct.define( 'proc', 'magenta' )

        t = datetime.datetime.now()
        self.ts = t.strftime( '%Y-%m-%d' )
        self.summary_log_name = None
        self.summary_log = None
        self.all_summary_lines = []

    def main( self, argv ):
        args = iter(argv)
        appname = Path( next(args) )

        positional_args = []

        if not self.loadConfig():
            return 1

        try:
            parseOptions( self, positional_args, args )

        except OptionError as e:
            self.error( '', str(e) )
            return 1

        if self.opt_help:
            print(
'''Usage: %(appname)s <options> <group>|<host>...

    %(appname)s version %(version)s

    group - read from the JSON config file:
            %(config_file)s

        each group is a list of hosts to be updated

    host - host to be updated

    options:''' % {'appname': appname.name
                  ,'version': VERSION
                  ,'config_file': self.config.readFilePath()} )

            printOptionsHelp( self )
            return 0

        if self.opt_list_config:
            fmt = '%-16s  %s'
            print( fmt % ('Group', 'Hosts') )
            print( fmt % ('-----', '-----') )

            for group in self.all_groups:
                print( fmt % (group, ', '.join( self.all_groups[ group ]) ) )

            print()
            print( 'Log directory: %s' % (self.logdir,) )
            return 0

        all_to_exclude = []
        if self.opt_exclude:
            all_to_exclude = self.all_groups.get( self.opt_exclude(), self.opt_exclude() )

        for group_or_host in positional_args:
            if group_or_host in self.all_groups:
                for host in self.all_groups[ group_or_host ]:
                    if host not in all_to_exclude:
                        self.all_hosts.append( host )
            else:
                if group_or_host not in all_to_exclude:
                    self.all_hosts.append( group_or_host )

        if len(self.all_hosts) == 0:
            self.error( '', 'No hosts to update' )
            print('''
For help:
    %s --help
''' % (appname.name,))
            return 1

        self.summary_log_name = self.logdir / ('update-summary-%s.log' % (self.ts,))

        with open( self.summary_log_name, 'a' ) as self.summary_log:
            t = datetime.datetime.now()
            self.header( 'Update summary %s' % (t.strftime( '%Y-%m-%d %H:%M:%S' ),) )

            for host in self.all_hosts:
                if host in all_to_exclude:
                    continue

                self.flushDns()
                if self.opt_check:
                    self.check( host )

                elif self.opt_install_package() is not None:
                    self.installPackage( host, self.opt_install_package )

                else:
                    if self.isThisHost( host ):
                        self.warn( host, 'Refusing to update this host' )

                    elif self.opt_system_upgrade:
                        self.systemUpgrade( host, self.opt_system_upgrade )

                    else:
                        self.update( host )

        print( '-' * 60 )
        for line in self.all_summary_lines:
            print( line )

        return 0

    def isThisHost( self, other_host ):
        this_host = socket.gethostname()
        this_info = socket.getaddrinfo( this_host, 'ssh', proto=socket.IPPROTO_TCP )
        this_addrs = set(info[4][0] for info in this_info) | set(['::1', '127.0.0.1'])

        try:
            other_info = socket.getaddrinfo( other_host, 'ssh', proto=socket.IPPROTO_TCP )
        except socket.gaierror as e:
            self.warn( other_host, str(e) )
            # return true to prevent update
            return True

        other_addrs = set(info[4][0] for info in other_info)

        # share any address in common?
        return len(this_addrs & other_addrs) > 0

    def loadConfig( self ):
        self.config = ConfigPath( 'update-linux', 'barrys-emacs.org', '.json' )
        config_file = self.config.readFilePath()
        default_json_config = default_json_config_template % {
                        'logdir': tempfile.gettempdir()
                        }
        if config_file is None:
            json_config = default_json_config
            self.debug( 'Using default builtin config' )
            config_file = self.config.saveFilePath( True )
            self.info( '', 'Creating default config in %s' % (config_file,) )
            with open( config_file, 'w' ) as f:
                f.write( json_config )

        else:
            self.info( '', 'Using config from %s' % (config_file,) )
            with open(config_file) as f:
                json_config = f.read()

        defaults = json.loads( default_json_config )
        try:
            user = json.loads( json_config )

        except json.decoder.JSONDecodeError as e:
            self.error( config_file, e )
            return False

        def getConfigSetting( name, user, defaults ):
            if name in user:
                return user[name]
            else:
                return defaults[name]

        self.all_groups = getConfigSetting( 'group', user, defaults )
        self.logdir = Path( getConfigSetting( 'logdir', user, defaults ) ).expanduser()

        return True

    def flushDns( self ):
        if platform.mac_ver()[0] == '':
            return

        # mac often needs its DNS cache flushing as it will
        # not notice newly booted hosts
        cmd = ['sudo', 'killall', '-HUP', 'mDNSResponder']
        self.runAndLog( None, cmd, log=False )

    def check( self, host ):
        rc = ssh_wait( host, wait=False, log_fn=None )
        if rc != 0:
            self.warn( host, 'Is not reachable' )
            return

        check_log_name = self.logdir / ('check-update-%s-%s.log' % (host, self.ts))

        self.info( host, 'Starting Check for Updates' )
        cmd = ['dnf', 'check-update', '--refresh']
        rc, stdout = self.runAndLog( host, cmd, log=False )
        self.writeLines( check_log_name, stdout )

        if rc == 0:
            self.info( host, 'Already up to date' )

        elif rc == 100:
            self.warn( host, 'Updates available' )

        else:
            self.error( host, 'check-update failed' )

        self.checkServices( host, check_log_name )

        release = self.releaseInfo( host )
        self.info( host, 'Running on Fedora release %s' % (release,) )

    def releaseInfo( self, host ):
        cmd = ['cat', '/etc/system-release-cpe']
        rc, stdout = self.runAndLog( host, cmd, log=False )
        cpe_parts = stdout[0].strip().split( ':' )
        if cpe_parts[3] != 'fedora':
            self.error( host, 'Host is not running Fedora' )
        return int( cpe_parts[4] )

    def installPackage( self, host, package ):
        rc = ssh_wait( host, wait=False, log_fn=None )
        if rc != 0:
            self.warn( host, 'Is not reachable' )
            return

        install_log_name = self.logdir / ('install-%s-%s.log' % (host, self.ts))

        cmd = ['dnf', '-y', 'install', '--refresh', package]
        rc, stdout = self.runAndLog( host, cmd )

        self.writeLines( install_log_name, stdout )

        if rc != 0:
            self.error( host, 'Install failed' )
            return

    def update( self, host ):
        rc = ssh_wait( host, wait=False, log_fn=None )
        if rc != 0:
            self.warn( host, 'Is not reachable' )
            return

        self.info( host, 'Starting Update' )

        update_log_name = self.logdir / ('update-%s-%s.log' % (host, self.ts))
        status_log_name = self.logdir / ('status-%s-%s.log' % (host, self.ts))

        cmd = ['dnf', '-vy', 'update', '--refresh']
        rc, stdout = self.runAndLog( host, cmd )

        self.writeLines( update_log_name, stdout )

        if rc != 0:
            self.error( host, 'Update failed' )
            return

        if 'Nothing to do.\n' in stdout:
            self.info( host, 'Already up to date' )
            if not self.opt_force_reboot:
                return

        self.info( host, 'Check all systemd jobs finished' )
        while True:
            cmd = ['systemctl', 'list-jobs']
            rc, stdout = self.runAndLog( host, cmd )
            self.writeLines( update_log_name, stdout )
            if rc != 0:
                self.error( host, 'cannot list jobs' )
                return

            if 'No jobs running.\n' in stdout:
                self.info( host, 'All systemd jobs finished' )
                break

            time.sleep( 10 )

        self.info( host, 'Rebooting' )
        if self.reboot( host, ['reboot'] ):
            self.checkServices( host, status_log_name )

    def reboot( self, host, cmd, wait_limit=600 ):
        while True:
            rc, stdout = self.runAndLog( host, cmd )
            if len(stdout) == 0:
                # no messages assume ok
                break

            if stdout[0] == ('Connection to %s closed by remote host.\r\n' % (host,)):
                # this is success
                break

            self.error( host, 'reboot stdout: %r' % (stdout,) )

            self.info( 'Retry reboot in 10s' )
            time.sleep( 10 )

        # wait for system to go down
        time.sleep( 30 )
        # wait for it to come back up
        rc = ssh_wait( host, log_fn=None, wait_limit=wait_limit )
        if rc != 0:
            self.error( host, 'Failed to reboot' )
            return False

        return True

    def checkServices( self, host, log_name=None ):
        cmd = ['systemctl', '--failed']
        rc, stdout = self.runAndLog( host, cmd, log=False )
        if log_name is not None:
            self.writeLines( log_name, stdout )

        if '0 loaded units listed.\n' not in stdout:
            for line in stdout:
                print( self.ct( '<>proc %s<>: %s' % (host, line.rstrip()) ) )

            self.error( host, 'Some services failed' )
            return False

        self.info( host, 'All services running' )
        return True

    def systemUpgrade( self, host, target_release ):
        current_release = self.releaseInfo( host )
        if current_release == target_release:
            self.info( host, 'Already running Fedora release %d' % (target_release,) )
            return

        upgrade_log_name = self.logdir / ('update-%s-%s.log' % (host, self.ts))

        self.info( host, 'Currently Fedora release %d' % (current_release,) )

        # only update by one release at a time
        next_release = current_release + 1

        cmd = ['dnf', 'system-upgrade', 'download', '--releasever=%d' % (next_release,), '--assumeyes']
        rc, stdout = self.runAndLog( host, cmd )
        self.writeLines( upgrade_log_name, stdout )

        if rc != 0:
            self.error( host, 'Failure to download release %d' % (next_release,) )
            return

        self.info( host, 'Rebooting to install system-upgrade' )
        # upgrades of lots of packages can be slow - wait for 45 minutes
        if self.reboot( host, ['dnf', 'system-upgrade', 'reboot'], wait_limit=45*60 ):
            self.checkServices( host, upgrade_log_name )

        self.info( host, 'Now running Fedora release %d' % (self.releaseInfo( host ),) )

    def runAndLog( self, host, cmd, log=True ):
        if host is not None:
            cmd = ['ssh', 'root@%s' % (host,)] + cmd

        self.debug( 'runAndLog( %s )' % (' '.join( cmd ),) )
        stdout = []
        p = subprocess.Popen( cmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE )
        while True:
            line = p.stdout.readline()
            if line == b'':
                break
            line = line.decode( 'utf-8' )
            if log:
                print( self.ct( '<>proc %s<>: %s' % (host, line.rstrip()) ) )
            stdout.append( line )

        p.wait( 5 )
        self.debug( 'runAndLog rc=%d' % (p.returncode,) )
        return p.returncode, stdout

    def writeLines( self, filename, all_lines ):
        with open( filename, 'a' ) as f:
            for line in all_lines:
                f.write( line )

    # log functions
    def debug( self, msg ):
        if self.opt_debug:
            print( self.ct( '<>red Debug:<> %s' % (msg,) ), flush=True )

    def info( self, host, msg ):
        self._log( '<>info %(TIME)s<> <>host %(HOST)10s<> %(MSG)s', host, msg )

    def error( self, host, msg ):
        self._log( '<>error %(TIME)s<> <>host %(HOST)10s<> <>error %(MSG)s<>', host, msg )

    def warn( self, host, msg ):
        self._log( '<>em %(TIME)s<> <>host %(HOST)10s<> <>em %(MSG)s<>', host, msg )

    def header( self, msg ):
        self._log( '<>em %(MSG)s<>', '', msg )

    def _log( self, fmt, host, msg ):
        t = datetime.datetime.now()
        log_line = self.ct( fmt % {'HOST': host
                                  ,'TIME': t.strftime( '%H:%M:%S' )
                                  ,'MSG': msg} )
        print( log_line, flush=True )
        if self.summary_log is not None:
            print( log_line, file=self.summary_log, flush=True )
            self.all_summary_lines.append( log_line )
