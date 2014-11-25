# pygeometa

pygeometa is a Python package to generate metadata for meteorological datasets.

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

### Running

```bash
generate_metadata.py path/to/file.mcf iso19139  # to stdout
generate_metadata.py path/to/file.mcf iso19139 > some_file.xml  # to file
```

## Development

### Setting up a Development Environment

Same as installing a package.  Use a virtualenv.  Also install developer requirements:

```bash
pip install -r requirements-dev.txt
```

### Adding Another Metadata Format

TODO

### Running Tests

TODO

### Code Conventions

- [PEP8](https://www.python.org/dev/peps/pep-0008)

### Bugs and Issues

All bugs, enhancements and issues can be logged on SSC GitLab at
http://gitlab-omnibus.ssc.etg.gc.ca/ec-msc/pygeometa/issues
