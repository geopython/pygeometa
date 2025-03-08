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

from datetime import date, datetime
import json
import logging
import os
from typing import Union

from pygeometa.core import get_charstring
from pygeometa.helpers import json_dumps
from pygeometa.schemas.base import BaseOutputSchema

THISDIR = os.path.dirname(os.path.realpath(__file__))

LOGGER = logging.getLogger(__name__)

TYPES = {
    'Series': 'series',
    'SoftwareApplication': 'software',
    'ProductModel': 'model',
    'Dataset': 'dataset',
    'WebAPI': 'service',
    'Property': 'attribute',
    'ListItem': 'feature'
}


class SchemaOrgOutputSchema(BaseOutputSchema):
    """Schema.org schema"""

    def __init__(self):
        """
        Initialize object

        :returns: pygeometa.schemas.base.BaseOutputSchema
        """

        description = 'Schema.org'

        super().__init__('schema-org', description, 'json', THISDIR)

    def import_(self, metadata: str) -> dict:
        """
        Import metadata into MCF

        :param metadata: string of metadata content

        :returns: `dict` of MCF content
        """

        md = json.loads(metadata)

        mcf = {
            'mcf': {
                'version': '1.0',
            },
            'metadata': {},
            'identification': {
                'extents': {
                    'spatial': []
                }
            },
            'contact': {},
            'distribution': {}
        }

        mcf['metadata']['identifier'] = md['identifier']
        mcf['metadata']['charset'] = 'utf-8'
        mcf['metadata']['type'] = TYPES[md.get('type', 'Dataset')]
        mcf['metadata']['language'] = md.get('inLanguage', 'en')

        if 'spatialCoverage' in md or 'spatial' in md:
            crs = 4326
            geo = md['spatialCoverage']['geo']
            if geo['@type'] == 'GeoCoordinates':
                mcf['spatial']['datatype'] = 'vector'
                mcf['spatial']['geomtype'] = 'point'
                bbox = [geo['longitude'], geo['latitude'],
                        geo['longitude'], geo['latitude']]
            elif geo['@type'] == 'GeoShape':
                mcf['spatial']['datatype'] = 'vector'
                mcf['spatial']['geomtype'] = 'polygon'
                bbox = geo['box'].split()

            mcf['identification']['extents']['spatial'].append({
                'bbox': bbox,
                'crs': crs
            })

        if 'temporalCoverage' in md:
            begin, end = md['temporalCoverage'].split('/')
            mcf['identification']['extents']['temporal'] = [{
                'begin': begin,
                'end': end
            }]

        mcf['identification']['language'] = mcf['metadata']['language']
        mcf['identification']['title'] = md['name']
        mcf['identification']['abstract'] = md['description']

        if 'dateCreated' in md:
            mcf['metadata']['identification']['creation'] = md['datePublished']
        if 'datePublished' in md:
            mcf['metadata']['identification']['publication'] = md['datePublished']  # noqa
        if 'dateModified' in md:
            mcf['metadata']['identification']['revision'] = md['dateModified']

        if 'version' in md:
            mcf['metadata']['identification']['edition'] = md['version']

        mcf['identification']['keywords'] = {
            'default': {
                'keywords': md['keywords']
            }
        }

        for dist in md['distribution']:
            mcf['distribution'][dist['name']] = {
                'name': dist['name'],
                'type': dist['encodingFormat'],
                'url': dist['contentUrl'],
                'rel': 'download',
                'function': 'download'
            }

        for ct in ['author', 'publisher', 'creator', 'provider', 'funder']:
            if ct in md:
                contact = {}
                contact['url'] = md[ct]['url']
                contact['individualname'] = md[ct]['name']
                if md[ct]['@type'] == 'Organization':
                    contact['organization'] = md[ct]['name']

                if 'address' in md[ct]:
                    contact['address'] = md[ct]['streetAddress']
                    contact['city'] = md[ct]['addressLocality']
                    contact['administrativearea'] = md[ct]['addressRegion']
                    contact['postalcode'] = md[ct]['postalCode']
                    contact['country'] = md[ct]['addressCountry']

                if 'contactPoint' in md[ct]:
                    cp = md[ct][0]
                    contact['email'] = cp['email']
                    contact['fax'] = cp['fax']

                mcf['contact'][ct] = contact

        return mcf

    def write(self, mcf: dict, stringify: str = True) -> Union[dict, str]:
        """
        Write outputschema to JSON string buffer

        :param mcf: dict of MCF content model
        :param stringify: whether to return a string representation (default)
                          else native (dict, etree)


        :returns: `dict` or `str` of MCF as an OARec record representation
        """

        self.lang1 = mcf['metadata'].get('language')
        self.lang2 = mcf['metadata'].get('language_alternate')

        minx, miny, maxx, maxy = (mcf['identification']['extents']
                                  ['spatial'][0]['bbox'])

        title = get_charstring(mcf['identification'].get('title'),
                               self.lang1, self.lang2)

        description = get_charstring(mcf['identification'].get('abstract'),
                                     self.lang1, self.lang2)

        LOGGER.debug('Generating baseline record')
        record = {
            'id': mcf['metadata']['identifier'],
            'conformsTo': [
                'http://www.opengis.net/spec/ogcapi-records-1/1.0/conf/record-core',  # noqa
            ],
            'type': 'Feature',
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
                'description': description[0],
                'themes': [],
                'type': mcf['metadata']['hierarchylevel'],
            },
            'links': []
        }

        if self.lang1 is not None:
            record['properties']['language'] = {
                'code': self.lang1
            }

        LOGGER.debug('Checking for temporal')
        try:
            begin = mcf['identification']['extents']['temporal'][0]['begin']
            end = mcf['identification']['extents']['temporal'][0].get('end')

            if begin in ['now', 'None', None]:
                begin = '..'
            else:
                begin = str(begin)

            if end in ['now', 'None', None]:
                end = '..'
            else:
                end = str(end)

            if [begin, end] == [None, None]:
                record['time'] = None
            elif [begin, end] == ['..', '..']:
                pass
            else:
                record['time'] = {
                    'interval': [begin, end]
                }

            if 'resolution' in  mcf['identification']['extents']['temporal'][0]:  # noqa
                record['time']['resolution'] =  mcf['identification']['extents']['temporal'][0]['resolution']  # noqa

        except (IndexError, KeyError):
            record['time'] = None

        LOGGER.debug('Checking for dates')

        if 'dates' in mcf['identification']:
            if 'creation' in mcf['identification']['dates']:
                record['properties']['created'] = self.generate_date(mcf['identification']['dates']['creation'])  # noqa

            if 'revision' in mcf['identification']['dates']:
                record['properties']['updated'] = self.generate_date(mcf['identification']['dates']['revision'])  # noqa

        rights = get_charstring(mcf['identification'].get('rights'),
                                self.lang1, self.lang2)

        if rights != [None, None]:
            record['properties']['rights'] = rights[0]

        formats = []
        for v in mcf['distribution'].values():
            format_ = get_charstring(v.get('format'), self.lang1, self.lang2)
            if format_[0] is not None:
                formats.append(format_[0])

        LOGGER.debug('Checking for formats')
        if formats:
            formats2 = set(formats)
            record['properties']['formats'] = [{'name': f} for f in formats2]

        LOGGER.debug('Checking for contacts')
        record['properties']['contacts'] = self.generate_contacts(
            mcf['contact'])

        all_keywords = []

        LOGGER.debug('Checking for keywords')
        for key, value in mcf['identification']['keywords'].items():
            theme = {'concepts': []}
            scheme = None

            keywords = get_charstring(value.get('keywords'), self.lang1,
                                      self.lang2)

            if 'vocabulary' in value:
                if 'url' in value['vocabulary']:
                    scheme = value['vocabulary']['url']
                elif 'name' in value['vocabulary']:
                    scheme = value['vocabulary']['name']

            if scheme is None:
                LOGGER.debug('Keywords found without vocabulary')
                LOGGER.debug('Aggregating as bare keywords')
                all_keywords.extend(keywords[0])
            else:
                LOGGER.debug('Adding as theme/concepts')
                for kw in keywords[0]:
                    theme['concepts'].append({'id': kw})

                theme['scheme'] = scheme

                record['properties']['themes'].append(theme)

        if all_keywords:
            record['properties']['keywords'] = all_keywords

        if not record['properties']['themes']:
            _ = record['properties'].pop('themes', None)

        LOGGER.debug('Checking for licensing')
        if mcf['identification'].get('license') is not None:
            license = mcf['identification']['license']

            if 'url' in license:
                LOGGER.debug('Encoding license as link')
                license_link = {
                    'rel': 'license',
                    'type': 'text/html',
                    'title': license.get('name', 'license for this resource'),
                    'url': license['url']
                }
                record['links'].append(self.generate_link(license_link))
            else:
                LOGGER.debug('Encoding license as property')
                record['properties']['license'] = license['name']

        LOGGER.debug('Checking for distribution')
        for value in mcf['distribution'].values():
            record['links'].append(self.generate_link(value))

        if stringify:
            return json_dumps(record)

        return record

    def generate_party(self, contact: dict,
                       lang1: str, lang2: str, roles: list) -> dict:
        """
        generate party construct from MCF contact

        :param contact: dict of MCF contact
        :param self.lang1: primary language
        :param self.lang2: alternate language
        :param roles: roles of contact

        :returns: MCF contact as a party representation
        """

        organization_name = get_charstring(contact.get('organization'),
                                           self.lang1, self.lang2)

        individual_name = get_charstring(contact.get('individualname'),
                                         self.lang1, self.lang2)

        position_name = get_charstring(contact.get('positionname'),
                                       self.lang1, self.lang2)

        hours_of_service = get_charstring(contact.get('hoursofservice'),
                                          self.lang1, self.lang2)

        contact_instructions = get_charstring(
            contact.get('contactinstructions'), self.lang1, self.lang2)

        address = get_charstring(contact.get('address'),
                                 self.lang1, self.lang2)

        city = get_charstring(contact.get('city'), self.lang1, self.lang2)

        administrative_area = get_charstring(contact.get('administrativearea'),
                                             self.lang1, self.lang2)

        postalcode = get_charstring(contact.get('postalcode'),
                                    self.lang1, self.lang2)

        country = get_charstring(contact.get('country'),
                                 self.lang1, self.lang2)

        rp = {
            'addresses': [{}],
            'roles': []
        }

        if organization_name[0] is not None:
            rp['organization'] = organization_name[0]
        if individual_name[0] is not None:
            rp['name'] = individual_name[0]
        if position_name[0] is not None:
            rp['position'] = position_name[0]
        if hours_of_service[0] is not None:
            rp['hoursOfService'] = hours_of_service[0]
        if contact_instructions[0] is not None:
            rp['contactInstructions'] = contact_instructions[0]

        if address[0] is not None:
            rp['addresses'][0]['deliveryPoint'] = [address[0]]
        if city[0] is not None:
            rp['addresses'][0]['city'] = city[0]
        if administrative_area[0] is not None:
            rp['addresses'][0]['administrativeArea'] = administrative_area[0]
        if postalcode[0] is not None:
            rp['addresses'][0]['postalCode'] = postalcode[0]
        if country[0] is not None:
            rp['addresses'][0]['country'] = country[0]

        if contact.get('phone') is not None:
            LOGGER.debug('Formatting phone number')
            phone = contact['phone']
            phone = phone.replace('-', '').replace('(', '').replace(')', '')
            phone = phone.replace('+0', '+').replace(' ', '')

            rp['phones'] = [{'value': phone}]

        if contact.get('email') is not None:
            rp['emails'] = [{'value': contact.get('email')}]

        if rp['addresses'][0] == {}:
            rp.pop('addresses')

        for r in set(roles):
            rp['roles'].append(r)

        if 'url' in contact:
            rp['links'] = [{
                'rel': 'canonical',
                'type': 'text/html',
                'href': contact['url']
            }]

        return rp

    def generate_contacts(self, contact: dict) -> list:
        """
        Generates 1..n contacts, streamlining identical
        contacts with multiple roles

        :param contact: `dict` of contacts

        :returns: `list` of contacts
        """

        contacts = []
        contacts2 = []

        for key, value in contact.items():
            if contacts:
                for c in contacts:
                    if value == c['contact']:
                        LOGGER.debug('Found matching contact; adding role')
                        c['roles'].append(key)
                    else:
                        LOGGER.debug('Adding contact')
                        contacts.append({
                            'contact': value,
                            'roles': [key]
                        })
            else:
                contacts.append({
                    'contact': value,
                    'roles': [key]
                })

        LOGGER.debug(f'Contacts: {contacts}')
        for c in contacts:
            contacts2.append(self.generate_party(c['contact'], self.lang1,
                             self.lang2, c['roles']))

        return contacts2

    def generate_link(self, distribution: dict) -> dict:
        """
        Generates OARec link object from MCF distribution object

        :param distribution: `dict` of MCF distribution

        :returns: OARec link object
        """

        title = get_charstring(distribution.get('title'),
                               self.lang1, self.lang2)

        name = get_charstring(distribution.get('name'), self.lang1, self.lang2)

        link = {
            'href': distribution['url']
        }

        if distribution.get('type') is not None:
            link['type'] = distribution['type']

        reltype = distribution.get('rel') or distribution.get('function')
        if reltype is not None:
            link['rel'] = reltype

        if title != [None, None]:
            link['title'] = title[0]
        elif name != [None, None]:
            link['title'] = name[0]

        if all(x in distribution['url'] for x in ['{', '}']):
            link['templated'] = True

        if 'channel' in distribution:
            link['channel'] = distribution['channel']

        return link

    def generate_date(self, date_value: str) -> str:
        """
        Helper function to derive RFC3339 date from MCF date type

        :param date_value: `str` of date value

        :returns: `str` of date-time value
        """

        value = None

        if isinstance(date_value, str) and date_value != 'None':
            if len(date_value) == 10:  # YYYY-MM-DD
                format_ = '%Y-%m-%d'
            elif len(date_value) == 7:  # YYYY-MM
                format_ = '%Y-%m'
            elif len(date_value) == 4:  # YYYY
                format_ = '%Y'
            elif len(date_value) == 19:  # YYYY-MM-DDTHH:MM:SS
                msg = 'YYYY-MM-DDTHH:MM:SS with no timezone; converting to UTC'
                LOGGER.debug(msg)
                format_ = '%Y-%m-%dT%H:%M:%S'

            LOGGER.debug('date type found; expanding to date-time')
            value = datetime.strptime(date_value, format_).strftime('%Y-%m-%dT%H:%M:%SZ')  # noqa

        elif isinstance(date_value, int) and len(str(date_value)) == 4:
            date_value2 = str(date_value)
            LOGGER.debug('date type found; expanding to date-time')
            format_ = '%Y'
            value = datetime.strptime(date_value2, format_).strftime('%Y-%m-%dT%H:%M:%SZ')  # noqa

        elif isinstance(date_value, (date, datetime)):
            value = date_value.strftime('%Y-%m-%dT%H:%M:%SZ')

        elif date_value in [None, 'None']:
            value = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')

        else:
            msg = f'Unknown date string: {date_value}'
            raise RuntimeError(msg)

        return value
