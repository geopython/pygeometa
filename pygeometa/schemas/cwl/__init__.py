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
# Copyright (c) 2025 Tom Kralidis
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

import datetime
import logging
import os
from typing import Union

import yaml

from pygeometa.schemas.base import BaseOutputSchema

THISDIR = os.path.dirname(os.path.realpath(__file__))

LOGGER = logging.getLogger(__name__)


class CWLOutputSchema(BaseOutputSchema):
    """Common Workflow Language v1.2 schema"""

    def __init__(self):
        """
        Initialize object

        :returns: pygeometa.schemas.cwl.CWLOutputSchema
        """

        description = 'Common Workflow Language v1.2'

        super().__init__('cwl', description, 'yaml', THISDIR)

    def import_(self, metadata: str) -> dict:

        metadata = yaml.safe_load(metadata)

        mcf = {
            'mcf': {
                'version': '1.0'
            },
            'metadata': {
                'language': 'eng',
                'charset': 'utf8'
            },
            'spatial': {
                'datatype': 'grid',
                'geomtype': 'solid'
            },
            'identification': {
                'charset': 'utf8',
                'language': 'missing',
                'keywords': {},
                'dates': {},
                'status': 'onGoing',
                'maintenancefrequency': 'continual'
            },
            'contact': {
              'pointOfContact': {},
              'distributor': {},
              'author': {}
            },
            'distribution': {},
            'dataquality': {
                'lineage': {}
            }
        }

        now = datetime.datetime.now(datetime.UTC)

        wf = list(filter(lambda x: x['class'] == 'Workflow', metadata.get('$graph')))[0]  # noqa

        mcf['metadata']['identifier'] = wf['id']
        mcf['metadata']['hierarchylevel'] = 'application'
        mcf['metadata']['datestamp'] = now
        mcf['identification']['title'] = wf['label']
        mcf['identification']['abstract'] = wf['doc']

        mcf['identification']['keywords']['default'] = {
            'keywords': [f'softwareVersion:{metadata["s:softwareVersion"]}', 'application', 'CWL'],  # noqa
            'keywords_type': 'theme'
        }

        if 's:keywords' in metadata:
            mcf['identification']['keywords']['default']['keywords'].extend(
                metadata['s:keywords'].split(',')
            )

        mcf['dataquality']['scope'] = {'level': 'application'}

        if 's:releaseNotes' in metadata:
            mcf['dataquality']['lineage']['statement'] = metadata['s:releaseNotes']  # noqa
            mcf['distribution']['releaseNotes'] = {
                'rel': 'related',
                'url': metadata['s:releaseNotes'],
                'type': 'text/html',
                'name': 'releaseNotes',
                'description': 'release notes'
            }

        if 's:version' in metadata:
            mcf['identification']['edition'] = metadata['s:version']

        if 's:author' in metadata:
            mcf['contact']['author'] = {
                'individualname': metadata['s:author'][0]['s:name'],
                'organization': metadata['s:author'][0]['s:affiliation'],
                'email': metadata['s:author'][0]['s:email'],
            }

        if 's:contributor' in metadata:
            mcf['contact']['pointOfContact'] = {
                'individualname': metadata['s:contributor'][0]['s:name'],
                'organization': metadata['s:contributor'][0]['s:affiliation'],
                'email': metadata['s:contributor'][0]['s:email'],
            }

        if 's:dateCreated' in metadata:
            mcf['identification']['dates'] = {
                'creation': metadata['s:dateCreated']
            }

        if 's:citation' in metadata:
            mcf['distribution']['citation'] = {
                'rel': 'cite-as',
                'url': metadata['s:citation'],
                'type': 'text/html',
                'name': 'citation',
                'description': 'citation'
            }

        if 's:codeRepository' in metadata:
            mcf['distribution']['codeRepository'] = {
                'rel': 'working-copy-of',
                'url': metadata['s:codeRepository'],
                'type': 'text/html',
                'name': 'codeRepository',
                'description': 'code repository'
            }

        if 's:license' in metadata:
            mcf['distribution']['license'] = {
                'rel': 'license',
                'url': metadata['s:license'],
                'type': 'text/html',
                'name': 'license',
                'description': 'license'
            }

        if 's:logo' in metadata:
            mcf['distribution']['logo'] = {
                'rel': 'icon',
                'url': metadata['s:logo'],
                'type': 'text/html',
                'name': 'logo',
                'description': 'logo'
            }

        mcf['identification']['extents'] = {
            'spatial': [{
                'bbox': [-180, -90, 180, 90],
                'crs': 4326
            }]
        }

        LOGGER.info(f'MCF: {mcf}')

        return mcf

    def write(self, mcf: dict, stringify: str = True) -> Union[dict, str]:
        raise NotImplementedError()
