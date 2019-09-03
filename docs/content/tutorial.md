# pygeometa Tutorial

## Overview

This tutorial provides a tour of pygeometa for both users and developers,
and is aimed at getting you up and running quickly.  Let's go!

## For Users

### Installation

You require Python 3 or greater to use pygeometa.

The easiest way to install pygeometa is using pip:

```bash
pip install pygeometa
```

This will install the latest stable release.  If you are looking to work with
pygeometa from source, see the [For Developers](#for-developers) section for
more information.

### Workflow

The basic pygeometa workflow is:

1. Create a 'metadata control file' YAML file that contains metadata information 
  1. Modify the [sample.yml](https://github.com/geopython/pygeometa/blob/master/sample.yml) example
  2. pygeometa supports nesting MCFs together, allowing providing a single MCF
     for common metadata parameters (e.g. common contact information)
  3. Refer to the [Metadata Control File Reference documentation](https://geopython.github.io/pygeometa/reference/formats/mcf) 
3. Run pygeometa for the .yml file with a specified target metadata schema

### Running

```bash
# generate an ISO document to stdout
pygeometa generate-metadata --mcf=path/to/file.yml --schema=iso19139

# generate an ISO document and save to disk
pygeometa generate-metadata --mcf=path/to/file.yml --schema=iso19139 --output=some_file.xml

# generate an ISO document, save to disk and set verbosity (ERROR, WARNING, INFO, DEBUG) for debugging issues
pygeometa generate-metadata --mcf=path/to/file.yml --schema=iso19139 --output=some_file.xml --verbosity=DEBUG

# to use your own defined schema:
pygeometa generate-metadata --mcf=path/to/file.yml --schema_local=/path/to/my-schema --output=some_file.xml
```

### Migration

#### Migrating old MCFs to YAML

pygeometa provides a `migrate` utility to convert legacy MCFs into YAML:

```bash
pygeometa migrate --mcf=path/to/file.mcf  # to stdout
pygeometa migrate --mcf=path/to/file.mcf --output=some_file.yml  # to file
```
The migrate utility doesn't support migrating comments from legacy MCFs to
YAML MCFs.

## For Developers

### Installation

pygeometa is best installed and used within a Python virtualenv.

#### Requirements

* Python 3 and above
* Python [virtualenv](https://virtualenv.pypa.io/) package

#### Dependencies

Dependencies are listed in `requirements.txt`. Dependencies
are automatically installed during pygeometa's installation.

#### Installing the Package from Source

```bash
python3 -m venv my-env
cd my-env
. bin/activate
git clone https://github.com/geopython/pygeometa.git
cd pygeometa
python setup.py build
python setup.py install
```

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

## Releasing

```bash
python setup.py sdist bdist_wheel --universal
twine upload dist/*
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

