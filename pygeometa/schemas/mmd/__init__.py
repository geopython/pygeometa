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
# Copyright (c) 2026 Tom Kralidis
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

from pygeometa.schemas.base import BaseOutputSchema

THISDIR = os.path.dirname(os.path.realpath(__file__))

LOGGER = logging.getLogger(__name__)

KEYWORD_SCHEMES = {
    'GCMDSK': 'https://gcmd.earthdata.nasa.gov/kms/concepts/concept_scheme/sciencekeywords',  # noqa
    'GCMDPLT': 'https://gcmd.earthdata.nasa.gov/kms/concepts/concept_scheme/platforms',  # noqa
    'GCMDINST': 'https://gcmd.earthdata.nasa.gov/kms/concepts/concept_scheme/instruments',  # noqa
    'GCMDLOC': 'https://gcmd.earthdata.nasa.gov/kms/concepts/concept_scheme/locations',  # noqa
    'GCMDPROV': 'https://gcmd.earthdata.nasa.gov/kms/concepts/concept_scheme/providers',  # noqa
    'CFSTDN': 'https://vocab.nerc.ac.uk/standard_name/',
    'GEMET': 'http://inspire.ec.europa.eu/theme',
    'NORTHEMES': 'https://register.geonorge.no/metadata-kodelister/nasjonal-temainndeling'  # noqa
}


