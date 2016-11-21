[![Build Status](https://travis-ci.org/geopython/pygeometa.png)](https://travis-ci.org/geopython/pygeometa)

# pygeometa

pygeometa is a Python package to generate metadata for geospatial datasets.

## Table of Contents
* [Overview](#overview)
* [Features](#features)
* [Quickstart](#quickstart)
* [Installation](#installation)
  * [Requirements](#requirements)
  * [Dependencies](#dependencies)
  * [Installing the Package](#installing-the-package)
* [Running](#running)
  * [From the command line](#from-the-command-line)
  * [Using the API from Python](#using-the-api-from-python)
* [Development](#development)
  * [Setting up a Development Environment](#setting-up-a-development-environment)
  * [Adding Another Metadata Schema to the Core](#adding-another-metadata-schema-to-the-core)
  * [Running Tests](#running-tests)
  * [Code Conventions](#code-conventions)
  * [Bugs and Issues](#bugs-and-issues)
* [History](#history)
* [Contact](#contact)


## Overview

pygeometa is a Python package to generate metadata for geospatial datasets. Metadata content is managed by pygeometa in simple Metadata Control Files (MCF) which consist of 'parameter = value' pairs. pygeometa generates metadata records from MCF files based on the schema specified by the user, such as ISO-19139. pygeometa supports nesting MCF files, which reduces duplication of metadata content common to multiple records and ease maintenance.

## Features

* simple configuration: inspired by Python's ConfigParser
* extensible: template architecture allows for easy addition of new metadata formats
* flexible: use as a command-line tool or integrate as a library

## Quickstart

Workflow to generate metadata XML:

1. Install pygeometa
2. Create a 'metadata control file' .mcf file that contains metadata information 
  1. Modify the [sample.mcf](https://github.com/geopython/pygeometa/blob/master/sample.mcf) example
  2. pygeometa supports nesting MCF files together, allowing providing a single MCF file for common metadata parameters (e.g. common contact information)
  3. Refer to the [Metadata Control File Reference documentation](https://github.com/geopython/pygeometa/blob/master/doc/MCF_Reference.md) 
3. Run pygeometa for the .mcf file with a specified target metadata schema



## Installation

pygeometa is best installed and used within a Python virtualenv.

### Requirements

* Python 2.7 and above.  Works with Python 3
* Python [virtualenv](https://virtualenv.pypa.io/) package

### Dependencies

Dependencies are listed in [requirements.txt](requirements.txt). Dependencies are automatically installed during pygeometa's installation.

### Installing the Package

```bash
virtualenv my-env
cd my-env
. bin/activate
git clone https://github.com/geopython/pygeometa.git
cd pygeometa
python setup.py build
python setup.py install
```

## Running

### From the command line

```bash
generate_metadata.py --mcf=path/to/file.mcf --schema=iso19139  # to stdout
generate_metadata.py --mcf=path/to/file.mcf --schema=iso19139 --output=some_file.xml  # to file
# to use your own defined schema:
generate_metadata.py --mcf=path/to/file.mcf --schema_local=/path/to/my-schema --output=some_file.xml  # to file
```

### Supported schemas
Schemas supported by pygeometa:
* iso19139, [reference](http://www.iso.org/iso/catalogue_detail.htm?csnumber=32557)
* iso19139-hnap, [reference](http://www.gcpedia.gc.ca/wiki/Federal_Geospatial_Platform/Policies_and_Standards/Catalogue/Release/Appendix_B_Guidelines_and_Best_Practices/Guide_to_Harmonized_ISO_19115:2003_NAP)
* [wmo-cmp](docs/wmo-cmp.md), [reference](http://wis.wmo.int/2013/metadata/version_1-3-0/WMO_Core_Metadata_Profile_v1.3_Part_1.pdf) 
* Local schema, specified with ```--schema_local=/path/to/my-schema```

### Using the API from Python

```python
from pygeometa import render_template
# default schema
xml_string = render_template('/path/to/file.mcf', schema='iso19139')
# user-defined schema
xml_string = render_template('/path/to/file.mcf', schema_local='/path/to/new-schema')
with open('output.xml', 'w') as ff:
    ff.write(xml_string)
# render from an MCF stored in a string
mcf_string = '...'  # some string
xml_string = render_template_string(mcf_string, schema='iso19139')
# render from an MCF as a ConfigParser object
from pygeometa import render_template
mcf_cp = '...'  # some ConfigParser object
xml_string = render_template_string(mcf_cp, schema='iso19139')
```

## Development

### Setting up a Development Environment

Same as installing a package.  Use a virtualenv.  Also install developer requirements:

```bash
pip install -r requirements-dev.txt
```

### Adding Another Metadata Schema to the Core

List of supported metadata schemas in `pygeometa/templates/`

To add support to new metadata schemas:
```bash
cp -r pygeometa/templates/iso19139 pygeometa/templates/new-schema
```
Then modify `*.j2` files in the new `pygeometa/templates/new-schema` directory to comply to new metadata schema.

### Running Tests

```bash
# via distutils
python setup.py test
# manually
cd tests
python run_tests.py
```

### Code Conventions

* [PEP8](https://www.python.org/dev/peps/pep-0008)

### Bugs and Issues

All bugs, enhancements and issues are managed on [GitHub](https://github.com/geopython/pygeometa/issues).

## History

pygeometa originated within an internal project called pygdm, which provided generic geospatial data management functions.  pygdm (now at end of life) was used for generating MSC/CMC geospatial metadata.  pygeometa was pulled out of pygdm to focus on the core requirement of generating geospatial metadata within a real-time environment.

In 2015 pygeometa was made publically available in support of the Treasury Board [Policy on Acceptable Network and Device Use](http://www.tbs-sct.gc.ca/pol/doc-eng.aspx?id=27122).

## Contact

* [Tom Kralidis](http://geds20-sage20.ssc-spc.gc.ca/en/GEDS20/?pgid=015&dn=CN%3Dtom.kralidis%40canada.ca%2COU%3DDAT-GES%2COU%3DMON-STR%2COU%3DMON-DIR%2COU%3DMSCB-DGSMC%2COU%3DDMO-CSM%2COU%3DEC-EC%2CO%3Dgc%2CC%3Dca)
* [Alexandre Leroux](http://geds20-sage20.ssc-spc.gc.ca/en/GEDS20/?pgid=015&dn=CN%3Dalexandre.leroux%40canada.ca%2COU%3DDPS-DPS%2COU%3DCAN-OPE%2COU%3DCAN-CEN%2COU%3DMSCB-DGSMC%2COU%3DDMO-CSM%2COU%3DEC-EC%2CO%3Dgc%2CC%3Dca)
