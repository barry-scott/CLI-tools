#!/usr/bin/env python3
# coding=utf-8
import sys
import os
import colour_text

usage = '''<>green Usage:<>  %(progname)s <>white string<>
        %(progname)s [<>yellow -m<><>white marker<>] <>white string<> [<>white arg<>]...
        %(progname)s <>yellow -h<> | <>yellow --help<>

%(progname)s is a command that makes printing coloured text
easier to do on Unix, macOS and Windows.

The command uses markup using <><>colour-name text<><>.
The default marker is <><> (tilda), which can be change using the <>yellow -m<> options.

    $ %(progname)s "<><>info Info:<><> This is an <><>em informational<><> message"
    <>info Info:<> This is an <>em informational<> message

    $ %(progname)s "<><>error Error: This is an error message<><>"
    <>error Error: This is an error message<>

The first argument is treated as a format string if there are more arguments.

    $ %(progname)s "<><>info Info:<><> Home folder is %%s" "$HOME"
    <>info Info:<> Home folder is /home/barry

The colour-name can be made up of multiple names seperated by ";".

    $ %(progname)s "<><>lightyellow;bg-blue yellow on blue background <><>"
    <>lightyellow;bg-blue  light yellow on blue background <>


Options:

    <>yellow --help<>, <>yellow -h<>  This help text
    <>yellow -m<><>white marker<>    set the marker to the string <>white marker<>
                The default marker is <><>.

Colour-names that start with "bg-" are blackground colours.
The semantic colour-names are "info", "error" and "em" (emphasis).

The builtin colour-names are:
'''


def main( argv=None ):
    msg_ct = colour_text.ColourText()
    msg_ct.initTerminal()

    marker = '<>'
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

            # Print the grid of defeined colours.

            bg_colours = [name for name in colour_text.colour_names if name.startswith( 'bg-' )]
            fg_colours = [name for name in colour_text.colour_names if not name.startswith( 'bg-' )]

            no_bg = 'no bg'
            len_no_bg = len(no_bg)
            no_fg = 'no fg'
            len_no_fg = len(no_fg)
            sample = 'Sample'
            len_sample = len(sample)

            # header with bg names
            print( '%13s %*s %s' % ('', -max( len_no_bg, len_sample ), no_bg, ' '.join( '%*s' % (-max( len_sample, len(bg) ), bg) for bg in bg_colours )) )
            # line for no fg colour
            print( msg_ct('%13s %*s %s' % (no_fg, -max( len(no_fg), len(sample) ), sample,
                    ' '.join( '<>%s %*s<>' % (bg, -max( len(bg), len(sample) ), sample) for bg in bg_colours ))) )
            # lines for each fg colout
            for fg in fg_colours:
                print( msg_ct('%13s <>%s %*s<> %s' % (fg, fg, -max( len(no_bg), len(sample) ), sample,
                        ' '.join( '<>%s;%s %*s<>' % (fg, bg, -max( len(bg), len(sample) ), sample) for bg in bg_colours ))) )

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
        print( msg_ct( '<>error Error:<> %s') % e )
        return 1

    except TypeError as e:
        print( msg_ct( '<>error Error:<> %s') % e )
        return 2

if __name__ == '__main__':
    sys.exit( main() )
