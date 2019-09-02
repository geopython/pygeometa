# WMO Core Metadata Profile Schema Reference

This documentation focuses on the [WMO Core Metadata Profile](http://wis.wmo.int/2013/metadata/version_1-3-0/WMO_Core_Metadata_Profile_v1.3_Part_1.pdf) based schema
enhancements in pygeometa.

## Sections

### `identification`

Property Name|Mandatory/Optional|Description|Example|Reference
-------------|------------------|-----------|-------|---------:
otherconstraints_wmo_data_policy|Mandatory|WMO data policy statment from WMO_DataLicenseCode (must be one of 'WMOEssential', 'WMOAdditional' 'WMOOther')|WMOEssential|WMO Core Metadata Profile 1.3, Part 1, Section 9.3.1
otherconstraints_wmo_gts_priority|Mandatory|WMO GTS priority (must be one of 'GTSPriority1', 'GTSPriority2', 'GTSPriority3', 'GTSPriority4')|GTSPriority2|WMO Core Metadata Profile 1.3, Part 1, Section 9.3.2


### `identification.keywords`

WMO support includes a `wmo` keywords section (WMO Core Metadata Profile 1.3, Part 2, Table 16).  Keyword requirements are the same as pygeometa's default keywords rules.


## Validation

WMO Core Metadata Profile output can be validated using the [WMO Core Metadata Profile Test Suite](https://github.com/wmo-im/wmo-cmp-ts).
