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
# Copyright (c) 2024 Tom Kralidis, Paul van Genuchten
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

import os, sys, yaml, json
from typing import Dict, Any, List, Optional, Union
from rdflib import Graph, URIRef, Namespace, Literal
from rdflib.namespace import RDF

from pygeometa.helpers import json_dumps
from pygeometa.schemas.base import BaseOutputSchema


# Namespaces
DCT = Namespace('http://purl.org/dc/terms/')
DCAT = Namespace('http://www.w3.org/ns/dcat#')
SKOS = Namespace('http://www.w3.org/2004/02/skos/core#')
PROV =  Namespace('http://www.w3.org/ns/prov#')
FOAF = Namespace('http://xmlns.com/foaf/0.1/')
ADMS = Namespace('http://www.w3.org/ns/adms#')
LOCN = Namespace('http://www.w3.org/ns/locn#')
VCARD = Namespace('http://www.w3.org/2006/vcard/ns#')
OWL = Namespace('http://www.w3.org/2002/07/owl#')
RDF = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
RDFS = Namespace('http://www.w3.org/2000/01/rdf-schema#')
SCHEMA = Namespace('http://schema.org/')
TIME = Namespace('http://www.w3.org/2006/time')
VCARD = Namespace('http://www.w3.org/2006/vcard/ns#')
XSD = Namespace('http://www.w3.org/2001/XMLSchema#')

# Default DCAT-AP 3.1 context URL for missing JSON-LD contexts
_DCAT_AP_CONTEXT_URL = "https://github.com/SEMICeu/DCAT-AP/raw/refs/heads/master/releases/3.0.1/context/dcat-ap.jsonld"

# default mapping aligning common DCAT/DCT terms to MCF paths
DEFAULT_MAPPING = {
    'dct:title':        'identification.title',
    'dct:description':  'identification.abstract',
    'dct:abstract':     'identification.abstract',
    'dct:subject':      'identification.subjects',
    'dct:temporal':     'identification.temporal',
    'dct:spatial':      'identification.geographic',
    'dct:license':      'identification.licence',
    'dcat:keyword':     'identification.subjects',
    'dct:language':     'metadata.language',
    'dct:modified':     'identification.modified',
    'dct:source':       'identification.source',
    'dct:accessRights': 'identification.rights',
    'dct:conformsTo':   'identification.conformsto',
    'dcat:contactPoint': 'identification.contactpoint',
    'dcat:endpointUrl': 'identification.endpointurl',
    'dct:format':       'identification.format',
    'dcat:landingPage': 'identification.landingpage',
    'dct:publisher':    'identification.publisher',
    'dct:creator':      'identification.creator',
    'dcat:distribution': 'identification.distribution',
    'dct:accrualPeriodicity': 'identification.accrualPeriodicity',
    'dcat:hasVersion':  'identification.hasVersion',
    'dct:identifier':   'metadata.identifier',
    'dcat:inSeries':    'identification.inSeries',
    'dct:isReferencedBy': 'identification.isReferencedBy',
    'dct:provenance':   'identification.provenance',
    'dct:relation':     'identification.relation',
    'dct:issued':       'identification.issued',
    'adms:sample':      'identification.sample',
    'dcat:spatialResolutionInMeters': 'identification.spatialResolutionInMeters',
    'dcat:temporalResolution': 'identification.temporalResolution',
    'dcat:theme':       'identification.subjects',
    'dct:type':         'metadata.hierarchylevel',
    'adms:versionNotes': 'identification.versionnotes',
    'prov:wasGeneratedBy': 'identification.wasgeneratedby'
}

INTL_MCF_FIELDS = ["identification.abstract,identification.title"]

# Parser formats to try in order
_PARSER_FORMATS = [
    'json-ld',
    'xml',
    'turtle',
    'n3',
    'trig',
]


THISDIR = os.path.dirname(os.path.realpath(__file__))


