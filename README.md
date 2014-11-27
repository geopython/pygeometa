# pygeometa

pygeometa is a Python package to generate metadata for geospatial datasets.

## Table of Contents
* [Overview](#overview)
* [Installation](#installation)
  * [Requirements](#requirements)
  * [Dependencies](#depedencies)
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
  * [To do](#to-do)
* [History](#history)
* [Contact](#contact)


## Overview

pygeometa is a Python package to generate metadata for geospatial datasets.

Workflow to generate metadata XML:
1. Install pygeometa
2. Create a 'metadata control file' .mcf file that contains metadata information 
  1. Modify the [sample.mcf](/ec-msc/pygeometa/blob/master/sample.mcf) example
  2. Refer to the [Metadata Control File Reference documentation](/ec-msc/pygeometa/blob/master/MCF_Reference.md) 
3. Run pygeometa for the .mcf file with a specified target metadata schema


## Installation

pygeometa is best installed and used within a Python virtualenv.

### Requirements

Python 2.6 and above.  Works with Python 3.

### Dependencies

See [requirements.txt](requirements.txt)

### Installing the Package

```bash
virtualenv my-env
cd my-env
. bin/activate
git clone http://gitlab-omnibus.ssc.etg.gc.ca/ec-msc/pygeometa.git
cd pygeometa
pip install -r requirements.txt
python setup.py build
python setup.py install
```

## Running

### From the command line

```bash
generate_metadata.py --mcf=path/to/file.mcf --schema=iso19139  # to stdout
generate_metadata.py --mcf=path/to/file.mcf --schema=iso19139 > some_file.xml  # to file
# to use your own defined schema:
generate_metadata.py --mcf=path/to/file.mcf --schema_local=/path/to/my-schema > some_file.xml  # to file
```

### Using the API from Python

```python
from pygeometa import render_template
# default schema
xml_string = render_template('/path/to/file.mcf', schema='iso19139')
# user-defined schema
xml_string = render_template('/path/to/file.mcf', schema_local='/path/to/new-schema')
with open('output.xml', 'w') as ff:
    ff.write(xml_string)
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

TODO

### Code Conventions

* [PEP8](https://www.python.org/dev/peps/pep-0008)

### Bugs and Issues

All bugs, enhancements and issues can be logged on SSC GitLab at
http://gitlab-omnibus.ssc.etg.gc.ca/ec-msc/pygeometa/issues

### To do

## History

pygeometa originated within the [pygdm](https://wiki.cmc.ec.gc.ca/wiki/Pygdm) project, which provided generic geospatial data management functions.  pygdm (now at end of life) was used for generating MSC/CMC geospatial metadata.

pygeometa was pulled out of pygdm to focus on the core requirement of generating geospatial metadata within a real-time environment.

## Contact

* [Tom Kralidis](http://geds20-sage20.ssc-spc.gc.ca/en/GEDS20/?pgid=015&dn=cn%3DKralidis\\%2C+Tom%2Cou%3DDAT-GES%2Cou%3DMON-STR%2Cou%3DMON-DIR%2Cou%3DMSCB-DGSMC%2COU%3DDMO-CSM%2COU%3DEC-EC%2CO%3Dgc%2CC%3Dca)
* [Alexandre Leroux](http://geds20-sage20.ssc-spc.gc.ca/en/GEDS20/?pgid=015&dn=cn%3DLeroux\\%2C+Alexandre%2Cou%3DDPS-DPS%2Cou%3DCAN-OPE%2Cou%3DCAN-CEN%2Cou%3DMSCB-DGSMC%2COU%3DDMO-CSM%2COU%3DEC-EC%2CO%3Dgc%2CC%3Dca)
