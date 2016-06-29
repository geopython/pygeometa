# =================================================================
#
# Terms and Conditions of Use
#
# Unless otherwise noted, computer program source code of this
# distribution # is covered under Crown Copyright, Government of
# Canada, and is distributed under the MIT License.
#
# The Canada wordmark and related graphics associated with this
# distribution are protected under trademark law and copyright law.
# No permission is granted to use them outside the parameters of
# the Government of Canada's corporate identity program. For
# more information, see
# http://www.tbs-sct.gc.ca/fip-pcim/index-eng.asp
#
# Copyright title to all 3rd party software distributed with this
# software is held by the respective copyright holders as noted in
# those files. Users are asked to read the 3rd Party Licenses
# referenced with those assets.
#
# Copyright (c) 2016 Government of Canada
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# =================================================================

from setuptools import setup, Command
import os
import sys
import re
import codecs

# set dependencies
with open('requirements.txt') as f:
    INSTALL_REQUIRES = f.read().splitlines()

KEYWORDS = [
    'geospatial',
    'metadata',
    'catalogue',
    'discovery'
]

DESCRIPTION = '''
pygeometa is a Python package to generate metadata for geospatial datasets
'''

try:
    import pypandoc
    LONG_DESCRIPTION = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    with open('README.md') as f:
        LONG_DESCRIPTION = f.read()

CONTACT = 'Meteorological Service of Canada, Environment Canada'

EMAIL = 'tom.kralidis@canada.ca'

URL = 'https://github.com/geopython/pygeometa'

if os.path.isfile('MANIFEST'):
    os.unlink('MANIFEST')


class PyTest(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import subprocess
        errno = subprocess.call([sys.executable, 'tests/run_tests.py'])
        raise SystemExit(errno)


# from https://github.com/pypa/pip/blob/f4694100e/setup.py#L28
def read(*parts):
    # from https://github.com/pypa/pip/blob/f4694100e/setup.py#L10
    here = os.path.abspath(os.path.dirname(__file__))
    # intentionally *not* adding an encoding option to open, See:
    #   https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    return codecs.open(os.path.join(here, *parts), 'r').read()


# from https://github.com/pypa/pip/blob/f4694100e/setup.py#L34
def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


# from https://wiki.python.org/moin/Distutils/Cookbook/AutoPackageDiscovery
def is_package(path):

    """decipher whether path is a Python package"""

    return (
        os.path.isdir(path) and
        os.path.isfile(os.path.join(path, '__init__.py'))
        )


def find_packages(path, base=''):
    """Find all packages in path"""

    packages = {}
    for item in os.listdir(path):
        dirpath = os.path.join(path, item)
        if is_package(dirpath):
            if base:
                module_name = "%(base)s.%(item)s" % vars()
            else:
                module_name = item
            packages[module_name] = dirpath
            packages.update(find_packages(dirpath, module_name))
    return packages


def find_packages_templates(location='.'):
    """get dirs to be specified as package_data keys (templates)"""

    packages = []
    for root, dirs, files in os.walk(location):
        if 'templates' in dirs:  # include as a package_data key
            packages.append(root.replace(os.sep, '.').replace('..', ''))

    return {'pygeometa': ['templates/*/*.j2']}
    return packages


setup(
    name='pygeometa',
    version=find_version('pygeometa', '__init__.py'),
    description=DESCRIPTION.strip(),
    long_description=LONG_DESCRIPTION,
    license='MIT',
    platforms='all',
    keywords=' '.join(KEYWORDS),
    author=CONTACT,
    author_email=EMAIL,
    maintainer=CONTACT,
    maintainer_email=EMAIL,
    url=URL,
    install_requires=INSTALL_REQUIRES,
    packages=find_packages('.').keys(),
    package_data=find_packages_templates('pygeometa'),
    entry_points={
        'console_scripts': [
            'generate_metadata.py=pygeometa:cli'
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: GIS'
    ],
    cmdclass={'test': PyTest},
    test_suite='tests.run_tests'
)
