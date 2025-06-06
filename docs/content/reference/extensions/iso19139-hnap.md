# HNAP Schema Reference

This document describes HNAP schema extensions in pygeometa.

### `identification.keywords`

HNAP support includes the following `keywords` sections.

* `gc_cst`: Government of Canada Core Subject Thesaurus
* `hnap_category_information`: HNAP
* `hnap_category_geography`: HNAP
* `hnap_category_content`: HNAP

Keyword requirements are the same as pygeometa's default keyword rules.

## `distribution`

Distribution identifier:

* To comply with HNAP, distribution methods require its sections to be duplicated and appended with `_eng-CAN` and `_fra-CAN` to distribution names

Distribution parameters:

* Name of the distribution method needs to be specified with name: en and name: fr
* Do not provide values for the 'description' parameter in the MCF file since HNAP requires a special description that is built by pygeometa
* Content type needs to be bilingual and be a valid HNAP value
 * Valid values are: Web Service,Service Web,Dataset,Données,API,Application,Supporting Document,Document de soutien 
* Format needs to be bilingual and based on the valid HNAP values
 * Valid values are: AI. AMF,Application,ASCII Grid,BMP,CDED ASCII,CDR,CSV,DOC,dxf,E00,ECW,EDI,EMF,EPS,ESRI REST,EXE,FGDB / GDB,Flat raster binary,GeoPDF,GeoRSS,GeoTIF,GIF,GML,HDF,HTML,IATI,JPEG 2000,JPG,JSON,JSON Lines,KML / KMZ,NetCDF,ODP,ODS,ODT,PDF,PNG,PPT,RDF,RDFa,RSS,SAR / CCT,SAV,SEGY,SHP,SQL,SVG,TIFF,TXT,XLS,XLSM,XML,WFS,WMS,WMTS,Zip,Other
* Format version needs to be specified with `format_version:`

## Example of distribution section

Example of valid HNAP distribution sections:

```yaml
distribution:
    waf_fra-CAN:
        url: https://dd.weather.gc.ca/model_gem_global/25km/grib2/lat_lon/
        type: WWW:LINK
        name:
            en: MSC Datamart
            fr: Datamart du SMC
        hnap_contenttype:
            en: Dataset
            fr: Données
        format:
            en: Other
            fr: Autre
        format_version: '0'
        function: download
        
    waf_eng-CAN:
        url: https://dd.weather.gc.ca/model_gem_global/25km/grib2/lat_lon/
        type: WWW:LINK
        name:
            en: MSC Datamart
            fr: Datamart du SMC
        hnap_contenttype:
            en: Dataset
            fr: Données
        format:
            en: Other
            fr: Autre
        format_version: '0'
        function: download
        
    wms_eng-CAN:
        url: https://geo.weather.gc.ca/geomet/?lang=E&service=WMS&request=GetCapabilities&layers=GDPS.ETA_TT
        hnap_contenttype:
            en: Web Service
            fr: Service Web
        type: OGC:WMS
        format: WMS
        format_version: '1.1.1'
        name:
            en: GDPS.ETA_TT
            fr: GDPS.ETA_TT
        function: download
        
    wms_fra-CAN:
        url: https://geo.weather.gc.ca/geomet/?lang=E&service=WMS&request=GetCapabilities&layers=GDPS.ETA_TT
        hnap_contenttype:
            en: Web Service
            fr: Service Web
        type: OGC:WMS
        format: WMS
        format_version: '1.1.1'
        name:
            en: GDPS.ETA_TT
            fr: GDPS.ETA_TT
        function: download
```
