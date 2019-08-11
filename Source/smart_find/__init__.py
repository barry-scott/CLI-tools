#!/usr/bin/env python
# coding: utf-8
from __future__ import print_function
import sys
import os
import subprocess
import json

VERSION = '1.0.0'

default_config_json = u'''{
    "folders_to_prune": [".svn", ".git", ".hg"],
    "files_to_prune":   ["*~"]
}
'''

class SmartFindError(Exception):
    pass

class SmartFind:
    '''
    Find goals
    * Simple find is short to type
    * Find . -name <filename-pattern> => sfind <filename-pattern> 
    * Find dir1 dir2 <filename-pattern> => sfind dir1 dir2 <filename-pattern> 
    * Find new files —since <time spec>, —before <time spec>
    * Add —contains <regex> to grep in found files
    * Only matches type f? Or type file, dir and symlink
    * Limit nesting to <N> levels with -1, -2, -3, etc

    if first arg is dir then use dir else start at .
    '''
    def __init__( self, argv ):
        self.argv = argv
        self.config = None

        self.folders_to_prune = []
        self.folders_to_search = []
        self.file_patterns = []
        self.file_contains = []

        self.opt_debug = False
        self.opt_usage = False
        self.opt_save_config = False

        # None means any depth
        self.opt_depth = None

        self.opt_grep_ignore_case = False
        self.opt_find_iname = False

    def loadConfig( self ):
        self.config = configPathFactory( 'sfind.json', 'sfind.barrys-emacs.org', 'sfind' )
        config_file = self.config.readFilePath()
        if config_file is None:
            json_config = default_config_json
            self.debug( 'Using default builtin config' )
        else:
            self.debug( 'Using config from %s' % (config_file,) )
            with open(config_file) as f:
                json_config = f.read()

        defaults = json.loads( default_config_json )
        user = json.loads( json_config )

        def getConfigSetting( name, user, defaults ):
            if name in user:
                return user[name]
            else:
                return defaults[name]

        self.folders_to_prune = getConfigSetting( 'folders_to_prune', user, defaults )
        self.files_to_prune = getConfigSetting( 'files_to_prune', user, defaults )

    def usage( self ):
        print( 'Usage: %s' % (os.path.basename( self.argv[0] ),) )
        print( '''
    -help               - print this help
    -contains (-c)      - grep for string in found files
    -ignore-case (-i)   - ignore case when greping
    -iname (-in)        - ignore case of filenames
    -save-config        - write the default config
                          into %(config)s
    -debug              - print the find command line
    -<int>              - limit find to a max depth of <int>
''' % {'config': self.config.saveFilePath( False )} )

    def execute( self ):
        try:
            self.parseArgs()
            self.loadConfig()
            self.executeCommand()
            return 0

        except SmartFindError as e:
            print( 'Error: %s' % (e,) )
            return 1

    def parseArgs( self ):
        args = iter( self.argv )
        prog_name = next( args )

        all_plain_args = []

        looking_for_opts = True

        try:
            while True:
                arg = next( args, None )
                if arg is None:
                    break

                if looking_for_opts and arg.startswith( '-' ):
                    if arg == '--':
                        looking_for_opts = False

                    if '-debug' == arg:
                        self.opt_debug = True

                    elif '-save-config' == arg:
                        self.opt_save_config = True

                    elif '-help'.startswith( arg ) and len(arg) >= 2:
                        self.opt_usage = True

                    elif '-iname'.startswith( arg ) and len(arg) >= 3:
                        self.opt_find_iname = True

                    elif '-ignore-case'.startswith( arg ):
                        self.opt_grep_ignore_case = True

                    elif '-contains'.startswith( arg ):
                        self.file_contains.append( next( args ) )

                    # look for -<int>
                    elif isInt( arg[1:] ):
                        self.opt_depth = int( arg[1:] )

                    else:
                        raise SmartFindError( 'Unknown options "%s:"' % (arg,) )

                else:
                    all_plain_args.append( arg )

        except StopIteration:
            raise SmartFindError( 'Need more args' )

        # all args that are not a folder are assumed to be patterns to match
        args = iter(reversed(all_plain_args))

        assume_filename = True
        for arg in args:
            if assume_filename and not os.path.isdir( arg ):
                self.file_patterns.append( arg )

            else:
                self.folders_to_search.append( arg )
                assume_filename = False

        self.folders_to_search = list( reversed( self.folders_to_search ) )

        if len(self.folders_to_search) == 0:
            self.folders_to_search = ['.']

    def executeCommand( self ):
        if self.opt_save_config:
            filename = self.config.saveFilePath( True )
            if os.path.exists( filename ):
                print( 'Config file already exists in %s' % (filename,) )
                return 1

            with open( filename, 'w' ) as f:
                f.write( default_config_json.encode('utf-8') )
                print( 'Wrote default config to %s' % (filename,) )
                return 0

        if self.opt_find_iname:
            opt_name = '-iname'
        else:
            opt_name = '-name'

        cmd = ['/usr/bin/find']
        cmd.extend( [str(path) for path in self.folders_to_search] )
        if self.opt_depth is not None:
            cmd.append( '-maxdepth' )
            cmd.append( '%d' % (self.opt_depth,) )

        # prune all folders that are not interesting
        cmd.extend( ('!', '(', '(') )
        sep = False
        for folder_to_prune in self.folders_to_prune:
            if sep:
                cmd.append( '-o' )
            cmd.extend( ('-path', '*/%s' % (folder_to_prune,)) )
            sep = True

        cmd.extend( (')', '-prune', ')') )

        if len(self.file_patterns) > 0:
            cmd.append( '(' )
            all_filenames = iter( self.file_patterns )
            cmd.append( opt_name )

            cmd.append( next(all_filenames) )
            for filename in all_filenames:
                cmd.append( '-o' )
                cmd.append( opt_name )
                cmd.append( filename )

            cmd.append( ')' )
        for file_to_prune in self.files_to_prune:
            cmd.extend( ('!', '-name', file_to_prune) )

        if len(self.file_contains) > 0:
            cmd.extend( ('-type', 'f', '-exec', 'grep') )
            if self.opt_grep_ignore_case:
                cmd.append( '--ignore-case' )
            cmd.extend( ('--color=always', '--with-filename', '--line-number') )

            for contains in self.file_contains:
                cmd.append( '-e' )
                cmd.append( contains )

            cmd.extend( ('{}', '+') )

        self.debug( ' '.join( ['"%s"' % (s,) for s in cmd] ) )

        if self.opt_usage:
            self.usage()

        elif len(self.file_contains) > 0:
            # turn kill to end of line in the output with ne
            # fn=:ln=:se=99 marks the : with \e[99m:\e[m
            os.environ['GREP_COLORS'] = 'ne:fn=:ln=:se=99'
            p = subprocess.Popen( cmd, stdin=None, stderr=subprocess.STDOUT, stdout=subprocess.PIPE )
            try:
                while True:
                    line = p.stdout.readline()
                    if line == b'':
                        break

                    line = line.decode( 'utf-8' )

                    # print( 'line: %r' % (line,) )
                    if sys.platform == 'darwin':
                        # mac grep is not as configurable as gnu grep
                        parts = line.split( ':', 2 )

                    else:
                        parts = line.split( '\x1b[99m:\x1b[m', 2 )

                    if len(parts) == 3:
                        filename, linenum, match = parts
                        #print( 'Q', repr(filename), '---', repr(linenum), '---', repr(match) )
                        # filename:line:<space>
                        prefix_len = len(filename) + 1 + len(linenum) + 1 + 1
                        pad = 4 - (prefix_len%4)
                        print( '\x1b[35m%s\x1b[m:\x1b[32m%s\x1b[m: %*s%s' %
                                (filename
                                ,linenum
                                ,pad, ''
                                ,match[:-1]) )
                    else:
                        print( line[:-1] )
            except KeyboardInterrupt:
                pass

        else:
            os.execv( cmd[0], cmd )

    def debug( self, msg ):
        if self.opt_debug:
            print( 'Debug: %s' % (msg,) )
            sys.stdout.flush()

    def error( self, msg ):
        print( 'Error: %s' % (msg,) )
        sys.stdout.flush()
        return 1

