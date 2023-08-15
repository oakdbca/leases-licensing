"""

The ABS API is quite complicated to use

The api path we are using from the settings file is something like this:

https://api.data.abs.gov.au/data/CPI/3.10001.10.5.Q

In this case, the api end point takes 5 parameters, seperated by a dot. i.e. 3.10001.10.5.Q

Description of the parameters:

CL_CPI_MEASURES   3       (Percentage change from last year)
CL_CPI_INDEX_17   10001   (All Groups CPI - for all categories, nothing excluded)
CL_TSEST          1       (Original - Not seasionally adjusted etc.)
CL_CPI_REGION     5      (Perth)
CL_FREQ           Q       (Quarterly)

"""

import logging
import xml.etree.ElementTree as ET

import requests
from django.core.management.base import BaseCommand

from leaseslicensing.components.invoicing.models import ConsumerPriceIndex
from leaseslicensing.settings import (
    ABS_API_CPI_PATH,
    ABS_API_CPI_SUBDIRECTORY,
    ABS_API_URL,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "This script will fetch the latest cpi data from the ABS api."

    def handle(self, *args, **options):
        url = f"{ABS_API_URL}{ABS_API_CPI_SUBDIRECTORY}{ABS_API_CPI_PATH}"
        logger.info(f"Querying {url} for CPI Data")
        cpi_data = requests.get(url)
        logger.info(f"Request took: {cpi_data.elapsed.total_seconds()} seconds.")
        root = ET.fromstring(cpi_data.content)
        for node in root[1][0]:
            if node[0].attrib["id"] != "TIME_PERIOD":
                continue

            time_period = node[0].attrib["value"]
            year = time_period.split("-")[0]
            quarter = time_period.split("-")[1].replace("Q", "")
            value = node[1].attrib["value"]
            cpi, created = ConsumerPriceIndex.objects.get_or_create(
                year=year, quarter=quarter, value=value
            )
            if created:
                logger.info(
                    f"Created New CPI Data Record - Time Period: {time_period}, Value: {value}"
                )
