#!/usr/bin/env python
# coding: utf-8
from __future__ import print_function

import sys
import os
import colour_filter
import colour_text
import json
from config_path import ConfigPath

def usage( ct, cfg_filename ):
    print( ct('''Usage: colour-filter <options> [<>em pattern<> <>em colour<>]*

Read lines from stdin and print them colour based on the <>em pattern<> <>em colour<> pairs.

The <>em pattern<> <>em colour<> pairs can be supplied on the command line or taken from a
pre-defined scheme.

Scheme definitions are stored in %s.

Options:
    -s, --scheme <>em scheme<> - Filter using filter scheme <>em scheme<>
    -a, --add                  - Add a filter <>em scheme<> with the
                                 <>em pattern<> <>em colour<> pairs.
                                 If the scheme always exists replace its
                                 definition.
    -d, --delete               - Delete the <>em scheme<>
    -l,--list-schemes          - List all the schemes that have been
                                 defined.
''') % (cfg_filename,) )

def main():
    args = iter( sys.argv )
    prog_name = next( args )

    opt_cmd = None
    opt_scheme = None

    all_filters = []

    ct = colour_text.ColourText()
    cf = colour_filter.ColourFilter()

    ct.initTerminal()

    cfg_path = ConfigPath( 'colour-filter', 'barrys-emacs.org', '.json' )

    try:
        while True:
            arg = next( args, None )
            if arg is None:
                break

            if arg.startswith( '-' ):
                if arg == '--debug':
                    cf.enableDebug()

                elif arg in ('-h', '--help'):
                    usage( ct, cfg_path.saveFilePath() )
                    return 0

                elif arg in ('-s', '--scheme'):
                    opt_scheme = next(args)

                elif arg in ('-a', '--add'):
                    opt_cmd = 'add'

                elif arg in ('-d', '--delete'):
                    opt_cmd = 'delete'

                elif arg in ('-l', '--list-schemes'):
                    opt_cmd = 'list'

                elif arg in ('-sa', '-as'):
                    opt_cmd = 'add'
                    opt_scheme = next(args)

                elif arg in ('-ds', '-sd'):
                    opt_cmd = 'delete'
                    opt_scheme = next(args)

                else:
                    print( ct('<>error Error:<> Unknown options "%s"') % (arg,) )
                    return 1

            else:
                pattern = arg
                colour = next( args )
                all_filters.append( (pattern, colour) )
                cf.define( pattern, colour )

        if opt_cmd == 'add':
            if opt_scheme is None:
                print( ct('<>error Error:<> --add requires a --scheme') )
                return 1

            if len(all_filters) == 0:
                print( ct('<>error Error:<> --add atleast one pattern/colour pair') )
                return 1

        if opt_cmd == 'delete' and opt_scheme is None:
            print( ct('<>error Error:<> --delete requires a --scheme') )
            return 1

        config = {}

        # load the config
        config_file = cfg_path.readFilePath()
        if config_file is not None:
            with open( config_file, 'r' ) as f:
                config = json.load( f )

        if opt_cmd == 'list':
            if len(config) == 0:
                print( 'No schemes are defined' )
                return 0

            for scheme in config:
                print( ct('Scheme <>info %s<>') % (scheme,) )
                for pattern, colour in config[scheme]:
                    print( ct('    %%r - <>%s %%s<>' % (colour,)) % (pattern, colour) )

            return 0

        if opt_cmd == 'add':
            config[opt_scheme] = all_filters

            config_file = cfg_path.saveFilePath()
            with open( config_file, 'w' ) as f:
                json.dump( config, f )

            print( ct('Added scheme <>em %s<> with %d definitions') % (opt_scheme, len(config[opt_scheme])) )
            return 0

        if opt_cmd == 'delete':
            if opt_scheme in config:
                del config[opt_scheme]

            config_file = cfg_path.saveFilePath()
            with open( config_file, 'w' ) as f:
                json.dump( config, f )

            print( ct('Deleted scheme <>em %s<>') % (opt_scheme,) )
            return 0

        if opt_scheme is None and len(config) >= 1:
            # default to the first scheme
            opt_scheme = sorted( config.keys() )[0]

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

if __name__ == '__main__':
    sys.exit( main() )
