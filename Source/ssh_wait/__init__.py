import time
import socket

VERSION='1.0.0'

def ssh_wait( host, service='ssh', wait=True, wait_limit=600, log_fn=print ):
    try:
        # assume numeric service
        port = int(service)

    except ValueError:
        try:
            port = socket.getservbyname( service )
        except socket.error as e:
            log_fn( 'Cannot convert service %s: %s' % (service, e) )
            return 2

    wait_limit = wait_limit + time.time()

    last_error = 'unknown'

    if log_fn is not None: log_fn( 'Connecting to %s:%s ...' % (host, service) )
    while time.time() < wait_limit:
        try:
            s = socket.create_connection( (host, service), 0.1 )
            if log_fn is not None: log_fn( 'Connected to %s:%s' % (host, service) )
            return 0

        except (socket.error, socket.timeout, socket.gaierror) as e:
            last_error = str(e)
            if not wait:
                if log_fn is not None: log_fn( 'Failed to connect: %s' % (last_error,) )
                return 1

            time.sleep( 0.1 )

    if log_fn is not None: log_fn( 'Wait limit reached: %s' % (last_error,) )
    return 1
