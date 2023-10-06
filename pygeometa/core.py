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
# Copyright (c) 2022 Tom Kralidis
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

from collections.abc import Mapping
from datetime import date, datetime
import json
import logging
import os
import pathlib
import pkg_resources
import re
from typing import IO, Union
from xml.dom import minidom

import click
from jinja2 import Environment, FileSystemLoader
from jinja2.exceptions import TemplateNotFound
from jsonschema import validate as jsonschema_validate
from jsonschema.exceptions import ValidationError
import yaml

from pygeometa import cli_options
from pygeometa.helpers import json_serial
from pygeometa.schemas import get_supported_schemas, load_schema

LOGGER = logging.getLogger(__name__)

SCHEMAS = pathlib.Path(__file__).resolve().parent / 'schemas'

VERSION = pkg_resources.require('pygeometa')[0].version


def get_charstring(option: Union[str, dict], language: str,
                   language_alternate: str = None) -> list:
    """
    convenience function to return unilingual or multilingual value(s)

    :param option: option value (str or dict if multilingual)
    :param language: language
    :param language_alternate: alternate language

    :returns: list of unilingual or multilingual values
    """

    if option is None:
        return [None, None]
    elif isinstance(option, str):  # unilingual
        return [option, None]
    elif isinstance(option, list):  # multilingual list
        return [option, None]
    else:  # multilingual
        return [option.get(language), option.get(language_alternate)]


def get_distribution_language(section: str) -> str:
    """
    derive language of a given distribution construct

    :param section: section name

    :returns: distribution language
    """

    try:
        return section.split('_')[1]
    except IndexError:
        return 'en'


def normalize_datestring(datestring: str, format_: str = 'default') -> str:
    """
    groks date string into ISO8601

    :param datestring: date in string representation
    :format_: datetring format ('year' or default [full])

    :returns: string of properly formatted datestring
    """

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
                return f"{mo.group('date')}T{mo.group('time')}"
        elif '$Date' in datestring:  # svn Date keyword embedded
            if format_ == 'year':
                mo = re.match(re3, datestring)
                return f"{mo.group('start')}{mo.group('year')}{mo.group('end')}"  # noqa
    except (AttributeError, TypeError):
        raise RuntimeError(f'Invalid datestring: {datestring}')

    return datestring


def prune_distribution_formats(formats: dict) -> list:
    """
    derive a unique list of distribution formats

    :param formats: distribution formats

    :returns: unique distribution formats list
    """

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


def prune_transfer_option(formats: dict, language: str) -> list:
    """
    derive a unique list of transfer options.
    The unique character is based on identification language

    :param formats: list of transfer options

    :returns: unique transfer options list
    """

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


def read_mcf(mcf: Union[dict, str]) -> dict:
    """
    returns dict of YAML file from filepath, string or dict

    :param mcf: str, dict or filepath of MCF data

    :returns: dict of MCF data
    """

    mcf_dict = {}
    mcf_versions = ['1.0']

    def __to_dict(mcf_object):
        """normalize mcf input into dict"""

        dict_ = None

        try:
            if isinstance(mcf_object, dict):
                LOGGER.debug('mcf object is already a dict')
                LOGGER.debug('Environment variables will NOT be interpreted')
                dict_ = mcf_object
            elif isinstance(mcf_object, pathlib.PurePath):
                LOGGER.debug('mcf object is a pathlib.PurePath')
                with mcf_object.open() as fh:
                    dict_ = yaml_load(fh)
            elif 'metadata:' in mcf_object:
                LOGGER.debug('mcf object is a string')
                dict_ = yaml_load(mcf_object)
            else:
                LOGGER.debug('mcf object is likely a filepath')
                with open(mcf_object, encoding='utf-8') as fh:
                    dict_ = yaml_load(fh)
        except yaml.scanner.ScannerError as err:
            msg = f'YAML parsing error: {err}'
            LOGGER.debug(msg)
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
                    and isinstance(merge_dct[k], Mapping)):
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

    LOGGER.debug(f'reading {mcf}')
    mcf_dict = __to_dict(mcf)

    LOGGER.debug('recursively parsing dict')

    mcf_dict = __parse_mcf_dict_recursive(mcf_dict)

    LOGGER.debug(f'Fully parsed MCF: {mcf_dict}')

    try:
        mcf_version = str(mcf_dict['mcf']['version'])
        LOGGER.info(f'MCF version: {mcf_version}')
    except KeyError:
        msg = 'no MCF version specified'
        LOGGER.error(msg)
        raise MCFReadError(msg)

    for mcf_version_ in mcf_versions:
        if not mcf_version_.startswith(mcf_version):
            msg = f'invalid / unsupported version {mcf_version}'
            LOGGER.error(msg)
            raise MCFReadError(msg)

    return mcf_dict


