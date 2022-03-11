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

import logging
import sys

import click

ARGUMENT_MCF = click.argument('mcf')
ARGUMENT_METADATA_FILE = click.argument('metadata-file', type=click.File())

OPTION_OUTPUT = click.option(
    '--output',
    type=click.File('w', encoding='utf-8'),
    help='Name of output file')


def OPTION_VERBOSITY(f):
    logging_options = ['ERROR', 'WARNING', 'INFO', 'DEBUG']

    def callback(ctx, param, value):
        if value is not None:
            logging.basicConfig(stream=sys.stdout,
                                level=getattr(logging, value))
        return True

    return click.option('--verbosity', '-v',
                        type=click.Choice(logging_options),
                        help='Verbosity',
                        callback=callback)(f)


def cli_callbacks(f):
    f = OPTION_VERBOSITY(f)
    return f
