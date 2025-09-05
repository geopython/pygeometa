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

import os
from typing import Union

from lxml import etree

from pygeometa.schemas.base import BaseOutputSchema

THISDIR = os.path.dirname(os.path.realpath(__file__))

NAMESPACES = {
    'gco': 'http://www.isotc211.org/2005/gco',
    'gmd': 'http://www.isotc211.org/2005/gmd',
    'gml': 'http://www.opengis.net/gml/3.2',
    'om': 'http://www.opengis.net/om/2.0',
    'wmdr': 'http://def.wmo.int/wmdr/2017',
    'xlink': 'http://www.w3.org/1999/xlink'
}


class WMOWIGOSOutputSchema(BaseOutputSchema):
    """WMO WIGOS output schema"""

    def __init__(self):
        """
        Initialize object

        :returns: pygeometa.schemas.base.BaseOutputSchema
        """

        description = 'WMO WIGOS Metadata Standard'

        super().__init__('wmo-wigos', description, 'xml', THISDIR)

    def import_(self, metadata: str) -> dict:
        """
        Import metadatra into MCF

        :param metadata: `str` of metadat content

        :returns: `dict` of MCF content
        """

        mcf = {
            'mcf': {
                'version': '1.0',
            },
            'metadata': {
                'charset': 'utf8',
            },
            'identification': {},
            'contact': {},
            'distribution': {},
            'facility': {}
        }

        self.exml = etree.fromstring(metadata)

        mcf['metadata']['identifier'] = self._get_xpath_value('//wmdr:facility/wmdr:ObservingFacility/gml:identifier')
        mcf['metadata']['datestamp'] = self._get_xpath_value('//wmdr:headerInformation//wmdr:fileDateTime')

        contact_xpaths = [
            '//wmdr:recordOwner/gmd:CI_ResponsibleParty',
            '//wmdr:facility/wmdr:ObservingFacility//gmd:CI_ResponsibleParty'
        ]

        for contact_xpath in contact_xpaths:
            role, contact = self._get_contact(contact_xpath)
            mcf['contact'][role] = contact

        return mcf

    def _get_xpath_value(self, xpath: str,
                         node: etree._Element = None) -> Union[str, list]:
        """
        Helper function to get a value by XPath

        :param xpath: `str` of XPath expression
        :param node: `etree._Element` of node

        :returns: `str` or `list` of matching values
        """

        node2 = self.exml

        if node is not None:
            node2 = node

        values = node2.xpath(xpath, namespaces=NAMESPACES)

        if len(values) == 1:
            if hasattr(values[0], 'text'):
                return values[0].text
            else:
                return str(values[0])
        else:
            return [value.text for value in values]

        return values

    def _get_contact(self, xpath: str) -> tuple:
        """
        Helper function to get contact information by XPath

        :param xpath: `str` of XPath expression

        :returns: `dict` of contact information
        """

        contact = {}
        role = None

        val = self._get_xpath_value(f'{xpath}/gmd:role/gmd:CI_RoleCode/@codeListValue')
        if val:
            role = val
        else:
            role = 'host'

        val = self._get_xpath_value(f'{xpath}/gmd:individualName/gco:CharacterString')
        if val:
            contact['individualname'] = val

        val = self._get_xpath_value(f'{xpath}/gmd:organisationName/gco:CharacterString')
        if val:
            contact['organization'] = val

        val = self._get_xpath_value(f'{xpath}//gmd:deliveryPoint/gco:CharacterString')
        if val:
            contact['address'] = val

        val = self._get_xpath_value(f'{xpath}//gmd:city/gco:CharacterString')
        if val:
            contact['city'] = val

        val = self._get_xpath_value(f'{xpath}//gmd:administrativeArea/gco:CharacterString')
        if val:
            contact['adminstrativearea'] = val

        val = self._get_xpath_value(f'{xpath}//gmd:country/gco:CharacterString')
        if val:
            contact['country'] = val

        val = self._get_xpath_value(f'{xpath}//gmd:electronicMailAddress/gco:CharacterString')
        if val:
            contact['email'] = val[0]


        return role, contact
