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
# Copyright (c) 2025 Tom Kralidis, Jiarong Li, Paul van Genuchten
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

from datetime import date, datetime
import logging
import os
import json
from typing import Union
import uuid

from pygeometa import __version__
from pygeometa.core import get_charstring
from pygeometa.helpers import json_dumps
from pygeometa.schemas.base import BaseOutputSchema

THISDIR = os.path.dirname(os.path.realpath(__file__))

LOGGER = logging.getLogger(__name__)


class OpenAireOutputSchema(BaseOutputSchema):
    """OpenAire: record schema"""

    def __init__(self):
        """
        Initialize object

        :returns: pygeometa.schemas.base.BaseOutputSchema
        """

        description = 'OpenAire'

        super().__init__('openaire', description, 'json', THISDIR)

    def import_(self, metadata: str) -> dict:
        """
        Import metadata into MCF

        :param metadata: string of metadata content

        :returns: `dict` of MCF content
        """

        # Initialized mcf
        mcf = {
            'mcf': {
                'version': '1.0',
            },
            'metadata': {},
            'identification': {},
            'contact': {},
            'tag': 'test'
        }

        # Process metadata (convert XML to JSON if needed)
        metadata = xml_to_json(metadata)
        md = json.loads(metadata)

        if md is None:
            LOGGER.info('invalid openaire metadata')
            return mcf
        

        header_ = md.get('header')
        metadata_ = md.get('results')[0]  

        # mcf: metadata

        pids_ = metadata_.get('pids', [])
        originIds_ = metadata_.get('originalIds', [])
        id_ = metadata_.get('id')

        children_instances_ = metadata_.get('instances')
        main_id_, altIds_, main_instance_ = process_id_and_instance(pids_, originIds_, id_, children_instances_)

        if main_id_:
            mcf['metadata']['identifier'] = main_id_

        if altIds_:
            mcf['metadata']['additional_identifiers'] = altIds_

        project_ = metadata_.get('projects')
        if project_ is not None and isinstance(project_, list):
            rel_project = []
            for p in project_:
                pids = p.get('pids', [])
                if pids is None or len(pids) == 0:
                    continue
                pid = pids[0]
                pro_dict = {'identifier': pid.get('value'), 'scheme': pid.get('scheme'), 'type': 'project'}
                rel_project.append(pro_dict)
            if len(rel_project) > 0:
                mcf['metadata']['relations'] = rel_project

        if main_instance_:
            instance_type_ = main_instance_.get('type')
            if instance_type_:
                mcf['metadata']['hierarchylevel'] = instance_type_
        
        date_of_collection = metadata_.get('dateOfCollection')
        if date_of_collection:
            mcf['metadata']['datestamp'] = metadata_.get('dateOfCollection')

        if main_instance_:
            urls = main_instance_.get('urls')
            if urls:
                mcf['metadata']['dataseturi'] = urls[0]

        # mcf: identification
        language_ = metadata_.get('language', {}).get('code')
        if language_:
            mcf['identification']['language'] = language_
        
        main_title = metadata_.get('mainTitle')
        # subtitle also exists
        if main_title:
            mcf['identification']['title'] = main_title
        
        description_ = metadata_.get('descriptions')
        if description_:
            mcf['identification']['abstract'] = description_[0]

        version_ = metadata_.get('version')
        if version_:
            mcf['identification']['edition'] = version_

        ## topiccategory

        right_ = metadata_.get('bestAccessRight', {}).get('label')
        instance_right_ = None
        if main_instance_:
            instance_right_ = main_instance_.get('accessRight', {}).get('label')
        if right_ is not None and right_ != 'unspecified':
            mcf['identification']['rights'] = right_
        elif instance_right_ is not None and instance_right_ != 'unspecified':
            mcf['identification']['rights'] = instance_right_
        
        if main_instance_:
            license_ = main_instance_.get('license')
            if license_:
                mcf['identification']['license'] = {'name': license_, 'url': ''}
        
        ## url
        dates_dict = {}
        p_date = metadata_.get('publicationDate')
        e_date = metadata_.get('embargoEndDate')
        if p_date:
            dates_dict['publication'] = p_date
        if e_date:
            dates_dict['embargoend'] = e_date
        if dates_dict:
            mcf['identification']['dates'] = dates_dict


        subjects_ = metadata_.get('subjects')
        if isinstance(subjects_, dict):
            mcf['identification']['keywords'] = process_keywords([subjects_])
        elif isinstance(subjects_, list):
            mcf['identification']['keywords'] = process_keywords(subjects_)

        ## contact point
        authors_ = metadata_.get('authors', [])
        orgs_ = metadata_.get('organizations', [])
        authors_ = authors_ or []
        orgs_ = orgs_ or []
        contact_ = authors_ + orgs_
        if len(contact_) > 0:
            mcf['contact'] = process_contact(contact_)

        return mcf

    def write(self, mcf: dict, stringify: str = True) -> Union[dict, str]:
        """
        Write outputschema to JSON string buffer

        :param mcf: dict of MCF content model
        :param stringify: whether to return a string representation (default)
                          else native (dict, etree)

        :returns: `dict` or `str` of MCF as Schema.org
        """

        # no write implementation for now

        return 'test'
      
        # return None

def xml_to_json(content: str) -> str:
    """
    Convert XML to JSON if content is detected as XML
    
    Write it later
    """
    return content


