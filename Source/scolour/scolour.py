#!/usr/bin/env python
# coding: utf-8
from __future__ import print_function
import sys
import os
import re

class SmartColourError(Exception):
    pass

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

colour_names = {
    'bold':         '1',

    'black':        '30',
    'brown':        '31',
    'green':        '32',
    'yellow':       '33',
    'blue':         '34',
    'magenta':      '35',
    'cyan':         '36',
    'gray':         '37',

    'red':          '31;1',
    'lightred':     '31;1',
    'lightgreen':   '32;1',
    'lightyellow':  '33;1',
    'lightblue':    '34;1',
    'lightmagenta,':'35;1',
    'lightcyan':    '36;1',
    'white':        '37;1',


    'bg-black':     '40',
    'bg-brown':     '41',
    'bg-green':     '42',
    'bg-yellow':    '43',
    'bg-blue':      '44',
    'bg-magenta':   '45',
    'bg-cyan':      '46',
    'bg-gray':      '47',
    'bg-white':     '47',
    '0':            '0',
    '1':            '1',
    '30':           '30',
    '31':           '31',
    '32':           '32',
    '33':           '33',
    '34':           '34',
    '35':           '35',
    '36':           '36',
    '37':           '37',
    '40':           '40',
    '41':           '41',
    '42':           '42',
    '43':           '43',
    '44':           '44',
    '45':           '45',
    '46':           '46',
    '47':           '47',
}

class SmartColour:
    '''
    scolour - colour input lines parts
    '''
    def __init__( self, argv ):
        self.argv = argv
        self.opt_debug = False
        self.opt_line_buffered = True

        self.all_patterns = []

    def execute( self ):
        try:
            self.parseArgs()
            self.executeCommand()
            return 0

        except SmartColourError as e:
            print( 'Error: %s' % (e,) )
            return 1

        except KeyboardInterrupt:
            return 0

    def executeCommand( self ):
        while True:
            line = sys.stdin.readline()
            if line == '':
                break

            for pattern, colour in self.all_patterns:
                line_parts = []

                while len(line) > 0:
                    match = pattern.search( line )
                    if match is None:
                        break

                    line_parts.append( line[0:match.start(0)] )
                    line_parts.append( '\033[%sm%s\033[m' %
                                        (colour
                                        ,line[match.start(0):match.end(0)]) )
                    line = line[match.end(0):]

                line_parts.append( line )
                line = ''.join( line_parts )

            sys.stdout.write( line )
            if self.opt_line_buffered:
                sys.stdout.flush()

    def parseArgs( self ):
        args = iter( self.argv )
        prog_name = next( args )

        try:
            while True:
                arg = next( args, None )
                if arg is None:
                    break

                if arg.startswith( '-' ):
                    if '-debug' == arg:
                        self.opt_debug = True

                    else:
                        raise SmartColourError( 'Unknown options "%s:"' % (arg,) )

                else:
                    pattern = re.compile( arg )
                    colour = next( args )
                    # TBD validate colour
                    # allow : instead of ';' for command ease
                    all_colour_parts = colour.replace( ':', ';' ).split(';')
                    # replace all the colour names with with the escape codes
                    all_colour_parts = [colour_names.get(colour, '0') for colour in all_colour_parts]

                    self.all_patterns.append( (pattern, ';'.join(all_colour_parts)) )

        except StopIteration:
            raise SmartColourError( 'Need more args' )

    def debug( self, msg ):
        if self.opt_debug:
            print( 'Debug: %s' % (msg,) )
            sys.stdout.flush()

if __name__ == '__main__':
    sys.exit( SmartColour( sys.argv ).execute() )
