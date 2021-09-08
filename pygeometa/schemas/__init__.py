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
# Copyright (c) 2020 Tom Kralidis
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

import importlib
import logging
import os

from pygeometa.schemas.base import BaseOutputSchema

LOGGER = logging.getLogger(__name__)
THISDIR = os.path.dirname(os.path.realpath(__file__))

SCHEMAS = {
    'iso19139': 'pygeometa.schemas.iso19139.ISO19139OutputSchema',
    'iso19139-2': 'pygeometa.schemas.iso19139_2.ISO19139_2OutputSchema',
    'iso19139-hnap': 'pygeometa.schemas.iso19139_hnap.ISO19139HNAPOutputSchema',  # noqa
    'oarec-record': 'pygeometa.schemas.ogcapi_records.OGCAPIRecordOutputSchema',  # noqa
    'stac-item': 'pygeometa.schemas.stac.STACItemOutputSchema',
    'dcat': 'pygeometa.schemas.dcat.DCATOutputSchema',
    'wmo-cmp': 'pygeometa.schemas.wmo_cmp.WMOCMPOutputSchema',
    'wmo-wigos': 'pygeometa.schemas.wmo_wigos.WMOWIGOSOutputSchema'
}


def get_supported_schemas() -> list:
    """
    Get supported schemas

    :returns: list of supported schemas
    """

    LOGGER.debug('Generating list of supported schemas')

    return SCHEMAS.keys()

    dirs = os.listdir(THISDIR)

    LOGGER.debug('directory listing: {}'.format(dirs))

    dirs.remove('common')
    dirs.remove('__init__.py')
    dirs.remove('base.py')

    try:
        dirs.remove('__pycache__')
    except ValueError:
        pass

    LOGGER.debug('schemas: {}'.format(dirs))

    return dirs


def load_schema(schema_name: str) -> BaseOutputSchema:
    """
    loads schema plugin by name

    :param schema_name: shortname of schema

    :returns: plugin object
    """

    LOGGER.debug('Schemas: {}'.format(SCHEMAS.keys()))

    if schema_name not in SCHEMAS.keys():
        msg = 'Schema {} not found'.format(schema_name)
        LOGGER.exception(msg)
        raise InvalidSchemaError(msg)

    name = SCHEMAS[schema_name]

    if '.' in name:  # dotted path
        packagename, classname = name.rsplit('.', 1)
    else:
        raise InvalidSchemaError('Schema path {} not found'.format(name))

    LOGGER.debug('package name: {}'.format(packagename))
    LOGGER.debug('class name: {}'.format(classname))

    module = importlib.import_module(packagename)
    class_ = getattr(module, classname)

    return class_()


class InvalidSchemaError(Exception):
    """Invalid plugin"""
    pass
