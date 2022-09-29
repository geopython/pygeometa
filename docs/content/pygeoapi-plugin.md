# pygeoapi plugin

## Overview

pygeometa also provides a custom [pygeoapi](https://pygeoapi.io) processing plugin, providing
metadata validation and generation via OGC API - Processes.

## Installation

To integrate this plugin in pygeoapi:

- ensure pygeometa is installed into the pygeoapi deployment environment

- add the two proceses to the pygeoapi configuration as follows:

```yaml
pygeometa-metadata-validate:
    type: process
    processor:
        name: pygeometa.pygeoapi_plugin.PygeometaMetadataValidateProcessor

pygeometa-metadata-generate:
    type: process
    processor:
        name: pygeometa.pygeoapi_plugin.PygeometaMetadataGenerateProcessor
```
- regenerate the pygeoapi OpenAPI configuration

```bash
pygeoapi openapi generate $PYGEOAPI_CONFIG --output-file $PYGEOAPI_OPENAPI
```

- restart pygeoapi

## Usage

The resulting processes will be available at the following endpoints:

* `/processes/pygeometa-metadata-validate`
* `/processes/pygeometa-metadata-generate`

Note that pygeoapi's OpenAPI/Swagger interface (at `/openapi`) also
provides a developer-friendly interface to test and run requests
