#!/usr/bin/env python3
import sys
import cprint

def main( argv=None ):
    if argv is None:
        argv = sys.argv

    try:
        ct = cprint.ColourText()
        ct.initTerminal()
        if len(argv) == 1:
            print()

        elif len(argv) == 2:
            print( ct( argv[1] ) )

        else:
            fmt = ct( argv[1] )
            args = tuple( argv[2:] )

            print( fmt % args )

        return 0

    except cprint.ColourTextError as e:
        print( e )
        return 1

    except TypeError as e:
        print( e )
        return 2

if __name__ == '__main__':
    sys.exit( main() )
