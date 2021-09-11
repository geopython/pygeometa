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

import json
import os

from pygeometa.core import get_charstring
from pygeometa.helpers import json_serial
from pygeometa.schemas.base import BaseOutputSchema

THISDIR = os.path.dirname(os.path.realpath(__file__))


class STACItemOutputSchema(BaseOutputSchema):
    """STAC Item output schema"""

    def __init__(self):
        """
        Initialize object

        :returns: pygeometa.schemas.base.BaseOutputSchema
        """

        super().__init__('stac-item', 'json', THISDIR)

    def write(self, mcf: dict) -> str:
        """
        Write outputschema to JSON string buffer

        :param mcf: dict of MCF content model

        :returns: MCF as a STAC item representation
        """

        lang1 = mcf['metadata'].get('language')
        lang2 = mcf['metadata'].get('language_alternate')

        minx, miny, maxx, maxy = (mcf['identification']['extents']
                                  ['spatial'][0]['bbox'])

        title = get_charstring(mcf['identification'].get('title'),
                               lang1, lang2)
        description = get_charstring(mcf['identification'].get('abstract'),
                                     lang1, lang2)

        stac_item = {
            'stac-version': '1.0.0-beta.2',
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
            'properties': {
                'title': title[0],
                'description': description[0]
            },
            'links': []
        }

        if 'temporal' in mcf['identification']['extents']:
            begin = mcf['identification']['extents']['temporal'][0]['begin']
            end = mcf['identification']['extents']['temporal'][0]['end']

            stac_item['properties']['start_datetime'] = begin
            stac_item['properties']['end_datetime'] = end

        if 'creation' in mcf['identification']['dates']:
            stac_item['properties']['created'] = mcf['identification']['dates']['creation']  # noqa
        if 'revision' in mcf['identification']['dates']:
            stac_item['properties']['updated'] = mcf['identification']['dates']['revision']  # noqa

        stac_item['properties']['provider'] = {'name': mcf['contact']['main']['organization']}  # noqa

        for value in mcf['distribution'].values():
            title = get_charstring(value.get('title'), lang1, lang2)
            link = {
                'rel': value['function'],
                'title': title,
                'href': value['url']
            }
            stac_item['links'].append(link)

        return json.dumps(stac_item, default=json_serial, indent=4)
