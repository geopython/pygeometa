#        <gmd:MD_Keywords>
#        {% set keywords = get_charstring('keywords', value, record['metadata']['language'], record['metadata']['language_alternate']) %}
#
#        ([['Cloud cover'], ['Couverture nuageuse']], {'keywords_fr': ['Couverture nuageuse'], 'keywords_en': ['Cloud cover']}, 'en', 'fr')
#        ['Couverture nuageuse']
#
#        ([['Cloud cover'], None], {'keywords_fr': ['Couverture nuageuse'], 'keywords_en': ['Cloud cover']}, 'en', 'fra')
#        None


import collections
from datetime import date, datetime
import io
import logging
import os
import pkg_resources
import re
from xml.dom import minidom

import click
from jinja2 import Environment, FileSystemLoader
from jinja2.exceptions import TemplateNotFound
import yaml

import sys


def get_charstring(option, section_items, language,
                   language_alternate=None):
    """convenience function to return unilingual or multilingual value(s)"""

    section_items = dict(section_items)
    option_value1 = None
    option_value2 = None

    if 'language_alternate' is None:  # unilingual
        option_tmp = '{}_{}'.format(option, language)
        if option_tmp in section_items:
            option_value1 = section_items[option_tmp]
        else:
            try:
                option_value1 = section_items[option]
            except KeyError:
                pass  # default=None
    else:  # multilingual
        option_tmp = '{}_{}'.format(option, language)
        if option_tmp in section_items:
            option_value1 = section_items[option_tmp]
        else:
            try:
                option_value1 = section_items[option]
            except KeyError:
                pass  # default=None
        option_tmp2 = '{}_{}'.format(option, language_alternate)
        print option_tmp2
        if option_tmp2 in section_items:
            option_value2 = section_items[option_tmp2]

    return [option_value1, option_value2]

print get_charstring('keywords', {'keywords_en': ['Weather and Climate'], 'keyword_fr': ['Temps et climat']}, 'en', 'fr')