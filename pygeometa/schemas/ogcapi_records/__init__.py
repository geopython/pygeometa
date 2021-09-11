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

        lang1 = mcf['metadata'].get('language')
        lang2 = mcf['metadata'].get('language_alternate')

        minx, miny, maxx, maxy = (mcf['identification']['extents']
                                  ['spatial'][0]['bbox'])

        title = get_charstring(mcf['identification'].get('title'),
                               lang1, lang2)

        description = get_charstring(mcf['identification'].get('abstract'),
                                     lang1, lang2)

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
                }
            },
            'properties': {
                'externalId': [mcf['metadata']['identifier']],
                'title': title[0],
                'description': description[0],
                'themes': [],
                'language': lang1,
                'type': mcf['metadata']['hierarchylevel'],
                'extents': {
                    'spatial': {
                        'bbox': [minx, miny, maxx, maxy],
                        'crs': 'http://www.opengis.net/def/crs/OGC/1.3/CRS84'  # noqa
                    }
                }
            },
            'associations': [],
            'links': []
        }

        if 'temporal' in mcf['identification']['extents']:
            begin = mcf['identification']['extents']['temporal'][0]['begin']
            end = mcf['identification']['extents']['temporal'][0]['end']

            if end == 'now':
                end = None

            temporal = {
                'interval': [begin, end],
                'trs': 'http://www.opengis.net/def/uom/ISO-8601/0/Gregorian'  # noqa
            }

            mcf['identification']['extents']['temporal'] = temporal

        if 'creation' in mcf['identification']['dates']:
            record['properties']['created'] = mcf['identification']['dates']['creation']  # noqa
        if 'revision' in mcf['identification']['dates']:
            record['properties']['updated'] = mcf['identification']['dates']['revision']  # noqa

        organization = get_charstring(mcf['contact']['main'].get('organization'),  # noqa
                                      lang1, lang2)

        record['properties']['publisher'] = organization[0]

        rights = get_charstring(mcf['identification'].get('rights'),
                                lang1, lang2)

        record['properties']['rights'] = rights[0]

        formats = []
        for v in mcf['distribution'].values():
            format_ = get_charstring(v.get('format'), lang1, lang2)
            if format_[0] is not None:
                formats.append(format_)

        if formats:
            record['properties']['formats'] = list(
                set([f[0] for f in formats]))

        record['properties']['contactPoint'] = self.generate_responsible_party(
            mcf['contact']['main'], lang1, lang2, 'pointOfContact')

        if 'distribution' in mcf['contact']:
            record['properties']['publisher'] = self.generate_responsible_party(  # noqa
                mcf['contact']['distribution'], lang1, lang2, 'distributor')

        for value in mcf['identification']['keywords'].values():
            theme = {'concepts': []}

            keywords = get_charstring(value.get('keywords'), lang1, lang2)

            for kw in keywords[0]:
                theme['concepts'].append(kw)

            if 'vocabulary' in value:
                if 'url' in value['vocabulary']:
                    theme['scheme'] = value['vocabulary']['url']
                elif 'name' in value['vocabulary']:
                    theme['scheme'] = value['vocabulary']['name']

            record['properties']['themes'].append(theme)

        for value in mcf['distribution'].values():
            title = get_charstring(value.get('title'), lang1, lang2)

            name = get_charstring(value.get('name'), lang1, lang2)

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

    def generate_responsible_party(self, contact: dict,
                                   lang1: str, lang2: str, role: str) -> dict:
        """
        generate responsibly party construct from MCF contact

        :param contact: dict of MCF contact
        :param lang1: primary language
        :param lang2: alternate language
        :param role: role of contact

        :returns: MCF contact as a responsible party representation
        """

        organization_name = get_charstring(contact.get('organization'),
                                           lang1, lang2)

        position_name = get_charstring(contact.get('positionname'),
                                       lang1, lang2)

        hours_of_service = get_charstring(contact.get('hoursofservice'),
                                          lang1, lang2)

        contact_instructions = get_charstring(
            contact.get('contactinstructions'), lang1, lang2)

        address = get_charstring(contact.get('address'), lang1, lang2)
        city = get_charstring(contact.get('city'), lang1, lang2)
        administrative_area = get_charstring(contact.get('administrativearea'),
                                             lang1, lang2)
        postalcode = get_charstring(contact.get('postalcode'), lang1, lang2)
        country = get_charstring(contact.get('country'), lang1, lang2)

        return {
            'individualName': contact['individualname'],
            'organizationName': organization_name[0],
            'positionName': position_name[0],
            'contactInfo': {
                'phone': {
                    'office': contact['phone']
                },
                'email': {
                    'office': contact['fax']
                },
                'address': {
                    'office': {
                        'deliveryPoint': address[0],
                        'city': city,
                        'administrativeArea': administrative_area[0],
                        'postalCode': postalcode[0],
                        'country': country[0]
                    },
                    'onlineResource': {
                        'href': contact['url']
                    },
                },
                'hoursOfService': hours_of_service[0],
                'contactInstructions': contact_instructions[0]
            },
            'role': {
                'name': role
            }
        }
