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
# provide pygeometa functionality via OGC API - Processes.
#
# To integrate this plugin in pygeoapi:
#
# 1. ensure pygeometa is installed into the pygeoapi deployment environment
#
# 2. add the processes to the pygeoapi configuration as follows:
#
# pygeometa-metadata-schemas:
#     type: process
#     processor:
#         name: pygeometa.pygeoapi_plugin.PygeometaMetadataSchemasProcessor
#
# pygeometa-metadata-import:
#     type: process
#     processor:
#         name: pygeometa.pygeoapi_plugin.PygeometaMetadataImportProcessor
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
# pygeometa-metadata-transform:
#     type: process
#     processor:
#         name: pygeometa.pygeoapi_plugin.PygeometaMetadataTransformProcessor
#
#
# 3. (re)start pygeoapi
#
# The resulting processes will be available at the following endpoints:
#
# /processes/pygeometa-metadata-schemas
#
# /processes/pygeometa-metadata-import
#
# /processes/pygeometa-metadata-validate
#
# /processes/pygeometa-metadata-generate
#
# /processes/pygeometa-metadata-transform
#
# Note that pygeoapi's OpenAPI/Swagger interface (at /openapi) will also
# provide a developer-friendly interface to test and run requests
#

import logging

from pygeometa import __version__
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

INPUT_METADATA = {
    'title': 'Metadata',
    'description': 'Metadata record',
    'schema': {
        'type': 'string',
    },
    'minOccurs': 1,
    'maxOccurs': 1,
    'metadata': None,
    'keywords': ['metadata', 'record']
}

INPUT_SCHEMA = {
    'title': 'Metadata schema',
    'description': 'Metadata schema',
    'schema': {
        'type': 'string',
        'enum': list(get_supported_schemas())
    },
    'minOccurs': 1,
    'maxOccurs': 1,
    'metadata': None,
    'keywords': ['metadata', 'schema']
}


PROCESS_METADATA_SCHEMAS = {
    'version': __version__,
    'id': 'pygeometa-metadata-schemas',
    'title': {
        'en': 'pygeometa metadata schemas',
    },
    'description': {
        'en': 'List supported schemas'
    },
    'keywords': ['pygeometa', 'metadata', 'schemas'],
    'links': [{
        'type': 'text/html',
        'rel': 'about',
        'title': 'information',
        'href': 'https://geopython.github.io/pygeometa/pygeoapi-plugin',
        'hreflang': 'en-US'
    }],
    'inputs': {},
    'outputs': {
        'result': {
            'title': 'List of supported schemas',
            'description': 'List of supported schemas',
            'schema': {
                'type': 'object',
                'contentMediaType': 'application/json'
            }
        }
    },
    'example': {
        'inputs': {}
    }
}
PROCESS_METADATA_IMPORT = {
    'version': __version__,
    'id': 'pygeometa-metadata-import',
    'title': {
        'en': 'pygeometa metadata import',
    },
    'description': {
        'en': 'Import metadata into MCF'
    },
    'keywords': ['pygeometa', 'metadata', 'import'],
    'links': [{
        'type': 'text/html',
        'rel': 'about',
        'title': 'information',
        'href': 'https://geopython.github.io/pygeometa/pygeoapi-plugin',
        'hreflang': 'en-US'
    }],
    'inputs': {
        'metadata': INPUT_METADATA,
        'schema': INPUT_SCHEMA
    },
    'outputs': {
        'result': {
            'title': 'Generated MCF',
            'description': 'Generated MCF',
            'schema': {
                'type': 'object',
                'contentMediaType': 'application/json'
            }
        }
    },
    'example': {
        'inputs': {
            'metadata': '<gmd:MD_Metadata>...</gmd:MD_Metadata>',
            'schema': 'iso19139'
        }
    }
}