class MMDOutputSchema(BaseOutputSchema):
    """MMD: record schema"""

    def __init__(self):
        """
        Initialize object

        :returns: pygeometa.schemas.base.BaseOutputSchema
        """

        description = 'MET Norway Metadata Format (MMD)'

        super().__init__('mmd', description, 'json', THISDIR)

    def import_(self, metadata: str) -> dict:
        """
        Import metadata into MCF

        :param metadata: string of metadata content

        :returns: `dict` of MCF content
        """

        # Initialized mcf
        mcf = {
            'mcf': {
                'version': '2.0',
            },
            'metadata': {
                'dates': {},
                'hierarchylevel': 'dataset',
                'language': 'en'
            },
            'identification': {
                'extents': {},
                'keywords': {}
            },
            'contact': {},
            'distribution': {}
        }

        mmd = json.loads(metadata)

        if mmd is None:
            raise ValueError('No MMD metadata')

        mmd = mmd['mmd:mmd']

        mcf['metadata']['identifier'] = mmd['mmd:metadata_identifier']
        mcf['identification']['title'] = mmd['mmd:title']['#text']
        mcf['identification']['abstract'] = mmd['mmd:abstract']['#text']

        LOGGER.debug('Handling mmd:alternate_identifier')
        additional_identifiers = self._get_alternate_identifier(
            mmd.get('mmd:alternate_identifier'))

        if additional_identifiers:
            mcf['metadata']['additional_identifiers'] = additional_identifiers

        LOGGER.debug('Handling mmd:last_metadata_update')
        mcf['metadata']['dates'] = self._get_dates(
            mmd.get('mmd:last_metadata_update'))

        LOGGER.debug('Handling mmd:geographic_extent / mmd:temporal_extent')
        mcf['identification']['extents'] = self._get_spatiotemporal_extents(
            mmd.get('mmd:temporal_extent'),
            mmd.get('mmd:geographic_extent'))

        LOGGER.debug('Handling mmd:dataset_production_status')
        mcf['identification']['status'] = mmd['mmd:dataset_production_status']

        LOGGER.debug('Handling mmd:dataset_language')
        if 'mmd:dataset_language' in mmd:
            mcf['identification']['language'] = mmd['mmd:dataset_language']

        LOGGER.debug('Handling mmd:iso_topic_category')
        if 'mmd:iso_topic_category' in mmd:
            ict = self._get_iso_topic_categories(_force_list(mmd['mmd:iso_topic_category']))  # noqa
            if ict:
                mcf['identification']['keywords']['iso'] = ict

        LOGGER.debug('Handling mmd:keywords')
        mcf['identification']['keywords'].update(
           self._get_keywords(mmd['mmd:keywords']))

        LOGGER.debug('Handling mmd:activity_type')
        mcf['identification']['keywords'].update(
           self._get_activity_type(mmd['mmd:activity_type']))

        LOGGER.debug('Handling mmd:project')
        mcf['identification']['keywords'].update(
            self._get_projects(mmd['mmd:project']))

        LOGGER.debug('Handling mmd:data_access')
        mcf['distribution'].update(
            self._get_data_access(mmd['mmd:data_access']))

        LOGGER.debug('Handling mmd:related_information')
        mcf['distribution'].update(
            self._get_data_access(mmd['mmd:related_information']))

        LOGGER.debug('Handling mmd:personnel')
        mcf['contact'].update(
            self._get_personnel(mmd['mmd:personnel']))

        return mcf

    def write(self, mcf: dict, stringify: str = True) -> Union[dict, str]:
        """
        Write outputschema to JSON string buffer

        :param mcf: dict of MCF content model
        :param stringify: whether to return a string representation (default)
                          else native (dict, etree)

        :returns: `dict` or `str` of MCF as MMD
        """

        # no write implementation for now
        return ''

    def _get_alternate_identifier(
            self, alternate_identifier: Union[dict, list, None]) -> list:
        """
        Helper function to derive MCF additional identifiers

        :param alternate_identifier: `dict` or `list` of alternate identifiers

        :returns: `list` of additional identifiers
        """

        additional_identifiers = []

        for ais in _force_list(alternate_identifier):
            additional_identifiers.append({
                'identifier': ais['#text'],
                'scheme': ais['@type']
            })

        return additional_identifiers

    def _get_dates(self, last_metadata_update: Union[dict, None]) -> dict:
        """
        Helper function to derive MCF metadata dates

        :param last_metadata_update: `dict` of last metadata element

        :returns: `dict` of metadata dates
        """

        dates_ = {}

        creation = None
        created_found = False
        modification_dates = []

        if last_metadata_update is None:
            return dates_

        mmd_updates = _force_list(last_metadata_update['mmd:update'])

        if len(mmd_updates) == 1:
            created = mmd_updates[0]['mmd:datetime']
            return {
                'creation': created
            }

        for mmd_update in mmd_updates:
            if mmd_update['mmd:type'] == 'Created':
                created_found = True
                creation = mmd_update['mmd:datetime']
                break
            if 'modification' in mmd_update['mmd:type']:
                modification_dates.append(mmd_update['mmd:datetime'])

        modification_dates.sort()

        if created_found:
            dates_['creation'] = creation
        else:
            dates_['creation'] = modification_dates[0]
            dates_['revision'] = modification_dates[-1]

        return dates_

    def _get_spatiotemporal_extents(self, temporal_extent: Union[dict, list, None],  # noqa
                                    geographic_extent: dict) -> dict:
        """
        Helper function to derive MCF metadata dates

        :param temporal_extent: `dict` or `list of temporal extent
        :param geographic_extent: `dict` of geographic extent

        :returns: `dict` of spatiotemporal extents
        """

        extents = {}

        temp_extents = []

        temp_extents2 = _force_list(temporal_extent)

        for temp_extent in temp_extents2:
            temp_extents.append({
                'begin': temp_extent['mmd:start_date'],
                'end': temp_extent['mmd:end_date']
            })

        if temp_extents:
            extents['temporal'] = temp_extents

        minx = float(geographic_extent['mmd:rectangle']['mmd:west'])
        miny = float(geographic_extent['mmd:rectangle']['mmd:south'])
        maxx = float(geographic_extent['mmd:rectangle']['mmd:east'])
        maxy = float(geographic_extent['mmd:rectangle']['mmd:north'])

        extents['spatial'] = [{
            'bbox': [minx, miny, maxx, maxy],
            'crs': 4326
        }]

        return extents

    def _get_iso_topic_categories(self, iso_topic_category: Union[str, list]) -> dict:  # noqa
        """
        Helper function to derive ISO topic categories as a keyword list

        :param iso_topic_category: `str` or `list` of ISO topic category

        :returns: `dict` of keywords object
        """

        keywords = []
        keywords_set = {}

        for itc in _force_list(iso_topic_category):
            if itc != 'Not available':
                keywords.append(itc)

        if keywords:
            keywords_set = {
                'keywords': keywords,
                'keywords_type': 'theme',
                'vocabulary': {
                    'name': 'ISO Topic Category',
                    'url': 'https://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#MD_TopicCategoryCode'  # noqa
                }
            }

        return keywords_set

    def _get_keywords(self, keywords: Union[dict, list]) -> dict:
        """
        Helper function to derive keywords

        :param keywords: `dict` or `list` of keywords

        :returns: `dict` of keywords
        """

        keywords_dict = {}

        for mks in _force_list(keywords):
            mks_keywords = _force_list(mks['mmd:keyword'])
            keywords_dict[mks['@vocabulary']] = {
                'keywords': mks_keywords,
                'keywords_type': 'theme',
                'vocabulary': {
                    'name': mks['@vocabulary'],
                    'url': KEYWORD_SCHEMES[mks['@vocabulary']]
                }
            }

        return keywords_dict

    def _get_activity_type(
            self, activity_type: Union[dict, list, str]) -> dict:
        """
        Helper function to derive activity type as keywords

        :param keywords: `dict` or `list` or `str` of projects

        :returns: `dict` of keywords
        """

        keywords = []

        for ats in _force_list(activity_type):
            keywords.append(ats)

        return {
            'activity_type': {
                'keywords': keywords,
                'keywords_type': 'theme',
                'vocabulary': {
                    'name': 'Activity Type',
                    'url': 'https://vocab.met.no/mmd/en/page/Activity_Type'
                }
            }
        }

    def _get_projects(self, projects: Union[dict, list]) -> dict:
        """
        Helper function to derive projects as keywords

        :param keywords: `dict` or `list` of projects

        :returns: `dict` of keywords
        """

        keywords = []

        for mps in _force_list(projects):
            if mps['mmd:short_name'] is not None:
                keywords.append(mps['mmd:short_name'])
            if mps['mmd:long_name'] is not None:
                keywords.append(mps['mmd:long_name'])

        return {
            'default': {
                'keywords': keywords,
                'keywords_type': 'theme',
            }
        }

    def _get_personnel(self, personnel: Union[dict, list]) -> dict:
        """
        Helper function to derive personnel

        :param data_access: `dict` or `list` of personnel

        :returns: `dict` of contacts
        """

        contacts = {}

        for ps in _force_list(personnel):
            url = None
            if isinstance(ps['mmd:organisation'], dict):
                org = ps['mmd:organisation']['#text']
                url = ps['mmd:organisation']['@uri']
            else:
                org = ps['mmd:organisation']

            contacts[ps['mmd:role']] = {
                'role': ps['mmd:role'],
                'individualname': ps['mmd:name'],
                'organization': org,
                'email': ps['mmd:email']
            }
            if url is not None:
                contacts[ps['mmd:role']]['url'] = url

        return contacts

    def _get_data_access(self, data_access: Union[dict, list]) -> dict:
        """
        Helper function to derive data access

        :param data_access: `dict` or `list` of data access definitions

        :returns: `dict` of distributions
        """

        distribution = {}

        for das in _force_list(data_access):
            link = {
                'type': das['mmd:type'],
                'rel': das['mmd:type'],
                'name': das['mmd:description'],
                'description': das['mmd:description'],
                'url': das['mmd:resource']
            }
            if link['url'].endswith('.nc'):
                link['type'] = 'application/x-netcdf'
            if link['rel'] == 'OGC WMS':
                link['type'] = 'application/xml'
            if 'doi.org' in link['url']:
                link['rel'] = 'cite-as'
                link['type'] = 'text/html'

            distribution[das['mmd:type']] = link

        return distribution


def _force_list(obj: Union[dict, str, list]) -> list:
    """
    Helper function to force list typing

    :param obj: `dict`, `list`, `str` of object

    :returns: `list` of object
    """

    if obj is None:
        return []
    if isinstance(obj, (dict, str)):
        return [obj]

    return obj
