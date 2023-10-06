# WMO Core Metadata Profile 2 (WCMP2) Schema Reference

This documentation focuses on the draft [WMO Core Metadata Profile](https://github.com/wmo-im/wcmp2) based schema
enhancements in pygeometa.

## Sections

### `identification`

Property Name|Mandatory/Optional|Description|Example|Reference
-------------|------------------|-----------|-------|---------:
wmo_data_policy|Mandatory|WMO data policy as per Resolution 1 (Cg-Ext(2021) (`core` or `recommended`)|`core`|WMO Core Metadata Profile 2, clause 7

### `identification.keywords`

pygeometa WCMP2 support includes the following `keywords` sections.

* `earth-system-discipline`: [Earth system categories](https://github.com/wmo-im/wis2-topic-hierarchy/blob/main/topic-hierarchy/earth-system-discipline.csv) as defined by the [WMO Unified Data Policy, Resolution 1 (Cg-Ext(2021), Annex 1](https://library.wmo.int/records/item/58009-wmo-unified-data-policy).

Ensure that `vocabulary.url` is set to https://github.com/wmo-im/wis2-topic-hierarchy/blob/main/topic-hierarchy/earth-system-discipline.csv).

## Validation

WMO Core Metadata Profile output can be validated using the [pywcmp](https://github.com/wmo-im/pywcmp) tool.
