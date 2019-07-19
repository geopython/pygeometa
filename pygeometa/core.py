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
# Copyright (c) 2017 Tom Kralidis
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

import collections
from datetime import date, datetime
import io
import logging
import os
import pkg_resources
import re
from xml.dom import minidom

import click
from jinja2 import Environment, FileSystemLoader
from jinja2.exceptions import TemplateNotFound
import yaml

LOGGER = logging.getLogger(__name__)

TEMPLATES = '{}{}templates'.format(os.path.dirname(os.path.realpath(__file__)),
                                   os.sep)

VERSION = pkg_resources.require('pygeometa')[0].version


def get_charstring(option, section_items, language,
                   language_alternate=None):
    """convenience function to return unilingual or multilingual value(s)"""

    section_items = dict(section_items)
    option_value1 = None
    option_value2 = None

    if 'language_alternate' is None:  # noqa unilingual
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
        return section.split('_')[1]
    except IndexError:
        return 'en'


def normalize_datestring(datestring, format_='default'):
    """groks date string into ISO8601"""

    today_and_now = datetime.utcnow()

    re1 = r'\$Date: (?P<year>\d{4})'
    re2 = r'\$Date: (?P<date>\d{4}-\d{2}-\d{2}) (?P<time>\d{2}:\d{2}:\d{2})'
    re3 = r'(?P<start>.*)\$Date: (?P<year>\d{4}).*\$(?P<end>.*)'

    try:
        if isinstance(datestring, date):
            if datestring.year < 1900:
                datestring2 = '{0.day:02d}.{0.month:02d}.{0.year:4d}'.format(
                    datestring)
            else:
                datestring2 = datestring.strftime('%Y-%m-%dT%H:%M:%SZ')
            if datestring2.endswith('T00:00:00Z'):
                datestring2 = datestring2.replace('T00:00:00Z', '')
            return datestring2
        elif isinstance(datestring, int) and len(str(datestring)) == 4:  # year
            return str(datestring)
        if datestring == '$date$':  # $date$ magic keyword
            return today_and_now.strftime('%Y-%m-%d')
        elif datestring == '$datetime$':  # $datetime$ magic keyword
            return today_and_now.strftime('%Y-%m-%dT%H:%M:%SZ')
        elif datestring == '$year$':  # $year$ magic keyword
            return today_and_now.strftime('%Y')
        elif '$year$' in datestring:  # $year$ magic keyword embedded
            return datestring.replace('$year$', today_and_now.strftime('%Y'))
        elif datestring.startswith('$Date'):  # svn Date keyword
            if format_ == 'year':
                mo = re.match(re1, datestring)
                return mo.group('year')
            else:  # default
                mo = re.match(re2, datestring)
                return '%sT%s'.format(mo.group('date', 'time'))
        elif '$Date' in datestring:  # svn Date keyword embedded
            if format_ == 'year':
                mo = re.match(re3, datestring)
                return '%s%s%s'.format(mo.group('start', 'year', 'end'))
    except AttributeError:
        raise RuntimeError('Invalid datestring: {}'.format(datestring))
    return datestring


def prune_distribution_formats(formats):
    """derive a unique list of distribution formats"""

    counter = 0
    formats_ = []
    unique_formats = []

    for k1, v1 in formats.items():
        row = {}
        for k2, v2 in v1.items():
            if k2.startswith('format'):
                row[k2] = v2
        formats_.append(row)

    num_elements = len(formats)

    for f in range(0, len(formats_)):
        counter += 1
        if formats_[f] not in unique_formats:
            unique_formats.append(formats_[f])
        if num_elements == counter:
            break
    return unique_formats


def prune_transfer_option(formats, language):
    """derive a unique list of transfer options.
    The unique character is based on identification language"""

    unique_transfer = []
    nil_reasons = ['missing',
                   'withheld',
                   'inapplicable',
                   'unknown',
                   'template']

    for k, v in formats.items():
        if language.split(";")[0] in k and language not in nil_reasons:
            unique_transfer.append(v)
        elif language in nil_reasons:
            unique_transfer.append(v)
    return unique_transfer


