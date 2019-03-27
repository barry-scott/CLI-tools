#!/usr/bin/env python
# coding: utf-8
from __future__ import print_function
import sys
import os
import re

class SmartColourError(Exception):
    pass

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

    def executeCommand( self ):
        while True:
            line = sys.stdin.readline()

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
                    # validate colour
                    self.all_patterns.append( (pattern, colour) )

        except StopIteration:
            raise SmartColourError( 'Need more args' )

    def debug( self, msg ):
        if self.opt_debug:
            print( 'Debug: %s' % (msg,) )
            sys.stdout.flush()

if __name__ == '__main__':
    sys.exit( SmartColour( sys.argv ).execute() )
