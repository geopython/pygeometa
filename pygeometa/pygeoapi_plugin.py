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

#
# pygeometa as a service
# ----------------------
#
# This file is intended to be used as a pygeoapi process plugin which will
# provide pygeometa validation and metadata generation via OGC API - Processes.
#
# To integrate this plugin in pygeoapi:
#
# 1. ensure pygeometa is installed into the pygeoapi deployment environment
#
# 2. add the two proceses to the pygeoapi configuration as follows:
#
# pygeometa-metadata-validate:
#     type: process
#     processor:
#         name: pygeometa.pygeoapi_plugin.PygeometaMetadataValidateProcessor
#
# pygeometa-metadata-generate:
#     type: process
#     processor:
#         name: pygeometa.pygeoapi_plugin.PygeometaMetadataGenerateProcessor
#
# 3. (re)start pygeoapi
#
# The resulting processes will be available at the following endpoints:
#
# /processes/pygeometa-metadata-validate
#
# /processes/pygeometa-metadata-generate
#
# Note that pygeoapi's OpenAPI/Swagger interface (at /openapi) will also
# provide a developer-friendly interface to test and run requests
#

import logging

from pygeometa.core import read_mcf, validate_mcf
from pygeometa.schemas import get_supported_schemas, load_schema

from pygeoapi.process.base import BaseProcessor, ProcessorExecuteError


LOGGER = logging.getLogger(__name__)

INPUT_MCF = {
    'title': 'Metadata control file (MCF)',
    'description': 'a pygeometa metadata control file (MCF) as JSON',
    'schema': {
        'type': 'object',
        'contentMediaType': 'application/json'
    },
    'minOccurs': 1,
    'maxOccurs': 1,
    'metadata': None,
    'keywords': ['metadata control file', 'mcf']
}

PROCESS_METADATA_VALIDATE = {
    'version': '0.1.0',
    'id': 'pygeometa-metadata-validate',
    'title': {
        'en': 'pygeometa metadata control file (MCF) validation',
    },
    'description': {
        'en': 'Validate metadata from a pygeometa metadata control file (MCF)',
    },
    'keywords': ['pygeometa', 'metadata', 'validate'],
    'links': [{
        'type': 'text/html',
        'rel': 'about',
        'title': 'information',
        'href': 'https://geopython.github.io/pygeometa/pygeoapi-plugin',
        'hreflang': 'en-US'
    }],
    'inputs': {
        'mcf': INPUT_MCF
    },
    'outputs': {
        'validate-report': {
            'title': 'Validate report',
            'description': 'Validate report',
            'schema': {
                'type': 'object',
                'contentMediaType': 'application/json'
            }
        }
    },
    'example': {
        'inputs': {
            'mcf': {'mcf': {'version': '1.0'}}
        }
    }
}


PROCESS_METADATA_GENERATE = {
    'version': '0.1.0',
    'id': 'pygeometa-metadata-generate',
    'title': {
        'en': 'pygeometa metadata generation',
    },
    'description': {
        'en': 'Generate metadata from a pygeometa metadata control file (MCF)'
    },
    'keywords': ['pygeometa', 'metadata', 'generate'],
    'links': [{
        'type': 'text/html',
        'rel': 'about',
        'title': 'information',
        'href': 'https://geopython.github.io/pygeometa/pygeoapi-plugin',
        'hreflang': 'en-US'
    }],
    'inputs': {
        'mcf': INPUT_MCF,
        'schema': {
            'title': 'Metadata schema',
            'description': 'Output metadata schema',
            'schema': {
                'type': 'string',
                'enum': list(get_supported_schemas())
            },
            'minOccurs': 1,
            'maxOccurs': 1,
            'metadata': None,
            'keywords': ['metadata', 'schema']
        }
    },
    'outputs': {
        'generation': {
            'title': 'Generated metadata',
            'description': 'Generated metadata',
            'schema': {
                'type': 'object',
                'contentMediaType': 'application/json'
            }
        }
    },
    'example': {
        'inputs': {
            'mcf': {'mcf': {'version': '1.0'}},
            'schema': 'oarec-record'
        }
    }
}


class PygeometaMetadataValidateProcessor(BaseProcessor):
    """pygeometa metadata validate example"""

    def __init__(self, processor_def):
        """
        Initialize object

        :param processor_def: provider definition

        :returns: pygeometa.pygeoapi_plugin.PygeometaMetadataValidateProcessor
        """

        super().__init__(processor_def, PROCESS_METADATA_VALIDATE)

    def execute(self, data):

        response = None
        mimetype = 'application/json'
        mcf = data.get('mcf')

        if mcf is None:
            msg = 'Missing input MCF'
            LOGGER.error(msg)
            raise ProcessorExecuteError(msg)

        try:
            LOGGER.debug('Validating MCF')
            instance = read_mcf(mcf)
            validate_mcf(instance)
            response = 'Valid MCF'
        except Exception as err:
            response = f'Invalid MCF: {err}'

        outputs = {
            'id': 'validate-report',
            'value': response
        }

        return mimetype, outputs

    def __repr__(self):
        return '<PygeometaMetadataValidateProcessor>'


class PygeometaMetadataGenerateProcessor(BaseProcessor):
    """pygeometa metadata generate example"""

    def __init__(self, processor_def):
        """
        Initialize object

        :param processor_def: provider definition

        :returns: pygeometa.pygeoapi_plugin.PygeometaMetadataGenerateProcessor
        """

        super().__init__(processor_def, PROCESS_METADATA_GENERATE)

    def execute(self, data):

        response = None
        mimetype = 'application/json'
        mcf = data.get('mcf')
        schema = data.get('schema')

        if None in [mcf, schema]:
            msg = 'Missing input MCF or schema'
            LOGGER.error(msg)
            raise ProcessorExecuteError(msg)

        try:
            LOGGER.debug('Generating metadata')
            instance = read_mcf(mcf)
            schema_object = load_schema(schema)

            if schema_object.outputformat == 'json':
                stringify = False
            else:
                mimetype = 'application/xml'
                stringify = True

            response = schema_object.write(instance, stringify=stringify)

        except Exception as err:
            response = f'Generation error: {err}'

        return mimetype, response

    def __repr__(self):
        return '<PygeometaMetadataGenerateProcessor>'
