# CLI-tools
A collection of command line (CLI) tools

## sfind a simpler find

sfind makes it easier to access the advanced features of
find and grep. See [Source/sfind/sfind.md](Source/sfind/sfind.md) for details.

Example find all python files containing `__future__`:

    $ sfind '*.py' -c __future__

## ssh-wait will wait for host to reboot

ssh-wait is a command that waits until a server
is able to offer ssh access. See [Source/ssh-wait/ssh-wait.md](blob/master/blob/Source/ssh-wait/ssh-wait.md) for details.

    $ ssh myserver reboot
    $ ssh-wait myserver && ssh myserver

## compgen bash completion helper in python

The bash_compgen.py provides a simple and pythonic way
to write command completion logic for bash.
See [Source/compgen/compgen.md](blob/master/blob/Source/compgen/compgen.md) for details.
