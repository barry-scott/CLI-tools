#!/usr/bin/python3
import sys
import glob
from colour_text import ColourText
from fedora_distro_aliases import get_distro_aliases

class AppError(Exception):
    pass

class App:
    CMDS = ('copr-release', 'copr-testing')
    ARCHS = ('x86_64', 'aarch64')

    def __init__(self):
        self.progname = None
        self.opt_build_cmd = None
        self.opt_package = None
        self.opt_fedora_rel = 'latest'
        self.opt_arch = 'all'
        self.build_for_releases = None
        self.build_for_archs = None
        self.build_packages = None

    def info(self, msg):
        print(self.ct('<>info Info:<> %s') % (msg,))

    def error(self, msg):
        print(self.ct('<>error Error: %s<>') % (msg,))

    def usage(self, error=None):
        print(f'''{self.progname} {'|'.join(self.CMDS)} [--all|<package-name>] [<fedora-release>|stable|latest|all|rawhide] all|{'|'.join(self.ARCHS)}
''')
        if self.error is not None:
            self.error(error)

    def main(self, argv):
        self.ct = ColourText()
        self.ct.initTerminal()

        try:
            self.parseCommandLine(argv)

            self.distro_info = get_distro_aliases()

            self.expandPackages()
            self.expandReleases()
            self.expandArchs()

            print('Build packages:', self.build_packages)
            print('Build for fedora releases:', self.build_for_releases)
            print('Build for arch:', self.build_for_archs)

            self.coprBuilds()

        except AppError as e:
            self.usage(e)

        return 0

    def parseCommandLine(self, argv):
        try:
            args = iter(argv)
            self.progname = next(args)
            self.opt_build_cmd = next(args)
            self.opt_package = next(args).replace('_', '-').strip('/')
            self.opt_fedora_rel = next(args)
            self.opt_arch = next(args)

        except StopIteration:
            pass

        if self.opt_build_cmd not in self.CMDS:
            raise AppError(f'Unknown command {self.opt_build_cmd}')

    def expandReleases(self):
        all_releases = {}
        for meta_name in ('all', 'latest', 'stable'):
            all_releases[meta_name] = [rel.version for rel in self.distro_info[f'fedora-{meta_name}']]

        for release in self.distro_info['fedora-all']:
            all_releases[release.version] = [release.version]

        self.build_for_releases = []
        if self.opt_fedora_rel not in all_releases:
            raise AppError(f'Unknown fedora release {self.opt_fedora_rel}')
        self.build_for_releases.extend(all_releases[self.opt_fedora_rel])

    def expandArchs(self):
        if self.opt_arch == 'all':
            self.build_for_archs = self.ARCHS

        elif self.opt_arch in self.ARCHS:
            self.build_for_archs = (self.opt_arch,)

        else:
            raise AppError(f'Unknown arch {self.opt_arch}')

    def expandPackages(self):
        # find all packages
        all_packages = [project_file.split('/')[0].replace('_', '-') for project_file in glob.glob('*/pyproject.toml')]
        if self.opt_package == '--all':
            self.build_packages = all_packages

        elif self.opt_package in all_packages:
            self.build_packages = [self.opt_package]

        else:
            raise AppError(f'Unknown package {self.opt_package}')

    def coprBuilds(self):
        if self.opt_build_cmd == 'copr-release':
            copr_repo = 'tools'

        elif self.opt_build_cmd == 'copr-testing':
            copr_repo = 'tools-testing'

        else:
            raise AppError(f'Unknown build command {self.opt_build_cmd}')

        for package in self.build_packages:
            for release in self.build_for_releases:
                for arch in self.build_for_archs:
                    rpm_root = f'fedora-{release}-{arch}'
                    self.info(self.ct(f'<>info Info:<> bulding <>em {package}<> for <>em {rpm_root}<> into repo {copr_repo}'))
                    cmd = ['copr-cli',
                            'buildpypi',
                            f'--chroot={rpm_root}',
                            f'--packagename={package}',
                            '--pythonversions=3',
                            copr_repo]
                    #self.info(cmd)


if __name__ == '__main__':
    sys.exit(App().main(sys.argv))
