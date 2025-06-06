# WMO WIGOS Metadata Standard Reference

This document describes [WMO WIGOS Metadata Standard](https://library.wmo.int/opac/doc_num.php?explnum_id=3653) schema
extensions in pygeometa.

## Codes

Codes for WMO WIGOS are available at https://codes.wmo.int/wmdr

## Sections

### `metadata`

See MCF reference

### `contact`

See MCF reference.  WMO WIGOS MCF add the contact type `facility` to
attach contact information to a facility.  The `pointOfContact` MCF contact is attached
to the `wmdr:Header` element.

### `identification`

See MCF reference

### `facility`

The `facility` object consists of 1..n keys.  Key names are up to the user
with key objects having the model below.

Property Name|Mandatory/Optional|Description|Example|Reference
-------------|------------------|-----------|-------|---------:
identifier|Mandatory|WMO WIGOS identifier|0-20008-0-JFJ|WIGOS Metadata Representation, Section 8.6.4
name|Mandatory|||WIGOS Metadata Representation, Section 4.3
type|Mandatory|The type of the observing facility from the Station/platform type codelist (https://codes.wmo.int/wmdr/_FacilityType)|landFixed|WIGOS Metadata Representation, Section 4.3.2
geopositioning_method|Optional|Element describes the geospatial reference system used for the specified geolocation (codelist https://codes.wmo.int/wmdr/_GeopositioningMethod)|gps|WIGOS Metadata Representation, Section 4.2.2
url|Optional|An online resource containing additional information about the facility or equipment|https://example.org/station/123|WIGOS Metadata Representation, Section 4.2.2
date_established|Mandatory|Date at which the observingFacility was established. Normally considered to be the date the first observations were made|2011-11-11T11:11:11Z|WIGOS Metadata Representation, Section 4.3.2
wmo_region|Mandatory|The WMO region the observing facility is located in, from the WMORegionType codelist (https://codes.wmo.int/wmdr/_WMORegion)|northCentralAmericaCaribbean|WIGOS Metadata Representation, Section 4.3.2

#### `territory`

The `territory` object is a child of the `facility` object and
allows for specifying 1..n child objects to model changing territory names
over time.  At least one child object is required.

Property Name|Mandatory/Optional|Description|Example|Reference
-------------|------------------|-----------|-------|---------:
name|Mandatory|The territory the observing facility is located in, from the TerritoryType codelist (https://codes.wmo.int/wmdr/_TerritoryName)|`CAN`|WIGOS Metadata Representation, Section 4.3.2
valid_period|Optional|Specifies at least the begin date of the indicated territoryName. If omitted, the dateEstablished of the facility will be assumed|`begin: 2011-11-11`, `end: now`|WIGOS Metadata Representation, Section 4.3.2

#### `spatiotemporal`

The `spatiotemporal` object is a child of the `facility` object and
allows for specifying 1..n child objects to model a moving location
over time.  At least one child object is required.

Property Name|Mandatory/Optional|Description|Example|Reference
-------------|------------------|-----------|-------|---------:
timeperiod|Mandatory|Specifies at least the begin date accompanying the location|`begin: 2011-11-11`, `end: now`|WIGOS Metadata Representation, Section 7.9
location|Mandatory.  The location property includes a `crs` property (EPSG code), and `point` property (x,y,z)|Representative or conventional geospatial location of observing facility, the reference location. This will always be a point location, but this location can change with time. |`crs: 4326, point: -75,45,400`, `end: now`|WIGOS Metadata Representation, Section 7.9

#### `program_affiliation`
The `program_affiliation` object is a child of the `facility` object and
allows for specifying 1..n child objects to model program affiliations.

Property Name|Mandatory/Optional|Description|Example|Reference
-------------|------------------|-----------|-------|---------:
program|Mandatory|Program Affiliation, see https://codes.wmo.int/wmdr/_ProgramAffiliation|`GOS`|WIGOS Metadata Representation, Section 4.3.2

#### `reporting_status`
The `reporting_status` object is a child of the `program_affiliation` object and
allows for specifying 1..n child objects to model program affiliations reporting status
over time.

Property Name|Mandatory/Optional|Description|Example|Reference
-------------|------------------|-----------|-------|---------:
status|Mandatory|Declared reporting status of the observing facility from the ReportingStatusType codelist (https://codes.wmo.int/wmdr/_ReportingStatus)|`operational`|
valid_period|Optional|Specifies at least the begin date of the indicated reportingStatus.|`begin: 2011-11-11`, `end: now`|

#### `climate_zone`
The `climate_zone` object is a child of the `facility` object and
allows for specifying 0..n child objects to model changing climate zones over time.

Property Name|Mandatory/Optional|Description|Example|Reference
-------------|------------------|-----------|-------|---------:
name|Mandatory|Climate zone of the observing facility, from the ClimateZone codelist (https://codes.wmo.int/wmdr/_ClimateZone)|`snowFullyHumidCoolSummer`|WIGOS Metadata Representation, Section 4.3.2
valid_period|Optional|Specifies at least the begin date of the indicated climate zone. If omitted, the dateEstablished of the facility will be assumed|`begin: 2011-11-11`, `end: now`|WIGOS Metadata Representation, Section 4.3.2

#### `surface_cover`
The `surface_cover` object is a child of the `facility` object and
allows for specifying 0..n child objects to model changing surface covers over time.

Property Name|Mandatory/Optional|Description|Example|Reference
-------------|------------------|-----------|-------|---------:
name|Mandatory|Predominant surface cover, from the given surface cover classification scheme and the SurfaceCover codelist (https://codes.wmo.int/wmdr/_SurfaceCover)|`rainfedCroplands`|WIGOS Metadata Representation, Section 4.3.2
surface_cover_classification|Mandatory|Surface cover classification scheme, from the SurfaceCoverClassification codelist (https://codes.wmo.int/wmdr/_SurfaceCoverClassification)|`globCover2009`|WIGOS Metadata Representation, Section 4.3.2
valid_period|Optional|Specifies at least the begin date. If omitted, the dateEstablished of the facility will be assumed|`begin: 2011-11-11`, `end: now`|WIGOS Metadata Representation, Section 4.3.2

#### `surface_roughness`
The `surface_roughness` object is a child of the `facility` object and
allows for specifying 0..n child objects.

Property Name|Mandatory/Optional|Description|Example|Reference
-------------|------------------|-----------|-------|---------:
name|Mandatory|Surface roughness of surrounding of the observing facility, from the SurfaceRoughness codelist (https://codes.wmo.int/wmdr/_SurfaceRoughness)|`rough`|WIGOS Metadata Representation, Section 4.3.2
valid_period|Optional|Specifies at least the begin date of the indicated surface roughness. If omitted, the dateEstablished of the facility will be assumed|`begin: 2011-11-11`, `end: now`|WIGOS Metadata Representation, Section 4.3.2

#### `topography_bathymetry`
The `topography_bathymetry` object is a child of the `facility` object and
allows for specifying 0..n child objects to model topography or bathymetry descriptions over time.

Property Name|Mandatory/Optional|Description|Example|Reference
-------------|------------------|-----------|-------|---------:
local_topography|Optional|Local topography of the observing facility from the LocalTopography codelist (https://codes.wmo.int/wmdr/_LocalTopography)|`flat`|WIGOS Metadata Representation, Section 4.3.2
relative_elevation|Optional|Relative elevation of the observing facility compared to its surrounding, from the RelativeElevation codelist (https://codes.wmo.int/wmdr/_RelativeElevation)|`inapplicable`|WIGOS Metadata Representation, Section 4.3.2
topographic_context|Optional|Topographic context of the observing facility, from the TopographicContext codelist (https://codes.wmo.int/wmdr/_TopographicContext)|`plains`|WIGOS Metadata Representation, Section 4.3.2
altitude_or_depth|Optional|Altitude or depth of observing facility, from the AltitudeOrDepth codelist (https://codes.wmo.int/wmdr/_AltitudeOrDepth)|`middleAltitude`|WIGOS Metadata Representation, Section 4.3.2
valid_period|Optional|Specifies at least the begin date. If omitted, the dateEstablished of the facility will be assumed|`begin: 2011-11-11`, `end: now`|WIGOS Metadata Representation, Section 4.3.2

#### `observations`
The `observations` object is a child of the `facility` object and
allows for specifying 0..n child objects to model observations provided by a facility.

Property Name|Mandatory/Optional|Description|Example|Reference
-------------|------------------|-----------|-------|---------:
name|mandatory|Freeform name of observed property|`Total column ozone`|WIGOS Metadata Representation, Section 4.3.2
timeperiod|Optional|The time period over which the property is observed.|`begin: 2011-11-11`, `end: now`|WIGOS Metadata Representation, Section 6.2.5
url|mandatory|The online resource of the final result (output) of the observation|https://example.org/data/atmos/spectral/total-column-ozone/111|WIGOS Metadata Representation, Section 6.2.5
observedproperty|Mandatory|The property type being observed (`ObservingMethodAtmosphere`, `ObservingMethodTerrestrial`, `ObservedVariableAtmosphere`, `ObservedVariableEarth`, `ObservedVariableOcean`, `ObservedVariableOuterSpace`, `ObservedVariableTerrestrial`) and name (see WMO code lists) relevant to the type||`type: ObservingMethodAtmosphere`, `name: 263`|WIGOS Metadata Representation, Section 6.2.5
