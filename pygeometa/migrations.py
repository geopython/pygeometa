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
# Copyright (c) 2026 Tom Kralidis
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

import click
import logging

import yaml

from pygeometa import cli_options
from pygeometa.core import read_mcf

LOGGER = logging.getLogger(__name__)


def migrate_from_1_0_to_2_0(mcf_dict: dict) -> dict:
    """
    migrate MCF from 1.0

    :param mcf_dict: `dict` of MCF

    :returns: `dict` of MCF migrated from 1.0
    """

    mcf_dict['mcf']['version'] = LATEST_MCF

    mcf_dict['metadata']['dates'] = {
        'creation': mcf_dict['metadata'].pop('datestamp', None)
    }

    return mcf_dict


LATEST_MCF = 2.0

MIGRATIONS = {
    '1.0': migrate_from_1_0_to_2_0
}


def migrate(mcf: dict) -> dict:
    """
    migrate MCF document

    :param mcf_dict: `dict` of MCF

    :returns: `dict` of MCF migrated from 1.0
    """

    mcf_dict = read_mcf(mcf, skip_version_fail=True)

    mcf_version = str(mcf_dict['mcf']['version'])
    LOGGER.info(f'Migrating MCF from version {mcf_version}')

    if mcf_version == str(LATEST_MCF):
        LOGGER.info('MCF is already at the latest version')
        return mcf_dict

    if mcf_version not in MIGRATIONS.keys():
        msg = 'Unsupported version for migration'
        raise RuntimeError(msg)

    return MIGRATIONS[mcf_version](mcf_dict)


@click.command('migrate')
@click.pass_context
@cli_options.ARGUMENT_MCF
@cli_options.OPTION_OUTPUT
@cli_options.OPTION_VERBOSITY
def migrate_(ctx, mcf, output, verbosity):
    """migrate an MCF document"""

    try:
        content = migrate(mcf)
    except RuntimeError as err:
        raise click.ClickException(err)

    if output is None:
        click.echo(yaml.dump(content))
    else:
        output.write(yaml.dump(content, indent=4))
