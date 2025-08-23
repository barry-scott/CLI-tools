# update-linux command

Command to automate the routine updating of packages and system upgrading for Unix systems.

update-linuk can check for updates (--check), install updates (--update) and do a system upgrade (--system-upgrade).

Supports Fedora like and Debian Like OS.

Fedora like includes Fedora, RHEL, Centos, Rocky etc that use DNF.

Debian like includes Dedian, Ubuntu etc that use apt.

update-linux uses ssh to run commands on the hosts being worked on.

It assumes that it can `ssh root@<host>` without a password prompt.

However when using the --self option to update localhost sudo will be used if not running as root. This will prompt for the sudo password as necessary.
Normally update-linux will reboot a host if that is required, but when working on --self no reboot is done unless --force-reboot is used.

If running update-linux on a macOS system it is necessary to flush DNS so that freshly booted hosts can be accessed by host-name.

This is done with the command `sudo killall -HUP mDNSResponder`.

update-linux will refuse to update the host it is running on unless the -self options is used.

Normally a reboot is done at the conclusion of an update unless update-linux can determine that the reboot is not required.

## update-linux update process

```
$ update-linux --update host
```

For an update the following steps are performed:

1. Update packages  - if there is nothing to update stop here

    Fedora: `dnf -vy update --refresh`

    Debian: `apt-get update --assume-yes` then `apt-get upgrade --assume-yes`

1. Wait until all systemd jobs have finished

    `systemctl list-jobs`

    For example akmod building nvidia drivers for a new kernel

1. Check if a reboot is needed.

    `dnf needs-restart -r`

1. Reboot the host

    `reboot`

1. Report on state of any failed services

    `systemctl --failed`

## udpate-linux check for updates

```
$ update-linux host --check
```

With the `--check` options these steps are performed:

1. Check if there are packages to update

    Fedora: `dnf check-update --refresh`

    Debian: `apt-get update --assume-yes` then `apt-get upgrade --assume-no`

1. Report on state of any failed services. Not possible upgrading localhost with --self.

    `systemctl --failed`

## update-linux system-upgrade process

```
$ update-linux --system-upgrade=38 host
```

For a system-upgrade update-linux will update one release at a time.

This means that a host running Fedora 36 that is being upgraded to Fedora 38 will first be upgraded to Fedora 37.

This is done as it is the safer then attempting skip over releases that can have required side-effects.

Run the `update-linux --system-upgrade` once for each release that is be upgraded.

For a system-upgrade these steps are used:

1. Check the current version of the Fedora installation against the requested version.

    If the host is already running the requested version stop here.

1. Download packages

    `dnf system-upgrade download --releasever=<version> --assumeyes`

1. Reboot to run the system-upgrade

    `dnf system-upgrade reboot`

1. Wait for the system to reboot

    There is a limit of 45 minutes to wait for the reboot

1. Report on state of any failed services. Not possible upgrading localhost with --self.

    `systemctl --failed`

## update-linux command

```
Usage: update-linux <options> <group>|<host>|--self...

    update-linux version 3.4.0

    Run one of the commands --check, --update, --system-upgrade
    or --install-package on a group of hosts.

    group - read from the JSON config file:
            /home/barry/.config/org.barrys-emacs.update-linux.json

        each group is a list of hosts to act on

    host - host to on

    --self - commands apply to this computer.
             By default no reboot is done.
             Use --force-reboot to reboot when required
             to complete the command.

    options:
        --check (default Off)
            check if update is required

        --debug (default Off)
            print debug messages

        --exclude=<group>|<host>[,<group>|<host>]
            exclude the <host> or host in a <group> from being updated

        --force-reboot (default Off)
            reboot if required for --update --self.
            For remote system --update always reboot host even if no packages where updated

        --help (default Off)
            print this help

        --install-package=<package>
            install <package> only

        --list-config (default Off)
            list the configuration from the JSON config file

        --list-hosts (default Off)
            list the matching hostnames

        --system-upgrade=<version>
            perform a system upgrade to version <version>

        --update (default Off)
            perform update of installed packages

        --self (default Off)
            apply command to this computer


```

## update-linux log files

All the log files are written to the configured `logdir` folder.
Each log file include the date in its name.
If update-linux is run more then once in a day the output of each run is appended the log files.

* update-summary-***date***.log

    Report the run of update-linux for all hosts.

* check-update-***host***-***date***.log

    Check update report for a ***host*** on ***date***.

* install--***host***-***date***.log

    Install package report for a ***host*** on ***date***.

* update-***host***-***date***.log

    Update report for a ***host*** on ***date***.

* status-***host***-***date***.log

    Staus report for a ***host*** on ***date***.

## Examples

Check to see of updates are available for some Fedora hosts:

```
$ update-linux --check host1 host2
```

Install updates:

```
$ update-linux host1 host2
```

Apply a system upgrade to Fedora 38:

```
$ update-linux --system-upgrade=38 host3
```

## update-linux configuration

The configuration for update-linux is stored in a JSON file.

On linux this is in ~/.config/org.barrys-emacs.update-linux.json and
on macOS this is in ~/Library/Preferences/org.barrys-emacs.update-linux.json

Example configuration:

```json
{
    "logdir":   "~/tmpdir",
    "group":
        {
            "all": [
                "router",
                "player",
                "vm"
                ],
            "vm": [
                "armf36",
                "armf37"
                ]
        }
}

```

The `logdir` is the where all the logs of the updates are written to which defaults to tempdir.

Groups are named list of hosts in the `group` dictionary.
