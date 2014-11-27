# -*- coding: utf-8 -*-
# =================================================================
#
# $Id$
#
# Copyright (c) YYYY Her Majesty the Queen in Right of Canada
#
# Author: Firstname Lastname <firstname.lastname@ec.gc.ca>
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

import unittest

from pygeometa import (read_mcf, pretty_print,
                       render_template, get_supported_schemas)


def msg(test_id, test_description):
    """convenience function to print out test id and desc"""
    return '%s: %s' % (test_id, test_description)


class PygeometaTest(unittest.TestCase):
    """Test suite for package pygeometa"""
    def setUp(self):
        """setup test fixtures, etc."""

        print msg(self.id(), self.shortDescription())

    def tearDown(self):
        """return to pristine state"""

        pass

    def test_read_mcf(self):
        """Test reading MCF files"""

        with self.assertRaises(IOError):
            mcf = read_mcf('../404.mcf')

        mcf = read_mcf('../sample.mcf')
        self.assertIsInstance(mcf, dict, 'Expected dict')

        self.assertTrue('metadata' in mcf, 'Expected metadata section')

    def test_pretty_print(self):
        """Test pretty-printing"""

        xml = render_template('../sample.mcf', 'iso19139')
        xml2 = pretty_print(xml)

        self.assertIsInstance(xml2, unicode, 'Expected unicode string')
        self.assertEqual(xml2[-1], '>', 'Expected closing bracket')
        self.assertTrue(xml2.startswith('<?xml'), 'Expected XML declaration')

    def test_get_supported_schemas(self):
        """Test supported schemas"""

        schemas = get_supported_schemas()
        self.assertIsInstance(schemas, list, 'Expected list')
        self.assertEqual(len(schemas), 2, 'Expected 2 supported schemas')
        self.assertEqual(schemas, ['iso19139', 'iso19139-hnap'],
                         'Expected exact list of supported schemas')

    def test_render_template(self):
        """test template rendering"""

        xml = render_template('../sample.mcf', 'iso19139')
        self.assertIsInstance(xml, unicode, 'Expected unicode string')

        # no schema provided
        with self.assertRaises(RuntimeError):
            render_template('../sample.mcf')

        # bad schema provided
        with self.assertRaises(RuntimeError):
            xml = render_template('../sample.mcf', 'bad_schema')

        # bad schema_local provided
        with self.assertRaises(RuntimeError):
            xml = render_template('../sample.mcf',
                                  schema_local='/bad_schema/path')

        # good schema_local provided
        xml = render_template('../sample.mcf', schema_local='sample_schema')


if __name__ == '__main__':
    unittest.main()
