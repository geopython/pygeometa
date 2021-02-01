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
# Copyright (c) 2021 Tom Kralidis
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

import json
import os

from pygeometa.core import get_charstring
from pygeometa.helpers import json_serial
from pygeometa.schemas.base import BaseOutputSchema

THISDIR = os.path.dirname(os.path.realpath(__file__))


class OGCAPIRecordOutputSchema(BaseOutputSchema):
    """OGC API - Records - Part 1: Core record schema"""

    def __init__(self):
        """
        Initialize object

        :returns: pygeometa.schemas.base.BaseOutputSchema
        """

        super().__init__('oarec-record', 'json', THISDIR)

    def write(self, mcf: dict, stringify: str = True) -> str:
        """
        Write outputschema to JSON string buffer

        :param mcf: dict of MCF content model
        :param stringify: whether to return a string representation (default)
                          else native (dict, etree)


        :returns: MCF as a STAC item representation
        """

        minx, miny, maxx, maxy = (mcf['identification']['extents']
                                  ['spatial'][0]['bbox'])

        title = get_charstring('title', mcf['identification'],
                               mcf['metadata']['language'],
                               mcf['metadata']['language_alternate'])
        description = get_charstring('abstract', mcf['identification'],
                                     mcf['metadata']['language'],
                                     mcf['metadata']['language_alternate'])

        begin = mcf['identification']['extents']['temporal'][0]['begin']
        end = mcf['identification']['extents']['temporal'][0]['end']

        if end == 'now':
            end = None

        record = {
            'id': mcf['metadata']['identifier'],
            'type': 'Feature',
            'bbox': [minx, miny, maxx, maxy],
            'geometry': {
                'type': 'Polygon',
                'coordinates': [[
                    [minx, miny],
                    [minx, maxy],
                    [maxx, maxy],
                    [maxx, miny],
                    [minx, miny]
                ]]
            },
            'extents': {
                'spatial': {
                    'bbox': [minx, miny, maxx, maxy],
                    'crs': 'http://www.opengis.net/def/crs/OGC/1.3/CRS84'  # noqa
                },
                'temporal': {
                    'interval': [begin, end],
                    'trs': 'http://www.opengis.net/def/uom/ISO-8601/0/Gregorian'  # noqa
                }
            },
            'properties': {
                'externalId': mcf['metadata']['identifier'],
                'title': title[0],
                'description': description[0],
                'themes': [],
                'language': mcf['metadata']['language'],
                'type': mcf['metadata']['hierarchylevel'],
            },
            'associations': [],
            'links': []
        }

        if 'creation' in mcf['identification']['dates']:
            record['properties']['created'] = mcf['identification']['dates']['creation']  # noqa
        if 'revision' in mcf['identification']['dates']:
            record['properties']['updated'] = mcf['identification']['dates']['revision']  # noqa

        organization = get_charstring('organization', mcf['contact']['main'],
                                      mcf['metadata']['language'],
                                      mcf['metadata']['language_alternate'])

        record['properties']['publisher'] = organization[0]

        rights = get_charstring('rights', mcf['identification'],
                                mcf['metadata']['language'],
                                mcf['metadata']['language_alternate'])

        record['properties']['rights'] = rights[0]

        formats = []
        for v in mcf['distribution'].values():
            format_ = get_charstring('format', v,
                                     mcf['metadata']['language'],
                                     mcf['metadata']['language_alternate'])
            if format_[0] is not None:
                formats.append(format_)

        if formats:
            record['properties']['formats'] = list(
                set([f[0] for f in formats]))

        record['properties']['contactPoint'] = mcf['contact']['main']['url']

        for value in mcf['identification']['keywords'].values():
            theme = {'concepts': []}

            keywords = get_charstring('keywords', value,
                                      mcf['metadata']['language'],
                                      mcf['metadata']['language_alternate'])

            for kw in keywords[0]:
                theme['concepts'].append(kw)

            if 'vocabulary' in value:
                if 'url' in value['vocabulary']:
                    theme['scheme'] = value['vocabulary']['url']
                elif 'name' in value['vocabulary']:
                    theme['scheme'] = value['vocabulary']['name']

            record['properties']['themes'].append(theme)

        for value in mcf['distribution'].values():
            title = get_charstring('title', value,
                                   mcf['metadata']['language'],
                                   mcf['metadata']['language_alternate'])

            name = get_charstring('name', value,
                                  mcf['metadata']['language'],
                                  mcf['metadata']['language_alternate'])

            link = {
                'rel': value['function'],
                'href': value['url'],
                'type': value['type']
            }
            if title != [None, None]:
                link['title'] = name[0]
            elif name != [None, None]:
                link['title'] = name[0]

            if all(x in value['url'] for x in ['{', '}']):
                link['templated'] = True

            record['associations'].append(link)

        return json.dumps(record, default=json_serial, indent=4)
