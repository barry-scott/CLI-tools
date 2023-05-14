import sys
import datetime
import subprocess
import time
import socket
import platform
import tempfile
import json
from config_path import ConfigPath  # type: ignore

VERSION = '2.3.0'

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

        self.all_hosts = list( self.hostIter( positional_args ) )

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

                os_plugin_type, os_id = self.detectOperatingSystem( host )
                if os_plugin_type is None:
                    if os_id is not None:
                        self.warn( host, 'Unsupported OS type %s' % (os_id,) )
                    continue

                self.info( host, 'OS is %s. Using OS plugin %s' % (os_id, os_plugin_type) )

                plugin = os_id_to_plugin[ os_plugin_type ]( self )

                self.flushDns()
                if self.opt_check:
                    plugin.check( host,
                        check_log_name=self.logdir / ('check-update-%s-%s.log' % (host, self.ts)) )

                elif self.opt_install_package() is not None:
                    self.installPackage( host, self.opt_install_package,
                        update_log_name=self.logdir / ('install-%s-%s.log' % (host, self.ts)) )

                else:
                    if self.isThisHost( host ):
                        self.warn( host, 'Refusing to update this host' )

                    elif self.opt_system_upgrade:
                        plugin.systemUpgrade( host, self.opt_system_upgrade,
                            upgrade_log_name=self.logdir / ('upgrade-%s-%s.log' % (host, self.ts)) )

                    else:
                        plugin.update( host,
                            update_log_name=self.logdir / ('update-%s-%s.log' % (host, self.ts)),
                            status_log_name=self.logdir / ('status-%s-%s.log' % (host, self.ts)) )

        print( '-' * 60 )
        for line in self.all_summary_lines:
            print( line )

        return 0

    def hostIter( self, all_groups_or_hosts, _handled=None ):
        if _handled is None:
            _handled = set()

        for group_or_host in all_groups_or_hosts:
            # deal with recursive groups and duplicate host
            # by ignoring them
            if group_or_host in _handled:
                continue

            _handled.add( group_or_host )
            if group_or_host in self.all_groups:
                yield from self.hostIter( self.all_groups[ group_or_host ], _handled )

            else:
                yield group_or_host

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

    def detectOperatingSystem( self, host ):
        rc = ssh_wait( host, wait=False, log_fn=None )
        if rc != 0:
            self.warn( host, 'Is not reachable' )
            return None, None

        os_release = {}

        cmd = ['cat', '/etc/os-release']
        rc, stdout = self.runAndLog( host, cmd, log=False )
        for line in stdout:
            line = line.strip()
            if line == '' or '=' not in line:
                continue

            key, value = line.split( '=', 1 )
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            os_release[key] = value

        os_main_id = os_release.get('ID', None)
        os_id_set = set([os_main_id])
        if 'ID_LIKE' in os_release:
            for ID in os_release['ID_LIKE'].split():
                os_id_set.add( ID )

        for os_id in os_id_set:
            if os_id in os_id_to_plugin:
                return os_id, os_main_id

        return None, os_main_id

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

            self.info( host, 'Retry reboot in 10s' )
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

        if len(stdout) < 1 and not stdout[0].startswith( '0 loaded units listed.' ):
            for line in stdout:
                print( self.ct( '<>proc %s<>: %s' % (host, line.rstrip()) ) )

            self.error( host, 'Some services failed' )
            return False

        self.info( host, 'All services running' )
        return True

    def waitAllSystemdJobsFinished( self, host, log_name=None ):
        self.info( host, 'Check all systemd jobs finished' )
        while True:
            cmd = ['systemctl', 'list-jobs']
            rc, stdout = self.runAndLog( host, cmd )
            self.writeLines( log_name, stdout )
            if rc != 0:
                self.error( host, 'cannot list jobs' )
                return

            if 'No jobs running.\n' in stdout:
                self.info( host, 'All systemd jobs finished' )
                break

            time.sleep( 10 )

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