def pretty_print(xml: str) -> str:
    """
    clean up indentation and spacing

    :param xml: str of XML data

    :returns: str of pretty-printed XML data
    """

    LOGGER.debug('pretty-printing XML')
    val = minidom.parseString(xml)
    return '\n'.join([val for val in val.toprettyxml(indent=' '*2).split('\n') if val.strip()])  # noqa


def render_j2_template(mcf: dict, template_dir: str = None) -> str:
    """
    convenience function to render Jinja2 template given
    an mcf file, string, or dict

    :param mcf: dict of MCF data
    :param template_dir: directory of schema templates

    :returns: str of metadata output
    """

    LOGGER.debug('Evaluating template directory')
    if template_dir is None:
        msg = 'template_dir or schema_local required'
        LOGGER.error(msg)
        raise RuntimeError(msg)

    LOGGER.debug(f'Setting up template environment {template_dir}')
    env = Environment(loader=FileSystemLoader([template_dir, SCHEMAS]))

    LOGGER.debug('Adding template filters')
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
        LOGGER.error(msg)
        raise RuntimeError(msg)

    LOGGER.debug('Processing template')
    xml = template.render(record=mcf,
                          pygeometa_version=VERSION).encode('utf-8')
    return pretty_print(xml)


def validate_mcf(instance_dict: dict) -> bool:
    """
    Validate an MCF document against the MCF schema

    :param instance_dict: dict of MCF instance

    :returns: `bool` of validation
    """

    schema_file = SCHEMAS / 'mcf' / 'core.yaml'

    with schema_file.open() as fh2:
        schema_dict = yaml_load(fh2)

        try:
            jsonschema_validate(instance_dict, schema_dict)
        except ValidationError as err:
            raise MCFValidationError(repr(err))

        return True


def get_abspath(mcf, filepath):
    """helper function absolute file access"""

    abspath = pathlib.Path(mcf).resolve().parent

    return abspath / filepath


def get_typed_value(value) -> Union[float, int, str]:
    """
    Derive true type from data value
    :param value: value
    :returns: value as a native Python data type
    """

    try:
        if '.' in value:  # float?
            value2 = float(value)
        elif len(value) > 1 and value.startswith('0'):
            value2 = value
        else:  # int?
            value2 = int(value)
    except ValueError:  # string (default)?
        value2 = value

    return value2


def yaml_load(obj: Union[IO, str]) -> dict:
    """
    serializes a YAML files into a pyyaml object

    :param obj: file handle or string

    :returns: `dict` representation of YAML
    """

    # support environment variables in config
    # https://stackoverflow.com/a/55301129
    path_matcher = re.compile(r'.*\$\{([^}^{]+)\}.*')

    def path_constructor(loader, node):
        env_var = path_matcher.match(node.value).group(1)
        if env_var not in os.environ:
            msg = f'Undefined environment variable {env_var} in config'
            raise EnvironmentError(msg)
        return get_typed_value(os.path.expandvars(node.value))

    class EnvVarLoader(yaml.SafeLoader):
        pass

    EnvVarLoader.add_implicit_resolver('!path', path_matcher, None)
    EnvVarLoader.add_constructor('!path', path_constructor)

    return yaml.load(obj, Loader=EnvVarLoader)


class MCFReadError(Exception):
    """Exception stub for format reading errors"""
    pass


class MCFValidationError(Exception):
    """Exception stub for validation errors"""
    pass


