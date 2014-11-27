# pygeometa

pygeometa is a Python package to generate metadata for geospatial datasets.

## Table of Contents
* [Overview](#overview)
* [Installation](#installation)
  * [Requirements](#requirements)
  * [Dependencies](#depedencies)
  * [Installing the Package](installing-the-package)
* [Running](#running)
  * [From the command line](#from-the-command-line)
  * [Using the API from Python](#using-the-api-from-python)
* [Development](#development)
  * [Setting up a Development Environment](#setting-up-a-development-environment)
  * [Adding Another Metadata Format](#adding-another-metadata-format)
  * [Running Tests](#running-tests)
  * [Code Conventions](#code-conventions)
  * [Bugs and Issues](#bugs-and-issues)
  * [To do](#to-do)
* [History](#history)
* [Contact](#contact)
* [Metadata Control File Reference](#metadata-control-file-reference)

## Overview

pygeometa is a Python package to generate metadata for geospatial datasets.

Workflow to generate metadata XML:
1. Install pygeometa
2. Create a 'metadata control file' .mcf file that contains metadata information 
  1. Refer to the [sample.mcf](/ec-msc/pygeometa/blob/master/sample.mcf) example
3. Run pygeometa for the .mcf file with a specified target metadata format


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
Then modify `*.j2` files in the new `pygeometa/templates/new-format` directory to comply to new metadata format.

### Running Tests

TODO

### Code Conventions

* [PEP8](https://www.python.org/dev/peps/pep-0008)

### Bugs and Issues

All bugs, enhancements and issues can be logged on SSC GitLab at
http://gitlab-omnibus.ssc.etg.gc.ca/ec-msc/pygeometa/issues

### To do

* Support local metadata format, in addition to the formats provided in `pygeometa/templates/`

## History

pygeometa originated within the [pygdm](https://wiki.cmc.ec.gc.ca/wiki/Pygdm) project, which provided generic geospatial data management functions.  pygdm (now at end of life) was used for generating MSC/CMC geospatial metadata.

pygeometa was pulled out of pygdm to focus on the core requirement of generating geospatial metadata within a real-time environment.

## Contact

* [Tom Kralidis](http://geds20-sage20.ssc-spc.gc.ca/en/GEDS20/?pgid=015&dn=cn%3DKralidis\\%2C+Tom%2Cou%3DDAT-GES%2Cou%3DMON-STR%2Cou%3DMON-DIR%2Cou%3DMSCB-DGSMC%2COU%3DDMO-CSM%2COU%3DEC-EC%2CO%3Dgc%2CC%3Dca)
* [Alexandre Leroux](http://geds20-sage20.ssc-spc.gc.ca/en/GEDS20/?pgid=015&dn=cn%3DLeroux\\%2C+Alexandre%2Cou%3DDPS-DPS%2Cou%3DCAN-OPE%2Cou%3DCAN-CEN%2Cou%3DMSCB-DGSMC%2COU%3DDMO-CSM%2COU%3DEC-EC%2CO%3Dgc%2CC%3Dca)

## Metadata Control File Reference

### Basic Concepts

* sections are case insensitive
* section parameters are case insensitive
* section parameter values are case sensitive
* if an optional section is specified, then its child parameters' cardinality are enforced
* filename conventions are up to the user. However, below are some suggestions:
 * use ``.mcf`` as file extension
 * name the MCF file basename the same as the dataset (e.g. ``foo.shp``, ``foo.mcf``)

### Sections

#### `[metadata]`

Property Name|Mandatory/Optional|Description|Example|Reference
-------------|------------------|-----------|-------|---------:
identifier|Mandatory|unique identifier for this metadata file|11800c2c-e6b9-11df-b9ae-0014c2c00eab|ISO 19115:2003 Section B.2.1
language|Mandatory|language used for documenting metadata|eng; CAN|ISO 19115:2003 Section B.2.1
charset|Mandatory|full name of the character coding standard used for the metadata set|utf8|ISO 19115:2003 Section B.2.1
parentidentifier|Optional|file identifier of the metadata to which this metadata is a subset|11800c2c-e6b9-11df-b9ae-0014c2c33ebe|ISO 19115:2003 Section B.2.1
hierarchylevel|Mandatory|level to which the metadata applies (must be one of 'series', 'software', 'featureType', 'model', 'collectionHardware', 'collectionSession', 'nonGeographicDataset', 'propertyType', 'fieldSession', 'dataset', 'service', 'attribute', 'attributeType', 'tile', 'feature', 'dimensionGroup'|dataset|ISO 19115:2003 Section B.2.1
datestamp|Mandatory|date that the metadata was created|2000-11-11 or 2000-01-12T11:11:11Z|ISO 19115:2003 Section B.2.1
dataseturi|Mandatory|Uniformed Resource Identifier (URI) of the dataset to which the metadata applies|urn:x-wmo:md:int.wmo.wis::http://geo.woudc.org/def/data/uv-radiation/uv-irradiance|ISO 19115:2003 Section B.2.1

#### `[spatial]`

Property Name|Mandatory/Optional|Description|Example|Reference
-------------|------------------|-----------|-------|---------:
datatype|Mandatory|method used to represent geographic information in the dataset (must be one of 'vector', 'grid', 'textTable', 'tin', 'stereoModel', 'video')|vector|Section B.5.26
geomtype|Mandatory|name of point or vector objects used to locate zero-, one-, two-, or threedimensional spatial locations in the dataset (must be one of 'complex', 'composite', 'curve', 'point', 'solid', 'surface')|point|ISO 19115:2003 B.5.15
crs|Mandatory|EPSG code identifier|4326|ISO 19115:2003 B.2.7.3
bbox|Mandatory|geographic position of the dataset, formatted as 'minx,miny,maxx,maxy'|-141,42,-52,84|ISO 19115:2003 Section B.3.1.2


#### `[identification]`

**This section is REQUIRED**

.. csv-table::
  :header: Property Name, Mandatory/Optional, Description, Example, Reference

  language,Mandatory,language(s) used within the dataset,eng; CAN,ISO 19115:2003 Section B.2.2.1
  charset,Mandatory,full name of the character coding standard used for the dataset,eng; CAN,ISO 19115:2003 Section B.2.1
  status,Mandatory,"the status of the resource(s) (must be one of
  'planned','historicalArchive','completed','onGoing',
  'underDevelopment','required','obsolete')",completed,ISO 19115:2003 Section B.2.2.1
  title,Mandatory,name by which the cited resource is known,Important Bird Areas,ISO 19115:2003 Section B.3.2.1
  abstract,Mandatory,brief narrative summary of the content of the resource(s),Birds in important areas...,ISO 19115:2003 Section B.2.2.1
  keywords,Mandatory,"category keywords","keyword1,keyword2,keyword3",ISO 19115:2003 Section B.2.2.1
  isotopiccategory,Mandatory,"main theme(s) of the dataset
  (must be one of 'geoscientificInformation', 'farming',
  'elevation', 'utilitiesCommunication',
  'oceans', 'boundaries',
  'inlandWaters', 'intelligenceMilitary',
  'environment', 'location',
  'economy', 'planningCadastre','biota', 'health',
  'imageryBaseMapsEarthCover',
  'transportation', 'society', 'structure',
  'climatologyMeteorologyAtmosphere'.  Can be repeated (comma separated)","imageryBaseMapsEarthCover,biota",ISO 19115:2003 Section B.5.27
  date,Mandatory,reference date for the cited resource,2000-09-01T00:00:00Z,ISO 19115:2003 Section B.3.2.4
  datetype,Mandatory,"date used for the reference date (must be one of 'revision', 'publication', 'creation)",creation,ISO 19115:2003 Section B.3.2.4
  url,Mandatory,URL of the dataset to which the metadata applies,http://host/path/,ISO 19115:2003 Section B.2.1
  temporal,Mandatory,"time period covered by the content of the dataset, either time period (startdate/enddate) or a single point in time value.  For data updated in realtime, use the term 'now' (i.e. '2005/now')",1950-07-31/1995-10-19,ISO 19115:2003 Section B.3.1.3
  accessconstraints,Mandatory,"access constraints
  applied to assure the protection of
  privacy or intellectual property, and any special
  restrictions or limitations on obtaining the
  resource or metadata (must be one of 'patent',
  'otherRestrictions','copyright','trademark',
  'patentPending','restricted','license',
  'intellectualPropertyRights').
  If there are no accessconstraints, use the term 'otherRestrictions'",None,ISO 19115:2003 Section B.2.3
  fees,Mandatory,"fees and terms for retreiving the resource.  Include monetary units (as specified in ISO 4217).  If there are no fees, use the term 'None'",None,ISO 19115:2003 Section B.2.10.6
  rights,Mandatory,Information about rights held in and over the resource,Copyright (c) 2010 Her Majesty the Queen in Right of Canada,DMCI 1.1


#### `[contact]`

**This section is REQUIRED**.

Note: additional contact sections can be defined in accordance with the ISO 19115 `CI_RoleCode <http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#CI_RoleCodeType>`_ enumeration:

- author
- processor
- publisher
- custodian
- pointOfContact
- distributor
- user
- resourceProvider
- originator
- owner
- principalInvestigator

Section parameters are identical to the main contact section.

Example:

.. code-block:: text

  [contact]

  city=Toronto
  ...

  [orginator]
  city=Montréal

This allows definition of multiple sections of contact information if required, which will be mapped to the appropriate slot in the output metadata.

The contact section itself is required for a main point of contact.

.. csv-table::
  :header: Property Name, Mandatory/Optional, Description, Example, ISO 19115:2003 Reference

  individualname,Mandatory,"name of the responsible person-surname,given name,title seperated by a delimiter","Kralidis, Tom",ISO 19115:2003 Section B.3.2.1
  organization,Mandatory,name of the responsible organization,Environment Canada,ISO 19115:2003 Section B.3.2.1
  positionname,Mandatory,role or position of the responsible person,Senior Systems Scientist,ISO 19115:2003 Section B.3.2.1
  phone,Mandatory,telephone number by which individuals can speak to the responsible organization or individual,+01-416-739-4907,ISO 19115:2003 Section B.3.2.7
  fax,Mandatory,telephone number of a facsimile machine for the responsible organization or individual,+01-416-739-4261,ISO 19115:2003 Section B.3.2.7
  address,Mandatory,"address line for the location (as described in ISO 11180, Annex A)",123 Main Street,ISO 19115:2003 Section B.3.2.2
  city,Mandatory,city of the location,Toronto,ISO 19115:2003 Section B.3.2.2
  administrativearea,Mandatory,"state, province of the location",Ontario, ISO 19115:2003 Section B.3.2.2
  postalcode,Mandatory,ZIP or other postal code,M3H 5T4,ISO 19115:2003 Section B.3.2.2
  country,Mandatory,country of the physical address,Canada,ISO 19115:2003 Section B.3.2.2
  email,Mandatory,address of the electronic mailbox of the responsible organization or individual,tom.kralidis@ec.gc.ca,ISO 19115:2003 Section B.3.2.2
  url,Mandatory,on-line information that can be used to contact the individual or organization,http://host/path,ISO 19115:2003 Section B.3.2.3
  hoursofservice,Optional,time period (including time zone) when individuals can contact the organization or individual,0700h - 1500h EST,ISO 19115:2003 Section B.3.2.3
  contactinstructions,Optional,supplementalinstructions on how or when to contact the individual or organization,contact during working business hours,ISO 19115:2003 Section B.3.2.3
  role,Mandatory,"function performed by the responsible party
  (must be one of 'author','processor','publisher','custodian',
  'pointOfContact','distributor','user','resourceProvider',
  'originator','owner','principalInvestigator')",pointOfContact,ISO 19115:2003 Section B.3.2.1

#### `[distribution]`

**This section is OPTIONAL**

.. csv-table::
  :header: Property Name, Mandatory/Optional, Description, Example, ISO 19115:2003 Reference

  kml,Optional,URL which provides this data as a KML document,http://host/path,ISO 19115:2003 Section B.3.2.5
  wms,Optional,URL which provides this data as a WMS layer,http://host/path,ISO 19115:2003 Section B.3.2.5
  wfs,Optional,URL which provides this data as a WFS feature type,http://host/path,ISO 19115:2003 Section B.3.2.5
  wcs,Optional,URL which provides this data as a WCS coverage,http://host/path,ISO 19115:2003 Section B.3.2.5
  wmc,Optional,URL which provides this data in a WMC document,http://host/path,ISO 19115:2003 Section B.3.2.5
  ftp,Optional,URL which provides this data via FTP download,http://host/path,ISO 19115:2003 Section B.3.2.5
  http,Optional,URL which provides this data via HTTP download,http://host/path,ISO 19115:2003 Section B.3.2.5
  rss,Optional,URL which provides this data via RSS feed,http://host/path,ISO 19115:2003 Section B.3.2.5
  related,Optional,related URL which provides information about this data,http://host/path,ISO 19115:2003 Section B.3.2.5
  samples,Optional,URL which showcases this data,http://host/path,ISO 19115:2003 Section B.3.2.5
  link,Optional,generic URL which provides more information about this data,http://host/path,ISO 19115:2003 Section B.3.2.5

