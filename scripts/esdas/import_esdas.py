from data_platform_catalogue.client.datahub_client import DataHubCatalogueClient
import os
import pandas as pd
import numpy as np
from data_platform_catalogue.entities import (
    Database,
    DomainRef,
    OwnerRef,
    Governance,
    EntityRef,
    TagRef,
)

CATALOGUE_TOKEN="value"
CATALOGUE_URL="value"

client = DataHubCatalogueClient(jwt_token=CATALOGUE_TOKEN, api_url=CATALOGUE_URL)


esda = pd.read_csv("scripts/ESDA20240801.csv", skiprows=2)
esda = esda.replace({np.nan: ""})
esda_d = esda.to_dict()


for i in range(len(esda)):
    domain_name = esda_d["domain"][i].capitalize()

    if len(esda_d["contactPoint_email"][i]) > 1:
        pre_ampersand = esda_d["contactPoint_email"][i].split("@")[0]
        if "." in pre_ampersand:
            sp = pre_ampersand.split(".")
            first_name = sp[0]
            surname = sp[1]
            owner_urn = f"urn:li:corpuser:{first_name}.{surname}"
        else:
            owner_urn = f"urn:li:corpGroup:{pre_ampersand}"
    else:
        owner_urn = ""

    email = esda_d["contactPoint_email"][i].split(" ")[0]
    display_name = esda_d["contactPoint_email"][i].split("@")[0]
    db = Database(
        urn=None,
        display_name=esda_d["title"][i],
        name=esda_d["title"][i],
        fully_qualified_name=esda_d["alternativeTitle"][i],
        description=esda_d["description"][i],
        domain=DomainRef(display_name=domain_name,
                         urn=f"urn:li:domain:{domain_name}"),
        governance=Governance(
            data_owner=OwnerRef(
                display_name=display_name,
                email=email,
                urn=owner_urn,
            ),
            data_stewards=[],
        ),
        platform=EntityRef(display_name="esda",
                           urn="urn:li:dataPlatform:esda"),
        tags=[
            TagRef(
                urn="urn:li:tag:dc_display_in_catalogue",
                display_name="dc_display_in_catalogue",
            )
        ],
    )
    urn = client.upsert_database(db)
    print(urn)

# remember to datahub init first and check which server/token your datahub has locally
# this command is useful
# datahub exists --urn xxxx

# These commands will recreate the esdas.
# datahub delete --platform esda --hard --entity-type container
# datahub put platform --name esda --display_name "ESDA" --logo "https://example.com"
# datahub user upsert -f scripts/esdas/user.yaml
# datahub group upsert -f scripts/esdas/datafirst.yaml
# datahub group upsert -f scripts/esdas/datalinkingteam.yaml
# python scripts/esdas/import_esdas.py