def isInt( s ):
    try:
        i = int( s )
        return True

    except ValueError:
        return False


def configPathFactory( name, vender, appname ):
    if sys.platform == 'darwin':
        # assume darwin mean macOS
        return MacOsConfigPath( name, vender )

    else:
        # assume all else are XDG compatable
        return XdgConfigPath( name, appname )


class ConfigPath(object):
    def __init__( self ):
        pass

    #
    #   to use a single config files use
    #   saveFilePath and readFilePath
    #
    def saveFilePath( self, mkdir=False ):
        raise NotImplementedError('saveFilePath')

    def readFilePath( self ):
        raise NotImplementedError('readFilePath')

    #
    #   to use a folder of config files use
    #   saveFolderPath and readFolderPath
    #
    def saveFolderPath( self, mkdir=False ):
        raise NotImplementedError('saveFolderPath')

    def readFolderPath( self ):
        raise NotImplementedError('readFolderPath')

class MacOsConfigPath(ConfigPath):
    # vender is a FQDN for the website of the vender for this app
    # example: sfind.barrys-emacs.org
    # name is the apps config filename
    # example: sfind.json
    def __init__( self, name, vender ):
        super(MacOsConfigPath, self).__init__()
        self.name = name
        self.vender = vender

    def saveFolderPath( self, mkdir=False ):
        return self.configFolderPath( mkdir )

    def readFolderPath( self ):
        return self.configFolderPath()

    def saveFilePath( self, mkdir=False ):
        return self.configFilePath( mkdir )

    def readFilePath( self ):
        config_path = self.configFilePath( False )
        if os.path.exists( config_path ):
            return config_path

        return None

    def configFolderPath( self, mkdir ):
        # any folder that do not exist will be created

        # change foo.org into org.foo
        reversed_vender = '.'.join( reversed( self.vender.split('.') ) )

        config_folder = os.path.join( self.getConfigFolder(), reversed_vender )

        if mkdir and not os.path.exists( config_folder ):
                os.makedirs( config_folder )

        return config_folder

    def configFilePath( self, mkdir ):
        # return the path to save the config data into
        config_path = os.path.join( self.getConfigFolder(), self.name )
        return config_path

    def getConfigFolder( self ):
        return os.path.join( os.environ['HOME'], 'Library/Preferences' )