class UpdatePluginFedora:
    def __init__( self, app ):
        self.app = app

    def check( self, host, check_log_name ):
        rc = ssh_wait( host, wait=False, log_fn=None )
        if rc != 0:
            self.app.warn( host, 'Is not reachable' )
            return

        self.app.info( host, 'Starting Check for Updates' )
        cmd = ['dnf', 'check-update', '--refresh']
        rc, stdout = self.app.runAndLog( host, cmd, log=False )
        self.app.writeLines( check_log_name, stdout )

        if rc == 0:
            self.app.info( host, 'Already up to date' )

        elif rc == 100:
            self.app.warn( host, 'Updates available' )

        else:
            self.app.error( host, 'check-update failed' )

        self.app.checkServices( host, check_log_name )

        release = self.releaseInfo( host )
        self.app.info( host, 'Running on release %s' % (release,) )

    def installPackage( self, host, package, install_log_name ):
        rc = ssh_wait( host, wait=False, log_fn=None )
        if rc != 0:
            self.app.warn( host, 'Is not reachable' )
            return

        cmd = ['dnf', '-y', 'install', '--refresh', package]
        rc, stdout = self.app.runAndLog( host, cmd )

        self.app.writeLines( install_log_name, stdout )

        if rc != 0:
            self.app.error( host, 'Install failed' )
            return

    def update( self, host, update_log_name, status_log_name ):
        rc = ssh_wait( host, wait=False, log_fn=None )
        if rc != 0:
            self.app.warn( host, 'Is not reachable' )
            return

        self.app.info( host, 'Starting Update' )

        cmd = ['dnf', '-vy', 'update', '--refresh']
        rc, stdout = self.app.runAndLog( host, cmd )

        self.app.writeLines( update_log_name, stdout )

        if rc != 0:
            self.app.error( host, 'Update failed' )
            return

        if 'Nothing to do.\n' in stdout:
            self.app.info( host, 'Already up to date' )
            if not self.app.opt_force_reboot:
                return

        self.app.waitAllSystemdJobsFinished( host, update_log_name )

        self.app.info( host, 'Rebooting' )
        if self.app.reboot( host, ['reboot'] ):
            self.app.checkServices( host, status_log_name )

    def systemUpgrade( self, host, target_release, upgrade_log_name ):
        current_release = self.app.releaseInfo( host )
        if current_release == target_release:
            self.app.info( host, 'Already running release %d' % (target_release,) )
            return

        self.app.info( host, 'Currently release %d' % (current_release,) )

        # only update by one release at a time
        next_release = current_release + 1

        cmd = ['dnf', 'system-upgrade', 'download', '--releasever=%d' % (next_release,), '--assumeyes']
        rc, stdout = self.app.runAndLog( host, cmd )
        self.app.writeLines( upgrade_log_name, stdout )

        if rc != 0:
            self.app.error( host, 'Failure to download release %d' % (next_release,) )
            return

        self.app.info( host, 'Rebooting to install system-upgrade' )
        # upgrades of lots of packages can be slow - wait for 45 minutes
        if self.app.reboot( host, ['dnf', 'system-upgrade', 'reboot'], wait_limit=45*60 ):
            self.app.checkServices( host, upgrade_log_name )

        self.app.info( host, 'Now running release %d' % (self.app.releaseInfo( host ),) )

    def releaseInfo( self, host ):
        cmd = ['cat', '/etc/system-release-cpe']
        rc, stdout = self.app.runAndLog( host, cmd, log=False )
        cpe_parts = stdout[0].strip().split( ':' )
        if len(cpe_parts) >= 4:
            return int( cpe_parts[4] )

        self.app.error( host, 'Not enough fields in /etc/system-release-cpe - %r' % (cpe_parts,) )
        return 0


class UpdatePluginDebian:
    def __init__( self, app ):
        self.app = app

    def check( self, host, check_log_name ):
        rc = ssh_wait( host, wait=False, log_fn=None )
        if rc != 0:
            self.app.warn( host, 'Is not reachable' )
            return

        self.app.info( host, 'Starting Check for Updates' )
        cmd = ['apt-get', 'update', '--assume-yes']
        rc, stdout = self.app.runAndLog( host, cmd, log=False )
        self.app.writeLines( check_log_name, stdout )
        if rc != 0:
            self.app.error( host, 'apt-get update failed' )
            return

        cmd = ['apt-get', 'upgrade', '--assume-no']
        rc, stdout = self.app.runAndLog( host, cmd, log=False )
        self.app.debug( 'check_log_name %s' % (check_log_name,) )
        self.app.writeLines( check_log_name, stdout )

        for line in stdout:
            words = line.split()
            self.app.debug( 'apt-get-upgrade: %r' % (words,) )
            if len(words) >= 2 and words[1] == 'upgraded,':
                if words[0] == '0':
                    self.app.info( host, 'Already up to date' )

                else:
                    self.app.warn( host, 'Updates available: %s' % (line,) )

                self.app.checkServices( host, check_log_name )
                return

        self.app.error( host, 'apt-get upgrade failed' )

    def installPackage( self, host, package, install_log_name ):
        pass

    def update( self, host, update_log_name, status_log_name ):
        rc = ssh_wait( host, wait=False, log_fn=None )
        if rc != 0:
            self.app.warn( host, 'Is not reachable' )
            return

        self.app.info( host, 'Starting Update' )
        cmd = ['apt-get', 'update', '--assume-yes']
        rc, stdout = self.app.runAndLog( host, cmd, log=False )
        self.app.writeLines( update_log_name, stdout )
        if rc != 0:
            self.app.error( host, 'apt-get update failed' )
            return

        cmd = ['apt-get', 'upgrade', '--assume-yes']
        rc, stdout = self.app.runAndLog( host, cmd )

        self.app.writeLines( update_log_name, stdout )

        for line in stdout:
            words = line.split()
            self.app.debug( 'apt-get-upgrade: %r' % (words,) )
            if len(words) >= 2 and words[1] == 'upgraded,':
                if words[0] == '0':
                    self.app.info( host, 'Already up to date' )
                    if not self.app.opt_force_reboot:
                        return

                else:
                    self.app.info( host, 'Updated: %s' % (line,) )
                break

        self.updateAptFileDatabase( host, update_log_name )

        self.app.waitAllSystemdJobsFinished( host, update_log_name )

        self.app.info( host, 'Rebooting' )
        if self.app.reboot( host, ['reboot'] ):
            self.app.checkServices( host, status_log_name )

    def updateAptFileDatabase( self, host, update_log_name ):
        cmd = ['/usr/bin/test', '-x', '/usr/bin/apt-file']
        rc, stdout = self.app.runAndLog( host, cmd, log=False )
        if rc == 0:
            self.app.info( host, 'Updating apt-file database' )
            cmd = ['/usr/bin/apt-file', 'update']
            rc, stdout = self.app.runAndLog( host, cmd, log=True )
            self.app.writeLines( update_log_name, stdout )

    def systemUpgrade( self, host, target_release, upgrade_log_name ):
        pass


os_id_to_plugin = {
    'fedora':   UpdatePluginFedora,
    'debian':   UpdatePluginDebian,
    }
