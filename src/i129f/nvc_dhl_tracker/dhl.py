import asyncio
import logging
import urllib.parse
from json import JSONDecodeError
from typing import Iterable

import httpx

from i129f.nvc_dhl_tracker.models import DhlApiKey
from i129f.nvc_dhl_tracker.signals.sender import (
    post_dhl_request_made,
    pre_dhl_request_made,
)

log = logging.getLogger(__name__)

host = "api-eu.dhl.com"
path = "/track/shipments"


async def query_dhl_number(
    client: httpx.AsyncClient, dhl_number: str, instance: DhlApiKey
) -> httpx.Response:
    query = urllib.parse.urlencode(
        {
            "trackingNumber": dhl_number,
        }
    )
    headers = {
        "Accept": "application/json",
        "DHL-API-Key": instance.key,
    }
    url = urllib.parse.urlunsplit(("https", host, path, "", ""))

    log.info("Querying DHL for %s at %s", dhl_number, url)
    try:
        await instance.can_make_request()
        pre_dhl_request_made.send_robust(DhlApiKey, instance=instance)
        r = await client.get(url, headers=headers, params=query)
        try:
            json = r.json()
        except JSONDecodeError:
            json = {}

        post_dhl_request_made.send_robust(
            DhlApiKey, instance=instance, response=r, json=json
        )

        log.info("DHL returned a HTTP-%s for %s", r.status_code, dhl_number)
    except Exception as e:
        log.exception(
            "Failed to query DHL at %s for %s because of %s(%s)",
            url,
            dhl_number,
            type(e),
            str(e),
        )
    else:
        return r


async def query_dhl_numbers(
    dhl_numbers: Iterable[str],
    client: httpx.AsyncClient,
    instance: DhlApiKey,
    delay: float = 0.0,
):
    for dhl_number in dhl_numbers:
        tracking_information = await query_dhl_number(client, dhl_number, instance)
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
            yield "became_pre_transit", event["timestamp"]
        elif "Shipment has departed" in event["description"] and not transit_found:
            transit_found = True
            yield "became_transit", event["timestamp"]
        elif "Delivered" in event["description"]:
            yield "became_delivered", event["timestamp"]
            break


def retrieve_status(dhl_number, as_json):
    try:
        yield from parse_json(as_json)
    except KeyError:
        log.info("%s was not found in the DHL API", dhl_number)
        yield dhl_number, {
            "status": "not_found",
            "location": "UNKNOWN",
        }


def parse_json(as_json):
    for shipment in as_json["shipments"]:
        for piece in shipment["details"]["pieceIds"]:
            status = shipment["status"]
            yield piece, {
                "status": status["statusCode"],
                "location": status["location"]["address"]["addressLocality"],
                "origin": shipment["origin"]["address"]["addressLocality"],
                "destination": shipment["destination"]["address"]["addressLocality"],
                "history": [
                    {
                        "timestamp": event["timestamp"],
                        "location": event["location"]["address"]["addressLocality"],
                    }
                    for event in shipment["events"]
                ],
                "statuses": dict(divine_statuses(shipment["events"])),
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


async def query_and_parse_responses(
    dhl_numbers: Iterable[str], delay: float, instance: DhlApiKey
):
    async with httpx.AsyncClient() as client:
        responses = [
            response
            async for response in query_dhl_numbers(
                dhl_numbers, client, instance, delay
            )
        ]
        return (convert_to_json(*response) for response in responses)
