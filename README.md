# pygeometa

pygeometa is a Python package to generate metadata for geospatial datasets.

## Table of Content
* Overview
* Installation
  * Requirements
  * Dependencies
  * Installing the Package
* Running
  * From the command line
  * Using the API from Python
* Development
  * Setting up a Development Environment
  * Adding Another Metadata Format
  * Running Tests
  * Code Conventions
  * Bugs and Issues

## Overview

pygeometa is a Python package to generate metadata for geospatial datasets.

Workflow to generate metadata XML:
1. Install pygeometa
2. Create a .mcd file that contains metadata information 
  1. Refer to the `sample.mcd` example
3. Run pygeometa for the .mcd file with a specified target metadata format


## Installation

pygeometa is best installed and used within a Python virtualenv.

### Requirements

Python 2.6 and above.  Works with Python 3.

### Dependencies

See `requirements.txt`

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
generate_metadata.py path/to/file.mcf iso19139  # to stdout
generate_metadata.py path/to/file.mcf iso19139 > some_file.xml  # to file
```

### Using the API from Python

```python
from pygeometa import render_template
xml_string = render_template('/path/to/file.mcf', 'iso19139')
with open('output.xml', 'w') as ff:
    ff.write(xml_string)
```

## Development

### Setting up a Development Environment

Same as installing a package.  Use a virtualenv.  Also install developer requirements:

```bash
pip install -r requirements-dev.txt
```

### Adding Another Metadata Format

List of supported metadata formats in `pygeometa/templates/`

To add support to new metadata formats:
```bash
cp -r pygeometa/templates/iso19139 pygeometa/templates/new-format
```
Then modify *.j2 files in the new pygeometa/templates/new-format directory to comply to new metadata format.

### Running Tests

TODO

### Code Conventions

* [PEP8](https://www.python.org/dev/peps/pep-0008)

### Bugs and Issues

All bugs, enhancements and issues can be logged on SSC GitLab at
http://gitlab-omnibus.ssc.etg.gc.ca/ec-msc/pygeometa/issues
