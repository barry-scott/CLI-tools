#!/usr/bin/env python
VERSION = '1.0.0'

import sys

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
}

class ColourTextError(Exception):
    pass

class ColourText:
    def __init__( self, marker='~' ):
        self.marker = marker
        self.named_colours = colour_names.copy()

        # define 
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
                    name_text = part.split( None, 1 )
                    if len(name_text) != 2:
                        raise ColourTextError( 'Expecting colour name and text in %r' % (part,) )

                    name, text = name_text
                    if name not in self.named_colours:
                        raise ColourTextError( 'Colour name %r has not been defined. Used in %r' % (name, colour_text) )

                    sgr = self.named_colours[ name ]
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

    print( ct( 'This is ~info INFO~ and this is ~error ERROR~ text' ) )
    print( ct( 'This is ~I info~ and this is ~E error~ text' ) )

    ct = ColourText( '‡' )
    print( ct( 'Hello ‡yellow World‡ use "‡‡" as the marker.' ) )


    ct = ColourText( '*' )
    print( ct( 'Hello *magenta World* use "**" as the marker.' ) )
    return 0

if __name__ == '__main__':
    sys.exit( main( sys.argv ) )
