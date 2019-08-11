# CLI-tools

A collection of command line (CLI) tools

## colour_text and colour-print

colour-print is a command that makes printing coloured text
easy to do on Unix, macOS and Windows.

See [Source/colour_text/README.md](Source/colour_text/README.md) for details.

For example:

    $ colour-print "~info Info:~ Home folder is %s" "$HOME"

From python use the ColourText class to implement the same features.

    from colour_text import ColourText

    ct = ColourText()
    ct.initTerminal()

    print( ct('~red Some red text~ and some ~green Green text~') )

## colour-filter colour parts of lines

colour-filter reads lines from its input, colours part of the line and prints the result on its output.

For example colour the output of a build script. Colour Info: in green
and all of the line that starts Error: in red.

   $ ./build.sh 2>&1 | colour-filter '^Info:' green 'Error:.*' red

## smart_find a smarter, simpler, find

smart-find makes it easier to access the advanced features of
find and grep. See [Source/smart-find/README.md](Source/smart-find/README.md) for details.

Example find all python files containing `__future__`:

    $ smart-find '*.py' -c __future__

## ssh-wait will wait for a host to reboot

ssh-wait is a command that waits until a server
is able to offer ssh access. See [Source/ssh_wait/README.md](Source/ssh_wait/README.md) for details.

    $ ssh myserver reboot
    $ ssh-wait myserver && ssh myserver

## compgen bash completion helper in python

The bash_compgen.py provides a simple and pythonic way
to write command completion logic for bash.
See [Source/compgen/compgen.md](Source/compgen/compgen.md) for details.
