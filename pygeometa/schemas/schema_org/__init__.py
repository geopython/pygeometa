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

import json
import logging
import os
from typing import Union

from pygeometa.core import get_charstring
from pygeometa.helpers import generate_datetime, json_dumps
from pygeometa.schemas.base import BaseOutputSchema

THISDIR = os.path.dirname(os.path.realpath(__file__))

LOGGER = logging.getLogger(__name__)

CONTACTS = [
    'accountablePerson',
    'author',
    'contributor',
    'copyrightHolder',
    'creator',
    'editor',
    'funder',
    'maintainer',
    'producer',
    'provider',
    'publisher',
    'sponsor'
]

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
            'spatial': {},
            'metadata': {},
            'identification': {
                'extents': {
                    'spatial': []
                }
            },
            'contact': {},
            'distribution': {}
        }

        id_ = md.get('identifier', md.get('@id'))
        mcf['metadata']['identifier'] = id_
        mcf['metadata']['charset'] = 'utf-8'
        mcf['metadata']['type'] = TYPES[md.get('type', 'Dataset')]
        mcf['metadata']['language'] = md.get('inLanguage', 'en')

        if 'spatialCoverage' in md or 'spatial' in md:
            sc = _get_list_or_dict(md['spatialCoverage'])
            crs = 4326

            geo = _get_list_or_dict(sc['geo'])

            if geo['@type'] == 'GeoCoordinates':
                mcf['spatial']['datatype'] = 'vector'
                mcf['spatial']['geomtype'] = 'point'
                bbox = [geo['longitude'], geo['latitude'],
                        geo['longitude'], geo['latitude']]
            elif geo['@type'] == 'GeoShape':
                mcf['spatial']['datatype'] = 'vector'
                mcf['spatial']['geomtype'] = 'polygon'
                bt = geo['box'].split()
                bbox = bt[1], bt[0], bt[3], bt[2]
            else:
                bbox = [-180, -90, 180, 90]

            mcf['identification']['extents']['spatial'].append({
                'bbox': bbox,
                'crs': crs
            })

        if 'temporalCoverage' in md:
            begin, end = md['temporalCoverage'][0].split('/')
            mcf['identification']['extents']['temporal'] = [{
                'begin': begin,
                'end': end
            }]

        mcf['identification']['language'] = mcf['metadata']['language']
        mcf['identification']['title'] = md['name']
        mcf['identification']['abstract'] = md['description']

        if 'dateCreated' in md:
            mcf['identification']['creation'] = md['datePublished']
        if 'datePublished' in md:
            mcf['identification']['publication'] = md['datePublished']  # noqa
        if 'dateModified' in md:
            mcf['identification']['revision'] = md['dateModified']

        if 'version' in md:
            mcf['identification']['edition'] = md['version']

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

                ct2 = _get_list_or_dict(md[ct])

                if ct2:
                    contact['individualname'] = ct2['name']

                    if 'url' in ct2:
                        contact['url'] = ct2['url']

                    if ct2['@type'] == 'Organization':
                        contact['organization'] = ct2['name']

                    if 'address' in ct2:
                        contact['address'] = ct2['address']['streetAddress']
                        contact['city'] = ct2['address']['addressLocality']
                        contact['administrativearea'] = ct2['address']['addressRegion']  # noqa
                        contact['postalcode'] = ct2['address']['postalCode']
                        contact['country'] = ct2['address']['addressCountry']

                    if 'contactPoint' in ct2:
                        cp = _get_list_or_dict(ct2['contactPoint'])
                        contact['email'] = cp.get('email')
                        contact['fax'] = cp.get('fax')

                    mcf['contact'][ct] = contact

        return mcf

    def write(self, mcf: dict, stringify: str = True) -> Union[dict, str]:
        """
        Write outputschema to JSON string buffer

        :param mcf: dict of MCF content model
        :param stringify: whether to return a string representation (default)
                          else native (dict, etree)

        :returns: `dict` or `str` of MCF as Schema.org
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
            'identifier': mcf['metadata']['identifier'],
            "@context": "http://schema.org/",
            '@type': 'schema:' + dict(zip(TYPES.values(), TYPES.keys()))[mcf['metadata']['hierarchylevel']],  # noqa
            'spatialCoverage': [{
                '@type': 'schema:Place',
                'geo': {
                    '@type': 'schema:GeoShape',
                    'box': f'{miny} {minx} {maxy} {maxx}'
                }
            }],
            'name': title[0],
            'description': description[0],
            'distribution': []
        }

        if self.lang1 is not None:
            record['inLanguage'] = self.lang1

        LOGGER.debug('Checking for temporal')
        try:
            begin = mcf['identification']['extents']['temporal'][0].get('begin')  # noqa
            end = mcf['identification']['extents']['temporal'][0].get('end')  # noqa

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
                record['temporalCoverage'] = [f'{begin}/{end}']
        except (IndexError, KeyError):
            pass

        LOGGER.debug('Checking for dates')

        for key, value in mcf['identification']['dates'].items():
            if key == 'creation':
                record['dateCreated'] = generate_datetime(value)
            elif key == 'revision':
                record['dateModified'] = generate_datetime(value)
            elif key == 'publication':
                record['datePublished'] = generate_datetime(value)

        LOGGER.debug('Checking for contacts')

        for ct in CONTACTS:
            contacts = self.generate_contacts(mcf['contact'], ct)
            if contacts and len(contacts) > 0:
                record[ct] = contacts

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

        if all_keywords:
            record['keywords'] = all_keywords

        LOGGER.debug('Checking for licensing')
        if mcf['identification'].get('license') is not None:
            license = mcf['identification']['license']

            if 'url' in license:
                LOGGER.debug('Encoding license as link')
                record['license'] = license['url']
            else:
                LOGGER.debug('Encoding license as property')
                record['license'] = license['name']

        LOGGER.debug('Checking for distribution')
        for value in mcf['distribution'].values():
            record['distribution'].append(self.generate_link(value))

        LOGGER.debug('Checking for content_info')
        if mcf.get('content_info', {}):
            ci = mcf['content_info']
            if ci.get('attributes', {}):
                record['variableMeasured'] = self.generate_variables(ci['attributes']) # noqa
            if ci.get('dimensions', {}):
                record['variableMeasured'] = self.generate_variables(ci['dimensions']) # noqa

        if stringify:
            return json_dumps(record)

        return record

    def generate_party(self, contact: dict,
                       lang1: str, lang2: str) -> dict:
        """
        generate party construct from MCF contact

        :param contact: dict of MCF contact
        :param self.lang1: primary language
        :param self.lang2: alternate language


        :returns: MCF contact as a party representation
        """

        organization_name = get_charstring(contact.get('organization'),
                                           self.lang1, self.lang2)

        individual_name = get_charstring(contact.get('individualname'),
                                         self.lang1, self.lang2)

        position_name = get_charstring(contact.get('positionname'),
                                       self.lang1, self.lang2)

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
            'roles': []
        }

        if individual_name[0] is not None:
            rp['@type'] = "schema:Person"
            rp['name'] = individual_name[0]
            if position_name[0] is not None:
                rp['jobTitle'] = position_name[0]
            rp['affiliation'] = {
                '@type': "schema:Organization",
                'name': organization_name[0]
            }
        else:
            rp['@type'] = "schema:Organization"
            rp['name'] = organization_name[0]

        if address[0] is not None:
            rp['address'] = {"@type": "schema:PostalAddress"}
            rp['address']['streetAddress'] = address[0]
            if city[0] is not None:
                rp['address']['addressLocality'] = city[0]
            if administrative_area[0] is not None:
                rp['address']['addressRegion'] = administrative_area[0]
            if postalcode[0] is not None:
                rp['address']['postalCode'] = postalcode[0]
            if country[0] is not None:
                rp['address']['addressCountry'] = country[0]

        if contact.get('phone') is not None:
            LOGGER.debug('Formatting phone number')
            phone = contact['phone']
            phone = phone.replace('-', '').replace('(', '').replace(')', '')
            phone = phone.replace('+0', '+').replace(' ', '')
            rp['telephone'] = phone

        if contact.get('email') is not None:
            rp['email'] = contact.get('email')

        if 'url' in contact:
            rp['url'] = contact['url']

        return rp

    def generate_variables(self, dict_: dict) -> list:
        """
        Generates 1..n variables

        :param dict_: `dict` of attributes

        :returns: `list` of variables
        """

        dict2 = []
        for d in dict_:
            d2 = {
                '@type': 'schema:PropertyValue',
                'name': d.get('name', ''),
                'decription': d.get('description', ''),
            }
            if d.get('max') is not None:
                d2['maxValue'] = d['max']
            if d.get('min') is not None:
                d2['minValue'] = d['min']
            if d.get('units') is not None:
                d2['unitCode'] = d['units']
            dict2.append(d2)

        return dict2

    def generate_contacts(self, contact: dict, role: str) -> list:
        """
        Generates 1..n contacts, streamlining identical
        contacts with multiple roles

        :param contact: `dict` of contacts
        :param role: `str` of role

        :returns: `list` of contacts
        """

        contacts = []

        role_mcf_schema_map = {
            'accountablePerson': [],
            'author': ['originator'],
            'contributor': ['user'],
            'copyrightHolder': ['owner'],
            'creator': [],
            'editor': [],
            'funder': [],
            'maintainer': ['processor', 'custodian'],
            'producer': ['distributor', 'principalInvestigator'],
            'provider': ['resourceProvider'],
            'publisher': ['pointOfContact'],
            'sponsor': []
        }

        for key, value in contact.items():
            if any([value.get('role', key) == role,
                    value.get('role', key) in role_mcf_schema_map[role]]):
                contacts.append(
                    self.generate_party(value, self.lang1, self.lang2))

        return contacts

    def generate_link(self, distribution: dict) -> dict:
        """
        Generates Schema.org link object from MCF distribution object

        :param distribution: `dict` of MCF distribution

        :returns: Schema.org link object
        """

        name = get_charstring(distribution.get('name'),
                              self.lang1, self.lang2)

        desc = get_charstring(distribution.get('description'),
                              self.lang1, self.lang2)

        link = {
            '@type': 'schema:DataDownload',
            'contentUrl': distribution['url']
        }

        if distribution.get('type') is not None:
            link['encodingFormat'] = distribution['type']

        if name != [None, None]:
            link['name'] = name[0]
        elif name != [None, None]:
            link['name'] = name[0]

        if desc != [None, None]:
            link['description'] = desc[0]

        return link


def _get_list_or_dict(value: Union[None, list, dict]) -> Union[None, dict]:
    """
    Helper function to determine whether an element is a list, object or `None`

    :param value: value to evaluate

    :returns: `dict` or None
    """

    if value is None:
        return None

    if isinstance(value, list):
        if len(value) == 0:
            return None
        else:
            return value[0]

    else:
        return value
