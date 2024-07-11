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

import json
import logging
import os
from typing import Union

from pygeometa.core import get_charstring
from pygeometa.helpers import json_serial
from pygeometa.schemas.base import BaseOutputSchema

THISDIR = os.path.dirname(os.path.realpath(__file__))

LOGGER = logging.getLogger(__name__)


class TDML_AIOutputSchema(BaseOutputSchema):
    """OGC Training Data Markup Language for Artificial Intelligence"""

    def __init__(self):
        """
        Initialize object

        :returns: pygeometa.schemas.base.BaseOutputSchema
        """

        description = 'OGC Training Data Markup Language for Artificial Intelligence'  # noqa

        super().__init__('tdml-ai', description, 'json', THISDIR)

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

        dataset = {
            'version': '1.0',
            'id': mcf['metadata']['identifier'],
            'type': 'AI_EOTrainingDataset',
            'name': title[0],
            'description': description[0],
            'extent': {
                'geographicElement': {
                    'geographicBoundingBox': {
                        'westBoundLongitude': minx,
                        'eastBoundLongitude': maxx,
                        'southBoundLatitude': miny,
                        'northBoundLatitude': maxy
                    }
                }
            }
        }

        LOGGER.debug('Checking for temporal')
        try:
            begin = mcf['identification']['extents']['temporal'][0]['begin']
            end = mcf['identification']['extents']['temporal'][0].get('end')

            if begin in ['now', 'None', None]:
                begin = None

            if end in ['now', 'None', None]:
                end = None

            if [begin, end] == [None, None]:
                pass

            else:
                dataset['extent']['temporalElement'] = {'TimePeriod': {}}
                for pos in [[begin, 'beginPosition'], ['end', 'endPosition']]:
                    if pos[0] is not None:
                        dataset['extent']['temporalElement']['TimePeriod'][pos[1]] = pos[0]  # noqa

        except (IndexError, KeyError):
            pass

        dataset['license'] = mcf['identification']['license']['name']

        LOGGER.debug('Checking for dates')
        if 'dates' in mcf['identification']:
            if 'creation' in mcf['identification']['dates']:
                dataset['createdTime'] = str(mcf['identification']['dates']['creation'])  # noqa
            if 'revision' in mcf['identification']['dates']:
                dataset['updatedTime'] = str(mcf['identification']['dates']['revision'])  # noqa

        LOGGER.debug('Checking for contacts')
        dataset['providers'] = self.generate_providers(mcf['contact'])

        LOGGER.debug('Checking for tasks')
        dataset['tasks'] = self.generate_tasks(mcf['tasks'])

        LOGGER.debug('Checking for classes')
        dataset['classes'] = self.generate_classes(mcf['classes'])
        dataset['numberOfClasses'] = len(dataset['classes'])

        LOGGER.debug('Checking for bands')
        dataset['variables'] = self.generate_variables(mcf['attributes'])

        LOGGER.debug('Checking for doi')
        if 'doi' in mcf['identification']:
            dataset['doi'] = mcf['identification']['doi']

        all_keywords = []

        LOGGER.debug('Checking for keywords')
        for key, value in mcf['identification']['keywords'].items():
            keywords = get_charstring(value.get('keywords'), self.lang1,
                                      self.lang2)

            for kw in keywords[0]:
                all_keywords.append(kw)

        if all_keywords:
            dataset['keywords'] = all_keywords

        LOGGER.debug('Checking for data')
        dataset['data'] = self.generate_data(mcf['training-data'])

        if stringify:
            return json.dumps(dataset, default=json_serial, indent=4)
        return dataset

    def generate_variables(self, attributes: list) -> list:
        """
        Generates 1..n tasks

        :param contact: `list` of attributes

        :returns: `list` of variable objects
        """

        variables = []

        for attribute in attributes:
            variable = {
                'name': attribute['name'],
            }
            if 'units' in attribute:
                variable['unit'] = attribute['units']
            if 'abstract' in attribute:
                variable['description'] = attribute['abstract']

            variables.append(variable)

        return variables

    def generate_classes(self, classes: list) -> list:
        """
        Generates 1..n tasks

        :param contact: `list` of classes

        :returns: `list` of class objects
        """

        classes_ = []

        for count, value in enumerate(classes):
            classes_.append({
                'key': value,
                'value': count
            })

        return classes_

    def generate_tasks(self, tasks: dict) -> list:
        """
        Generates 1..n tasks

        :param contact: `dict` of tasks

        :returns: `list` of tasks
        """

        tasks_ = []

        for key, value in tasks.items():
            tasks_.append({
                'id': key,
                'type:': 'AI_EOTask',
                'description': value['description'],
                'taskType': value['type']
            })

        return tasks_

    def generate_providers(self, contact: dict) -> list:
        """
        Generates 1..n providers

        :param contact: `dict` of contacts

        :returns: `list` of providers
        """

        providers = []

        for key, value in contact.items():
            providers.append(value['organization'])

        return providers

    def generate_data(self, training_data: dict) -> dict:
        """
        Generates training data objects from MCF training-data object

        :param training_data: `dict` of MCF training-data

        :returns: `list` of training data objects
        """

        datas = []

        for key, value in training_data.items():
            data = {
                'type': 'AI_EO_TrainingData',
                'id': key,
                'dataURL': [value['url']],
                'labels': []
            }
            for label in value['labels']:
                data['labels'].append({
                    'type': f"AI_{label['type']}Label",
                    f"{label['type']}LabelURL": label['url'],
                    f"{label['type']}LabelField": label['field'],
                })

            datas.append(data)

        return datas
