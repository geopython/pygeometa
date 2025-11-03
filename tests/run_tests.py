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
# Copyright (c) 2025 Tom Kralidis
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
import json
import os
import unittest

from jsonschema.protocols import Validator
import yaml

from pygeometa.core import (read_mcf, pretty_print, render_j2_template,
                            get_charstring, import_metadata,
                            normalize_datestring, prune_distribution_formats,
                            prune_transfer_option, MCFReadError,
                            MCFValidationError, SCHEMAS, transform_metadata,
                            validate_mcf)
from pygeometa.helpers import json_dumps
from pygeometa.schemas import (get_supported_schemas, InvalidSchemaError,
                               load_schema)
from pygeometa.schemas.iso19139 import ISO19139OutputSchema
from pygeometa.schemas.ogcapi_records import OGCAPIRecordOutputSchema

from sample_schema import SampleOutputSchema

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
        mcf_dict = yaml.load(mcf_string, Loader=yaml.FullLoader)
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

        iso_os = ISO19139OutputSchema()

        xml = render_j2_template(read_mcf(get_abspath('../sample.yml')),
                                 iso_os.template_dir)
        xml2 = pretty_print(xml)

        self.assertIsInstance(xml2, str, 'Expected unicode string')
        self.assertEqual(xml2[-1], '>', 'Expected closing bracket')
        self.assertTrue(xml2.startswith('<?xml'), 'Expected XML declaration')

    def test_get_charstring(self):
        """Test support of unilingual or multilingual value(s)"""

        values = get_charstring('foo', 'en')
        self.assertEqual(values, ['foo', None], 'Expected specific values')

        values = get_charstring({'en': 'foo', 'fr': 'bar'}, 'en', 'fr')
        self.assertEqual(values, ['foo', 'bar'], 'Expected specific values')

        values = get_charstring({'fr': 'foo', 'en': 'bar'}, 'fr', 'en')  # noqa
        self.assertEqual(values, ['foo', 'bar'], 'Expected specific values')

        values = get_charstring({'fr': 'foo', 'en': 'bar'}, 'fr')
        self.assertEqual(values, ['foo', None], 'Expected specific values')

        values = get_charstring(None, 'fr')
        self.assertEqual(values, [None, None], 'Expected specific values')

    def test_normalize_datestring(self):
        """Test datestring utility"""

        self.assertIsInstance(normalize_datestring(2013), str)

        with self.assertRaises(RuntimeError):
            self.assertIsInstance(normalize_datestring(None), str)

    def test_prune_distribution_formats(self):
        """Test deriving unique distribution formats"""

        formats = {
            'wms': {
                'format_en': 'image',
                'format_fr': 'image',
                'format_version': '2'
            },
            'wfs': {
                'format_en': 'GRIB2',
                'format_fr': 'GRIB2',
                'format_version': '2'
            },
            'wcs': {
                'format_en': 'GRIB2',
                'format_fr': 'GRIB2',
                'format_version': '2'
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
        self.assertEqual(len(schemas), 11,
                         'Expected specific number of supported schemas')
        self.assertEqual(sorted(schemas),
                         sorted(['cwl', 'dcat', 'iso19139', 'iso19139-2',
                                 'iso19139-hnap', 'oarec-record', 'schema-org',
                                 'stac-item', 'wmo-cmp', 'wmo-wcmp2',
                                 'wmo-wigos']),
                         'Expected exact list of supported schemas')

        schemas = get_supported_schemas(include_autodetect=True)
        self.assertEqual(len(schemas), 12,
                         'Expected specific number of supported schemas')
        self.assertIn('autodetect', schemas, 'Expected autodetect in list')

    def test_render_j2_template(self):
        """test template rendering"""

        test_mcf_paths = [
            '../sample.yml',
            'unilingual.yml',
            'nil-identification-language.yml'
        ]

        for mcf_path in test_mcf_paths:

            iso_os = ISO19139OutputSchema()

            # working template directory
            xml = render_j2_template(read_mcf(get_abspath(mcf_path)),
                                     iso_os.template_dir)
            self.assertIsInstance(xml, str, 'Expected unicode string')

            # no template directory or local schema provided
            with self.assertRaises(RuntimeError):
                render_j2_template(read_mcf(get_abspath(mcf_path)))

            # bad template directory provided
            with self.assertRaises(RuntimeError):
                xml = render_j2_template(read_mcf(get_abspath(mcf_path)),
                                         'bad_dir')

            # bad j2 template_dir provided
            with self.assertRaises(RuntimeError):
                xml = render_j2_template(read_mcf(get_abspath(mcf_path)),
                                         template_dir='/bad_schema/path')

            # good j2 template_dir provided
            xml = render_j2_template(read_mcf(get_abspath(mcf_path)),
                                     template_dir=get_abspath('sample_schema_j2'))  # noqa

            # good sample output schema
            s_os = SampleOutputSchema()
            _ = s_os.write(read_mcf(get_abspath(mcf_path)))

    def test_nested_mcf(self):
        """test nested mcf support"""

        mcf = read_mcf(get_abspath('child.yml'))

        self.assertEqual(mcf['metadata']['identifier'], 's5678',
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

        self.assertEqual(mcf['contact']['pointOfContact']['positionname'],
                         'Senior Systems Scientist', 'Expected specific name')

    def test_pre1900_dates(self):
        """test datestrings that are pre-1900"""

        iso_os = ISO19139OutputSchema()

        xml = render_j2_template(read_mcf(get_abspath('dates-pre-1900.yml')),
                                 iso_os.template_dir)
        self.assertIsInstance(xml, str, 'Expected unicode string')

    def test_broken_yaml(self):
        """test against broken YAML"""

        iso_os = ISO19139OutputSchema()
        with self.assertRaises(MCFReadError):
            render_j2_template(read_mcf(get_abspath('broken-yaml.yml')),
                               iso_os.template_dir)

    def test_wmo_wigos(self):
        """test WMO WIGOS Metadata support"""

        mcf = read_mcf(get_abspath('../sample-wmo-wigos.yml'))
        self.assertEqual(len(mcf['facility'].keys()), 1)
        self.assertEqual(
            len(mcf['facility']['first_station']['spatiotemporal']), 1)

    def test_19139_2(self):
        """test ISO 19139-2 Metadata support"""

        mcf = read_mcf(get_abspath('../sample.yml'))
        self.assertIn('acquisition', mcf)
        self.assertIn('platforms', mcf['acquisition'])
        self.assertIn('instruments', mcf['acquisition']['platforms'][0])

    def test_json_output_schema(self):
        """test JSON as dict-based output schemas"""

        mcf = read_mcf(get_abspath('../sample.yml'))

        record = OGCAPIRecordOutputSchema().write(mcf)
        self.assertIsInstance(record, str)

        mcf = read_mcf(get_abspath('../sample.yml'))
        record = OGCAPIRecordOutputSchema().write(mcf, stringify=False)
        self.assertIsInstance(record, dict)

    def test_output_schema(self):
        """test output schema"""

        with self.assertRaises(InvalidSchemaError):
            load_schema('404')

        iso_os = load_schema('iso19139')
        self.assertIsInstance(iso_os, ISO19139OutputSchema)
        self.assertEqual(iso_os.name, 'iso19139', 'Expected specific name')
        self.assertEqual(iso_os.outputformat, 'xml',
                         'Expected specific output format')

    def test_validate_mcf_schema(self):
        """test MCF schema validation"""

        schema_file = os.path.join(SCHEMAS, 'mcf', 'core.yaml')

        with open(schema_file) as fh:
            schema = yaml.load(fh, Loader=yaml.SafeLoader)
            Validator.check_schema(schema)

    def test_validate_mcf(self):
        """test MCF validation"""

        mcf = read_mcf(get_abspath('../sample.yml'))

        instance = json.loads(json_dumps(mcf))

        is_valid = validate_mcf(instance)
        assert is_valid

        # validated nested MCF
        mcf = read_mcf(get_abspath('./sample-child.yml'))

        instance = json.loads(json_dumps(mcf))

        is_valid = validate_mcf(instance)
        assert is_valid

        with self.assertRaises(MCFValidationError):
            is_valid = validate_mcf({'foo': 'bar'})

    def test_schema_import(self):
        """test direct metadata schema import"""

        schema = ISO19139OutputSchema()

        with open(get_abspath('md-SMJP01RJTD-gmd.xml')) as fh:
            mcf = schema.import_(fh.read())

            self.assertEqual(
                mcf['identification']['title'],
                'WIS/GTS bulletin SMJP01 RJTD in FM12 SYNOP',
                'Expected specific title')

            self.assertEqual(len(mcf['distribution']), 1,
                             'Expected specific number of links')

            result_bbox = mcf['identification']['extents']['spatial'][0]['bbox']  # noqa
            expected_bbox = [124.167, 24.333, 145.583, 45.4]
            self.assertEqual(expected_bbox, result_bbox,
                             'Expected specific BBOX')

        with open(get_abspath('x-wmo-md-int.wmo.wis.ISMD01EDZW.xml')) as fh:  # noqa
            mcf = schema.import_(fh.read())

            self.assertEqual(
                mcf['identification']['title'],
                'GTS Bulletin: ISMD01 EDZW - Observational data (Binary coded) - BUFR (details are described in the abstract)',  # noqa
                'Expected specific title')

            self.assertEqual(len(mcf['distribution']), 1,
                             'Expected specific number of links')

            result_bbox = mcf['identification']['extents']['spatial'][0]['bbox']  # noqa
            expected_bbox = [6.3467, 47.7244, 14.1203, 55.0111]
            self.assertEqual(expected_bbox, result_bbox,
                             'Expected specific BBOX')

    def test_import_metadata(self):
        """test metadata import"""

        with open(get_abspath('md-SMJP01RJTD-gmd.xml')) as fh:
            mcf = import_metadata('iso19139', fh.read())

            self.assertEqual(
                mcf['identification']['title'],
                'WIS/GTS bulletin SMJP01 RJTD in FM12 SYNOP',
                'Expected specific title')

        with open(get_abspath('md-SMJP01RJTD-gmd.xml')) as fh:
            mcf = import_metadata('autodetect', fh.read())

            self.assertEqual(
                mcf['identification']['title'],
                'WIS/GTS bulletin SMJP01 RJTD in FM12 SYNOP',
                'Expected specific title')

    def test_empty_extents(self):
        # do not fail on empty elements
        schema = ISO19139OutputSchema()
        with open(get_abspath('iso19139-no-bbox.xml')) as fh:
            # owslib selects the first EX_GeographicBoundingBox,
            # so if it is empty, it will not check others
            mcf = schema.import_(fh.read())
            self.assertEqual(
                len(mcf['identification']['extents']['spatial'][0]['bbox']),
                0,
                'empty box')
            # owslib selects first beginPosition element,
            # so it skips empty temporalElements
            self.assertEqual(
                mcf['identification']['extents']['temporal'][0]['begin'],
                '2005-11-03',
                'assert date, skip empty period')
        with open(get_abspath('707a02ac-9240-4a2d-afbd-395b69756534.xml')) as fh:  # noqa
            # owslib does currently not parse gmd:polygon -> empty box
            mcf = schema.import_(fh.read())
            self.assertEqual(
                len(mcf['identification']['extents']['spatial'][0]['bbox']),
                0,
                'empty box')

    def test_transform_metadata(self):
        """test metadata transform"""

        with open(get_abspath('md-SMJP01RJTD-gmd.xml')) as fh:
            m = transform_metadata('iso19139', 'oarec-record', fh.read())

            m = json.loads(m)
            self.assertEqual(
                m['properties']['title'],
                'WIS/GTS bulletin SMJP01 RJTD in FM12 SYNOP',
                'Expected specific title')

        with open(get_abspath('md-SMJP01RJTD-gmd.xml')) as fh:
            m = transform_metadata('autodetect', 'oarec-record', fh.read())

            m = json.loads(m)
            self.assertEqual(
                m['properties']['title'],
                'WIS/GTS bulletin SMJP01 RJTD in FM12 SYNOP',
                'Expected specific title')


def get_abspath(filepath):
    """helper function absolute file access"""

    return os.path.join(THISDIR, filepath)


if __name__ == '__main__':
    unittest.main()
