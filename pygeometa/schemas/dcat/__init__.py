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

import os
import json
import logging
import uuid
from shapely import from_wkt
from typing import Dict, Any, List, Optional, Union
from rdflib import Graph, URIRef, Namespace, Literal, BNode
from rdflib.namespace import RDF, SKOS, DCTERMS, DCAT, PROV, FOAF

from pygeometa.helpers import json_dumps
from pygeometa.schemas.base import BaseOutputSchema

LOGGER = logging.getLogger(__name__)
THISDIR = os.path.dirname(os.path.realpath(__file__))

# Namespaces
SCHEMA = Namespace('http://schema.org/')
ADMS = Namespace('http://www.w3.org/ns/adms#')
LOCN = Namespace('http://www.w3.org/ns/locn#')
VCARD = Namespace('http://www.w3.org/2006/vcard/ns#')

# Default DCAT-AP 3.1 context URL for missing JSON-LD contexts
_DCAT_AP_CONTEXT_URL = "https://github.com/SEMICeu/DCAT-AP/raw/refs/heads/master/releases/3.0.1/context/dcat-ap.jsonld"  # noqa

# default mapping aligning common DCAT/DCT terms to MCF paths
DEFAULT_MAPPING = {
    'dct:title':        'identification.title',
    'dct:description':  'identification.abstract',
    'dct:abstract':     'identification.abstract',
    'dct:license':      'identification.licence',
    'dct:language':     'metadata.language',
    'dct:modified':     'identification.modification',
    'dct:created':      'identification.creation',
    'dct:issued':       'identification.publication',
    'dct:source':       'identification.source',
    'dct:accessRights': 'identification.rights',
    'dct:conformsTo':   'identification.conformsto',
    'dct:format':       'identification.format',
    'dcat:landingPage': 'identification.landingpage',
    'dct:accrualPeriodicity': 'identification.maintenancefrequency',
    'dcat:version':     'identification.edition',
    'dct:identifier':   'metadata.identifier',
    'dct:isPartOf':     'metadata.relations',
    'dcat:hasVersion':  'metadata.relations',
    'dcat:inSeries':    'metadata.relations',
    'dct:isReferencedBy': 'metadata.relations',
    'dct:provenance':   'identification.provenance',
    'dct:relation':     'metadata.relations',
    'adms:sample':      'identification.sample',
    'dcat:spatialResolutionInMeters': 'identification.spatialResolutionInMeters', # noqa
    'dcat:temporalResolution': 'identification.temporalResolution',
    'dct:type':         'metadata.hierarchylevel',
    'adms:versionNotes': 'identification.edition',
    'prov:wasGeneratedBy': 'dataquality.lineage'
}

DISTRIBUTION_MAPPING = {
    "dct:format": "type",
    "dct:title": "name",
    "dct:description": "description",
    "dcat:accessService": "url",
    "dcat:downloadURL": "url",
    "dcat:byteSize": "size",
    "dcat:mediaType": "type",
    "dcat:accessURL": "url",
    "dcat:landingPage": "url",
    "dct:rights": "rights",
    "dct:license": "license",
    "dct:identifier": "identifier",
    "dcat:packageFormat": "type"
}

CONTACT_MAPPING = {
    "foaf:name": "individualname",
    "foaf:mbox": "email",
    "foaf:homepage": "url",
    "locn:address": "address",
    "vcard:hasEmail": "email",
    "vcard:fn": "individualname",
    "vcard:hasAddress": "address",
    "vcard:country-name": "country",
    "vcard:locality": "city",
    "vcard:postal-code": "postcode",
    "vcard:street-address": "address",
    "vcard:hasTelephone": "phone",
    "vcard:nickname": "individualname",
}

INTL_MCF_FIELDS = ["identification.abstract", "identification.title"]

