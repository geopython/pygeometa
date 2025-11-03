# Metadata Control File Reference

Version: 1.0

## Basic Concepts

* Section names are case sensitive
* Section parameter names are case sensitive
* Section parameter codelist values are case sensitive
* YAML [rules, conventions and features](https://en.wikipedia.org/wiki/YAML) are suppported, such as:
    * node anchors / references
    * data typing
    * commented lines (`#`)
* If an optional section is specified, then its child parameter cardinality is enforced
* Filename conventions are up to the user. However, below are some suggestions:
    * use `.yml` as file extension
    * name the MCF basename the same as the dataset (e.g. `foo.shp`, `foo.yml`)
* For colons (`:`) in text values, use quotation marks (`"` or `'`) on either side of your text to avoid parsing errors

## Version format

MCFs are versioned using X.Y (MAJOR.MINOR changes) format. If a non supported MCF version is provided, pygeometa will throw an error and stop processing the MCF. Thus, the user must provide a valid and supported MCF version to generate the metadata.

## Encoding

The MCF **MUST** be UTF-8 encoded.  That is all.

```bash
# editing in vim
# :set encoding=utf8
# pasting in vim
# in insert mode, hit CTRL-V $CODE, where $CODE is as per https://www.htmlhelp.com/reference/charset
# to see how the file is actually encoded on disk
file --mime-encoding file.txt
file -i file.txt
# to convert from one encoding to another
iconv -f iso8859-1 -t utf-8 file.yml > file.yml.new
```

## Nesting MCFs

In the case where the user is generating metadata for multiple datasets which have common information, it becomes efficient to nest MCFs. pygeometa allows chaining MCFs to inherit values from other MCFs. Example: multiple datasets MCFs can refer a single MCF that contain contact information common to all those datasets.

To use MCF nesting:

* Add `base_mcf: foo.yml` at the top of any section of a MCF
* Specify the corresponding section in the base_mcf file

Notes about nesting MCFs: 

* One `base_mcf` per section of a MCF may be used
* Multiple sections can refer to the same base_mcf file
* When a parameter is defined in both the base_mcf file and the current MCF, it's always the current MCF that overwrites the base_mcf file
    * Note that if a parameter in the current MCF is a YAML list, the corresponding base_mcf list (if it exists) is entirely overwritten  
* MCFs can be nested in chains, meaning a MCF can be use a 'child' MCF and be used by a 'parent' MCF

## Environment variables

pygeometa supports use of environment variables, using the notation in the example MCF snippet below:

```yaml
metadata:
    identifier: 3f342f64-9348-11df-ba6a-0014c2c00eab
    parentidentifier: ${COLLECTION_ID}
```

## Multilingual support

pygeometa supports default and alternate languages in ISO metadata.

Multilingual support is driven by the following sections in `[metadata]`:

* `language`: 2 letter language code (i.e. `en`, `fr`) of primary language
* `language_alternate`: 2 letter language code (i.e. `en`, `fr`) of secondary language

Example:

```yaml
metadata:
    language: en
    language_alternate: fr
```

If `language_alternate` is not defined or missing, pygeometa assumes a single language.

Values which support multilingual values can be specified with as keys to denote the respective language.  Examples:

```yaml
# single language
title: foo

# single language, explicit
title:
    en: foo

# two languages, explicit
title:
    en: foo
    fr: bar
```

The ```language``` value in the ```metadata``` section **must** be a 2 letter language code (e.g. ```es``` for Spanish).

## Keyword Substitution

pygeometa supports using the following keyword substitutions:

Keyword|Description|Format|Example
-------|-----------|------|-------:
`$year$`|current year|`YYYY`|2016
`$date$`|current date|`YYYY-MM-DD`|2016-12-22
`$datetime$`|current date and time|`YYYY-MM-DDThh:mm:ssZ`|2016-12-22T16:34:15Z

# Reference

## Sections

### `mcf`

Property Name|Mandatory/Optional|Description|Example|Reference
-------------|------------------|-----------|-------|---------:
version|Mandatory|version of MCF format|1.0|pygeometa

### `metadata`

Property Name|Mandatory/Optional|Description|Example|Reference
-------------|------------------|-----------|-------|---------:
identifier|Mandatory|unique identifier for this metadata file|11800c2c-e6b9-11df-b9ae-0014c2c00eab|ISO 19115:2003 Section B.2.1
language|Mandatory|primary language used for documenting metadata, the metadata records themselves can be provided in multiple languages nonetheless|en|ISO 19115:2003 Section B.2.1
language_alternate|Optional|alternate language used for documenting metadata|en|ISO 19115:2003 Annex J
charset|Mandatory|full name of the character coding standard used for the metadata set|utf8|ISO 19115:2003 Section B.2.1
parentidentifier|Optional|file identifier of the metadata to which this metadata is a subset|11800c2c-e6b9-11df-b9ae-0014c2c33ebe|ISO 19115:2003 Section B.2.1
hierarchylevel|Mandatory|level to which the metadata applies (must be one of 'series', 'software', 'featureType', 'model', 'collectionHardware', 'collectionSession', 'nonGeographicDataset', 'propertyType', 'fieldSession', 'dataset', 'service', 'attribute', 'attributeType', 'tile', 'feature', 'dimensionGroup'|dataset|ISO 19115:2003 Section B.2.1
datestamp|Mandatory|date that the metadata was created, pygeometa supports specifying the $date$ or $datetime$ variable to update the date value at run time|2000-11-11 or 2000-01-12T11:11:11Z|ISO 19115:2003 Section B.2.1
dataseturi|Optional|Uniformed Resource Identifier (URI) of the dataset to which the metadata applies|`urn:x-wmo:md:int.wmo.wis::http://geo.woudc.org/def/data/uv-radiation/uv-irradiance`|ISO 19115:2003 Section B.2.1

### `metadata.additional_identifiers`

Property Name|Mandatory/Optional|Description|Example|Reference
-------------|------------------|-----------|-------|---------:
identifier|Mandatory|identifier|10.5324/3f342f64|ISO 19115:2003 Section B.2.1
scheme|Optional|scheme in which this identifier is defined (e.g. ark, doi, handle, isbn, lccn, sku).  Note that the schema may also be a URI|https://doi.org|ISO 19115:2003 Section B.2.1

### `metadata.relations`

Property Name|Mandatory/Optional|Description|Example|Reference
-------------|------------------|-----------|-------|---------:
identifier|Mandatory|identifier|10.5324/3f342f64|ISO 19115:2003 Section B.2.1
scheme|Optional|scheme in which this identifier is defined (e.g. ark, doi, handle, isbn, lccn, sku).  Note that the schema may also be a URI|https://doi.org|ISO 19115:2003 Section B.2.1
type|Optional|a relation type (source, partof, version, reference, ...)|source|ISO 19115:2003 Section B.2.1

### `spatial`

Property Name|Mandatory/Optional|Description|Example|Reference
-------------|------------------|-----------|-------|---------:
datatype|Mandatory|method used to represent geographic information in the dataset (must be one of 'vector', 'grid', 'textTable', 'tin', 'stereoModel', 'video')|vector|Section B.5.26
geomtype|Mandatory|name of point or vector objects used to locate zero-, one-, two-, or threedimensional spatial locations in the dataset (must be one of 'complex', 'composite', 'curve', 'point', 'solid', 'surface')|point|ISO 19115:2003 B.5.15

### `identification`

Property Name|Mandatory/Optional|Description|Example|Reference
-------------|------------------|-----------|-------|---------:
language|Optional|language(s) used within the dataset. If the dataset is made of numerical values, the dataset language can be set to 'missing', 'withheld', 'inapplicable', 'unknown' or 'template'|eng; CAN|ISO 19115:2003 Section B.2.2.1
charset|Optional|full name of the character coding standard used for the dataset|eng; CAN|ISO 19115:2003 Section B.2.1
title|Mandatory|name by which the cited resource is known|Important Bird Areas|ISO 19115:2003 Section B.3.2.1
edition|Optional|version of the cited resource|1.8.0|ISO 19115:2003 Section B.3.2.1
abstract|Mandatory|brief narrative summary of the content of the resource(s)|Birds in important areas...|ISO 19115:2003 Section B.2.2.1
topiccategory|Optional|main theme(s) of the dataset (must be one of 'geoscientificInformation', 'farming', 'elevation', 'utilitiesCommunication', 'oceans', 'boundaries', 'inlandWaters', 'intelligenceMilitary', 'environment', 'location', 'economy', 'planningCadastre','biota', 'health', 'imageryBaseMapsEarthCover', 'transportation', 'society', 'structure', 'climatologyMeteorologyAtmosphere'. More than one topic category can be specified|climatologyMeteorologyAtmosphere|ISO 19115:2003 Section B.5.27
fees|Optional|fees and terms for retreiving the resource.  Include monetary units (as specified in ISO 4217).  If there are no fees, use the term 'None'|None|ISO 19115:2003 Section B.2.10.6
accessconstraints|Optional|access constraints applied to assure the protection of privacy or intellectual property, and any special restrictions or limitations on obtaining the resource or metadata (must be one of 'patent', 'otherRestrictions','copyright','trademark', 'patentPending','restricted','license', 'intellectualPropertyRights').  If there are no accessconstraints, use the term 'otherRestrictions'|None|ISO 19115:2003 Section B.2.3
rights|Mandatory|Information about rights held in and over the resource. pygeometa supports using the $year$ variable to update the year value at run time. |Copyright (c) 2010 Her Majesty the Queen in Right of Canada|DMCI 1.1
url|Mandatory|URL of the dataset to which the metadata applies|https://example.org/data|ISO 19115:2003 Section B.2.1
status|Mandatory|"the status of the resource(s) (must be one of 'planned','historicalArchive','completed','onGoing', 'underDevelopment','required','obsolete')"|completed|ISO 19115:2003 Section B.2.2.1
maintenancefrequency|Optional|frequency with which modifications and deletions are made to the data after it is first produced (must be one of 'continual', 'daily', 'weekly', 'fortnightly', 'monthly', 'quarterly', 'biannually', 'annually', 'asNeeded', 'irregular', 'notPlanned', 'unknown'|continual|ISO 19115:2003 B.5.18
browsegraphic|Optional|graphic that provides an illustration of the dataset|https://example.org/dataset.png|ISO 19115:2003 B.2.2.2

#### `identification.dates`

`identification.dates` sections can have 1..n `dates` sections as required with the following object names/types:

Property Name|Mandatory/Optional|Description|Example|Reference
-------------|------------------|-----------|-------|---------:
creation|Mandatory*|'creation' reference date for the cited resource, referring to when the resource was brought into existence, *: presence of creation or publication or revision is mandatory|2000-09-01 or 2000-09-01T00:00:00Z|ISO 19115:2003 Section B.3.2.4
publication|Optional*|'publication' reference date for the cited resource, referring to when the resource was issued, *: presence of creation or publication or revision is mandatory|2000-09-01 or 2000-09-01T00:00:00Z|ISO 19115:2003 Section B.3.2.4
revision|Optional*|'revision' reference date for the cited resource, refersring to when the resource was examined or re-examined and improved or amended, *: presence of creation or publication or revision is mandatory|2000-09-01 or 2000-09-01T00:00:00Z|ISO 19115:2003 Section B.3.2.4

```yaml
identification:
    ...
    dates:
        creation: 2011-11-11
        publication: 2000-09-01T00:00:00Z
```

#### `identification.extents`

`identification.extents` sections can have 1..n `spatial` and `temporal` sections as required with the following properties.

Property Name|Mandatory/Optional|Description|Example|Reference
-------------|------------------|-----------|-------|---------:
spatial.bbox|Mandatory|geographic position of the dataset, formatted as as list of [minx,miny,maxx,maxy]|-141,42,-52,84|ISO 19115:2003 Section B.3.1.2
spatial.crs|Mandatory|EPSG code identifier|4326|ISO 19115:2003 Section B.2.7.3
spatial.description|Optional|description of the geographic area using an identifier|Toronto, Ontario, Canada|ISO 19115:2003 Section B.3.1.2
temporal.begin|Optional|Starting time period covered by the content of the dataset, either time period (startdate/enddate) or a single point in time value|1950-07-31|ISO 19115:2003 Section B.3.1.3
temporal.end|Optional|End time period covered by the content of the dataset, either time period (startdate/enddate) or a single point in time value.  For data updated in realtime, use the term `now`|now|ISO 19115:2003 Section B.3.1.3
temporal.resolution|Optional|Minimum time period resolvable in the dataset, as an ISO 8601 duration|P1D|ISO 19108

```yaml
identification:
    ...
    extents:
        spatial:
            - bbox: [-141,42,-52,84]
              crs: 4326
        temporal:
            - begin: 1950-07-31
              end: now
              resolution: P1D
```

#### `identification.keywords`

`identification` sections can have 1..n `keywords` sections as required using nesting.  Example:

```yaml
identification:
    ...
    keywords:
        default:
            keywords:
                en: [foo1, bar1]
                fr: [foo2, bar2]
            keywords_type: theme
            vocabulary:
                name: my vocabulary
                url: https://example.org/vocab
        wmo:
            keywords:
                en: [foo3, bar3]
                fr: [foo4, bar4]
            keywords_type: theme
            keywords_codelist: https://wis.wmo.int/2011/schemata/iso19139_2007/schema/resources/Codelist/gmxCodelists.xml#MD_KeywordTypeCode
```

Schema specific keywords sections

* `wmo`: World Meteorological Organization keywords (used for WMO Core Metadata Profile)
* `gc_cst`: Government of Canada Core Subject Thesaurus (used for HNAP)
* `hnap_category_information`: HNAP
* `hnap_category_geography`: HNAP
* `hnap_category_content`: HNAP

Within each `keywords` section, the following elements are supported:

Property Name|Mandatory/Optional|Description|Example|Reference
-------------|------------------|-----------|-------|---------:
keywords|Mandatory|category keywords|keyword1,keyword2,keyword3|ISO 19115:2003 Section B.2.2.1
keywords_type|Mandatory|subject matter used to group similar keywords (must be one of 'discipline', 'place', 'stratum', 'temporal', 'theme')|theme|ISO 19115:2003 Section B.2.2.3
keywords_codelist|Optional|specific code list URL (for advanced use cases, else the default is as per the given specified schema)|https://wis.wmo.int/2011/schemata/iso19139_2007/schema/resources/Codelist/gmxCodelists.xml|ISO 19115:2003 Section B.2.2.3


##### `identification.keywords.vocabulary`

`identification.keywords` sections can specify an optional `vocabulary` section with the following elements:

Property Name|Mandatory/Optional|Description|Example|Reference
-------------|------------------|-----------|-------|---------:
name|Mandatory|name of the source of keywords (English)|my thesaurus name|ISO 19115:2003 Section B.2.2.3
url|Optional|URL of source of keywords|https://example.org/my-vocab|-

##### `identification.license`

`identification.license` sections can provide a optinoal license via a name or URL using the following elements:

Property Name|Mandatory/Optional|Description|Example|Reference
-------------|------------------|-----------|-------|---------:
name|Mandatory|name of license|CC BY 4.0|-
url|Optional|URL of license|https://creativecommons.org/licenses/by/4.0|-

### `content_info`

Property Name|Mandatory/Optional|Description|Example|Reference
-------------|------------------|-----------|-------|---------:
type|Mandatory|Content type (must be one of 'coverage', 'image', 'feature_catalogue'|image|ISO 19115:2003 Section B.2.8.1
cloud_cover|Optional|area of the dataset obscured by clouds, expressed as a percentage of the spatial extent|72|ISO 19115:2003 Section B.2.8.1
processing_level|Optional|image distributor’s code that identifies the level of radiometric and geometric processing that has been applied|L1|ISO 19115:2003 Section B.2.8.1

#### `content_info.attributes`

`content_info` sections can have 1..n `attributes` sections as required using nesting.  Example:

```yaml
attributes:
    - name: temperature
      title:
          en: Air temperature
      abstract:
          en: Description of air temperature attribute
      type: number
      units: K
      values: [1.2, 2.5, 1.3]
```

Property Name|Mandatory/Optional|Description|Example|Reference
-------------|------------------|-----------|-------|---------:
name|Mandatory|attribute name|`temperature`||
title|Optional|attribute title|Air temperature||
abstract|Optional|attribute description|Description of air temperature||
url|Optional|URL with more information about the attribute|Air temperature||
type|Optional|data type|(must be one of 'string', 'number', 'integer', 'object', 'array', 'boolean')|string||
units|Optional|SI units|K|https://en.wikipedia.org/wiki/International_System_of_Units|
values|Optional|specification of attribute values|see below||

##### `content_info.attributes.values`

Attributes may also provide the values within a given domain, via one of the following constructs:

###### `content_info.attributes.values.enum`

Property Name|Mandatory/Optional|Description|Example|Reference
-------------|------------------|-----------|-------|---------:
enum|Optional|Enumerated list of values|[1, 2, 3, 4]||

Example:

```yaml
 values:
    enum: [1, 2, 3. 4]
```

###### `content_info.attributes.values.range`

Property Name|Mandatory/Optional|Description|Example|Reference
-------------|------------------|-----------|-------|---------:
range|Optional|Range of values (min/max)|[1, 4]||

Example:

```yaml
 values:
    range: [1, 4]
```

###### `content_info.attributes.values.codelist`

Property Name|Mandatory/Optional|Description|Example|Reference
-------------|------------------|-----------|-------|---------:
codelist|Optional|codelist of values|see below||
codelist.name|Mandatory|value name|foo||
codelist.title|Optional|value title|Foo||
codelist.abstract|Optional|value abstract|Description of value Foo||
codelist.url|Optional|URL with more information about the value|https://example.org/foo|

Example:

```yaml
values:
    codelist:
     - name: foo
       title:
           en: foo title
       abstract:
           en: foo description
       url: https://example.org/values/foo
```

#### `content_info.dimensions`

`content_info` objects support 1..n `dimension` objects.


Property Name|Mandatory/Optional|Description|Example|Reference
-------------|------------------|-----------|-------|---------:
name|Mandatory|name of dimension|B1|ISO 19115:2003 Section B.2.8.2
units|Mandatory|units in which sensor wavelengths are expressed|nm|ISO 19115:2003 Section B.2.8.2
min|Mandatory|shortest wavelength that the sensor is capable of collecting within a designated band|101|ISO 19115:2003 Section B.2.8.2
max|Mandatory|longest wavelength that the sensor is capable of collecting within a designated band|199|ISO 19115:2003 Section B.2.8.2

### `contact`

MCFs can have 1..n `contact` sections as required using nesting.  Example:

```yaml
contact:
    pointOfContact:
        ....
    distributor:
        ....
```

The `contact.pointOfContact` section provides information for the `pointOfContact` role (see ISO 19115:2003 Section B.3.2.1).  This section is minimally required.

Within each `contact` section, the following elements are supported:

Property Name|Mandatory/Optional|Description|Example|Reference
-------------|------------------|-----------|-------|---------:
organization|Mandatory|name of the responsible organization|Environment Canada|ISO 19115:2003 Section B.3.2.1
url|Mandatory|on-line information that can be used to contact the individual or organization|https://example.org/data|ISO 19115:2003 Section B.3.2.3
individualname|Mandatory|name of the responsible person-surname|given name|title seperated by a delimiter|Lastname, Firstname|ISO 19115:2003 Section B.3.2.1
positionname|Mandatory|role or position of the responsible person|Senior Systems Scientist|ISO 19115:2003 Section B.3.2.1
phone|Mandatory|telephone number by which individuals can speak to the responsible organization or individual|+01-123-456-7890|ISO 19115:2003 Section B.3.2.7
fax|Mandatory|telephone number of a facsimile machine for the responsible organization or individual|+01-123-456-7890|ISO 19115:2003 Section B.3.2.7
address|Mandatory|address line for the location (as described in ISO 11180| Annex A)|4905 Dufferin Street|ISO 19115:2003 Section B.3.2.2
city|Mandatory|city of the location|Toronto|ISO 19115:2003 Section B.3.2.2
administrativearea|Mandatory|state, province of the location|Ontario|ISO 19115:2003 Section B.3.2.2
postalcode|Mandatory|ZIP or other postal code|M3H 5T4|ISO 19115:2003 Section B.3.2.2
country|Mandatory|country of the physical address|Canada|ISO 19115:2003 Section B.3.2.2
email|Mandatory|address of the electronic mailbox of the responsible organization or individual|foo@bar.tld|ISO 19115:2003 Section B.3.2.2
hoursofservice|Optional|time period (including time zone) when individuals can contact the organization or individual|0700h - 1500h EST|ISO 19115:2003 Section B.3.2.3
contactinstructions|Optional|supplementalinstructions on how or when to contact the individual or organization|contact during working business hours|ISO 19115:2003 Section B.3.2.3

### `contact.distributor`

The `contact.distributor` section provides information for the `distributor` role (see ISO 19115:2003 Section B.3.2.1) and has the identical structure as `contact.pointOfContact`.

If contact information is the same for both, use YAML node anchors and references to have it provided in both sections in the metadata:

```yaml
contact:
    pointOfContact: &id_contact_poc
        ...

    distributor: *id_contact_poc
```

### `distribution`

MCFs can have 1..n `distribution` sections as required using nesting.  Example:

```yaml
distribution:
    wms:
        ....
    waf:
        ....
```

Within each `distribution` section, the following elements are supported:

Property Name|Mandatory/Optional|Description|Example|Reference
-------------|------------------|-----------|-------|---------:
url|Mandatory|location (address) for on-line access using a Uniform Resource Locator address or similar addressing scheme such as http://www.isotc211.org/|https://example.org/data|ISO 19115:2003 Section B.3.2.5
type|Mandatory|connection protocol to be used.  Must be one of the `identifier` values from https://github.com/OSGeo/Cat-Interop/blob/master/LinkPropertyLookupTable.csv|WWW:LINK|ISO 19115:2003 Section B.3.2.5
rel|Optional|the type or semantic of the relation.  The value should be an [IANA link relation](https://www.iana.org/assignments/link-relations/link-relations.xhtml) or a relation type specific to an established standard|canonical|Link Relations - Internet Assigned Numbers Authority
name|Mandatory|name of the online resource|Download portal|ISO 19115:2003 Section B.3.2.5
description|Mandatory|detailed text description of what the online resources is/does|brief description of the online resource (English)|ISO 19115:2003 Section B.3.2.5
function|Mandatory|code for function performed by the online resource (must be one of 'download', 'information', 'offlineAccess', 'order', 'search')|download|ISO 19115:2003 Section B.3.2.5
format|Optional|Format of the distribution method|WMS|HNAP 2.3
format_version|Optional|Format version of the distribution method. Note: this value needs to be encoded as a string|1.0|HNAP 2.3
channel|Optional|channel/topic/exchange when link is a Pub/Sub endpoint|my/cool/topic|OGC API - Pub/Sub



### `dataquality`

Property Name|Mandatory/Optional|Description|Example|Reference
-------------|------------------|-----------|-------|---------:
scope.level|Optional|hierarchical level of the data specificed by the scope|dataset|ISO 19115:2003 Section B.2.4.5
lineage.statement|Optional|general explanation of the data producer's knowledge about the lineage of a dataset|this dataset was produced from a custom process against dataset xyz|ISO 19115:2003 Section B.2.4.2.1
