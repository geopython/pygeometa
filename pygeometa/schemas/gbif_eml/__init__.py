import re
from pathlib import Path

import pycountry
from bs4 import BeautifulSoup
from pygeometa.schemas.base import BaseOutputSchema

THISDIR = Path(__file__).parent


def text_or_null(node, strip=False):
    if not node:
        return None

    if strip:
        return node.text.strip()

    return node.text


def text_or_empty(node, strip=False):
    if not node:
        return ""

    if strip:
        return node.text.strip()

    return node.text


def scrub_dict(d):
    if type(d) is dict:
        return dict(
            (k, scrub_dict(v))
            for k, v in d.items()
            if v is not None and scrub_dict(v) is not None
        )
    else:
        return d


def to_contact_role(node, role, mapped_role=None):
    if not mapped_role:
        mapped_role = role

    for idx, contact in enumerate(node.find_all(role)):
        name = f'{text_or_empty(contact.find("surName"))}, '
        name += text_or_empty(contact.find("givenName"))
        org = text_or_empty(contact.find("organizationName"))
        yield (
            mapped_role + (f"_{idx}" if idx else ""),
            {
                "organization": org,
                "individualname": name,
                "positionname": text_or_empty(contact.find("positionName"))
                or text_or_empty(contact.find("role")),
                "phone": "",
                "url": "",
                "fax": "",
                "address": "",
                "city": "",
                "administrativearea": "",
                "postalcode": "",
                "country": text_or_empty(contact.find("country")),
                "email": text_or_empty(contact.find("electronicMailAddress")),
            },
        )


class GBIF_EMLOutputSchema(BaseOutputSchema):
    def __init__(self):
        super().__init__("gbif-eml", "EML - GBIF profile", "xml", THISDIR)

    def import_(self, metadata):
        soup = BeautifulSoup(metadata, features="lxml-xml")
        dataset = soup.find("dataset")
        mcf = {
            "mcf": {
                "version": 1,
            },
            "metadata": {
                "charset": "utf8",
                "hierarchylevel": "dataset",
                "datestamp": "$datetime$",
            },
            "identification": {},
            "contact": {},
            "distribution": {},
        }

        for identifier in dataset.find_all("alternateIdentifier"):
            mcf["metadata"]["identifier"] = text_or_null(identifier)

        if language := dataset.find("language"):
            lang = text_or_null(language)
            if lang and pycountry.languages.get(alpha_3=lang):
                mcf["metadata"]["language"] = pycountry.languages.get(
                    alpha_3=lang
                ).alpha_2

        idf = mcf["identification"]

        idf["title"] = text_or_null(dataset.find("title"))
        idf["abstract"] = text_or_null(dataset.find("abstract"))

        if intellectual_rights := dataset.find("intellectualRights"):
            url = (
                intellectual_rights.find("ulink")["url"]
                if intellectual_rights.find("ulink")
                else None
            )
            idf["rights"] = {
                "name": text_or_null(intellectual_rights.find("citetitle")),
                "url": url,
            }

        idf["url"] = text_or_null(dataset.find("alternateIdentifier"))
        idf["status"] = "completed"

        # if maintenance := dataset.find("maintenance"):
        #     metadata.maintenance_update_description = text_or_null(
        #         maintenance.find("description")
        #     )

        idf["maintenancefrequency"] = (
            text_or_null(dataset.find("maintenanceUpdateFrequency"))
            or "unknown"
        )

        idf["dates"] = {"publication": text_or_null(dataset.find("pubDate"))}
        idf["extents"] = {}

        if coords := dataset.find("boundingCoordinates"):
            idf["extents"]["spatial"] = [{}]
            spatial = idf["extents"]["spatial"][0]

            spatial["bbox"] = [
                float(coords.find("westBoundingCoordinate").text),
                float(coords.find("southBoundingCoordinate").text),
                float(coords.find("eastBoundingCoordinate").text),
                float(coords.find("northBoundingCoordinate").text),
            ]

            spatial["crs"] = 4326
            spatial["description"] = text_or_null(
                dataset.find("geographicDescription")
            )

        # temporal = idf["extents"]["temporal"]
        # temporal["begin"]
        # temporal["end"]
        # temporal["resolution"]

        idf["keywords"] = {}

        ct = mcf["contact"]

        for r, obj in to_contact_role(dataset, "contact", "pointOfContact"):
            ct[r] = obj

        for r, obj in to_contact_role(
            dataset, "metadataProvider", "distributor"
        ):
            ct[r] = obj

        for r, obj in to_contact_role(dataset, "creator"):
            ct[r] = obj

        for r, obj in to_contact_role(
            dataset, "personnel", "projectPersonnel"
        ):
            ct[r] = obj

        for idx, keyword_set in enumerate(dataset.find_all("keywordSet")):
            thesaurus = text_or_null(keyword_set.find("keywordThesaurus"))
            match = re.search(r"(?P<url>https?://[^\s]+)", thesaurus)
            definition = match.group("url") if match else None

            idf["keywords"][f"default-{idx}"] = {
                "keywords": [
                    text_or_null(kw) for kw in keyword_set.find_all("keyword")
                ],
                "vocabulary": {"name": thesaurus, "url": definition},
            }

        mcf["spatial"] = {"datatype": "vector", "geomtype": "composite"}

        mcf["distribution"] = {
            "file": {
                "url": idf["url"],
                "type": "WWW:LINK",
                "function": "information",
                "description": "",
                "name": "Darwin Core Archive",
            }
        }

        return scrub_dict(mcf)
