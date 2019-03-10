#!/bin/python2
from __future__ import print_function

import sys
import os
import types
import fnmatch


def main( argv ):
    log = open( './qqq.log', 'w', 1 )
    for name in os.environ:
        if name.startswith('COMP'):
            print( '%s: %r' % (name, os.environ[name]), file=log )

    line = os.environ['COMP_LINE']
    point = int(os.environ['COMP_POINT'])

    print( '%r:%r' % (line[0:point], line[point:]), file=log )

    tokens = BashLineParser( line[0:point] ).tokens()
    print( 'tokens: %r' % (tokens,), file=log )
    if len(tokens) <= 1:
        return

    tree = CompCommand( {
        'first': CompSequence( ExpChoice( 'able', 'baker', 'charley' ) ),
        'second': CompSequence( ExpChoice( 'fred', 'joe', 'zoo' ), ExpSshHost() ),
        'forth': CompRepeat( ExpAnyOf( ExpChoice( '--a', '--r', '--x' ), ExpFilename( exclude=('*~', '*.py[co]') ) ) ),
        'file': CompRepeat( ExpFilename() ),
        } )

    # walk the already completed tokens
    comp = tree
    for token in tokens[1:-1]:
        comp = comp.next( token )
        print( 'DBG: T: %r comp: %s' % (token, comp.__class__.__name__), file=log )
        if comp is None:
            return

    for expansion in comp.expand( tokens[-1] ):
        print( 'DBG: Result: %r' % (expansion,), file=log )
        print( expansion )

    return 0

class CompCommand(object):
    def __init__( self, cmds ):
        assert type(cmds) == types.DictType
        self.cmds = cmds

    def next( self, token ):
        return self.cmds.get( token.value() )

    def expand( self, token ):
        return [c for c in self.cmds if c.startswith( token.value() )]

class CompRepeat(object):
    def __init__( self, comp ):
        self.comp = comp

    def next( self, token ):
        return self

    def expand( self, token ):
        return self.comp.expand( token )

class CompSequence(object):
    def __init__( self, *comps ):
        self.comps = comps

    def next( self, token ):
        # if the last part of the squence is another Comp return it.
        if len(self.comps) == 2 and hasattr( self.comps[1], 'next' ):
            return self.comps[1]

        if len(self.comps) == 1:
            return None

        return CompSequence( *self.comps[1:] )

    def expand( self, token ):
        return self.comps[0].expand( token )

class ExpAnyOf(object):
    def __init__( self, *comps ):
        self.comps = comps

    def expand( self, token ):
        expansions = []
        for comp in self.comps:
            expansions.extend( comp.expand( token ) )

        return expansions

class ExpChoice(object):
    def __init__( self, *choices ):
        self.choices = choices

    def expand( self, token ):
        return [c for c in self.choices if c.startswith( token.value() )]


class ExpFilename(object):
    def __init__( self, exclude=None ):
        if exclude is None:
            self.excludes = []

        elif type(exclude) in (types.TupleType, types.ListType):
            self.excludes = exclude

        elif type(exclude) == types.StringType:
            self.excludes = [exclude]

        else:
            assert False, 'Unsupported exclude type %r' % (exclude,)

    def expand( self, token ):
        if os.path.isdir( token.value() ):
            folder = token.value()
            name = ''
            prefix = token.value()
            if not prefix.endswith( '/' ):
                prefix = prefix + '/'

        else:
            folder = os.path.dirname( token.value() )
            name = os.path.basename( token.value() )

            if folder == '':
                prefix = ''
                folder = '.'
            else:
                prefix = folder + '/'

        result = []
        try:
            all_files = [f for f in os.listdir( folder ) if f.startswith( name )]

        except OSError:
            # the folder does not exist - return nothing meaning cannot expand
            return []

        for exclude in self.excludes:
            all_files = [f for f in all_files if not fnmatch.fnmatch( f, exclude )]

        for f in all_files:
            f = prefix + f

            if os.path.isdir( f ):
                f = f + '/'

            result.append( f )

        # result folder/ and folder to prevent bash
        # from adding a space and moving to the next token
        if len(result) == 1 and os.path.isdir( result[0] ):
            result.append( result[0][:-1] )

        if token.quote() == '"':
            ch_needs_quote = ('"', '\\')

        elif token.quote() == "'":
            ch_needs_quote = ('\\', "'")

        else: # Token Simple 
            ch_needs_quote = (' ', '"', '\\', "'")

        quoted_result = []
        for unquoted_f in result:
            f = []
            for ch in unquoted_f:
                if ch in ch_needs_quote:
                    f.append( '\\' )
                f.append( ch )

            quoted_result.append( ''.join( f ) )

        return quoted_result

