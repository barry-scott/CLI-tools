# ssh_wait module and ssh-wait command



## ssh-wait command

    Usage: ssh-wait <options> <host>

    ssh-wait will wait for the service to be available
    on <host>.

        --verbose
            - print progress messages
        --nowait
            - check once and exit 0 if can connect exit 1 if cannot
        --wait-limit=<limit>
            - exit 2 if service is not avaiable within <limit> seconds.
              defaults to 600.
        --service=<service>
            - check the service <service>. Can be a service
              name or a port number. Default is ssh.

## ssh_wait module

ssh_wait module

- `ssh_wait( host, service='ssh', wait=True, wait_limit=600, log_fn=print )`

The `ssh_wait` function waits for `host` to be available if 'wait` is True. Otherwise
it will checks once and returns.

The return code to indicate status of the host:

- 0 - success the host is accepting ssh connections
- 1 - failed to connect to host
- 2 - failed to connect within `wait_limit` seconds
- 3 - `service` is not known

The `service` argument can be either the name of the service (as listed in `/etc/services`) or the port number.

By default `log_fn` is the print function and will be used to log messages.
Pass `None` for `log_fn` to surpress all messages.
