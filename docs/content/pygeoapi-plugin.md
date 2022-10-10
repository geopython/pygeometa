# pygeoapi plugin

## Overview

pygeometa also provides a custom [pygeoapi](https://pygeoapi.io) processing plugin, providing
pygeometa functionality via OGC API - Processes.

## Installation

To integrate this plugin in pygeoapi:

- ensure pygeometa is installed into the pygeoapi deployment environment

- add the processes to the pygeoapi configuration as follows:

```yaml
pygeometa-metadata-import:
    type: process
    processor:
        name: pygeometa.pygeoapi_plugin.PygeometaMetadataImportProcessor

pygeometa-metadata-validate:
    type: process
    processor:
        name: pygeometa.pygeoapi_plugin.PygeometaMetadataValidateProcessor

pygeometa-metadata-generate:
    type: process
    processor:
        name: pygeometa.pygeoapi_plugin.PygeometaMetadataGenerateProcessor

pygeometa-metadata-transform:
    type: process
    processor:
        name: pygeometa.pygeoapi_plugin.PygeometaMetadataTransformProcessor
```
- regenerate the pygeoapi OpenAPI configuration

```bash
pygeoapi openapi generate $PYGEOAPI_CONFIG --output-file $PYGEOAPI_OPENAPI
```

- restart pygeoapi

## Usage

The resulting processes will be available at the following endpoints:

* `/processes/pygeometa-metadata-import`
* `/processes/pygeometa-metadata-validate`
* `/processes/pygeometa-metadata-generate`
* `/processes/pygeometa-metadata-transform`

Note that pygeoapi's OpenAPI/Swagger interface (at `/openapi`) also
provides a developer-friendly interface to test and run requests