class ExpSshHost(object):
    def __init__( self ):
        pass

    def expand( self, token ):
        if '@' in token.value():
            user, partial_host = token.value().split( '@', 1 )
            prefix = user + '@'

        else:
            prefix = ''
            partial_host = token.value()

        all_hosts = []
        try:
            with open( os.path.expanduser( '~/.ssh/config' ), 'r' ) as f:
                for line in f:
                    if line.startswith( 'Host' ):
                        hosts = line.split()[1:]
                        for host in hosts:
                            if '*' not in host and host.startswith( partial_host ):
                                all_hosts.append( prefix + host )

        except IOError:
           pass

        return all_hosts

class StringBuffer(object):
    def __init__( self, data ):
        self.data = data
        self.position = 0

    def __repr__( self ):
        return '<StringBuffer: %r|%r>' % (self.data[:self.position], self.data[self.position:])

    def consumeChar( self ):
        self.position += 1

    def peekChar( self ):
        return self.data[self.position:self.position+1]

#
#   BaseLineParser can parse partial command lines
#   missing closing quotes do not matter for completion code
#
class BashLineParser(object):
    def __init__( self, line ):
        self.all_tokens = []
        self.cur_token = []

        self.line = StringBuffer( line )

        self.parseLine()

    def parseLine( self ):
        state = self.stateSkipSpaces

        while state != self.stateEndOfLine:
            #print( 'DBG: L: %r A: %r C: %r S: %r' % (self.line, self.all_tokens, self.cur_token, state.__name__) )
            state = state()

    def tokens( self ):
        return self.all_tokens

    def addCurToken( self, cls ):
        self.all_tokens.append( cls( ''.join( self.cur_token ) ) )
        self.cur_token = []

    def stateEndOfLine( self ):
        raise RuntimeError( 'No one should call stateEndOfLine!' )

    def stateSkipSpaces( self ):
        consumed = False
        while self.line.peekChar() == ' ':
            consumed = True
            self.line.consumeChar()

        ch = self.line.peekChar()
        if ch == "'":
            self.line.consumeChar()
            return self.stateSingleQuoteToken

        if ch == '"':
            self.line.consumeChar()
            return self.stateDoubleQuoteToken

        if ch == '\\':
            self.line.consumeChar()
            return self.stateSimpleToken

        if ch != '':
            return self.stateSimpleToken

        if consumed:
            # add an empty token
            self.addCurToken( TokenSimple )

        return self.stateEndOfLine

    def stateSimpleToken( self ):
        while True:
            ch = self.line.peekChar()
            if ch in ('', ' '):
                # end of token
                self.addCurToken( TokenSimple )
                return self.stateSkipSpaces

            if ch == '\\':
                self.line.consumeChar()
                ch = self.line.peekChar()

            self.line.consumeChar()
            self.cur_token.append( ch )

    def stateSingleQuoteToken( self ):
        while True:
            ch = self.line.peekChar()
            if ch == '':
                # end of token
                self.addCurToken( TokenSingleQuote )
                return self.stateSkipSpaces

            if ch == "'":
                self.line.consumeChar()
                self.addCurToken( TokenSingleQuote )
                return self.stateSkipSpaces

            if ch == '\\':
                self.line.consumeChar()
                ch = self.line.peekChar()

            self.line.consumeChar()
            self.cur_token.append( ch )

    def stateDoubleQuoteToken( self ):
        while True:
            ch = self.line.peekChar()
            if ch == '':
                # end of token
                self.addCurToken( TokenDoubleQuote )
                return self.stateSkipSpaces

            if ch == '"':
                self.line.consumeChar()
                self.addCurToken( TokenDoubleQuote )
                return self.stateSkipSpaces

            if ch == '\\':
                self.line.consumeChar()
                ch = self.line.peekChar()

            self.line.consumeChar()
            self.cur_token.append( ch )


class TokenSimple(object):
    def __init__( self, value ):
        self._value = value

    def __repr__( self ):
        return '<TokenSimple: %r>' % (self._value,)

    def quote( self ):
        return ''

    def value( self ):
        return self._value


class TokenSingleQuote(object):
    def __init__( self, value ):
        self._value = value

    def __repr__( self ):
        return '<TokenSingleQuote: %r>' % (self._value,)

    def quote( self ):
        return "'"

    def value( self ):
        return self._value


class TokenDoubleQuote(object):
    def __init__( self, value ):
        self._value = value

    def __repr__( self ):
        return '<TokenDoubleQuote: %r>' % (self._value,)

    def quote( self ):
        return '"'

    def value( self ):
        return self._value

if __name__ == '__main__':
    sys.exit( main( sys.argv ) )
