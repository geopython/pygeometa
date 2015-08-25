# HNAP Schema Reference

This documentation focuses on unique HNAP schema specifities in pygeometa.

## Distribution section

Distribution identifier:
* To comply with HNAP, distribution methods require its sections to be duplicated and appended _eng-CAN and _fra-CAN to distribution names

Distribution parameters:
* Name of the distribution method needs to be specified with name_en= and name=Fr
* Do not provide values for the 'description' parameter in the MCF file since HNAP requires a special description that is built by pygeometa
* Content type needs to be specified with hnap_contenttype_en= and hnap_contenttype_fr= and be a valid HNAP value
 * Valid values are: Web Service,Service Web,Dataset,Données,API,Application,Supporting Document,Document de soutien 
* Format needs to be specified with format_en= and format_fr=, based on the valid HNAP values
 * Valid values are: AI. AMF,Application,ASCII Grid,BMP,CDED ASCII,CDR,CSV,DOC,dxf,E00,ECW,EDI,EMF,EPS,ESRI REST,EXE,FGDB / GDB,Flat raster binary,GeoPDF,GeoRSS,GeoTIF,GIF,GML,HDF,HTML,IATI,JPEG 2000,JPG,JSON,JSON Lines,KML / KMZ,NetCDF,ODP,ODS,ODT,PDF,PNG,PPT,RDF,RDFa,RSS,SAR / CCT,SAV,SEGY,SHP,SQL,SVG,TIFF,TXT,XLS,XLSM,XML,WFS,WMS,WMTS,Zip,Other
* Format version needs to be specified with format_version=

## Example of distribution section

Example of valid HNAP distribution sections:

```
[distribution:waf_fra-CAN]
url=http://dd.weather.gc.ca/model_gem_global/25km/grib2/lat_lon/
type=WWW:LINK
name_en=MSC Datamart
name_fr=Datamart du SMC
hnap_contenttype_en=Dataset
hnap_contenttype_fr=Données
format_en=Other
format_fr=Autre
format_version=0
function=download

[distribution:waf_eng-CAN]
url=http://dd.weather.gc.ca/model_gem_global/25km/grib2/lat_lon/
type=WWW:LINK
name_en=MSC Datamart
name_fr=Datamart du SMC
hnap_contenttype_en=Dataset
hnap_contenttype_fr=Données
format_en=Other
format_fr=Autre
format_version=0
function=download

[distribution:wms_eng-CAN]
url=http://geo.weather.gc.ca/geomet/?lang=E&service=WMS&request=GetCapabilities&layers=GDPS.ETA_TT
hnap_contenttype_en=Web Service
hnap_contenttype_fr=Service Web
type=OGC:WMS
format=WMS
format_version=1.1.1
name_en=GDPS.ETA_TT
name_fr=GDPS.ETA_TT
function=download

[distribution:wms_fra-CAN]
url=http://geo.weather.gc.ca/geomet/?lang=E&service=WMS&request=GetCapabilities&layers=GDPS.ETA_TT
hnap_contenttype_en=Web Service
hnap_contenttype_fr=Service Web
type=OGC:WMS
format=WMS
format_version=1.1.1
name_en=GDPS.ETA_TT
name_fr=GDPS.ETA_TT
function=download

```
