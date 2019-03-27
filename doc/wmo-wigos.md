# WMO WIGOS Metadata Standard Reference

This documentation focuses on the [WMO WIGOS Metadata Standard](https://library.wmo.int/opac/doc_num.php?explnum_id=3653) based schema
enhancements in pygeometa.

pygeometa's MCF model for WIGOS Metadata inherits as well as extends the core
MCF constructs.

## Codes

Codes for WMO WIGOS are available at http://test.wmocodes.info/wmdr

## Sections

### `metadata`

See MCF reference

### `contact`

See MCF reference.  WMO WIGOS MCF add the contact type `facility` to
attach contact information to a facility.  The main MCF contact is attached
to the `wmdr:Header` element.

### `identification`

See MCF reference

### `facility`

The `facility` object consists of 1..n keys.  Key names are up to the user
with key objects having the model below.

Property Name|Mandatory/Optional|Description|Example|Reference
-------------|------------------|-----------|-------|---------:
identifier|Mandatory|WMO WIGOS identifier|0-20008-0-JFJ|WIGOS Metadata Representation, Section 8.6.4
name|Mandatory|WIGOS Metadata Representation, Section 4.3
type|Optional|The type of the observing facility from the MonitoringFacilityType codelist (http://test.wmocodes.info/wmdr/_FacilityType)|landFixed|WIGOS Metadata Representation, Section 4.3.2
geopositioning_method|Element describes the geospatial refer ence system used for the specified geolocation (codelist http://test.wmocodes.info/wmdr/_GeopositioningMethod)|Optional|gps|WIGOS Metadata Representation, Section 4.2.2
url|Optional|An online resource containing additional information about the facility or equipment|https://example.org/station/123|WIGOS Metadata Representation, Section 4.2.2
date_established|Mandatory|Date at which the observingFacility was established. Normally considered to be the date the first observations were made|2011-11-11T11:11:11Z|WIGOS Metadata Representation, Section 4.3.2
wmo_region|Mandatory|The WMO region the observing facility is located in, from the WMORegionType codelist (http://test.wmocodes.info/wmdr/_WMORegion)|northCentralAmericaCaribbean|WIGOS Metadata Representation, Section 4.3.2

#### `territory`

The `territory` object is a child of the `facility` object

Property Name|Mandatory/Optional|Description|Example|Reference
-------------|------------------|-----------|-------|---------:
name|The territory the observing facility is located in, from the TerritoryType codelist (http://test.wmocodes.info/wmdr/_TerritoryName)|Mandatory|CAN|WIGOS Metadata Representation, Section 4.3.2
valid_period|Specifies at least the begin date of the indicated territoryName. If omitted, the dateEstablished of the facility will be assumed|Optional|`begin:2011-11-11`, `end: now`|WIGOS Metadata Representation, Section 4.3.2

#### `spatiotemporal`

The `spatiotemporal` object is a child of the `facility` object and
allows for specifying 1..n child objects to model a moving location
over time.  At least one child object is required.

Property Name|Mandatory/Optional|Description|Example|Reference
-------------|------------------|-----------|-------|---------:
timeperiod|Specifies at least the begin date accompanying the location|Mandatory|`begin:2011-11-11`, `end: now`|WIGOS Metadata Representation, Section 7.9
location|Representative or conventional geospatial location of observing facility, the reference location. This will always be a point location, but this location can change with time. |Mandatory.  The location property includes a `crs` property (EPSG code), and `point`` property (x,y,z)|`crs: 4326, point: -75,45,400`, `end: now`|WIGOS Metadata Representation, Section 7.9