class DCATOutputSchema(BaseOutputSchema):
    """dcat output schema"""

    def __init__(self):
        """
        Initialize object

        :returns: pygeometa.schemas.base.BaseOutputSchema
        """

        description = 'DCAT'
        super().__init__('dcat', description, 'json', THISDIR)


    def _inject_jsonld_context(self, content: str) -> str:
        """
        Inject DCAT-AP context into JSON content if missing.


        Returns modified JSON string if '@context' not found.
        If parsing fails, returns original content.
        """
        try:
            data = json.loads(content)
            if isinstance(data, dict) and '@context' not in data:
                data['@context'] = _DCAT_AP_CONTEXT_URL
                return json.dumps(data)
        except Exception:
            pass
        return content

    def parse_dcat_content(self, content: str, base: Optional[str] = None) -> Graph:
        """
        Parse content into an rdflib.Graph, trying a set of common RDF serialisations.

        Raises ValueError if none of the attempted formats succeed.
        """
        last_exc = None

        # Try to detect if JSON-LD and may need context injection
        try:
            sample = content.strip()[:100].lstrip()
            if sample.startswith('{') or sample.startswith('['):
                content = self._inject_jsonld_context(content)
        except Exception:
            pass

        for fmt in _PARSER_FORMATS:
            try:
                g = Graph()
                g.parse(data=content, format=fmt, publicID=base)
                return g
            except Exception as exc:
                last_exc = exc
        raise ValueError(f"Unable to parse content as a known RDF serialisation. Last error: {last_exc}")


    def _to_uriref(self, key: str) -> URIRef:
        """Convert a mapping key into a URIRef.

        Accepts full URIs or qnames like 'dct:title' or 'dcat:keyword'.
        Unknown prefixes default to the DCT namespace.
        """
        if key.startswith('http://') or key.startswith('https://'):
            return URIRef(key)
        if ':' in key:
            prefix, local = key.split(':', 1)
            ns = {
                'dct': DCT,
                'dcat': DCAT,
                'skos': SKOS,
                'prov': PROV,
                'foaf': FOAF, 
                'adms': ADMS,
                'locn': LOCN,
                'vcard':  VCARD,
                'schema': SCHEMA
            }.get(prefix)
            if ns is not None:
                return ns[local]
        return DCT[key]


    def _collect_literals_by_lang(self, values: List[Any], deflang='eng') -> Dict[str, List[str]]:
        """
        Given a list of rdflib nodes, return dict lang -> list(strings).

        Literals without language tags go under the empty-string key ''.
        Non-literals (URIRefs) are converted to their string representation
        and put under ''.
        """
        out: Dict[str, List[str]] = {}
        for v in values:
            if isinstance(v, Literal):
                s = str(v)
                lang = v.language or deflang
            else:
                s = str(v)
                lang = deflang
            if s not in (None,''):
                out.setdefault(lang, []).append(s)
        return out


    def _join_lang_values(self, values: List[str]) -> str:
        """Join multiple values for the same language into a single scalar.

        The join token is ' | '. This keeps values readable while producing a
        single scalar as required by the MCF core schema.
        """
        if not values:
            return ''
        if len(values) == 1:
            return values[0]
        return ' | '.join(values)


    def build_mcf_dict(self, g: Graph, mapping: Dict[str, str], dataset_uri: Optional[str] = None) -> Dict[str, Any]:
        """
        Build an MCF-compatible nested dict from the provided graph.

        :param g: rdflib.Graph containing DCAT metadata
        :param mapping: dict mapping source DCAT/DCT property (qname or URI) to
                        a dot-separated MCF path (e.g. 'identification.title')
        :param dataset_uri: optional URI to focus extraction on a single dataset
        :returns: nested dict suitable for YAML serialization according to pygeometa's MCF
        """
        # Identify dataset node
        dataset_node = None
        if dataset_uri:
            dataset_node = URIRef(dataset_uri)
        else:
            for s, p, o in g.triples((None, RDF.type, DCAT['Dataset'])):
                dataset_node = s
                break
            if dataset_node is None:
                # fallback to first subject found in the graph
                for s, p, o in g.triples((None, None, None)):
                    dataset_node = s
                    break

        if dataset_node is None:
            raise ValueError('No dataset node found in the provided graph')

        mcf: Dict[str, Any] = {}

        for src_prop, tgt_path in mapping.items():
            prop_ref = self._to_uriref(src_prop)
            values = [o for o in g.objects(subject=dataset_node, predicate=prop_ref)]
            if not values or len(values) == 0:
                continue
            
            if tgt_path in INTL_MCF_FIELDS:
                lang_map = self._collect_literals_by_lang(values)
                # Convert lists to single scalar per language according to MCF core schema
                scalar_lang_map: Dict[str, str] = {}
                for lang, vals in lang_map.items():
                    scalar_lang_map[(lang or 'eng')] = self._join_lang_values(vals)
            else:
                scalar_lang_map = g.qname(values[0]) if isinstance(values[0], URIRef) else values[0]

            # Insert into nested mcf by splitting tgt_path
            parts = tgt_path.split('.')
            cur = mcf
            for part in parts[:-1]:
                cur = cur.setdefault(part, {})
            final_key = parts[-1]

            existing = cur.get(final_key)
            if existing is None or tgt_path not in INTL_MCF_FIELDS:
                # set the language-keyed scalar mapping
                cur[final_key] = scalar_lang_map
            else:
                # merge: preserve existing languages and overwrite/append others
                for lang, val in scalar_lang_map.items():
                    if lang in existing and existing[lang]:
                        # if an existing value is present, join with the new one
                        existing[lang] = existing[lang] + ' | ' + val
                    else:
                        existing[lang] = val
                cur[final_key] = existing

        return mcf


    def import_(self, metadata: str) -> dict:
        """
        Import metadata into MCF

        :param metadata: string of metadata content

        :returns: `dict` of MCF content
        """

        # Either xml or jsonld

        g = self.parse_dcat_content(metadata)
        return self.build_mcf_dict(g, DEFAULT_MAPPING, dataset_uri=None)


    def write(self, mcf: dict, stringify: str = True) -> Union[dict, str]:
        """
        Write MCF to DCAT

        :param mcf: dict of MCF content model
        :param stringify: whether to return a string representation (default)
                          else native (dict, etree)

        :returns: `dict` or `str` of MCF as a DCAT representation
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
            "keywords": [],
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
                                        if k5 in dcat:
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
            elif (key in ['distributor', 'contact']):
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

        if stringify:
            return json_dumps(dcat)

        return dcat
