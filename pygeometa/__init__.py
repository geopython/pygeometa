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

import codecs
from datetime import datetime
import logging
import os
import re
from xml.dom import minidom

import click
from jinja2 import Environment, FileSystemLoader
from jinja2.exceptions import TemplateNotFound

from six import StringIO
from six.moves.configparser import ConfigParser

__version__ = '0.2-dev'

LOGGER = logging.getLogger(__name__)

TEMPLATES = '{}{}templates'.format(os.path.dirname(os.path.realpath(__file__)),
                                   os.sep)


def get_charstring(option, section_items, language,
                   language_alternate=None):
    """convenience function to return unilingual or multilingual value(s)"""

    section_items = dict(section_items)
    option_value1 = None
    option_value2 = None

    if 'language_alternate' is None:  # unilingual
        option_tmp = '{}_{}'.format(option, language)
        if option_tmp in section_items:
            option_value1 = section_items[option_tmp]
        else:
            try:
                option_value1 = section_items[option]
            except KeyError:
                pass  # default=None
    else:  # multilingual
        option_tmp = '{}_{}'.format(option, language)
        if option_tmp in section_items:
            option_value1 = section_items[option_tmp]
        else:
            try:
                option_value1 = section_items[option]
            except KeyError:
                pass  # default=None
        option_tmp2 = '{}_{}'.format(option, language_alternate)
        if option_tmp2 in section_items:
            option_value2 = section_items[option_tmp2]

    return [option_value1, option_value2]


def get_distribution_language(section):
    """derive language of a given distribution construct"""

    try:
        return section.split(':')[1].split('_')[1]
    except IndexError:
        return 'en'


def normalize_datestring(datestring, fmt='default'):
    """groks date string into ISO8601"""

    today_and_now = datetime.utcnow()

    re1 = r'\$Date: (?P<year>\d{4})'
    re2 = r'\$Date: (?P<date>\d{4}-\d{2}-\d{2}) (?P<time>\d{2}:\d{2}:\d{2})'
    re3 = r'(?P<start>.*)\$Date: (?P<year>\d{4}).*\$(?P<end>.*)'

    try:
        if datestring == '$date$':  # $date$ magic keyword
            return today_and_now.strftime('%Y-%m-%dT%H:%M:%SZ')
        elif datestring == '$year$':  # $year$ magic keyword
            return today_and_now.strftime('%Y')
        elif '$year$' in datestring:  # $year$ magic keyword embedded
            return datestring.replace('$year$', today_and_now.strftime('%Y'))
        elif datestring.startswith('$Date'):  # svn Date keyword
            if fmt == 'year':
                mo = re.match(re1, datestring)
                return mo.group('year')
            else:  # default
                mo = re.match(re2, datestring)
                return '%sT%s'.format(mo.group('date', 'time'))
        elif '$Date' in datestring:  # svn Date keyword embedded
            if fmt == 'year':
                mo = re.match(re3, datestring)
                return '%s%s%s'.format(mo.group('start', 'year', 'end'))
    except AttributeError:
        raise RuntimeError('Invalid datestring: {}'.format(datestring))
    return datestring


