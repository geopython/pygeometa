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
# Copyright (c) 2017 Government of Canada
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

import codecs
import logging

import click
from configparser import SafeConfigParser
import yaml

LOGGER = logging.getLogger(__name__)


def configparser2yaml(cpfile):
    dict_ = {}
    cp = SafeConfigParser()

    with codecs.open(cpfile, encoding='utf-8') as fh:
        cp.readfp(fh)

    for section in cp.sections():
        if section.startswith('contact:'):  # contacts are now nested
            if 'contact' not in dict_:
                dict_['contact'] = {}
            section2 = dict_['contact'][section.split(':')[1]] = {}
        elif section.startswith('distribution:'):  # distributions now nested
            if 'distribution' not in dict_:
                dict_['distribution'] = {}
            section2 = dict_['distribution'][section.split(':')[1]] = {}
        else:
            section2 = dict_[section] = {}

        for k, v in cp.items(section):
            if section == 'identification':  # keywords are now nested
                if 'keywords' not in section2:
                    section2['keywords'] = {}
                if 'default' not in section2['keywords']:
                    section2['keywords']['default'] = {}
                if 'gc_cst' not in section2['keywords']:
                    section2['keywords']['gc_cst'] = {}
                if 'wmo' not in section2['keywords']:
                    section2['keywords']['wmo'] = {}
                if 'hnap_category_information' not in section2['keywords']:
                    section2['keywords']['hnap_category_information'] = {}
                if 'hnap_category_geography' not in section2['keywords']:
                    section2['keywords']['hnap_category_geography'] = {}
                if 'hnap_category_content' not in section2['keywords']:
                    section2['keywords']['hnap_category_content'] = {}

            if k in ['topiccategory']:
                section2['topiccategory'] = [v]
            if k in ['keywords_en', 'keywords_fr']:
                section2['keywords']['default'][k] = [k2.strip() for k2 in v.split(',')]  # noqa
            if k in ['keywords_gc_cst_en']:
                section2['keywords']['gc_cst']['keywords_en'] = [k2.strip() for k2 in v.split(',')]  # noqa
            if k in ['keywords_gc_cst_fr']:
                section2['keywords']['gc_cst']['keywords_fr'] = [k2.strip() for k2 in v.split(',')]  # noqa
            if k in ['keywords_wmo']:
                section2['keywords']['wmo']['keywords_en'] = [k2.strip() for k2 in v.split(',')]  # noqa
            if k in ['hnap_category_information_en']:
                section2['keywords']['hnap_category_information']['keywords_en'] = [v]  # noqa
                section2['keywords']['hnap_category_information']['keywords_fr'] = [v]  # noqa
            if k in ['hnap_category_geography_en']:
                section2['keywords']['hnap_category_geography']['keywords_en'] = [v]  # noqa
            if k in ['hnap_category_geography_fr']:
                section2['keywords']['hnap_category_geography']['keywords_fr'] = [v]  # noqa
            if k in ['hnap_category_content_en']:
                section2['keywords']['hnap_category_content']['keywords_en'] = [v]  # noqa
            if k in ['hnap_category_content_fr']:
                section2['keywords']['hnap_category_content']['keywords_fr'] = [v]  # noqa

            if k == 'keywords_type':
                section2['keywords']['default'][k] = v
                section2['keywords']['gc_cst'][k] = v
                section2['keywords']['wmo'][k] = v
                section2['keywords']['hnap_category_geography'][k] = v
                section2['keywords']['hnap_category_information'][k] = v
                section2['keywords']['hnap_category_content'][k] = v

            else:
                section2[k] = v

    return yaml.safe_dump(dict_, default_flow_style=False, allow_unicode=True)


@click.command()
@click.option('--mcf',
              type=click.Path(exists=True, resolve_path=True),
              help='Path to old MCF (.ini) file format')
@click.option('--output', type=click.File('w', encoding='utf-8'),
              help='Name of output file')
def migrate(mcf, output):
    if mcf is None:
        raise click.UsageError('Missing arguments')
    else:
        content = configparser2yaml(mcf).decode('utf-8')

        if output is None:
            click.echo_via_pager(content)
        else:
            output.write(content)
