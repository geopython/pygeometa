## pygeometa

[![Join the chat at https://matrix.to/#/#geopython_pygeometa:gitter.im](https://badges.gitter.im/Join%20Chat.svg)](https://matrix.to/#/#geopython_pygeometa:gitter.im)

<h2>Metadata Creation for the Rest of Us</h2>

pygeometa provides a lightweight and Pythonic approach for users to easily
manage geospatial metadata in standards-based formats using simple
configuration files (affectionately called Metadata Control Files \[MCF\]).
Leveraging the simple but powerful YAML format, pygeometa can generate metadata
in numerous standards. Users can also create their own custom metadata formats
which can be plugged into pygeometa for custom metadata format output.

For developers, pygeometa provides a Pythonic API that allows developers to
tightly couple metadata generation within their systems and integrate nicely
into metadata production pipelines.

The project supports various metadata formats out of the box including ISO
19115, the WMO Core Metadata Profile, and the WIGOS Metadata Standard. Can't
find the format you're looking for?  Element(s) missing from a given format?
Feel free to open an [issue](https://github.com/geopython/pygeometa/issues)!

pygeometa has minimal dependencies (wheel install is less than 100 kB), and provides
a flexible extension mechanism leveraging the Jinja2 templating system.

pygeometa is [open source](https://opensource.org) and released under an
[MIT license](https://github.com/geopython/pygeometa/blob/master/LICENSE.md).

## Features
* simple YAML-based configuration
* real-time MCF validation
* extensible: plugin architecture allows for easy addition of new metadata
  formats using Jinja2 templates or custom workflow (JSON, YAML, CSV, etc.)
* flexible: use as a command-line tool or integrate as a library
* import from external metadata sources
* multilingual support

## Format support

|Id|Description|Read|Write|
|---|---|---|---|
|[csvw](https://csvw.org)|CSV on the Web (CSVW)|True|True|
|[cwl](https://www.commonwl.org)|Common Workflow Language|True|False|
|[dcat](https://dcat.org)|Data Catalog Vocabulary (DCAT)|False|True|
|[iso19139](https://www.iso.org/standard/53798.html)|ISO 19115-1:2014 Geographic information - Metadata Part 1: Metadata Part 1: Fundamentals|True|True|
|[iso19139-2](https://www.iso.org/standard/67039.html)|ISO 19115-2:2019 Geographic information - Metadata Part 2: Metadata Part 2: Extensions for acquisition and processing|False|True|
|[iso19139-hnap](https://docs.geocat.net/catalogue/schema_plugins/iso19139.ca.HNAP)|Canadian profile on Harmonized North American Profile (HNAP)|False|True|
|[mmd](https://htmlpreview.github.io/?https://github.com/metno/mmd/blob/master/doc/mmd-specification.html)|MET Norway Metadata Format Specification (MMD)|True|False|
|[oarec-record](https://docs.ogc.org/is/20-004r1/20-004r1.html#clause-record-core)|OGC API - Records: Part 1: Core (Record Core)|False|True|
|[openaire](https://www.openaire.eu)|OpenAIRE|True|False|
|[schema-org](https://schema.org)|Schema.org|True|True|
|[stac-item](https://github.com/radiantearth/stac-spec/blob/master/item-spec/item-spec.md)|STAC Item|False|True|
|[wmo-cmp](https://community.wmo.int/site/knowledge-hub/programmes-and-initiatives/wmo-coordination-mechanism-wcm-support-humanitarian-activities/wcmp)|WMO Core Metadata Profile (WCMP)|False|True|
|[wmo-wcmp2](https://wmo-im.github.io/wcmp2/standard/wcmp2-STABLE.html)|WMO Core Metadata Profile (WCMP) Version 2|False|True|
|[wmo-wigos](https://library.wmo.int/idurl/4/55626)|WMO WIGOS Metadata Standard|False|True|

## History

Started in 2009, pygeometa originated within an internal project called pygdm,
which provided generic geospatial data management functions.  pygdm (now end
of life) was used for generating MSC/CMC geospatial metadata.  pygeometa was
pulled out of pygdm to focus on the core requirement of generating geospatial
metadata within a real-time environment and automated workflows.

In 2015 pygeometa was made publically available in support of the Treasury
Board [Policy on Acceptable Network and Device Use](https://www.tbs-sct.gc.ca/pol/doc-eng.aspx?id=27122).