def read_mcf(mcf):
    """returns dict of ConfigParser object from filepath"""

    mcf_list = []
    mcf_dict = {}

    def __to_configparser(mcf_object):
        """normalize mcf input into ConfigParser object"""

        cp_obj = None

        if isinstance(mcf_object, ConfigParser):
            LOGGER.debug('mcf object is already a ConfigParser object')
            cp_obj = mcf_object
        elif '[metadata]' in mcf_object:
            LOGGER.debug('mcf object is a string')
            s = StringIO(mcf_object)
            c = ConfigParser()
            c.readfp(s)
            cp_obj = c
        else:
            LOGGER.debug('mcf object is likely a filepath')
            c = ConfigParser()
            with codecs.open(mcf_object, encoding='utf-8') as fh:
                c.readfp(fh)
            cp_obj = c

        return cp_obj

    def makelist(mcf2):
        """recursive function for MCF by reference inclusion"""

        c = __to_configparser(mcf2)

        LOGGER.debug('reading {}'.format(mcf2))
        mcf_dict = c.__dict__['_sections']
        for section in mcf_dict.keys():
            if 'base_mcf' in mcf_dict[section]:
                base_mcf_path = get_abspath(mcf, mcf_dict[section]['base_mcf'])
                makelist(base_mcf_path)
                mcf_list.append(mcf2)
            else:  # leaf
                mcf_list.append(mcf2)

    makelist(mcf)

    for mcf_file in mcf_list:
        LOGGER.debug('reading {}'.format(mcf_file))
        c = __to_configparser(mcf_file)
        c_dict = c.__dict__['_sections']

        for section in c_dict.keys():
            if section not in mcf_dict:  # add the whole section
                LOGGER.debug('section {} does not exist. Adding'.format(
                             section))
                mcf_dict[section] = c_dict[section]
            else:
                LOGGER.debug('section {} exists. Adding options'.format(
                             section))
                for key, value in c_dict[section].items():
                    mcf_dict[section][key] = value

    return mcf_dict


def pretty_print(xml):
    """clean up indentation and spacing"""

    LOGGER.debug('pretty-printing XML')
    val = minidom.parseString(xml)
    return '\n'.join([l for l in
                      val.toprettyxml(indent=' '*2).split('\n') if l.strip()])


def render_template(mcf, schema=None, schema_local=None):
    """
    convenience function to render Jinja2 template given
    an mcf file, string, or ConfigParser object
    """

    LOGGER.debug('Evaluating schema path')
    if schema is None and schema_local is None:
        msg = 'schema or schema_local required'
        LOGGER.exception(msg)
        raise RuntimeError(msg)
    if schema_local is None:  # default templates dir
        abspath = '{}{}{}'.format(TEMPLATES, os.sep, schema)
    elif schema is None:  # user-defined
        abspath = schema_local

    LOGGER.debug('Setting up template environment {}'.format(abspath))
    env = Environment(loader=FileSystemLoader([abspath, TEMPLATES]))
    env.filters['normalize_datestring'] = normalize_datestring
    env.filters['get_distribution_language'] = get_distribution_language
    env.filters['get_charstring'] = get_charstring
    env.globals.update(zip=zip)
    env.globals.update(get_charstring=get_charstring)
    env.globals.update(normalize_datestring=normalize_datestring)

    try:
        LOGGER.debug('Loading template')
        template = env.get_template('main.j2')
    except TemplateNotFound:
        msg = 'Missing metadata template'
        LOGGER.exception(msg)
        raise RuntimeError(msg)

    LOGGER.debug('Processing template')
    xml = template.render(record=read_mcf(mcf),
                          software_version=__version__).encode('utf-8')
    return pretty_print(xml)


def get_supported_schemas():
    """returns a list of supported schemas"""

    LOGGER.debug('Generating list of supported schemas')
    dirs = os.listdir(TEMPLATES)
    dirs.remove('common')
    return dirs


def get_abspath(mcf, filepath):
    """helper function absolute file access"""

    abspath = os.path.dirname(os.path.realpath(mcf))
    return os.path.join(abspath, filepath)


@click.command()
@click.option('--mcf',
              type=click.Path(exists=True, resolve_path=True),
              help='Path to metadata control file (.mcf)')
@click.option('--output', type=click.File('w', encoding='utf-8'),
              help='Name of output file')
@click.option('--schema',
              type=click.Choice(get_supported_schemas()),
              help='Metadata schema')
@click.option('--schema_local',
              type=click.Path(exists=True, resolve_path=True,
                              dir_okay=True, file_okay=False),
              help='Locally defined metadata schema')
def cli(mcf, schema, schema_local, output):
    if mcf is None or (schema is None and schema_local is None):
        raise click.UsageError('Missing arguments')
    else:
        content = render_template(mcf, schema=schema,
                                  schema_local=schema_local)
        if output is None:
            click.echo_via_pager(content)
        else:
            output.write(content)
