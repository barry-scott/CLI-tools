from __future__ import print_function

import sys
import ssh_wait

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

def main( argv=None ):
    if argv is None:
        argv = sys.argv

    host = None
    service = 'ssh'
    wait_limit = 600
    opt_wait = True
    opt_verbose = False

    if len(argv) == 1:
        usage()
        return 1

    for arg in argv[1:]:
        if arg.startswith( '--' ):
            if arg == '--help':
                usage()
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

    if opt_verbose:
        log_fn = print
    else:
        log_fn = None

    return ssh_wait.ssh_wait( host, service=service,
                     wait=opt_wait, wait_limit=wait_limit,
                     log_fn=log_fn )

if __name__ == '__main__':
    sys.exit( main() )