class XdgConfigPath(ConfigPath):
    # if appname is given put the config in a folder of that name
    # name is the name of the config file
    def __init__( self, name, appname ):
        super(XdgConfigPath, self).__init__()
        self.name = name
        self.appname = appname

    def saveFolderPath( self, mkdir=False ):
        config_home = self.getConfigHome()
        config_folder = os.path.join( config_home, self.appname )

        if mkdir and not os.path.exists( config_folder ):
            os.makedirs( config_folder )

        return config_folder

    def readFolderPath( self, mkdir ):
        # return the path to read the folder that store config files.
        # any folder that do not exist will be created
        config_home = self.getConfigHome()
        config_folder = os.path.join( config_home, self.appname )

        if mkdir and not os.path.exists( config_folder ):
            os.makedirs( config_folder )

        return config_folder

    def saveFilePath( self, mkdir=False ):
        # return the path to save the config data into
        # any folder that do not exist will be created
        config_home = self.getConfigHome()
        config_path = os.path.join( config_home, self.name )
        if mkdir and not os.path.exists( config_home ):
            os.makedirs( config_home )

        return config_path

    def readFilePath( self ):
        # look for the config file in the config home then the config dirs
        # return the None is not found otherwise the config path.
        for config_dir in [self.getConfigHome()] + self.getConfigDirs():
            config_path = os.path.join( config_dir, self.name )
            if os.path.exists( config_path ):
                return config_path

        return None

    def getConfigHome( self ):
        return self.getEnvVar( 'XDG_CONFIG_HOME', os.path.join( os.environ['HOME'], '.config' ) )

    def getConfigDirs( self ):
        return self.getEnvVar( 'XDG_CONFIG_DIRS', '/etc/xdg' ).split(':')

    def getEnvVar( self, name, default ):
        # XDG says if missing or empty use the default
        value = os.environ.get( name, '' )
        if value != '':
            return value
        return default

if __name__ == '__main__':
    sys.exit( SmartFind( sys.argv ).execute() )
