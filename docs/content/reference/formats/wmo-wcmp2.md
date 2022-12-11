# WMO Core Metadata Profile 2 Schema Reference

This documentation focuses on the draft [WMO Core Metadata Profile](https://github.com/wmo-im/wcmp2) based schema
enhancements in pygeometa.

## Sections

### `identification`

Property Name|Mandatory/Optional|Description|Example|Reference
-------------|------------------|-----------|-------|---------:
wmo_data_policy|Mandatory|WMO data policy as per Resolution 1 (Cg-Ext(2021) (`core` or `recommended`)|`core`|WMO Core Metadata Profile 2, clause 7

### `distribution`

Property Name|Mandatory/Optional|Description|Example|Reference
-------------|------------------|-----------|-------|---------:
wmo_topic|Optional|WMO topic hierarchy for MQTT links|`mwi.mwi_met_centre.data.core.weather.surface-based-observations.synop`|WMO Core Metadata Profile 2, clause 7


## Validation

WMO Core Metadata Profile output can be validated using the [pywcmp](https://github.com/wmo-im/pywcmp) tool.
