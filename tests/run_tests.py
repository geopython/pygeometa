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
# Copyright (c) 2015 Government of Canada
# Copyright (c) 2016 ERT Inc.
# Copyright (c) 2017 Tom Kralidis
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

import datetime
import os
import unittest

from six import text_type
import yaml

from pygeometa.core import (read_mcf, pretty_print, render_template,
                            get_charstring, get_supported_schemas,
                            normalize_datestring,
                            prune_distribution_formats,
                            prune_transfer_option, MCFReadError)

THISDIR = os.path.dirname(os.path.realpath(__file__))


def msg(test_id, test_description):
    """convenience function to print out test id and desc"""
    return '%s: %s' % (test_id, test_description)


class PygeometaTest(unittest.TestCase):
    """Test suite for package pygeometa"""
    def setUp(self):
        """setup test fixtures, etc."""

        print(msg(self.id(), self.shortDescription()))

    def tearDown(self):
        """return to pristine state"""

        pass

    def test_read_mcf(self):
        """Test reading MCFs, strings or dict"""

        # test as file
        with self.assertRaises(IOError):
            mcf = read_mcf(get_abspath('../404.yml'))

        mcf = read_mcf(get_abspath('../sample.yml'))
        self.assertIsInstance(mcf, dict, 'Expected dict')

        # test MCF section
        self.assertTrue('version' in mcf['mcf'], 'Expected MCF version')
        self.assertTrue('metadata' in mcf, 'Expected metadata section')

        # test as string
        with open(get_abspath('../sample.yml')) as fh:
            mcf_string = fh.read()

        mcf = read_mcf(mcf_string)
        self.assertTrue('metadata' in mcf, 'Expected metadata section')

        # test as dict
        mcf_dict = yaml.load(mcf_string)
        mcf = read_mcf(mcf_dict)
        self.assertTrue('metadata' in mcf, 'Expected metadata section')

    def test_mcf_version(self):
        """Test MCF version validation"""

        with self.assertRaises(MCFReadError):
            read_mcf(get_abspath('missing-version.yml'))

        with self.assertRaises(MCFReadError):
            read_mcf(get_abspath('bad-version.yml'))

    def test_mcf_model(self):
        """test mcf model and types"""

        mcf = read_mcf(get_abspath('../sample.yml'))
        self.assertIsInstance(mcf['identification']['dates'], dict,
                              'Expected list')
        self.assertIsInstance(mcf['identification']['keywords'], dict,
                              'Expected dict')
        self.assertIsInstance(mcf['identification']['topiccategory'], list,
                              'Expected list')
        self.assertIsInstance(mcf['contact'], dict, 'Expected dict')
        self.assertIsInstance(mcf['distribution'], dict, 'Expected dict')

    def test_pretty_print(self):
        """Test pretty-printing"""

        xml = render_template(get_abspath('../sample.yml'), 'iso19139')
        xml2 = pretty_print(xml)

        self.assertIsInstance(xml2, text_type, 'Expected unicode string')
        self.assertEqual(xml2[-1], '>', 'Expected closing bracket')
        self.assertTrue(xml2.startswith('<?xml'), 'Expected XML declaration')

    def test_get_charstring(self):
        """Test support of unilingual or multilingual value(s)"""

        values = get_charstring('title', {'title': 'foo'}, 'en')
        self.assertEqual(values, ['foo', None], 'Expected specific values')

        values = get_charstring('title',
                                {'title_en': 'foo', 'title_fr': 'bar'},
                                'en', 'fr')
        self.assertEqual(values, ['foo', 'bar'], 'Expected specific values')

        values = get_charstring('title',
                                {'title': 'foo', 'title_fr': 'bar'},
                                'en', 'fr')
        self.assertEqual(values, ['foo', 'bar'], 'Expected specific values')

        values = get_charstring('title',
                                {'title_fr': 'foo', 'title_en': 'bar'},
                                'fr', 'en')
        self.assertEqual(values, ['foo', 'bar'], 'Expected specific values')

        values = get_charstring('title',
                                {'title_fr': 'foo', 'title_en': 'bar'}, 'fr')
        self.assertEqual(values, ['foo', None], 'Expected specific values')

        values = get_charstring('notfound',
                                {'title_fr': 'foo', 'title_en': 'bar'}, 'fr')
        self.assertEqual(values, [None, None], 'Expected specific values')

    def test_normalize_datestring(self):
        """Test datestring utility"""

        date_value = normalize_datestring(2013)
        self.assertIsInstance(date_value, str)

    def test_prune_distribution_formats(self):
        """Test deriving unique distribution formats"""

        formats = {
            'wms': {
                'format_en': 'image', 'format_fr': 'image', 'format_version': 2
            },
            'wfs': {
                'format_en': 'GRIB2', 'format_fr': 'GRIB2', 'format_version': 2
            },
            'wcs': {
                'format_en': 'GRIB2', 'format_fr': 'GRIB2', 'format_version': 2
            }
        }

        new_formats = prune_distribution_formats(formats)

        self.assertEqual(len(new_formats), 2,
                         'Expected 2 unique distribution formats')

    def test_prune_transfer_option(self):
        """Test deriving unique trasnfer options"""

        language = "eng; CAN"
        unique_transfer = {
            'waf_eng-CAN': {
                'name': 'Datamart'
            },
            'wms_eng-CAN': {
                'name': 'GeoMet'
            },
            'wms_fra-CAN': {
                'name': 'GeoMet french'
            }
        }

        new_transfer = prune_transfer_option(unique_transfer, language)

        self.assertEqual(len(new_transfer), 2,
                         'Expected 2 unique transfer option')

    def test_get_supported_schemas(self):
        """Test supported schemas"""

        schemas = sorted(get_supported_schemas())
        self.assertIsInstance(schemas, list, 'Expected list')
        self.assertEqual(len(schemas), 4, 'Expected 4 supported schemas')
        self.assertEqual(schemas,
                         sorted(['iso19139', 'iso19139-hnap', 'wmo-cmp',
                                 'wmo-wigos']),
                         'Expected exact list of supported schemas')

    def test_render_template(self):
        """test template rendering"""

        test_mcf_paths = [
            '../sample.yml',
            'unilingual.yml',
            'nil-identification-language.yml'
        ]

        for mcf_path in test_mcf_paths:
            xml = render_template(get_abspath(mcf_path), 'iso19139')
            self.assertIsInstance(xml, text_type, 'Expected unicode string')

            # no schema provided
            with self.assertRaises(RuntimeError):
                render_template(get_abspath(mcf_path))

            # bad schema provided
            with self.assertRaises(RuntimeError):
                xml = render_template(get_abspath(mcf_path), 'bad_schema')

            # bad schema_local provided
            with self.assertRaises(RuntimeError):
                xml = render_template(get_abspath(mcf_path),
                                      schema_local='/bad_schema/path')

            # good schema_local provided
            xml = render_template(get_abspath(mcf_path),
                                  schema_local=get_abspath('sample_schema'))

    def test_nested_mcf(self):
        """test nested mcf support"""

        mcf = read_mcf(get_abspath('child.yml'))

        self.assertEqual(mcf['metadata']['identifier'], 5678,
                         'Expected specific identifier')

        self.assertEqual(mcf['distribution']['waf']['type'], 'WWW:LINK',
                         'Expected specific distribution type')

        self.assertEqual(mcf['distribution']['waf']['url'],
                         'http://example.org/waf',
                         'Expected specific distribution url')

        self.assertEqual(mcf['metadata']['datestamp'],
                         datetime.date(2011, 11, 11),
                         'Expected specific metadata datestamp')

        self.assertIsInstance(mcf, dict, 'Expected dict')

    def test_deep_nested_mcf(self):
        """test deep nested mcf support"""

        mcf = read_mcf(get_abspath('deep-nest-child.yml'))

        self.assertEqual(mcf['metadata']['identifier'], 'MYID',
                         'Expected specific identifier')

        self.assertEqual(mcf['identification']['title_en'], 'child title',
                         'Expected specific title')
        self.assertEqual(mcf['distribution']['waf']['url'],
                         'http://dd.meteo.gc.ca', 'Expected specific URL')

        self.assertEqual(mcf['contact']['main']['positionname'],
                         'Senior Systems Scientist', 'Expected specific name')

    def test_pre1900_dates(self):
        """test datestrings that are pre-1900"""

        xml = render_template(get_abspath('dates-pre-1900.yml'), 'iso19139')
        self.assertIsInstance(xml, text_type, 'Expected unicode string')

    def test_wmo_wigos(self):
        """test WMO WIGOS Metadata support"""

        mcf = read_mcf(get_abspath('../sample-wmo-wigos.yml'))
        self.assertEqual(len(mcf['facility'].keys()), 1)
        self.assertEqual(
            len(mcf['facility']['first_station']['spatiotemporal']), 1)


def get_abspath(filepath):
    """helper function absolute file access"""

    return os.path.join(THISDIR, filepath)


if __name__ == '__main__':
    unittest.main()
