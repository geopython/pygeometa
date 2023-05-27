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
# Copyright (c) 2023 Tom Kralidis
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

from datetime import datetime
import json
import logging
import os
from typing import Union

from pygeometa.helpers import json_serial
from pygeometa.schemas.ogcapi_records import OGCAPIRecordOutputSchema

THISDIR = os.path.dirname(os.path.realpath(__file__))

LOGGER = logging.getLogger(__name__)


class WMOWCMP2OutputSchema(OGCAPIRecordOutputSchema):
    """OGC API - Records - Part 1: Core record schema"""

    def __init__(self):
        """
        Initialize object

        :returns: pygeometa.schemas.base.BaseOutputSchema
        """

        description = 'WMO Core Metadata Profile 2 (WCMP2)'

        super().__init__()

        self.description = description

    def write(self, mcf: dict, stringify: str = True) -> Union[dict, str]:
        """
        Write outputschema to JSON string buffer

        :param mcf: dict of MCF content model
        :param stringify: whether to return a string representation (default)
                          else native (dict, etree)


        :returns: `dict` or `str` of MCF as an OARec record representation
        """

        record = super().write(mcf, stringify=False)

        LOGGER.debug('Setting WCMP2 conformance')
        record['conformsTo'] = ['http://wis.wmo.int/spec/wcmp/2/conf/core']

        if 'edition' in mcf['identification']:
            record['properties']['version'] = mcf['identification']['version']

        LOGGER.debug('Setting WCMP2 distribution links')
        record['links'] = []
        for key, value in mcf['distribution'].items():
            link = self.generate_link(value)

            record['links'].append(link)

        if mcf['metadata'].get('hierarchylevel') == 'dataset':
            try:
                record['properties']['wmo:dataPolicy'] = mcf['identification']['wmo_data_policy']  # noqa
            except KeyError:
                LOGGER.warning('Missing wmo:dataPolicy')

        if 'dates' not in record['properties']:
            record['properties']['created'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')  # noqa

        if stringify:
            return json.dumps(record, default=json_serial, indent=4)
        else:
            return record