@click.command('import')
@click.pass_context
@cli_options.ARGUMENT_METADATA_FILE
@cli_options.OPTION_OUTPUT
@cli_options.OPTION_VERBOSITY
@click.option('--schema', required=True,
              type=click.Choice(get_supported_schemas()),
              help='Metadata schema')
def import_(ctx, metadata_file, schema, output, verbosity):
    """import metadata"""

    LOGGER.info(f'Importing {metadata_file} into {schema}')
    schema_object = load_schema(schema)

    try:
        content = schema_object.import_(metadata_file.read())
    except NotImplementedError:
        raise click.ClickException(f'Import not supported for {schema}')

    if output is None:
        click.echo(yaml.dump(content))
    else:
        output.write(yaml.dump(content, indent=4))


@click.command()
@click.pass_context
@cli_options.ARGUMENT_MCF
@cli_options.OPTION_OUTPUT
@click.option('--schema',
              type=click.Choice(get_supported_schemas()),
              help='Metadata schema')
@click.option('--schema_local',
              type=click.Path(exists=True, resolve_path=True,
                              dir_okay=True, file_okay=False),
              help='Locally defined metadata schema')
@cli_options.OPTION_VERBOSITY
def generate(ctx, mcf, schema, schema_local, output, verbosity):
    """generate metadata"""

    if schema is None and schema_local is None:
        raise click.UsageError('Missing arguments')
    elif None not in [schema, schema_local]:
        raise click.UsageError('schema / schema_local are mutually exclusive')

    mcf_dict = read_mcf(mcf)

    if schema is not None:
        LOGGER.info(f'Processing {mcf} into {schema}')
        schema_object = load_schema(schema)
        content = schema_object.write(mcf_dict)
    else:
        content = render_j2_template(mcf_dict, template_dir=schema_local)

    if output is None:
        click.echo(content)
    else:
        output.write(content)


@click.command()
@click.pass_context
@cli_options.ARGUMENT_MCF
@cli_options.OPTION_VERBOSITY
def info(ctx, mcf, verbosity):
    """provide information about an MCF"""

    LOGGER.info(f'Processing {mcf}')
    try:
        content = read_mcf(mcf)

        click.echo('MCF overview')
        click.echo(f"  version: {content['mcf']['version']}")
        click.echo(f"  identifier: {content['metadata']['identifier']}")
        click.echo(f"  language: {content['metadata']['language']}")
    except Exception as err:
        raise click.ClickException(err)


@click.command()
@click.pass_context
@cli_options.OPTION_VERBOSITY
def schemas(ctx, verbosity):
    """list supported schemas"""
    click.echo('Supported schemas')

    for schema in get_supported_schemas(details=True):
        s = f"{schema['id']} (read: {schema['read']}, write: {schema['write']}): {schema['description']}"  # noqa
        click.echo(s)


@click.command()
@click.pass_context
@cli_options.ARGUMENT_MCF
@cli_options.OPTION_VERBOSITY
def validate(ctx, mcf, verbosity):
    """validate MCF Document"""

    click.echo(f'Validating {mcf}')

    instance = json.loads(json.dumps(read_mcf(mcf), default=json_serial))
    validate_mcf(instance)

    click.echo('Valid MCF document')


@click.command()
@click.pass_context
@cli_options.ARGUMENT_METADATA_FILE
@cli_options.OPTION_OUTPUT
@cli_options.OPTION_VERBOSITY
@click.option('--input-schema', required=True,
              type=click.Choice(get_supported_schemas()),
              help='Metadata schema of input file')
@click.option('--output-schema', required=True,
              type=click.Choice(get_supported_schemas()),
              help='Metadata schema of input file')
def transform(ctx, metadata_file, input_schema, output_schema, output,
              verbosity):
    """transform metadata"""

    LOGGER.info(f'Importing {metadata_file} into {input_schema}')
    schema_object_input = load_schema(input_schema)
    content = None

    try:
        content = schema_object_input.import_(metadata_file.read())
    except NotImplementedError:
        raise click.ClickException(f'Import not supported for {input_schema}')

    LOGGER.info(f'Processing into {output_schema}')
    schema_object_output = load_schema(output_schema)
    content = schema_object_output.write(content)

    if output is None:
        click.echo(content)
    else:
        output.write(content)
