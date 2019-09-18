[![Build Status](https://travis-ci.org/geopython/pygeometa.png)](https://travis-ci.org/geopython/pygeometa)
[![Join the chat at https://gitter.im/geopython/pygeometa](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/geopython/pygeometa)

# pygeometa

[pygeometa](https://geopython.github.io/pygeometa) is a Python package to
generate metadata for geospatial datasets.

## Installation

pygeometa is best installed and used within a Python virtualenv.

### Requirements

* Python 3 and above
* Python [virtualenv](https://virtualenv.pypa.io/) package

### Dependencies

Dependencies are listed in [requirements.txt](requirements.txt). Dependencies
are automatically installed during pygeometa's installation.

### Installing the Package

```bash
python3 -m venv my-env
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
pygeometa generate-metadata --mcf=path/to/file.yml --schema=iso19139  # to stdout
pygeometa generate-metadata --mcf=path/to/file.yml --schema=iso19139 --output=some_file.xml  # to file
pygeometa generate-metadata --mcf=path/to/file.yml --schema=iso19139 --output=some_file.xml --verbosity=DEBUG # add verbose (ERROR, WARNING, INFO, DEBUG)
# to use your own defined schema:
pygeometa generate-metadata --mcf=path/to/file.yml --schema_local=/path/to/my-schema --output=some_file.xml  # to file
```

### Supported schemas
Schemas supported by pygeometa:
* iso19139, [reference](http://www.iso.org/iso/catalogue_detail.htm?csnumber=32557)
* iso19139-hnap, [reference](http://www.gcpedia.gc.ca/wiki/Federal_Geospatial_Platform/Policies_and_Standards/Catalogue/Release/Appendix_B_Guidelines_and_Best_Practices/Guide_to_Harmonized_ISO_19115:2003_NAP)
* [wmo-cmp](doc/content/reference/formats/wmo-cmp.md), [reference](http://wis.wmo.int/2013/metadata/version_1-3-0/WMO_Core_Metadata_Profile_v1.3_Part_1.pdf)
* [wmo-wigos](doc/content/reference/formats/wmo-wigos.md), [reference](https://library.wmo.int/opac/doc_num.php?explnum_id=3653)
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
# via setuptools
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

## Contact

* [Tom Kralidis](https://github.com/tomkralidis)
* [Alexandre Leroux](https://github.com/alexandreleroux)
