#!/usr/bin/env python
# coding: utf-8
from __future__ import print_function

import sys
import colour_filter
import colour_text


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

def main():
    args = iter( sys.argv )
    prog_name = next( args )

    ct = colour_text.ColourText()
    cf = colour_filter.ColourFilter()

    ct.initTerminal()

    try:
        while True:
            arg = next( args, None )
            if arg is None:
                break

            if arg.startswith( '-' ):
                if '-debug' == arg:
                    cf.enableDebug()

                else:
                    print( ct('~error Error:~ Unknown options "%s"') % (arg,) )

            else:
                pattern = arg
                colour = next( args )
                cf.define( pattern, colour )

        cf.filterLines( sys.stdin, sys.stdout, line_buffered=True )
        return 0

    except StopIteration:
        print( ct('~error Error:~ Need more args' ) )
        return 1

    except colour_filter.ColourFilterError as e:
        print( ct('~error Error:~ %s') % (e,) )
        return 1

    except KeyboardInterrupt:
        return 0

if __name__ == '__main__':
    sys.exit( main() )
