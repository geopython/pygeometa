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

import ast
import logging
import os

from lxml import etree
from owslib.iso import CI_OnlineResource, CI_ResponsibleParty, MD_Metadata

from pygeometa.schemas.base import BaseOutputSchema

LOGGER = logging.getLogger(__name__)
THISDIR = os.path.dirname(os.path.realpath(__file__))


class ISO19139OutputSchema(BaseOutputSchema):
    """ISO 19139 output schema"""

    def __init__(self):
        """
        Initialize object

        :returns: pygeometa.schemas.base.BaseOutputSchema
        """

        description = 'ISO 19115/19139'

        super().__init__('iso19139', description, 'xml', THISDIR)

    def import_(self, metadata: str) -> dict:
        """
        Import metadata into MCF

        :param metadata: string of metadata content

        :returns: `dict` of MCF content
        """

        mcf = {
            'mcf': {
                'version': '1.0',
            },
            'metadata': {},
            'identification': {},
            'contact': {},
            'distribution': {}
        }

        LOGGER.debug('Parsing ISO metadata')
        try:
            m = MD_Metadata(etree.fromstring(metadata))
        except ValueError:
            m = MD_Metadata(etree.fromstring(bytes(metadata, 'utf-8')))

        LOGGER.debug('Setting metadata')
        mcf['metadata']['identifier'] = m.identifier

        mcf['metadata']['hierarchylevel'] = m.hierarchy
        mcf['metadata']['datestamp'] = m.datestamp

        LOGGER.debug('Setting language')
        if m.language:
            mcf['metadata']['language'] = m.language
        elif m.languagecode:
            mcf['metadata']['language'] = m.languagecode

        identification = m.identification[0]

        LOGGER.debug('Setting identification')
        mcf['identification']['title'] = identification.title
        mcf['identification']['abstract'] = identification.abstract

        if identification.date:
            mcf['identification']['dates'] = {}
            for date_ in identification.date:
                mcf['identification']['dates'][date_.type] = date_.date

        if identification.keywords:
            mcf['identification']['keywords'] = {}
            for count, value in enumerate(identification.keywords):
                key = f'keywords-{count}'
                mcf['identification']['keywords'][key] = {
                    'keywords_type': value.type,
                    'keywords': [k.name for k in value.keywords]
                }
                if value.thesaurus is not None:
                    mcf['identification']['keywords'][key]['vocabulary'] = {
                        'name': value.thesaurus['title'],
                        'url': value.thesaurus['url']
                    }

        mcf['identification']['topiccategory'] = identification.topiccategory  # noqa

        mcf['identification']['extents'] = {
            'spatial': [{
                'bbox': [
                    ast.literal_eval(identification.extent.boundingBox.minx),
                    ast.literal_eval(identification.extent.boundingBox.miny),
                    ast.literal_eval(identification.extent.boundingBox.maxx),
                    ast.literal_eval(identification.extent.boundingBox.maxy)
                ]
            }],
            'temporal': []
        }

        temp_extent = {
            'begin': None,
            'end': None
        }

        if identification.temporalextent_start:
            temp_extent['begin'] = identification.temporalextent_start
        if identification.temporalextent_end:
            temp_extent['end'] = identification.temporalextent_end

        mcf['identification']['extents']['temporal'].append(temp_extent)

        if identification.accessconstraints:
            mcf['identification']['accessconstraints'] = identification.accessconstraints[0]  # noqa

        mcf['identification']['status'] = identification.status

        LOGGER.debug('Setting contacts')
#        for contact in m.get_all_contacts():
#            mcf['contact'].update(get_contact(contact))
        mcf['contact'].update(get_contact(m.contact[0]))

        LOGGER.debug('Setting distribution')
        if m.distribution:
            for count, value in enumerate(m.distribution.online):
                key = f'link-{count}'
                mcf['distribution'][key] = get_link(value)

        return mcf


def get_contact(contact: CI_ResponsibleParty) -> dict:
    """
    Generates an MCF contact from an OWSLib contact

    :param contact: OWSLib `CI_ResponsibleParty` object

    :returns: dict of MCF contact
    """

    mcf_contact = {contact.role: {}}

    cm_lookup = {
        'name': 'name',
        'organization': 'organization',
        'positionname': 'position',
        'phone': 'phone',
        'fax': 'fax',
        'address': 'address',
        'city': 'city',
        'administrativearea': 'region',
        'postalcode': 'postcode',
        'country': 'country',
        'email': 'email'
    }

    for key, value in cm_lookup.items():
        if getattr(contact, value) is not None:
            mcf_contact[contact.role][key] = getattr(contact, value)

    if hasattr(contact.onlineresource, 'url'):
        mcf_contact[contact.role]['url'] = contact.onlineresource.url

    return mcf_contact


def get_link(link: CI_OnlineResource) -> dict:
    """
    Generates an MCF link from an OWSLib distribution URL

    :param contact: OWSLib `CI_OnlineResource` object

    :returns: dict of MCF link
    """

    mcf_link = {
        'url': link.url,
        'type': link.protocol,
        'name': link.name,
        'description': link.description,
        'function': link.function
    }

    return mcf_link
