[![Build Status](https://github.com/geopython/pygeometa/workflows/build%20%E2%9A%99%EF%B8%8F/badge.svg)](https://github.com/geopython/pygeometa/actions)
[![Join the chat at https://matrix.to/#/#geopython_pygeometa:gitter.im](https://badges.gitter.im/Join%20Chat.svg)](https://matrix.to/#/#geopython_pygeometa:gitter.im)

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
python3 setup.py build
python3 setup.py install
```

## Running

### From the command line

```bash
# show all subcommands
pygeometa

# show all supported schemas
pygeometa metadata schemas

# provide a basic sanity check/report on an MCF
pygeometa metadata info path/to/file.yml

# generate an ISO 19139 document to stdout
pygeometa metadata generate path/to/file.yml --schema=iso19139

# generate an ISO 19139 document to disk
pygeometa metadata generate path/to/file.yml --schema=iso19139 --output=some_file.xml

# generate an ISO 19139 document to disk with debugging (ERROR, WARNING, INFO, DEBUG)
pygeometa metadata generate path/to/file.yml --schema=iso19139 --output=some_file.xml --verbosity=DEBUG # add verbose (ERROR, WARNING, INFO, DEBUG)

# use your own defined schema
pygeometa metadata generate path/to/file.yml --schema_local=/path/to/my-schema --output=some_file.xml  # to file

# validate your MCF
pygeometa metadata validate path/to/file.yml

# import a metadata document to MCF
pygeometa metadata import path/to/file.xml --schema=iso19139

# transform from one metadata representation to another
pygeometa metadata transform path/to/file.xml --input-schema=iso19139 --output-schema=oarec-record
```

### Supported schemas
Schemas supported by pygeometa:
* dcat, [reference](https://www.w3.org/TR/vocab-dcat-2/)
* iso19139, [reference](http://www.iso.org/iso/catalogue_detail.htm?csnumber=32557)
* iso19139-hnap, [reference](http://www.gcpedia.gc.ca/wiki/Federal_Geospatial_Platform/Policies_and_Standards/Catalogue/Release/Appendix_B_Guidelines_and_Best_Practices/Guide_to_Harmonized_ISO_19115:2003_NAP)
* OGC API - Records - Part 1: Core, record model, [reference](https://github.com/opengeospatial/ogcapi-records/blob/master/core/openapi/schemas/record.yaml)
* SpatioTemporal Asset Catalog [(STAC)](https://stacspec.org)
* iso19139-2, [reference](https://www.iso.org/standard/67039.html)
* [wmo-cmp](doc/content/reference/formats/wmo-cmp.md), [reference](http://wis.wmo.int/2013/metadata/version_1-3-0/WMO_Core_Metadata_Profile_v1.3_Part_1.pdf)
* [wmo-wcmp2](doc/content/reference/formats/wmo-wcmp2.md), [reference](https://wmo-im.github.io/wcmp2)
* [wmo-wigos](doc/content/reference/formats/wmo-wigos.md), [reference](https://library.wmo.int/opac/doc_num.php?explnum_id=3653)
* Local schema, specified with ```--schema_local=/path/to/my-schema```

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
xml_string = render_j2_template(mcf_dict, template_dir='/path/to/new-schema')

# write to disk
with open('output.xml', 'wb') as ff:
    ff.write(xml_string)
```

## Development

### Setting up a Development Environment

Same as installing a package.  Use a virtualenv.  Also install developer
requirements:

```bash
pip3 install -r requirements-dev.txt
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

### Running Tests

```bash
# via setuptools
python3 setup.py test
# manually
cd tests
python3 run_tests.py
```

## Releasing

```bash
# update version
vi pygeometa/__init__.py
vi debian/changelog  # add changelog entry and summary of updates
git commit -m 'update release version' pygeometa/__init__.py debian/changelog
# push changes
git push origin master
git tag -a x.y.z -m 'tagging release x.y.z'
# push tag
git push --tags
rm -fr build dist *.egg-info
python3 setup.py sdist bdist_wheel --universal
twine upload dist/*
```

### Code Conventions

* [PEP8](https://www.python.org/dev/peps/pep-0008)

### Bugs and Issues

All bugs, enhancements and issues are managed on [GitHub](https://github.com/geopython/pygeometa/issues).

## Contact

* [Tom Kralidis](https://github.com/tomkralidis)
* [Alexandre Leroux](https://github.com/alexandreleroux)
