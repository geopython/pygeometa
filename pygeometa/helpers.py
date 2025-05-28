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
# Copyright (c) 2024 Tom Kralidis
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

import base64
from datetime import date, datetime, time
from decimal import Decimal
import json
import logging
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger(__name__)

THISDIR = Path(__file__).resolve().parent


def json_dumps(obj) -> str:
    """
    Helper function to dump dict to JSON string

    :param obj: `dict` of JSON

    :returns: `str` of JSON
    """

    return json.dumps(obj, default=json_serial, indent=4, ensure_ascii=False)


def json_serial(obj) -> Any:
    """
    Helper function to convert to JSON non-default
    types (source: https://stackoverflow.com/a/22238613)

    :param obj: `object` to be evaluated

    :returns: JSON non-default type to `str`
    """

    if isinstance(obj, (datetime, date, time)):
        return obj.isoformat()
    elif isinstance(obj, bytes):
        try:
            LOGGER.debug('Returning as UTF-8 decoded bytes')
            return obj.decode('utf-8')
        except UnicodeDecodeError:
            LOGGER.debug('Returning as base64 encoded JSON object')
            return base64.b64encode(obj)
    elif isinstance(obj, Decimal):
        return float(obj)

    msg = f'{obj} type {type(obj)} not serializable'
    LOGGER.error(msg)
    raise TypeError(msg)


def generate_datetime(date_value: str) -> str:
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
