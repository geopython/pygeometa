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
  3. Refer to the [Metadata Control File Reference documentation](https://geopython.github.io/pygeometa/reference/mcf) 
3. Run pygeometa for the .yml file with a specified target metadata schema

### Running

```bash
# show all subcommands
pygeometa

# show all supported schemas
pygeometa metadata schemas

# provide a basic sanity check/report on an MCF (Metadata Control File)
pygeometa metadata info path/to/file.yml

# generate an ISO 19139 document to stdout
pygeometa metadata generate path/to/file.yml --schema=iso19139

# generate an ISO 19139 document to disk
pygeometa metadata generate path/to/file.yml --schema=iso19139 --output=some_file.xml

# generate an ISO 19139 document to disk with debugging (ERROR, WARNING, INFO, DEBUG)
pygeometa metadata generate path/to/file.yml --schema=iso19139 --output=some_file.xml --verbosity=DEBUG # add verbose (ERROR, WARNING, INFO, DEBUG)

# use your own defined schema
pygeometa metadata generate path/to/file.yml --schema_local=/path/to/my-schema --output=some_file.xml  # to file

# validate an MCF document
pygeometa validate path/to/file.yml

# import a metadata document to MCF
pygeometa metadata import path/to/file.xml --schema=iso19139

# transform from one metadata representation to another
pygeometa metadata transform path/to/file.xml --input-schema=iso19139 --output-schema=oarec-record
```

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
from pygeometa.core import read_mcf, render_j2_template

# read from disk
mcf_dict = read_mcf('/path/to/file.yml')
# read from string
mcf_dict = read_mcf(mcf_string)

# choose ISO 19139 output schema
from pygeometa.schemas.iso19139 import ISO19139OutputSchema
iso_os = ISO19139OutputSchema()

# default schema
xml_string = iso_os.write(mcf_dict)

# user-defined schema
xml_string = render_j2_template(mcf_dict, schema_local='/path/to/new-schema')

# write to disk
with open('output.xml', 'wb') as ff:
    ff.write(xml_string)
```

## Development

### Setting up a Development Environment

Same as installing a package.  Use a virtualenv.  Also install developer
requirements:

```bash
pip install -r requirements-dev.txt
```

### Adding a Metadata Schema to the Core

Adding an output metadata schemas to pygeometa involves extending
`pygeometa.schemas.base.BaseOutputSchema` and supporting the `write`
function to return a string of exported metadata content.  If you are using
Jinja2 templates, see the next section.  If you are using another means of
generating metadata (lxml, xml.etree, json, etc.), override the ABS `write`
class to emit a string using your tooling/workflow accordingly.  See the
below sections for examples.

Once you have added your metadata schema, you need to register it with
pygeometa's schema registry:

```bash
vi pygeometa/schemas/__init__.py
# edit the SCHEMAS dict with the metadata schema name and dotted path of class
```

#### Jinja2 templates

To add support for a new metadata schema using Jinja2 templates:
```bash
cp -r pygeometa/schemas/iso19139 pygeometa/schemas/new-schema
```
Then modify `*.j2` files in the new `pygeometa/schemas/new-schema` directory
to comply to new metadata schema.

#### Custom tooling

To add support for a new metadata schemas using other tooling/workflow:
```bash
mkdir pygeometa/schemas/foo
cp pygeometa/schemas/iso19139/__init__.py pygeometa/schemas/foo
vi pygeometa/schemas/foo/__init__.py
# update class name and super().__init__() function accordingly 
```

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
