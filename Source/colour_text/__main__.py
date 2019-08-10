#!/usr/bin/env python3
import sys
import colour_text

def main( argv=None ):
    err_ct = colour_text.ColourText()

    if argv is None:
        argv = sys.argv

    try:
        ct = colour_text.ColourText()
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

    except colour_text.ColourTextError as e:
        print( err_ct( '~error Error:~ %s') % e )
        return 1

    except TypeError as e:
        print( err_ct( '~error Error:~ %s') % e )
        return 2

if __name__ == '__main__':
    sys.exit( main() )
