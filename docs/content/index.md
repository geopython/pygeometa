## pygeometa

[![Join the chat at https://gitter.im/geopython/pygeometa](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/geopython/pygeometa) 

<h2>Metadata Creation for the Rest of Us</h2>

pygeometa provides a lightweight and Pythonic approach for users to easily
create geospatial metadata in standards-based formats using simple
configuration files (affectionately called metadata control files [MCF]).
Leveraging the simple but powerful YAML format, pygeometa can generate metadata
in numerous standards. Users can also create their own custom metadata formats
which can be plugged into pygeometa for custom metadata format output.

For developers, pygeometa provides a Pythonic API that allows developers to
tightly couple metadata generation within their systems and integrate nicely
into metadata production pipelines.

The project supports various metadata formats out of the box including ISO
19115, the WMO Core Metadata Profile, and the WIGOS Metadata Standard. Can't
find the format you're looking for?  Element(s) missing from a given format?
Feel free to open an [issue](https://github.com/geopython/pygeometa/issues)!

pygeometa has minimal dependencies (install is less than 50K), and provides
a flexible extension mechanism leveraging the Jinja2 templating system.

pygeoapi is [open source](https://opensource.org) and released under an
[MIT license](https://github.com/geopython/pygeoapi/blob/master/LICENSE.md).

## Features
* simple YAML-based configuration
* extensible: template architecture allows for easy addition of new metadata
  formats
* flexible: use as a command-line tool or integrate as a library

## History

Started in 2009, pygeometa originated within an internal project called pygdm,
which provided generic geospatial data management functions.  pygdm (now end
of life) was used for generating MSC/CMC geospatial metadata.  pygeometa was
pulled out of pygdm to focus on the core requirement of generating geospatial
metadata within a real-time environment and automated workflows.

In 2015 pygeometa was made publically available in support of the Treasury
Board [Policy on Acceptable Network and Device Use](http://www.tbs-sct.gc.ca/pol/doc-eng.aspx?id=27122).
