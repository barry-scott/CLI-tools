#!/usr/bin/env python
# coding: utf-8
from __future__ import print_function

import sys
import os
import colour_filter
import colour_text
import json


'''
               0   to restore default color
               1   for brighter colors
               4   for underlined text
               5   for flashing text
              30   for black foreground
              31   for red foreground
              32   for green foreground
              33   for yellow (or brown) foreground
              34   for blue foreground
              35   for purple foreground
              36   for cyan foreground
              37   for white (or gray) foreground
              40   for black background
              41   for red background
              42   for green background
              43   for yellow (or brown) background
              44   for blue background
              45   for purple background
              46   for cyan background
              47   for white (or gray) background
'''

def usage( ct ):
    print( ct('''Usage: colour_filter <options> [<>em pattern<> <>em colour<>]*

Read lines from stdin and print them colour based on the <>em pattern<> <>em colour<> pairs.

The <>em pattern<> <>em colour<> pairs can be supplied on the command line or taken from a
pre-defined scheme.


Options:
    --scheme=<>em scheme<> - filter using filter scheme <>em scheme<>
    --define-scheme=<>em scheme<> - define a filter scheme from the <>em pattern<> <>em colour<> pairs
    --show-schemes - show all the schemes that have been defined.
''') )

def main():
    args = iter( sys.argv )
    prog_name = next( args )

    opt_define_scheme = False
    opt_show_schemes = False
    opt_scheme = None

    all_filters = []

    ct = colour_text.ColourText()
    cf = colour_filter.ColourFilter()

    ct.initTerminal()

    try:
        while True:
            arg = next( args, None )
            if arg is None:
                break

            if arg.startswith( '-' ):
                if '--debug' == arg:
                    cf.enableDebug()

                elif arg in ('-h', '--help'):
                    usage( ct )
                    return 0

                elif arg.startswith('--scheme='):
                    opt_scheme = arg[len('--scheme='):]

                elif arg.startswith('--define-scheme='):
                    opt_define_scheme = True
                    opt_scheme = arg[len('--define-scheme='):]

                elif arg == '--show-schemes':
                    opt_show_schemes = True

                else:
                    print( ct('<>error Error:<> Unknown options "%s"') % (arg,) )
                    return 1

            else:
                pattern = arg
                colour = next( args )
                all_filters.append( (pattern, colour) )
                cf.define( pattern, colour )

        config_path = configPathFactory( 'colour-filter.json', 'colour-filter.barrys-emacs.org', 'colour-filter' )
        config = {}

        # load the config
        config_file = config_path.readFilePath()
        if config_file is not None:
            with open( config_file, 'r' ) as f:
                config = json.load( f )

        if opt_show_schemes:
            if len(config) == 0:
                print( 'No schemes are defined' )
                return 0

            for scheme in config:
                print( ct('Scheme <>info %s<>') % (scheme,) )
                for pattern, colour in config[scheme]:
                    print( ct('    %%s: <>%s %%s<>' % (colour,)) % (pattern, colour) )

            return 0

        if opt_define_scheme:
            config[opt_scheme] = all_filters

            config_file = config_path.saveFilePath()
            with open( config_file, 'w' ) as f:
                json.dump( config, f )

            print( ct('<>info Added scheme %s with %d definitions<>') % (opt_scheme, len(config[opt_scheme])) )
            return 0

        if opt_scheme is not None:
            if opt_scheme not in config:
                print( ct('<>error Error: Unknown scheme %s') % (opt_scheme,) )
                return 1

            for pattern, colour in config[opt_scheme]:
                cf.define( pattern, colour )

        cf.filterLines( sys.stdin, sys.stdout, line_buffered=True )
        return 0

    except StopIteration:
        print( ct('<>error Error:<> Need more args' ) )
        return 1

    except colour_filter.ColourFilterError as e:
        print( ct('<>error Error:<> %s') % (e,) )
        return 1

    except KeyboardInterrupt:
        return 0

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
    sys.exit( main() )
