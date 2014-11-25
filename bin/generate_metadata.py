#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
# =================================================================
#
# $Id$
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

import os
import sys

from pygeometa import get_supported_formats, render_template

SUPPORTED_FORMATS = get_supported_formats()

if len(sys.argv) < 3:
    print('Usage: {} <mcf file> <format>'.format(sys.argv[0]))
    sys.exit(1)

if sys.argv[2] not in SUPPORTED_FORMATS:
    print('Invalid format {}. Supported formats: {}'.format(sys.argv[2],
          '.'.join(SUPPORTED_FORMATS)))
    sys.exit(2)

print(render_template(sys.argv[1], sys.argv[2]))
