# -*- coding: iso-8859-15 -*-
# =================================================================
#
# Copyright (c) 2014 Her Majesty the Queen in Right of Canada
#
# Author: Tom Kralidis <tom.kralidis@ec.gc.ca>
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
from ConfigParser import ConfigParser
import logging
import os
import re
from xml.dom import minidom

from jinja2 import Environment, FileSystemLoader
from jinja2.exceptions import TemplateNotFound

__version__ = '0.1.0'

LOGGER = logging.getLogger(__name__)

TEMPLATES = '%s%stemplates' % (os.path.dirname(os.path.realpath(__file__)),
                               os.sep)


def normalize_datestring(datestring):
    """groks date string into ISO8601"""

    if datestring.startswith('$Date'):  # it's an svn Date keyword
        rp = r'\$Date: (?P<date>\d{4}-\d{2}-\d{2}) (?P<time>\d{2}:\d{2}:\d{2})'
        mo = re.match(rp, datestring)
        return '%sT%s' % mo.group('date', 'time')
    return datestring


def read_mcf(mcf):
    """returns dict of ConfigParser object"""

    c = ConfigParser()
    LOGGER.debug('reading {}'.format(mcf))
    with codecs.open(mcf, encoding='utf-8') as fh:
        c.readfp(fh)
        mcf_dict = c.__dict__['_sections']
        if 'base_mcf' in mcf_dict['metadata']:  # overwrite
            base_mcf = read_mcf(mcf_dict['metadata']['base_mcf'])
            mcf_dict.update(base_mcf)
        return mcf_dict


def pretty_print(xml):
    """clean up indentation and spacing"""

    LOGGER.debug('pretty-printing XML')
    val = minidom.parseString(xml)
    return '\n'.join([l for l in
                      val.toprettyxml(indent=' '*2).split('\n') if l.strip()])


def render_template(mcf, schema=None, schema_local=None):
    """convenience function to render Jinja2 template"""

    LOGGER.debug('Evaluating schema path')
    if schema is None and schema_local is None:
        msg = 'schema or schema_local required'
        LOGGER.exception(msg)
        raise RuntimeError(msg)
    if schema_local is None:  # default templates dir
        abspath = '{}{}{}'.format(TEMPLATES, os.sep, schema)
    elif schema is None:  # user-defined
        abspath = schema_local

    LOGGER.debug('Setting up template environment {}'.format(abspath))
    env = Environment(loader=FileSystemLoader(abspath))
    env.filters['normalize_datestring'] = normalize_datestring
    env.globals.update(zip=zip)

    try:
        LOGGER.debug('Loading template')
        template = env.get_template('main.j2')
    except TemplateNotFound:
        msg = 'Missing metadata template'
        LOGGER.exception(msg)
        raise RuntimeError(msg)

    LOGGER.debug('Processing template')
    xml = template.render(record=read_mcf(mcf),
                          software_version=__version__).encode('utf-8')
    return pretty_print(xml)


def get_supported_schemas():
    """returns a list of supported schemas"""

    LOGGER.debug('Generating list of supported schemas')
    return os.listdir(TEMPLATES)
