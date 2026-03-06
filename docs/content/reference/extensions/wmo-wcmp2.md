# WMO Core Metadata Profile 2 (WCMP2) Schema Reference

This document describes [WMO Core Metadata Profile (WCMP2)](https://wmo-im.github.io/wcmp2/standard/wcmp2-STABLE.html) schema
extensions in pygeometa.

## Sections

### `identification`

Property Name|Mandatory/Optional|Description|Example|Reference
-------------|------------------|-----------|-------|---------:
wmo_data_policy|Mandatory|WMO data policy as per Resolution 1 (Cg-Ext(2021) (`core` or `recommended`)|`core`|WMO Core Metadata Profile 2, clause 7

### `identification.keywords`

pygeometa WCMP2 support includes the following `keywords` sections.

* `earth-system-discipline`: [Earth system categories](https://codes.wmo.int/wis/topic-hierarchy/earth-system-discipline) as defined by the [WMO Unified Data Policy, Resolution 1 (Cg-Ext(2021), Annex 1](https://library.wmo.int/records/item/58009-wmo-unified-data-policy).

Ensure that `vocabulary.url` is set to https://codes.wmo.int/wis/topic-hierarchy/earth-system-discipline

## Validation

WMO Core Metadata Profile output can be validated using the [pywcmp](https://github.com/wmo-im/pywcmp) tool.