def process_id_and_instance(pids: list, originIds: list, id: str, instances: list) -> tuple[str, list, dict]:
    """
    Get the main_id, alternative_ids and main_instance from the input data
    
    Alternative ids are the unique ids from pids and originIds
    
    Main id is the first doi from pids, otherwise the first pid, 
    otherwise a doi from originId, otherwise an http url from originId, otherwise the first originId.

    main_instance is the first instance with the matched id of main_id, otherwise the first instance.

    """

    # altids and main_id
    pids_schemevalue = None
    if pids is not None:
        first_id = pids[0]
        main_id = first_id.get('value') if first_id else None
        if len(pids) > 1:
            for i in pids:
                if i.get('scheme') == "doi":
                    main_id = i.get('value')
                    break
        pids_schemevalue = [
        {
        'identifier': i.get('value'),
        'scheme': i.get('scheme')
         }
        for i in pids]
    elif originIds is not None:
        main_id = next((item for item in originIds if item.startswith('10.')), None)
        if main_id is None:
            main_id = next((item for item in originIds if item.startswith('http')), None)
        if main_id is None:
            main_id = originIds[0]
    elif id is not None:
        main_id = id
    else:
        LOGGER.error('no valid identifier')
        main_id = None
    
    origin_and_ids = originIds + [id] if originIds else [id]
    origin_and_ids_uni = list(set(origin_and_ids)) if origin_and_ids is not None else []

    if pids_schemevalue:
        pids_values = [i.get('identifier') for i in pids_schemevalue]
        for i in origin_and_ids_uni:
            if i not in pids_values and i is not None:
                pids_schemevalue.append({
                'identifier': i,
                'scheme': None
                })
    else:
        pids_schemevalue = [
        {
            'identifier': i,
            'scheme': None
        }
        for i in origin_and_ids_uni
        ]
     
    # instance
    if instances is None or len(instances) == 0:
        return main_id, pids_schemevalue, None
    
    # get the instance matched with the main id
    main_instance = instances[0]
    for ins in instances:
        pid = ins.get('pid', {})
        if isinstance(pid, list): # instance has multiple pid
            pid_values = [i.get('value') for i in pid]
            if main_id in pid_values:
                main_instance = ins
                break
        elif isinstance(pid, dict): # instance has one pid
            if pid.get('value') == main_id:
                main_instance = ins
                break
        else:
            continue
    
    return main_id, pids_schemevalue, main_instance
    
def process_keywords(subjects: list) -> dict:
    """
    convert openaire keywords to mcf keywords

    group keywords by scheme
    
    """
    unique_scheme = list(set([s.get('subject', {}).get('scheme') for s in subjects]))

    scheme_uuid_dict = {scheme: str(uuid.uuid4()) for scheme in unique_scheme}

    keywords_dict = {
    value: {
        'keywords': [],
        'vocabulary': {
            'name': key
        }
    }
    for key, value in scheme_uuid_dict.items()
    }

    for s in subjects:
        s_value = s.get('subject')
        for k, v in keywords_dict.items():
            if s_value.get('scheme') == v.get('vocabulary', {}).get('name'):
                v['keywords'].append(s_value.get('value'))
                break 
    return keywords_dict


def process_contact(contact_list: list) -> dict:
    """
    Process authors and organizations into MCF contact format
    
    :param authors: list of author objects
    :param orgs: list of organization objects
    
    :returns: dict with UUID keys and contact point values
    """
    contact_dict = {}
    
    for contact in contact_list:
        contact_uuid = str(uuid.uuid4())
        # Initialize contact point structure
        contactpoint_dict = {
            'individualname': '',
            'organization': '',
            'url': ''
        }
        # Process authors
        if 'fullName' in contact:
            contactpoint_dict['individualname'] = contact.get('fullName')
            pid = contact.get('pid')
            if pid is not None and pid.get('id') is not None:
                pid_scheme = pid.get('id', {}).get('scheme')
                pid_value = pid.get('id', {}).get('value')
                if pid_scheme is not None and pid_value is not None:
                    contactpoint_dict['url'] = id2url(pid_scheme, pid_value)
        
        # Process organizations
        elif 'legalName' in contact:
            org_name = contact.get('legalName') 
            contactpoint_dict['organization'] = org_name
            pids = contact.get('pids', [])
            if pids is not None:
                for p in pids:
                    if p.get('scheme').lower() == 'ror':
                        contactpoint_dict['url'] = id2url(p.get('scheme'), p.get('value'))
                        break
                    elif p.get('scheme').lower() == 'grid':
                        contactpoint_dict['url'] = id2url(p.get('scheme'), p.get('value'))
                        break
                    elif p.get('scheme').lower() == 'wikidata':
                        contactpoint_dict['url'] = id2url(p.get('scheme'), p.get('value'))
                        break
                    elif p.get('scheme').lower() == 'isni':
                        contactpoint_dict['url'] = id2url(p.get('scheme'), p.get('value'))
                        break      
        # Add to contactpoint dict
        if contactpoint_dict['individualname'] or contactpoint_dict['organization']:
            contact_dict[contact_uuid] = contactpoint_dict
    
    return contact_dict



def id2url(scheme: str, id: str) -> str:
    """
    Convert orcid, wikidata, ror or grid value to url
    """
    if scheme.lower() == 'orcid':
        return 'https://orcid.org/' + id
    elif scheme.lower() == 'ror':
        return id
    elif scheme.lower() == 'grid':
        return id
    elif scheme.lower() == 'wikidata':
        return 'https://www.wikidata.org/wiki/' + id
    elif scheme.lower() == 'isni':
        return 'https://isni.org/isni/' + id
    else:
        return None