# Parser formats to try in order
_PARSER_FORMATS = [
    'json-ld',
    'xml',
    'turtle',
    'n3',
    'trig',
]


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
                LOGGER.debug('Adding DCAT context to json-ld document')
                data['@context'] = _DCAT_AP_CONTEXT_URL
                return json.dumps(data)
        except Exception:
            pass
        return content

    def _parse_dcat_content(self, content: str, base: Optional[str] = None) -> Graph: # noqa
        """
        Parse content into an rdflib.Graph, trying a set of common RDF serialisations. # noqa

        Raises ValueError if none of the attempted formats succeed.
        """
        last_exc = None

        for fmt in _PARSER_FORMATS:
            try:
                g = Graph()
                g.parse(data=content, format=fmt, publicID=base)
                return g
            except Exception as exc:
                last_exc = exc
        raise ValueError(f"Unable to parse content as a known RDF serialisation. Last error: {last_exc}") # noqa

    def _get_keywords(self, g, main):
        qry = f"""
            PREFIX dcat:  <http://www.w3.org/ns/dcat#>
            PREFIX dct:   <http://purl.org/dc/terms/>
            PREFIX skos:  <http://www.w3.org/2004/02/skos/core#>

            SELECT DISTINCT
                ?prop
                ?term
                ?keywordLiteral
                ?prefLabel
                ?scheme
                ?schemeTitle
            WHERE {{
                VALUES ?dataset {{ <{main}> }}
                VALUES ?prop {{ dcat:keyword dct:subject dcat:theme }}
                ?dataset ?prop ?term .

                # literal → string, resource → ""
                BIND( IF(isLiteral(?term), STR(?term), "") AS ?keywordLiteral )

                OPTIONAL {{
                    FILTER(!isLiteral(?term))
                    ?term skos:prefLabel ?prefLabel .
                }}
                OPTIONAL {{
                    FILTER(!isLiteral(?term))
                    ?term (skos:inScheme | skos:conceptScheme) ?scheme .
                    ?scheme dct:title ?schemeTitle .
                }}
                }}
            ORDER BY ?prop ?term
            """
        keywords = {}
        for row in g.query(qry):
            rscheme = 'default'
            if row[5]:
                rscheme = str(row[5])
            if rscheme not in keywords.keys():
                keywords[rscheme] = {'keywords': []}
            keywords[rscheme]['keywords'].append(str(row[3] or row[2] or row[1])) # noqa
        return keywords

    def _to_uriref(self, key: str) -> URIRef:
        """Convert a mapping key into a URIRef.

        Accepts full URIs or qnames like 'dct:title' or 'dcat:keyword'.
        Unknown prefixes default to the DCTERMS namespace.
        """
        if key.startswith('http://') or key.startswith('https://'):
            return URIRef(key)
        if ':' in key:
            prefix, local = key.split(':', 1)
            ns = {
                'dct':  DCTERMS,
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
        return DCTERMS[key]

    def _collect_literals_by_lang(self, values: List[Any], g, deflang) -> Dict[str, List[str]]: # noqa
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
                s = str(self._get_rdfval(g, v))
                lang = deflang
            if s not in (None, ''):
                out.setdefault(lang, []).append(s)
        return out

    def _identify_main_entity(self, g: Graph):
        """
        The main entity can be Dataset, DataService
        Other entities can be skos-concept, vcard:organization,
        dcat.distribution, dcat.catalogue or dcat.catalogueRecord
        """
        for s, p, o in g.triples((None, RDF.type, None)):
            if o in (DCAT.Dataset, DCAT.DataService, DCAT.Resource):
                LOGGER.debug(f'Main type is {str(o)}, {str(s)}')
                return s
        # fallback to first subject of any type
        for s, p, o in g.triples((None, RDF.type, None)):
            LOGGER.debug(f'No main type found, use first {str(o)}, {str(s)}')
            return s
        # fallback to any subject
        for s, p, o in g.triples((None, None, None)):
            LOGGER.debug(f'No type found, using first subject {str(s)}')
            return s

    def _get_contact(self, g, main_entity, lang, type):
        pred_ref = self._to_uriref(type)
        values = [o for o in g.objects(subject=main_entity, predicate=pred_ref)] # noqa
        if not values or len(values) == 0:
            return {}
        contacts = {}
        for contact in values:
            cid = str(uuid.uuid1())
            contacts[cid] = self._build_mcf_dict(g, CONTACT_MAPPING, contact, lang) # noqa
            if contacts[cid]:
                contacts[cid]['role'] = type.split('.').pop()
        return contacts

    def _get_rdfval(self, g, v):
        # takes the string from literal or uuidref, if it does not resolve
        if isinstance(v, URIRef) or isinstance(v, BNode):
            values = [o for o in g.objects(subject=v, predicate=None)]
            if not values or len(values) == 0:
                return str(v)
            return ", ".join([str(i) for i in values if i != ''])
        else:
            return str(v)

    def _join_arr(self, vals):
        # merges the content of a dict from _extract_literals to a string
        if isinstance(vals, list):
            return " ".join([v for v in vals if isinstance(v, str)])
        if isinstance(vals, dict):
            return "".join([" ".join(v) for v in vals.values() if isinstance(v, list)]) # noqa  

    def _join_vals_of_dict(self, adict):
        """
        for any dict with lists as values, merge the values to a single string
        """
        vls = []
        if isinstance(adict, dict):
            for v in adict.values():  # dict of pred:obj
                if not isinstance(v, list):
                    v = [v]
                for v2 in v:  # list of vals
                    if v2 not in vls:  # prevent duplicates
                        vls.append(v2)
        elif isinstance(adict, list):
            for v2 in adict:
                if v2 not in vls:  # prevent duplicates
                    vls.append(v2)
        else:
            if adict not in vls:  # prevent duplicates
                vls.append(adict)
        return vls

    def _build_mcf_dict(self, g: Graph, mapping: Dict[str, str], main_entity, lang: str) -> Dict[str, Any]: # noqa
        """
        Build an MCF-compatible nested dict from the provided graph.

        :param g: rdflib.Graph containing DCAT metadata
        :param mapping: dict mapping source DCAT/ DCTERMS property (qname or URI) to
                        a dot-separated MCF path (e.g. 'identification.title')
        :param dataset_uri: optional URI to focus extraction on a single dataset
        :returns: nested dict suitable for YAML serialization according to pygeometa's MCF # noqa
        """
        mcf: Dict[str, Any] = {}

        for src_prop, tgt_path in mapping.items():
            prop_ref = self._to_uriref(src_prop)
            values = [o for o in g.objects(subject=main_entity, predicate=prop_ref)] # noqa
            if not values or len(values) == 0:
                continue

            LOGGER.debug(f'Parsing {str(prop_ref)} to {tgt_path} as {values}')
            if tgt_path in INTL_MCF_FIELDS:
                lang_map = self._collect_literals_by_lang(values, g, lang)
                # Convert lists to single scalar per language
                scalar_lang_map: Dict[str, str] = {}
                for alang, vals in lang_map.items():
                    if not isinstance(vals, list):
                        vals = [vals]
                    vals2 = []
                    for v in vals:
                        v2 = self._extract_literals(g, v)
                        for v2 in self._join_vals_of_dict(v):
                            vals2.append(v2)
                    if len(vals2) > 0:
                        scalar_lang_map[(alang or lang)] = " ".join([v for v in vals2 if v != '']) # noqa
                if len(scalar_lang_map.keys()) == 0:
                    scalar_lang_map = ""
                elif len(scalar_lang_map.keys()) == 1:
                    scalar_lang_map = list(scalar_lang_map.values())[0]
            else:
                vals2 = []
                for v in values:
                    v2 = self._extract_literals(g, v)
                    for v2 in self._join_vals_of_dict(v):
                        vals2.append(v2)
                if len(vals2) > 0:
                    scalar_lang_map = " ".join([v for v in vals2 if v != ''])

            # Insert into nested mcf by splitting tgt_path
            parts = tgt_path.split('.')
            cur = mcf
            for part in parts[:-1]:
                cur = cur.setdefault(part, {})
            final_key = parts[-1]

            existing = cur.get(final_key)
            if existing is None:
                # set the language-keyed scalar mapping
                cur[final_key] = scalar_lang_map
            else:
                if tgt_path in INTL_MCF_FIELDS:
                    # merge: preserve existing languages and overwrite/append others # noqa
                    for lang, val in scalar_lang_map.items():
                        if lang in existing and existing[lang]:
                            # if an existing value is present, join with the new one # noqa
                            existing[lang] = existing[lang] + ' | ' + val
                        else:
                            existing[lang] = val
                else:
                    existing = existing + ' | ' + scalar_lang_map
                cur[final_key] = existing

        return mcf

    def _get_lang(self, g: Graph, main_entity):
        values = [o for o in g.objects(subject=main_entity, predicate= DCTERMS.language)] # noqa
        lang = str(next(iter(values), ''))
        if '/' in lang or '#' in lang:  # sometimes lang is a URI
            lang = lang.split('/').pop().split('#').pop()
        LOGGER.debug(f'Languag identified: {lang}')
        return lang

    def _get_distribution(self, g: Graph, main_entity, lang):
        values = [o for o in g.objects(subject=main_entity, predicate=DCAT.distribution)] # noqa
        if not values or len(values) == 0:
            return {}
        dists = {}
        for dist in values:
            did = str(uuid.uuid1())
            dists[did] = self._build_mcf_dict(g, DISTRIBUTION_MAPPING, dist, lang) # noqa
            LOGGER.debug(f"process distribution {dists[did].get('url')}") # noqa
        return dists

    def _parse_geom(self, geom):
        """
        tries to parse various types of geometry (wkt, bbox)
        """
        if isinstance(geom, list):
            return geom
        try:
            # return the bounds around wkt string, parsed by shapely
            # in some cases asWKT is prepended with <CRS>
            box = geom
            if '>' in geom:
                box = geom.split('>').pop()
                # crs = geom.split('>')[0].replace('<', '')
            return list(from_wkt(box).bounds)
        except Exception as e:
            LOGGER.debug(f'wkt parse {geom} failed, {e}')
        try:  # Try as bbox Array
            geom2 = str(geom)
            geom3 = [c for c in geom2.replace(' ', ', ').split(', ') if c != ''] # noqa
            if len(geom3) == 4:
                return geom3
        except Exception as e:
            LOGGER.debug(f'Geom {geom} can not be parsed, {e}')

        LOGGER.debug(f'Geom {geom} can not be parsed')
        return None

    def _get_rdfvals(self, g, main, type):
        pred_ref = self._to_uriref(type)
        values = [o for o in g.objects(subject=main, predicate=pred_ref)]
        items = []
        for elm in (values or []):
            items2 = self._extract_literals(g, elm, pred_ref)
            if items2:
                items.append(items2)
        return items

    def _extract_literals(self, graph, start_node, pred=''):
        """
        Recursively traverses RDF graph starting from `start_node`,
        collecting all literals encountered.
        """
        results = {}
        visited = set()

        def node_has_triples(node):
            # Returns True if graph has any triples with `node` as subject.
            return any(graph.predicate_objects(node))

        def return_val(predicate, obj):
            if isinstance(obj, Literal):
                results.setdefault(str(predicate), []).append(str(obj))

            elif isinstance(obj, URIRef):
                if node_has_triples(obj):
                    recurse(obj)
                else:
                    # Unresolved URIRef: return it as a string under the pred
                    results.setdefault(str(predicate), []).append(str(obj))

            elif isinstance(obj, BNode):
                if node_has_triples(obj):
                    recurse(obj)
                else:  # Unresolved BNode: skip it
                    None

        def recurse(node):
            if node in visited:
                return
            visited.add(node)
            for predicate, obj in graph.predicate_objects(node):
                if predicate == RDF.type:  # skip type triples
                    continue
                return_val(predicate, obj)

        if node_has_triples(start_node):
            recurse(start_node)
        else:
            return_val(pred, start_node)

        return results

    def import_(self, metadata: str) -> dict:
        """
        Import metadata into MCF

        :param metadata: string of metadata content

        :returns: `dict` of MCF content
        """

        # Try detect if JSON-LD and may need context injection
        try:
            sample = metadata.strip()[:100].lstrip()
            if sample.startswith('{') or sample.startswith('['):
                metadata = self._inject_jsonld_context(metadata)
        except Exception as e:
            LOGGER(f'Intial json check failed, {e}')
        # Either xml, ttl, n3 or jsonld
        g = self._parse_dcat_content(metadata)
        if not g or len(g) == 0:
            raise ValueError('Document is an empty graph')
        main_entity = self._identify_main_entity(g)  # returns None, URI or BN
        if main_entity is None:
            raise ValueError('No main entity found in the provided graph')
        lang = self._get_lang(g, main_entity)
        if not lang:
            lang = 'en'
        mcf = self._build_mcf_dict(g, DEFAULT_MAPPING, main_entity, lang)

        if 'identification' not in mcf:
            raise ValueError(f'Empty document after parsing of main entity {str(main_entity)}') # noqa

        # use identifier if no identifier, else set as additional
        if isinstance(main_entity, URIRef):
            if 'identifier' in mcf.get('metadata', {}):
                if str(main_entity) not in [i.get('identifier') for i in mcf['metadata'].get('additional_identifiers',[])]: # noqa
                    mcf['metadata'].setdefault('additional_identifiers',[]).append({'identifier': str(main_entity)}) # noqa
            else:
                mcf['metadata']['identifier'] = str(main_entity)
        # distributions
        mcf['distribution'] = self._get_distribution(g, main_entity, lang)
        # duplicate license/right to main, if they are not in main
        if 'license' not in mcf['identification']:
            for v in mcf['distribution'].values():
                if 'license' in v:
                    mcf['identification']['license'] = v['license']
                if 'rights' in v and 'rights' not in mcf['identification']:
                    mcf['identification']['rights'] = v['rights']
                break

        # contacts
        for tp in "dct:creator, dct:publisher, dcat:contactPoint".split(', '): # noqa
            for k,v in (self._get_contact(g, main_entity, lang, tp).items() or {}): # noqa
                mcf.setdefault('contact', {})[k] = v
        # dates
        for d in "creation,modification,publication".split(', '):
            if d in mcf['identification'].keys():
                mcf['identification'].setdefault('dates', {})[d] = mcf['identification'].pop(d) # noqa

        # coverage
        geoms = []
        for geom2 in (self._get_rdfvals(g, main_entity, 'dct:spatial') or []):
            for k, v in (geom2 or {}).items():
                if k == str(SKOS.prefLabel):
                    geoms.append({'description': v})
                else:  # various flavour of geom
                    LOGGER.debug(f'Parsing geom for {k}:{v}')
                    for v2 in v:
                        bounds = self._parse_geom(v2)
                        if bounds and len(bounds) == 4:
                            geoms.append({'bbox': bounds, 'crs': 4326})
                if len(geoms) > 0:
                    mcf['identification'].setdefault('extents', {})['spatial'] = geoms # noqa
        temps = []
        for temp in (self._get_rdfvals(g, main_entity, 'dct:temporal') or []):
            temp2 = {}
            for k, v in (temp or {}).items():
                if k == str(DCAT.startDate) or k == str(SCHEMA.startDate):
                    temp2['begin'] = str(next(iter(v), ''))
                elif k == str(DCAT.endDate) or k == str(SCHEMA.endDate):
                    temp2['end'] = str(next(iter(v), ''))
                else:
                    LOGGER.debug(f'Not a known period property {str(k)} for {v}') # noqa
            if 'begin' in temp2 or 'end' in temp2:
                temps.append(temp2)
        mcf['identification'].setdefault('extents', {})['temporal'] = temps

        mcf['identification']['keywords'] = self._get_keywords(g, main_entity)

        return mcf

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
