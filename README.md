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
* [Migration](#migration)
  * [Migrating old MCFs to YAML](#migrating-old-mcfs-to-yaml)
* [Development](#development)
  * [Setting up a Development Environment](#setting-up-a-development-environment)
  * [Adding a Metadata Schema to the Core](#adding-a-metadata-schema-to-the-core)
  * [Running Tests](#running-tests)
  * [Code Conventions](#code-conventions)
  * [Bugs and Issues](#bugs-and-issues)
* [History](#history)
* [Contact](#contact)

## Overview

pygeometa is a Python package to generate metadata for geospatial datasets.
Metadata content is managed by pygeometa in simple Metadata Control Files
(MCF) which consist of 'parameter = value' pairs. pygeometa generates metadata
records from MCFs based on the schema specified by the user, such as ISO19139,
associated profiles, and WMO WIGOS. pygeometa supports nesting MCFs, which
reduces duplication of metadata content common to multiple records and ease
maintenance.

## Features

* simple YAML-based configuration
* extensible: template architecture allows for easy addition of new metadata
  formats
* flexible: use as a command-line tool or integrate as a library

## Quickstart

Workflow to generate metadata XML:

1. Install pygeometa
2. Create a 'metadata control file' .yml file that contains metadata
   information 
  1. Modify the [sample.yml](https://github.com/geopython/pygeometa/blob/master/sample.yml) example
  2. pygeometa supports nesting MCFs together, allowing providing a single MCF
     for common metadata parameters (e.g. common contact information)
  3. Refer to the [Metadata Control File Reference documentation](https://github.com/geopython/pygeometa/blob/master/doc/MCF_Reference.md) 
3. Run pygeometa for the .yml file with a specified target metadata schema

## Installation

pygeometa is best installed and used within a Python virtualenv.

### Requirements

* Python 3 and above.  Works with Python 2.7
* Python [virtualenv](https://virtualenv.pypa.io/) package

### Dependencies

Dependencies are listed in [requirements.txt](requirements.txt). Dependencies
are automatically installed during pygeometa's installation.

### Installing the Package

```bash
virtualenv -p python3 my-env
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
pygeometa generate_metadata --mcf=path/to/file.yml --schema=iso19139  # to stdout
pygeometa generate_metadata --mcf=path/to/file.yml --schema=iso19139 --output=some_file.xml  # to file
pygeometa generate_metadata --mcf=path/to/file.yml --schema=iso19139 --output=some_file.xml --verbosity=DEBUG # add verbose (ERROR, WARNING, INFO, DEBUG)
# to use your own defined schema:
pygeometa generate_metadata --mcf=path/to/file.yml --schema_local=/path/to/my-schema --output=some_file.xml  # to file
```

### Supported schemas
Schemas supported by pygeometa:
* iso19139, [reference](http://www.iso.org/iso/catalogue_detail.htm?csnumber=32557)
* iso19139-hnap, [reference](http://www.gcpedia.gc.ca/wiki/Federal_Geospatial_Platform/Policies_and_Standards/Catalogue/Release/Appendix_B_Guidelines_and_Best_Practices/Guide_to_Harmonized_ISO_19115:2003_NAP)
* [wmo-cmp](doc/wmo-cmp.md), [reference](http://wis.wmo.int/2013/metadata/version_1-3-0/WMO_Core_Metadata_Profile_v1.3_Part_1.pdf) 
* [wmo-wigos](doc/wmo-wigos.md), [reference](https://library.wmo.int/opac/doc_num.php?explnum_id=3653)
* Local schema, specified with ```--schema_local=/path/to/my-schema```

### Using the API from Python

```python
from pygeometa.core import render_template
# default schema
xml_string = render_template('/path/to/file.yml', schema='iso19139')
# user-defined schema
xml_string = render_template('/path/to/file.yml', schema_local='/path/to/new-schema')
# dictionary representation of YAML
xml_string = render_template(yaml_dict, schema='iso19139')
with open('output.xml', 'w') as ff:
    ff.write(xml_string)
# render from an MCF stored in a string
mcf_string = '...'  # some string
xml_string = render_template_string(mcf_string, schema='iso19139')
# render from an MCF as a ConfigParser object
mcf_cp = '...'  # some ConfigParser object
xml_string = render_template_string(mcf_cp, schema='iso19139')
```

## Migration

### Migrating old MCFs to YAML

pygeometa provides a `migrate` utility to convert legacy MCFs into YAML:

```bash
pygeometa migrate --mcf=path/to/file.mcf  # to stdout
pygeometa migrate --mcf=path/to/file.mcf --output=some_file.yml  # to file
```
The migrate utility doesn't support migrating comments from legacy MCFs tox
 YAML MCFs.

## Development

### Setting up a Development Environment

Same as installing a package.  Use a virtualenv.  Also install developer
requirements:

```bash
pip install -r requirements-dev.txt
```

### Adding a Metadata Schema to the Core

List of supported metadata schemas in `pygeometa/templates/`

To add support to new metadata schemas:
```bash
cp -r pygeometa/templates/iso19139 pygeometa/templates/new-schema
```
Then modify `*.j2` files in the new `pygeometa/templates/new-schema` directory
to comply to new metadata schema.

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

Started in 2009, pygeometa originated within an internal project called pygdm,
which provided generic geospatial data management functions.  pygdm (now end
of life) was used for generating MSC/CMC geospatial metadata.  pygeometa was
pulled out of pygdm to focus on the core requirement of generating geospatial
metadata within a real-time environment and automated workflows.

In 2015 pygeometa was made publically available in support of the Treasury
Board [Policy on Acceptable Network and Device Use](http://www.tbs-sct.gc.ca/pol/doc-eng.aspx?id=27122).

## Contact

* [Tom Kralidis](https://github.com/tomkralidis)
* [Alexandre Leroux](https://github.com/alexandreleroux)
