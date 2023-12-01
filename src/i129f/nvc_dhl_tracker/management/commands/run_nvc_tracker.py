import asyncio
import datetime as dt
import random

import httpx
from channels.db import database_sync_to_async
from django.core.management.base import BaseCommand
from django.db.models import Q

from i129f.nvc_dhl_tracker.dhl import query_dhl_number
from i129f.nvc_dhl_tracker.google import update_google_sheet
from i129f.nvc_dhl_tracker.models import (
    DhlApiKey,
    DhlKeyUsage,
    DhlPackage,
    GoogleKeyUsage,
)


def positive(answer: str):
    return answer.casefold() in {
        "y",
        "yes",
        "yeah",
        "yup",
        "1",
        "si",
    }


class Command(BaseCommand):
    help = "Runs the NVC tracker"

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-input",
            action="store_true",
            help="Don't ask for input",
        )
        parser.add_argument(
            "--dhl-keys",
            nargs="+",
            type=str,
            help="The DHL API keys to add to the project",
        )
        parser.add_argument(
            "--clear-keys",
            action="store_true",
            help="Delete all DHL API keys",
        )
        parser.add_argument(
            "--start-number",
            nargs="1",
            type=str,
            help="The DHL package number to start with",
        )
        parser.add_argument(
            "--google-spreadsheet-url",
            nargs="1",
            type=str,
            help="The Google spreadsheet URL",
        )
        parser.add_argument(
            "--google-sheet-id",
            nargs="1",
            type=str,
            help="The ID of the page of the spreadsheet",
        )

    def handle(self, *args, **options):
        dhl_keys = DhlApiKey.objects.all()
        allow_input = not options["no-input"]

        if (
            options["clear_keys"]
            or allow_input
            and positive(
                input(
                    f"You have {dhl_keys.count()} DHL "
                    f"keys setup, do you want to remove them? "
                )
            )
        ):
            dhl_keys.delete()

        while allow_input and (
            key := input(
                "If you want to add new DHL API keys enter "
                "them now, leave blank when finished: "
            )
        ):
            DhlApiKey.objects.get_or_create(key=key)

        for key in options["dhl-keys"]:
            DhlApiKey.objects.get_or_create(key=key)

        if starting_number := options["start-number"]:
            ...
        if not DhlPackage.objects.last() and allow_input:
            starting_number = input(
                "What DHL package number should we start tracking at? "
            )
        elif not starting_number:
            self.stdout.write(f"Starting at {DhlPackage.objects.last().number}")
            starting_number = DhlPackage.objects.last().number

        google_spreadsheet = options["google-spreadsheet-url"] or (
            allow_input and input("What is the google spreadsheet URL? ")
        )
        google_sheet = options["google-sheet-id"] or (
            allow_input and input("What is the google sheet id? ")
        )
        keys = get_dhl_key()
        next_number = starting_number
        asyncio.run(
            run(
                async_query(keys, next_number, 1.0, self.stdout.write),
                update_google(google_spreadsheet, google_sheet),
                clean_db_of_packages(),
            )
        )


async def run(*coros):
    await asyncio.gather(*coros)


@database_sync_to_async
def get_dhl_key():
    if not hasattr(get_dhl_key, "last_reset"):
        get_dhl_key.last_reset = dt.datetime.now()

    if (dt.datetime.now() - get_dhl_key.last_reset).total_seconds() > 60 * 60 * 24:
        # Un-exhaust keys after a day
        DhlApiKey.objects.filter(
            exhausted=True, udpated__gt=dt.datetime.now() - dt.timedelta(days=1)
        ).update(exhausted=False)

    keys = DhlApiKey.objects.filter(Q(exhausted=False))
    return random.choice(keys)


async def clean_db_of_packages():
    while True:
        await DhlPackage.objects.filter(
            updated__lt=dt.datetime.now() - dt.timedelta(days=31)
        ).adelete()
        await DhlKeyUsage.objects.filter(
            updated__lt=dt.datetime.now() - dt.timedelta(days=2)
        ).adelete()
        await GoogleKeyUsage.objects.filter(
            updated__lt=dt.datetime.now() - dt.timedelta(days=2)
        ).adelete()
        await asyncio.sleep(60 * 60 * 12)


@database_sync_to_async
def get_tracked_numbers():
    return (
        DhlPackage.objects.filter(
            ~Q(current_status="delivered")
            & ~Q(
                current_status="not_found",
                created__lt=dt.datetime.now() - dt.timedelta(days=10),
            )
            & ~Q(updated__gt=dt.datetime.now() - dt.timedelta(hours=12)),
        )
        .values_list(
            "number",
            flat=True,
        )
        .order_by("-created")
        .first()
    )


async def async_query(keys, next_number, delay, log):
    while True:
        async with httpx.AsyncClient() as client:
            key = await get_dhl_key()
            await query_dhl_number(client, next_number, key)
            await asyncio.sleep(delay)
            if already_being_tracked := await get_tracked_numbers():
                next_number = already_being_tracked
                log(f"Querying tracked number: {next_number}")
            else:
                # Divine the next number
                next_number = next_number[:2] + str(int(next_number[2:]) + 1).rjust(
                    len(next_number[2:]), "0"
                )
                log(f"Querying new number: {next_number}")


async def update_google(spreadsheet_id, sheet_id):
    while True:
        query = DhlPackage.objects.filter(
            updated__gt=dt.datetime.now() - dt.timedelta(days=30),
        ).order_by("number")
        data = await database_sync_to_async(list)(query)
        update_google_sheet(spreadsheet_id, sheet_id, data)
        # await asyncio.sleep(60 * 60 * 24)
        await asyncio.sleep(30)
