# update-linux command

## update-linux command

Usage: update-linux <options> <group>|<host>...
    group - read from the JSON config file:
            /home/barry/.config/org.barrys-emacs.update-linux.json

        each group is a list of hosts to be updated

    host - host to be updated

    options:
        --check default Off
            check if update is required

        --debug default Off
            print debug messages

        --exclude=<host> default None
            exclude the <host> from being updated

        --force-reboot default Off
            always reboot host even if no packages where updated

        --help default Off
            print this help

        --install-package=<package> default None
            install <package> only

        --list-groups default Off
            list all groups defined in the JSON config

        --system-upgrade=<version> default None
            perform a system upgrade to version <version>
