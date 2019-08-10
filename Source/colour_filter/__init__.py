from __future__ import print_function

import sys
import os
import re

VERSION = '1.0.0'

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

class ColourFilterError(Exception):
    pass

class ColourFilter:
    '''
    ColourFilter - colour parts of input lines matching regex patterns
    '''
    def __init__( self ):
        self.opt_debug = False

        self.all_patterns = []

    def enableDebug( self, enable=True ):
        self.opt_debug = enable

    def define( self, pattern, colour ):
        pattern = re.compile( pattern )

        # TBD validate colour
        # allow : instead of ';' for command ease
        all_colour_parts = colour.replace( ':', ';' ).split(';')

        # replace all the colour names with with the escape codes
        all_colour_parts = [colour_names.get(colour, '0') for colour in all_colour_parts]

        self.all_patterns.append( (pattern, ';'.join(all_colour_parts)) )


    def filterLines( self, input_file, output_file, line_buffered ):
        while True:
            line = input_file.readline()
            if line == '':
                break

            # list of tuples of (coloured, text)
            # only colour in text that is not already coloured
            line_parts = [(False, line)]

            for pattern, colour in self.all_patterns:
                index = 0

                while index < len(line_parts):
                    coloured, text = line_parts[index]

                    if coloured:
                        index += 1
                        continue

                    match = pattern.search( text )
                    # no match or match is zero width for patterns like [0-9]*
                    if match is None or match.start(0) == match.end(0):
                        index += 1
                        continue

                    pre = text[0:match.start(0)]
                    middle = text[match.start(0):match.end(0)]
                    post = text[match.end(0):]

                    if len(pre) > 0:
                        line_parts.insert( index, (False, pre) )
                        index += 1

                    line_parts[index] = (True, '\033[%sm%s\033[m' % (colour, middle))
                    index += 1

                    if len(post) > 0:
                        line_parts.insert( index, (False, post) )

            output_file.write( ''.join( [text for coloured, text in line_parts] ) )
            if line_buffered:
                output_file.flush()

    def debug( self, msg ):
        if self.opt_debug:
            print( 'Debug: %s' % (msg,) )
            sys.stdout.flush()