def read_mcf(mcf):
    """returns dict of YAML file from filepath, string or dict"""

    mcf_dict = {}
    mcf_versions = ['1.0']

    def __to_dict(mcf_object):
        """normalize mcf input into dict"""

        dict_ = None

        try:
            if isinstance(mcf_object, dict):
                LOGGER.debug('mcf object is already a dict')
                dict_ = mcf_object
            elif 'metadata:' in mcf_object:
                LOGGER.debug('mcf object is a string')
                dict_ = yaml.load(mcf_object, Loader=yaml.FullLoader)
            else:
                LOGGER.debug('mcf object is likely a filepath')
                with io.open(mcf_object, encoding='utf-8') as fh:
                    dict_ = yaml.load(fh, Loader=yaml.FullLoader)
        except yaml.scanner.ScannerError as err:
            msg = 'YAML parsing error: {}'.format(err)
            LOGGER.exception(msg)
            raise MCFReadError(msg)

        return dict_

    # from https://gist.github.com/angstwad/bf22d1822c38a92ec0a9
    def __dict_merge(dct, merge_dct):
        """
        Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
        updating only top-level keys, __dict_merge recurses down into dicts
        nested to an arbitrary depth, updating keys. The ``merge_dct`` is
        merged into ``dct``.

        :param dct: dict onto which the merge is executed
        :param merge_dct: dct merged into dct

        :returns: None
        """
        for k, v in merge_dct.items():
            if (k in dct and isinstance(dct[k], dict)
                    and isinstance(merge_dct[k], collections.Mapping)):
                __dict_merge(dct[k], merge_dct[k])
            else:
                if k in dct and k in merge_dct:
                    pass
                else:
                    dct[k] = merge_dct[k]

    def __parse_mcf_dict_recursive(dict2):
        for k, v in dict2.copy().items():
            if isinstance(v, dict):
                __parse_mcf_dict_recursive(v)
            else:
                if k == 'base_mcf':
                    base_mcf_dict = __to_dict(get_abspath(mcf, v))
                    for k2, v2 in base_mcf_dict.copy().items():
                        if k2 == 'base_mcf':
                            base_mcf_dict2 = __to_dict(get_abspath(mcf, v2))
                            __dict_merge(base_mcf_dict, base_mcf_dict2)
                            base_mcf_dict.pop(k2, None)
                    __dict_merge(dict2, base_mcf_dict)
                    dict2.pop(k, None)
        return dict2

    LOGGER.debug('reading {}'.format(mcf))
    mcf_dict = __to_dict(mcf)

    LOGGER.debug('recursively parsing dict')

    mcf_dict = __parse_mcf_dict_recursive(mcf_dict)

    LOGGER.debug('Fully parsed MCF: {}'.format(mcf_dict))

    try:
        mcf_version = str(mcf_dict['mcf']['version'])
        LOGGER.info('MCF version: {}'.format(mcf_version))
    except KeyError:
        msg = 'no MCF version specified'
        LOGGER.error(msg)
        raise MCFReadError(msg)

    for mcf_version_ in mcf_versions:
        if not mcf_version_.startswith(mcf_version):
            msg = 'invalid / unsupported version {}'.format(mcf_version)
            LOGGER.error(msg)
            raise MCFReadError(msg)

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
    an mcf file, string, or dict
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
    env.filters['prune_distribution_formats'] = prune_distribution_formats
    env.filters['prune_transfer_option'] = prune_transfer_option
    env.globals.update(zip=zip)
    env.globals.update(get_charstring=get_charstring)
    env.globals.update(normalize_datestring=normalize_datestring)
    env.globals.update(prune_distribution_formats=prune_distribution_formats)
    env.globals.update(prune_transfer_option=prune_transfer_option)

    try:
        LOGGER.debug('Loading template')
        template = env.get_template('main.j2')
    except TemplateNotFound:
        msg = 'Missing metadata template'
        LOGGER.exception(msg)
        raise RuntimeError(msg)

    LOGGER.debug('Processing template')
    xml = template.render(record=read_mcf(mcf),
                          pygeometa_version=VERSION).encode('utf-8')
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


class MCFReadError(Exception):
    """Exception stub for format reading errors"""
    pass


@click.command('generate-metadata')
@click.pass_context
@click.option('--mcf',
              type=click.Path(exists=True, resolve_path=True),
              help='Path to metadata control file (.yml)')
@click.option('--output', type=click.File('w', encoding='utf-8'),
              help='Name of output file')
@click.option('--schema',
              type=click.Choice(get_supported_schemas()),
              help='Metadata schema')
@click.option('--schema_local',
              type=click.Path(exists=True, resolve_path=True,
                              dir_okay=True, file_okay=False),
              help='Locally defined metadata schema')
@click.option('--verbosity', type=click.Choice(['ERROR', 'WARNING',
              'INFO', 'DEBUG']), help='Verbosity')
def generate_metadata(ctx, mcf, schema, schema_local, output, verbosity):
    """generate metadata"""

    if verbosity is not None:
        logging.basicConfig(level=getattr(logging, verbosity))

    if mcf is None or (schema is None and schema_local is None):
        raise click.UsageError('Missing arguments')
    else:
        LOGGER.info('Processing {} into {}'.format(mcf, schema))
        content = render_template(mcf, schema=schema,
                                  schema_local=schema_local)
        if output is None:
            click.echo_via_pager(content)
        else:
            output.write(content)
