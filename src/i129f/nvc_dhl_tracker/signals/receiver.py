import asyncio
import logging

from django.dispatch import receiver

from i129f.nvc_dhl_tracker.dhl import parse_json
from i129f.nvc_dhl_tracker.models import (
    DhlApiKey,
    DhlKeyUsage,
    DhlPackage,
    GoogleKeyUsage,
)
from i129f.nvc_dhl_tracker.signals.sender import (
    google_request_made,
    post_dhl_request_made,
    pre_dhl_request_made,
)


@receiver(google_request_made, sender=GoogleKeyUsage)
def record_google_api_request(**kwargs):
    asyncio.create_task(GoogleKeyUsage.objects.acreate())


@receiver(pre_dhl_request_made, sender=DhlApiKey)
def record_dhl_api_request(instance, **kwargs):
    asyncio.create_task(DhlKeyUsage.objects.acreate(key=instance))


@receiver(post_dhl_request_made, sender=DhlApiKey)
def record_dhl_package(instance, response, json, **kwargs):
    if json and response.is_success:
        try:
            data = list(parse_json(json))
        except Exception as e:
            logging.exception("Could not parse %s because %s(%s)", json, type(e), e)
            return

        for number, package_data in data:
            asyncio.create_task(
                DhlPackage.objects.aupdate_or_create(
                    number=number,
                    defaults=dict(
                        origin=package_data["origin"],
                        location=package_data["location"],
                        current_status=package_data["status"],
                        **package_data["statuses"]
                    ),
                ),
                name="Save DHL Package Data",
            )
    else:
        if response.status_code in {401, 403}:
            instance.exhausted = True
            instance.save()
            logging.error("Permission denied, exhausting API key!")
