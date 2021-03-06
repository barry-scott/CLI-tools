"""

setup.py for CLI-tools colour print

"""

import setuptools
import os.path

# Use the VERSION defined in __init__.py
import smart_find

url = 'https://github.com/barry-scott/CLI-tools'

here = os.path.abspath( os.path.dirname(__file__) )

# Get the long description from the README file
with open( os.path.join(here, 'smart_find', 'README.md'), encoding='utf-8' ) as f:
    long_description = f.read()

def getDevStatusFromVersion():
    if 'a' in smart_find.VERSION:
        return 'Development Status :: 3 - Alpha'

    elif 'b' in smart_find.VERSION:
        return 'Development Status :: 4 - Beta'

    else:
        return 'Development Status :: 5 - Production/Stable'

setuptools.setup(
    name='smart-find',

    libraries = [],

    version=smart_find.VERSION,

    description='Smart find',
    long_description=long_description,
    long_description_content_type='text/markdown',

    # The project's main homepage.
    url=url,

    # Author details
    author='Barry Scott',
    author_email='barry@barrys-emacs.org',

    # Choose your license
    license='Apache 2.0',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        getDevStatusFromVersion(),

        # Indicate who your project is intended for
        'Intended Audience :: End Users/Desktop',
        'Topic :: Utilities',

        'Environment :: Console',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: Apache Software License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],

    # What does your project relate to?
    keywords='development',

    packages=['smart_find'],
    install_requires=['config_path'],
    entry_points = {
        'console_scripts': ['smart-find=smart_find.__main__:main'],
        }
    )
