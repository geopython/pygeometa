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

import logging

LOGGER = logging.getLogger(__name__)


def generate_geometry(spatial: list) -> dict:
    """
    Helper function to generate GeoJSON geometry from an
    MCF spatial extent

    :param spatial: `list` of spatial extents defined

    :returns: `dict` of GeoJSON geometry
    """

    geometry = None

    if len(spatial) == 1:
        LOGGER.debug('spatial extent is a default bbox')
        try:
            minx, miny, maxx, maxy = (spatial[0]['bbox'])
            geometry = {
                'type': 'Polygon',
                'coordinates': [[
                    [minx, miny],
                    [minx, maxy],
                    [maxx, maxy],
                    [maxx, miny],
                    [minx, miny]
                ]]
            }
        except TypeError:
            geometry = None
    elif len(spatial) > 1:
        LOGGER.debug('spatial extent is a multiple bbox')
        bboxes = []
        for s in spatial:
            try:
                minx, miny, maxx, maxy = (s['bbox'])
                bboxes.append([[
                        [minx, miny],
                        [minx, maxy],
                        [maxx, maxy],
                        [maxx, miny],
                        [minx, miny]
                    ]])
            except TypeError:
                LOGGER.debug('bbox failed')

        geometry = {
            'type': 'MultiPolygon',
            'coordinates': bboxes
        }
    else:
        LOGGER.debug('Invalid spatial extent')
        geometry = None

    return geometry