PROCESS_METADATA_VALIDATE = {
    'version': __version__,
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
        'result': {
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
    'version': __version__,
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
        'schema': INPUT_SCHEMA
    },
    'outputs': {
        'result': {
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


PROCESS_METADATA_TRANSFORM = {
    'version': __version__,
    'id': 'pygeometa-metadata-transform',
    'title': {
        'en': 'pygeometa metadata transformation',
    },
    'description': {
        'en': 'Transform metadata'
    },
    'keywords': ['pygeometa', 'metadata', 'transform'],
    'links': [{
        'type': 'text/html',
        'rel': 'about',
        'title': 'information',
        'href': 'https://geopython.github.io/pygeometa/pygeoapi-plugin',
        'hreflang': 'en-US'
    }],
    'inputs': {
        'metadata': INPUT_METADATA,
        'input-schema': INPUT_SCHEMA,
        'output-schema': INPUT_SCHEMA
    },
    'outputs': {
        'result': {
            'title': 'Transformed metadata',
            'description': 'Transformed metadata',
            'schema': {
                'type': 'object',
                'contentMediaType': 'application/json'
            }
        }
    },
    'example': {
        'inputs': {
            'metadata': '<gmd:MD_Metadata>...</gmd:MD_Metadata>',
            'input-schema': 'iso19139',
            'output-schema': 'oarec-record'
        }
    }
}


class PygeometaMetadataSchemasProcessor(BaseProcessor):
    """pygeometa metadata schemas example"""

    def __init__(self, processor_def):
        """
        Initialize object

        :param processor_def: provider definition

        :returns: pygeometa.pygeoapi_plugin.PygeometaMetadataSchemasProcessor
        """

        super().__init__(processor_def, PROCESS_METADATA_SCHEMAS)

    def execute(self, data):

        mimetype = 'application/json'

        outputs = {
            'id': 'schemas',
            'value': get_supported_schemas(details=True)
        }

        return mimetype, outputs

    def __repr__(self):
        return '<PygeometaMetadataSchemasProcessor>'


class PygeometaMetadataImportProcessor(BaseProcessor):
    """pygeometa metadata import example"""

    def __init__(self, processor_def):
        """
        Initialize object

        :param processor_def: provider definition

        :returns: pygeometa.pygeoapi_plugin.PygeometaMetadataImportProcessor
        """

        super().__init__(processor_def, PROCESS_METADATA_IMPORT)

    def execute(self, data):

        response = None
        mimetype = 'application/json'
        metadata = data.get('metadata')
        schema = data.get('schema')

        if None in [metadata, schema]:
            msg = 'Missing metadata or schema'
            LOGGER.error(msg)
            raise ProcessorExecuteError(msg)

        try:
            LOGGER.info(f'Importing metadata into {schema}')
            schema_object = load_schema(schema)
            response = schema_object.import_(metadata)
        except NotImplementedError:
            msg = f'Import not supported for {schema}'
            response = msg
            raise ProcessorExecuteError(msg)
        except Exception as err:
            msg = f'Invalid metadata: {err}'
            response = msg

        outputs = {
            'id': 'import-report',
            'value': response
        }

        return mimetype, outputs

    def __repr__(self):
        return '<PygeometaMetadataImportProcessor>'


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


class PygeometaMetadataTransformProcessor(BaseProcessor):
    """pygeometa metadata transform example"""

    def __init__(self, processor_def):
        """
        Initialize object

        :param processor_def: provider definition

        :returns: pygeometa.pygeoapi_plugin.PygeometaMetadataGenerateProcessor
        """

        super().__init__(processor_def, PROCESS_METADATA_TRANSFORM)

    def execute(self, data):

        content = None
        response = None
        mimetype = 'application/json'
        metadata = data.get('metadata')
        input_schema = data.get('input-schema')
        output_schema = data.get('output-schema')

        if None in [metadata, input_schema, output_schema]:
            msg = 'Missing metadata or input-schema or output-schema'
            LOGGER.error(msg)
            raise ProcessorExecuteError(msg)

        try:
            LOGGER.info(f'Importing {metadata} into {input_schema}')
            schema_object_input = load_schema(input_schema)
            content = schema_object_input.import_(metadata)
        except NotImplementedError:
            msg = f'Import not supported for {input_schema}'
            LOGGER.error(msg)
            raise ProcessorExecuteError(msg)

        schema_object_output = load_schema(output_schema)

        if schema_object_output.outputformat == 'json':
            stringify = False
        else:
            mimetype = 'application/xml'
            stringify = True

        response = schema_object_output.write(content, stringify=stringify)

        return mimetype, response

    def __repr__(self):
        return '<PygeometaMetadataGenerateProcessor>'
