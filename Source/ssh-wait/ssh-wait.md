# ssh-wait

## Usage

    Usage: ssh-wait <options> <host>

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
