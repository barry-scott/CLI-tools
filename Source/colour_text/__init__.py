#!/usr/bin/env python
# coding=utf-8

VERSION = '1.0.3'

import sys

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
    'lightmagenta': '35;1',
    'lightcyan':    '36;1',
    'white':        '37;1',


    'bg-black':     '40',
    'bg-brown':     '41',
    'bg-green':     '42',
    'bg-yellow':    '43',
    'bg-blue':      '44',
    'bg-magenta':   '45',
    'bg-cyan':      '46',
    'bg-white':     '47',
}

class ColourTextError(Exception):
    pass

class ColourText:
    def __init__( self, marker='<>' ):
        self.marker = marker
        self.named_colours = colour_names.copy()

        # define useful semantic names
        self.define( 'info', 'green' )
        self.define( 'error', 'red' )
        self.define( 'em', 'yellow' )   # Emphasized

    def initTerminal( self ):
        if sys.platform == 'win32':
            import ctypes
            kernel32 = ctypes.windll.kernel32
            # turn on the console ANSI colour handling
            kernel32.SetConsoleMode( kernel32.GetStdHandle( -11 ), 7 )

    def define( self, name, colour_def ):
        self.named_colours[ name ] = self._toSgr( colour_def )

    def _toSgr( self, colour_def ):
        if type(colour_def) == str:
            colour_def = (colour_def,)

        all_sgr = []
        for colour in colour_def:
            if colour in self.named_colours:
                all_sgr.append( self.named_colours[ colour ] )

            else:
                try:
                    colour = int(colour)

                except ValueError:
                    raise ColourTextError( 'Unknown colour %r' % (colour,) )

                all_sgr.append( '%d' % (colour,) )

        return ';'.join( all_sgr )

    def convert( self, colour_text ):
        all_parts = colour_text.split( self.marker )
        state = 'plain'
        all_converted_text = []
        if len(all_parts) == 0:
            return 0

        if (len(all_parts) % 2) != 1:
            raise ColourTextError( 'Expecting pairs of the marker %r in %r' % (self.marker, colour_text ) )

        for part in all_parts:
            if state == 'plain':
                all_converted_text.append( part )
                state = 'colour'

            elif state == 'colour':
                # insert the marker? e.g. "this is the marker ~~ text"
                if len(part) == 0:
                    all_converted_text.append( self.marker )

                else:
                    # a colour region "colour this ~name text~ here"
                    name_text = part.split( ' ', 1 )
                    if len(name_text) != 2:
                        raise ColourTextError( 'Expecting colour name and text in %r' % (part,) )

                    name, text = name_text

                    sgr = self._toSgr( name.split(';') )
                    all_converted_text.append( '\x1b[%sm%s\x1b[m' % (sgr, text) )

                state = 'plain'

            else:
                assert False, 'How did this happen?'

        return ''.join( all_converted_text )


    def __call__( self, colour_text ):
        return self.convert( colour_text )


def main( argv ):
    ct = ColourText()
    ct.define( 'I', 'info' )
    ct.define( 'E', 'error' )
    ct.initTerminal()

    print( ct( 'This is <>info INFO<> and this is <>error ERROR<> text' ) )
    print( ct( 'This is <>I info<> and this is <>E error<> text' ) )

    ct = ColourText( '‡' )
    print( ct( 'Hello ‡yellow World‡ use "‡‡" as the marker.' ) )


    ct = ColourText('*')
    print( ct( 'Hello *magenta World* use "**" as the marker.' ) )
    return 0

if __name__ == '__main__':
    sys.exit( main( sys.argv ) )
