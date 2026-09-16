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
# Copyright (c) 2026 Niccolò Cantù
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

from pathlib import Path
import re

from bs4 import BeautifulSoup
import pycountry

from pygeometa.schemas.base import BaseOutputSchema

THISDIR = Path(__file__).parent


def text_or_null(node, strip=False):
    if not node:
        return None

    if strip:
        return node.text.strip()

    return node.text


def text_or_empty(node, strip=False):
    if not node:
        return ''

    if strip:
        return node.text.strip()

    return node.text


def scrub_dict(d):
    if type(d) is dict:
        return dict(
            (k, scrub_dict(v))
            for k, v in d.items()
            if v is not None and scrub_dict(v) is not None
        )
    else:
        return d


def to_contact_role(node, role, mapped_role=None):
    if not mapped_role:
        mapped_role = role

    for idx, contact in enumerate(node.find_all(role)):
        name = f'{text_or_empty(contact.find("surName"))}, '
        name += text_or_empty(contact.find('givenName'))
        org = text_or_empty(contact.find('organizationName'))
        yield (
            mapped_role + (f'_{idx}' if idx else ''),
            {
                'organization': org,
                'individualname': name,
                'positionname': text_or_empty(contact.find('positionName'))
                or text_or_empty(contact.find('role')),
                'phone': '',
                'url': '',
                'fax': '',
                'address': '',
                'city': '',
                'administrativearea': '',
                'postalcode': '',
                'country': text_or_empty(contact.find('country')),
                'email': text_or_empty(contact.find('electronicMailAddress'))
            },
        )


class GBIF_EMLOutputSchema(BaseOutputSchema):
    def __init__(self):
        super().__init__('gbif-eml', 'EML - GBIF profile', 'xml', THISDIR)

    def import_(self, metadata):
        soup = BeautifulSoup(metadata, features='lxml-xml')
        dataset = soup.find('dataset')
        mcf = {
            'mcf': {
                'version': 1,
            },
            'metadata': {
                'charset': 'utf8',
                'hierarchylevel': 'dataset',
                'datestamp': text_or_null(dataset.find('pubDate'), strip=True)
                or '$date$',
            },
            'identification': {},
            'contact': {},
            'distribution': {}
        }

        for identifier in dataset.find_all('alternateIdentifier'):
            mcf['metadata']['identifier'] = text_or_null(identifier)

        if language := dataset.find('language'):
            lang = text_or_null(language)
            if lang and pycountry.languages.get(alpha_3=lang):
                mcf['metadata']['language'] = pycountry.languages.get(
                    alpha_3=lang
                ).alpha_2

        idf = mcf['identification']

        idf['title'] = text_or_null(dataset.find('title'))
        idf['abstract'] = text_or_null(dataset.find('abstract'))

        if intellectual_rights := dataset.find('intellectualRights'):
            url = (
                intellectual_rights.find('ulink')['url']
                if intellectual_rights.find('ulink')
                else None
            )
            idf['rights'] = {
                'name': text_or_null(intellectual_rights.find('citetitle')),
                'url': url
            }

        idf['url'] = text_or_null(dataset.find('alternateIdentifier'))
        idf['status'] = 'completed'

        idf['maintenancefrequency'] = (
            text_or_null(dataset.find('maintenanceUpdateFrequency'))
            or 'unknown'
        )

        idf['dates'] = {
            'publication': text_or_null(dataset.find('pubDate'), strip=True)
        }
        idf['extents'] = {}

        if coords := dataset.find('boundingCoordinates'):
            idf['extents']['spatial'] = [{}]
            spatial = idf['extents']['spatial'][0]

            spatial['bbox'] = [
                float(coords.find('westBoundingCoordinate').text),
                float(coords.find('southBoundingCoordinate').text),
                float(coords.find('eastBoundingCoordinate').text),
                float(coords.find('northBoundingCoordinate').text)
            ]

            spatial['crs'] = 4326
            spatial['description'] = text_or_null(
                dataset.find('geographicDescription')
            )

        idf['keywords'] = {}

        ct = mcf['contact']

        for r, obj in to_contact_role(dataset, 'contact', 'pointOfContact'):
            ct[r] = obj

        for r, obj in to_contact_role(
            dataset, 'metadataProvider', 'distributor'
        ):
            ct[r] = obj

        for r, obj in to_contact_role(dataset, 'creator'):
            ct[r] = obj

        for r, obj in to_contact_role(
            dataset, 'personnel', 'projectPersonnel'
        ):
            ct[r] = obj

        for idx, keyword_set in enumerate(dataset.find_all('keywordSet')):
            thesaurus = text_or_null(keyword_set.find('keywordThesaurus'))
            match = re.search(r'(?P<url>https?://[^\s]+)', thesaurus)
            definition = match.group('url') if match else None

            idf['keywords'][f'default-{idx}'] = {
                'keywords': [
                    text_or_null(kw) for kw in keyword_set.find_all('keyword')
                ],
                'vocabulary': {'name': thesaurus, 'url': definition},
            }

        mcf['spatial'] = {'datatype': 'vector', 'geomtype': 'composite'}

        mcf['distribution'] = {
            'file': {
                'url': idf['url'],
                'type': 'WWW:LINK',
                'function': 'information',
                'description': '',
                'name': 'Darwin Core Archive'
            }
        }

        return scrub_dict(mcf)
