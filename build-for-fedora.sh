#!/bin/bash
set -e

function usage() {
    cat <<EOF
$0 copr-release|copr-testing <pypi-package>|--all [<fedora-version>]
EOF

}

function copr_build() {
    PACKAGE_NAME=${1:?package name}
    for ARCH in x86_64 aarch64
    do
        colour-print "<>info Info:<> bulding <>em ${PACKAGE_NAME}<> for <>em ${RPM_ROOT}-${ARCH}<>"
        copr-cli buildpypi --chroot=${RPM_ROOT}-${ARCH} --packagename=${PACKAGE_NAME} --pythonversions=3 ${COPR_REPO}
    done
}

case "$1" in
copr-release)
    COPR_REPO=tools
    ;;

copr-testing)
    COPR_REPO=tools-testing
    ;;

*)
    usage
    exit 1
    ;;
esac

case "$3" in
[0-9][0-9])
    RPM_ROOT=fedora-${3}
    ;;
"")
    . /etc/os-release
    RPM_ROOT=fedora-${VERSION_ID}
    ;;
*)
    usage
    exit 1
    ;;
esac

# use user's arch for rpm

case "$2" in
--all)
    copr_build colour-text
    copr_build colour-filter
    copr_build ssh-wait
    copr_build update-linux
    ;;

[a-z]*)
    copr_build "${2}"
    ;;

*)
    usage
    exit 1
    ;;
esac
