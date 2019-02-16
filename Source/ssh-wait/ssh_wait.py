#!/usr/bin/env python
from __future__ import print_function

import sys
import time
import socket

def usage():
    print( '''Usage: ssh-wait <options> <host>

ssh-wait will wait for the service to be available
on <host>.

    --verbose
        - print progress messages
    --nowait
        - check one and exit 0 if can connect 1 if cannot
    --wait-limit=<limit>
        - exit 1 if service is not avaiable within <limit> seconds.
          defaults to 600.
    --service=<service>
        - check the service <service>. Can be a service
          name of a port number. Default is ssh.
''' )

def main( argv ):
    host = None
    service = 'ssh'
    wait_limit = 600
    opt_wait = True
    opt_verbose = False

    for arg in argv[1:]:
        if arg.startswith( '--' ):
            if arg == '--help':
                ussage()
                return 0

            if arg == '--nowait':
                opt_wait = False

            elif arg.startswith( '--wait-limit=' ):
                try:
                    wait_limit = int( arg[len('--wait-limit='):] )
                except ValueError:
                    print( 'Bad value for %s' % (arg,) )
                    return 2

            elif arg == '--verbose':
                opt_verbose = True

            elif arg.startswith( '--service=' ):
                service = arg[len('--service='):]

            else:
                print( 'Unknown option %r' % (arg,) )
                return 2

        elif  host is None:
            host = arg

        else:
            print( 'Unnecessary arg %r' % (arg,) )
            return 2

    try:
        # assume numeric service
        port = int(service)

    except ValueError:
        try:
            port = socket.getservbyname( service )
        except socket.error as e:
            print( 'Cannot convert service %s: %s' % (service, e) )
            return 2

    wait_limit = wait_limit + time.time()

    last_error = 'unknown'

    if opt_verbose: print( 'Connecting to %s:%s ...' % (host, service) )
    while time.time() < wait_limit:
        try:
            s = socket.create_connection( (host, service), 0.1 )
            if opt_verbose: print( 'Connected to %s:%s' % (host, service) )
            return 0

        except (socket.error, socket.timeout, socket.gaierror) as e:
            last_error = str(e)
            if not opt_wait:
                if opt_verbose: print( 'Failed to connect: %s' % (last_error,) )
                return 1

            time.sleep( 0.1 )

    if opt_verbose: print( 'Wait limit reached: %s' % (last_error,) )
    return 1

if __name__ == '__main__':
    sys.exit( main( sys.argv ) )
