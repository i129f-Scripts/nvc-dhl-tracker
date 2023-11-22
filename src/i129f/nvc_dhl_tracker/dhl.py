import asyncio
import logging
import urllib.parse
from typing import Iterable

import httpx

from i129f.nvc_dhl_tracker.meta import META

log = logging.getLogger(__name__)

host = "api-eu.dhl.com"
path = "/track/shipments"

headers = {
    "Accept": "application/json",
    "DHL-API-Key": "GeaWTrJf08irgRInANiTuvhz3NYNHG9R",
}


async def query_dhl_number(client: httpx.AsyncClient, dhl_number: str) -> dict:
    query = urllib.parse.urlencode(
        {
            "trackingNumber": dhl_number,
        }
    )
    url = urllib.parse.urlunsplit(("https", host, path, "", ""))

    log.info("Querying DHL for %s", dhl_number)
    try:
        r = await client.get(url, headers=headers, params=query)
        META.dhl_request_count += 1

        log.info("DHL returned a HTTP-%s for %s", r.status_code, dhl_number)
    except Exception as e:
        log.exception(
            "Failed to query DHL for %s because of %s(%s)", dhl_number, type(e), str(e)
        )
    else:
        return r


async def query_dhl_numbers(
    dhl_numbers: Iterable[str], client: httpx.AsyncClient, delay: float = 0.0
):
    for dhl_number in dhl_numbers:
        tracking_information = await query_dhl_number(client, dhl_number)
        if tracking_information:
            yield dhl_number, tracking_information
        else:
            log.info("Skipping %s", dhl_number)

        if delay > 0:
            log.info("Sleeping for %s", delay)
            await asyncio.sleep(delay)


def divine_statuses(events):
    for event in reversed(events):
        pre_transit_found = False
        transit_found = False
        if "Shipment picked up" in event["description"] and not pre_transit_found:
            pre_transit_found = True
            yield "pre-transit", event["timestamp"]
        elif "Shipment has departed" in event["description"] and not transit_found:
            transit_found = True
            yield "transit", event["timestamp"]
        elif "Delivered" in event["description"]:
            yield "delivered", event["timestamp"]
            break


def retrieve_status(dhl_number, as_json):
    try:
        for shipment in as_json["shipments"]:
            for piece in shipment["details"]["pieceIds"]:
                status = shipment["status"]
                yield piece, {
                    "status": status["statusCode"],
                    "location": status["location"]["address"]["addressLocality"],
                    "origin": shipment["origin"]["address"]["addressLocality"],
                    "destination": shipment["destination"]["address"][
                        "addressLocality"
                    ],
                    "history": [
                        {
                            "timestamp": event["timestamp"],
                            "location": event["location"]["address"]["addressLocality"],
                        }
                        for event in shipment["events"]
                    ],
                    "statuses": dict(divine_statuses(shipment["events"])),
                }
    except KeyError:
        log.info("%s was not found in the DHL API", dhl_number)
        yield dhl_number, {
            "status": "not_found",
            "location": "UNKNOWN",
        }


def convert_to_json(dhl_number, response):
    try:
        as_json = response.json()
        return retrieve_status(dhl_number, as_json)
    except Exception:
        log.exception(
            "Unexpected exception while converting to Json. %s -> %s.",
            response.request.url,
            response.status_code,
        )


async def query_and_parse_responses(dhl_numbers: Iterable[str], delay: float):
    async with httpx.AsyncClient() as client:
        responses = [
            response async for response in query_dhl_numbers(dhl_numbers, client, delay)
        ]
        return (convert_to_json(*response) for response in responses)
