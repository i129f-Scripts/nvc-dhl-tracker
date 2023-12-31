from typing import Iterable

import gspread
from gspread import NoValidUrlKeyFound

from i129f.nvc_dhl_tracker.models import DhlPackage, GoogleKeyUsage
from i129f.nvc_dhl_tracker.signals.sender import google_request_made


def update_google_sheet(sheet_key, sheet, dhl_packages: Iterable[DhlPackage]):
    gc = gspread.service_account()
    try:
        sh = gc.open_by_url(sheet_key)
    except NoValidUrlKeyFound as e:
        raise ValueError(
            f"GSpread could not open the google spreadsheet. "
            f"Is `{sheet_key}` a URL of a valid Google spreadsheet?"
        ) from e
    table = {
        "headers": [
            "Tracking Number",
            "Discovered",
            "Location",
            "Status",
            "Status - Pre Transit",
            "Status - Transit",
            "Status - Delivered",
            "Total Time in Transit (seconds)",
        ],
    }

    for package in dhl_packages:
        table[package.number] = [
            package.number,
            package.created.isoformat(),
            package.location,
            package.current_status,
            package.became_pre_transit.isoformat(),
            package.became_transit.isoformat(),
            package.became_delivered.isoformat(),
            (package.became_delivered - package.became_pre_transit).total_seconds(),
        ]

    sh.get_worksheet_by_id(sheet).update(range_name="A1", values=list(table.values()))
    google_request_made.send(sender=GoogleKeyUsage)
