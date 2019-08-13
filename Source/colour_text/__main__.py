#!/usr/bin/env python3
# coding=utf-8
import sys
import os
import colour_text

usage = '''~green Usage:~  %(progname)s ~white string~
        %(progname)s [~yellow -m~~white marker~] ~white string~ [~white arg~]...
        %(progname)s ~yellow -h~ | ~yellow --help~

%(progname)s is a command that makes printing coloured text
easier to do on Unix, macOS and Windows.

The command uses markup using ~~colour-name text~~.

    $ %(progname)s "~~info Info:~~ this is an ~~em informational~~ message"
    ~info Info:~ this is an ~em informational~ message

    $ %(progname)s "~~error Error: This is an error message~~"
    ~error Error: This is an error message~

The first argument is treated as a format string if there are more arguments.

    $ %(progname)s "~~info Info:~~ Home folder is %%s" "$HOME"
    ~info Info:~ Home folder is /home/barry

Options:

    ~yellow --help~, ~yellow -h~  This help text
    ~yellow -m~~white marker~    set the marker to the string ~white marker~
                The default marker is ~~.

Defined colour-names:
'''


def main( argv=None ):
    msg_ct = colour_text.ColourText()

    marker = '~'
    text_args = []

    if argv is None:
        argv = sys.argv

    args = iter(argv)
    progname = next(args)

    if os.path.basename( progname ) == '__main__.py':
        progname = '%s -m colour_text' % (os.path.basename( sys.executable ),)

    else:
        progname = os.path.basename( progname )

    for arg in args:
        if arg in ('-h', '--help'):
            print( msg_ct(usage) % {'progname': progname} )
            bg_colours = [name for name in colour_text if name.startswith( 'bg-' )]
            fg_colours = [name for name in colour_text if !name.startswith( 'bg-' )]

            for fg in fg_colours:
                for bg in bg_colours:
                    print( '%15s ' )
                print( msg_ct('    %15s ~bg-black;%s  Dark-mode example ~ ~%s;bg-white Light-mode example ~' % (name, name, name)) )
            return 0

        elif arg.startswith( '-m' ):
            marker = arg[len('-m'):]
            if marker == '':
                print( 'Expecting value of -m' )
                return 1

        else:
            text_args.append( arg )

    try:
        ct = colour_text.ColourText( marker=marker )
        ct.initTerminal()

        if len(text_args) == 0:
            print()

        elif len(text_args) == 1:
            print( ct( text_args[0] ) )

        else:
            fmt = ct( text_args[0] )
            args = tuple( text_args[1:] )

            print( fmt % args )

        return 0

    except colour_text.ColourTextError as e:
        print( msg_ct( '~error Error:~ %s') % e )
        return 1

    except TypeError as e:
        print( msg_ct( '~error Error:~ %s') % e )
        return 2

if __name__ == '__main__':
    sys.exit( main() )
