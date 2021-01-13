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
# Copyright (c) 2020 Tom Kralidis, Paul van Genuchten
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
import os

from pygeometa.helpers import json_serial
from pygeometa.schemas.base import BaseOutputSchema

THISDIR = os.path.dirname(os.path.realpath(__file__))


class DCATOutputSchema(BaseOutputSchema):
    """dcat output schema"""

    def __init__(self):
        """
        Initialize object

        :returns: pygeometa.schemas.base.BaseOutputSchema
        """

        super().__init__('dcat', 'json', THISDIR)

    def write(self, mcf: dict) -> str:
        """
        Write outputschema to JSON string buffer

        :param mcf: dict of MCF content model

        :returns: MCF as a dcat representation
        """

        dcat = {
            "@context": {
                # namespaces
                "adms": "http://www.w3.org/ns/adms#",
                "dcat": "http://www.w3.org/ns/dcat#",
                "dct": "http://purl.org/dc/terms/",
                "foaf": "http://xmlns.com/foaf/0.1/",
                "gsp": "http://www.opengis.net/ont/geosparql#",
                "locn": "http://www.w3.org/ns/locn#",
                "owl": "http://www.w3.org/2002/07/owl#",
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "schema": "http://schema.org/",
                "skos": "http://www.w3.org/2004/02/skos/core#",
                "time": "http://www.w3.org/2006/time",
                "vcard": "http://www.w3.org/2006/vcard/ns#",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
                # mcf-property to dcat mappings
                "topiccategory": "dcat:theme",
                "language": "dct:language",
                # todo: support any range of languages from source
                "title": "dct:title",
                "title_en": {"@id": "dct:title", "@language": "en"},
                "title_fr": {"@id": "dct:title", "@language": "fr"},
                "abstract_en": {"@id": "dct:description", "@language": "en"},
                "abstract_fr": {"@id": "dct:description", "@language": "fr"},
                "distribution": "dcat:distribution",
                "url": "dcat:accessURL",
                "name": "dct:title",
                "name_en": {"@id": "dct:title", "@language": "en"},
                "name_fr": {"@id": "dct:title", "@language": "fr"},
                "description": "dct:description",
                "description_en": {"@id": "dct:description",
                                   "@language": "en"},
                "description_fr": {"@id": "dct:description",
                                   "@language": "fr"},
                "keywords": "dct:keyword",
                "keywords_en": {"@id": "dct:keyword", "@language": "en"},
                "keywords_fr": {"@id": "dct:keyword", "@language": "fr"},
                "dataseturi": {"@type": "@id", "@id": "@id"},
                "contact": "dcat:contactPoint",
                "spatial": "dct:spatial",
                "temporal": "dct:temporal",
                "creation": "dct:issued",
                "modified": "dct:modified",
                "maintenancefrequency": "dct:accrualPeriodicity",
                "type": "dcat:mediaType",
                "size": "dcat:byteSize",
                "status": "adms:status",
                "organization": "vcard:hasOrganizationName",
                "individualname": "vcard:fn",
                "phone": "vcard:hasTelephone",
                "address": "vcard:street-address",
                "city": "vcard:locality",
                "postalcode": "vcard:postal-code",
                "country": "vcard:country-name",
                "email": "vcard:hasEmail",
                "accessconstraints": "dct:accessRights",
                "rights": "dct:rights",
                "rights_en": {"@id": "dct:rights", "@language": "en"},
                "rights_fr": {"@id": "dct:rights", "@language": "fr"},
                "bbox": "dcat:bbox",
                "begin": "dcat:startDate",
                "end": "dcat:endDate"
            },
            "@type": "dcat:Dataset",
            "keywords_en": [],
            "keywords_fr": [],
            "distribution": [],
            "contact": []
        }

        # prepare mcf for json-ld
        for key, value in mcf.items():
            # do nothing for these items (yet)
            if (key in ['mcf', 'content_info', 'acquisition']):
                None
            # unnest these items
            elif (key in ['metadata', 'identification']):
                for k, v in value.items():
                    if (k == 'extents'):
                        for k1, v1 in v.items():
                            # assign dct:location type
                            if (k1 == 'spatial'):
                                dcat["spatial"] = []
                                for k2 in v1:
                                    k2['@type'] = 'dct:Location'
                                    dcat["spatial"].append(k2)
                            # assign dct:PeriodOftime type
                            elif (k1 == 'temporal'):
                                dcat['temporal'] = []
                                for k3 in v1:
                                    k3['@type'] = 'dct:PeriodOfTime'
                                    dcat["temporal"].append(k3)
                    # unnest keywords
                    elif (k == 'keywords'):
                        for k4, v4 in v.items():
                            for k5, v5 in v4.items():
                                if (k5 != 'keywords_type'):
                                    for kw in v5:
                                        # assumes a key for language exists
                                        dcat[k5].append(kw)
                    elif (k in ['identifier']):
                        # mint a url from identifier if non exists on mcf
                        if (not mcf['metadata']['dataseturi']):
                            dcat['dataseturi'] = 'http://example.com/#' + \
                                str(v)
                    elif (k in ['dates']):
                        for k6, v6 in v.items():
                            dcat[k6] = v6
                    else:
                        dcat[k] = v
            # transform set of keys to array
            elif (key in ['distribution', 'contact']):
                for k, v in value.items():
                    # add id (if url exists)
                    if (not isinstance(v, str) and v['url']):
                        v['@id'] = v['url']
                    # add type
                    if (key == 'distribution'):
                        v['@type'] = 'dcat:Distribution'
                    else:
                        v['@type'] = 'vcard:Organization'
                    dcat[key].append(v)
            # other cases: root properties
            else:
                dcat[key] = value

        return json.dumps(dcat, default=json_serial, indent=4)
