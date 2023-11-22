import dataclasses

import gspread
from dateutil.parser import parse

from i129f.nvc_dhl_tracker.meta import META


def update_google_sheet(sheet_key, sheet, meta_sheet, data):
    gc = gspread.service_account()
    sh = gc.open_by_url(sheet_key)
    raw = sh.get_worksheet_by_id(sheet).get_all_values()
    META.google_request_count += 1
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
        **{r[0]: r for r in sorted(raw[1:], key=lambda _r: _r[0])},
    }

    for tracking_number, dat in data:
        if dat["status"] != "not_found":
            statuses = dat.get("statuses", {})
            timestamps = (
                [
                    statuses.get(key, None)
                    for key in ["pre-transit", "transit", "delivered"]
                ]
                if statuses
                else []
            )

            if (start := timestamps[0]) and (end := timestamps[-1]):
                seconds = (parse(end) - parse(start)).total_seconds
            else:
                seconds = None
            table[tracking_number] = [
                tracking_number,
                dat["history"][-1]["timestamp"],
                dat["location"],
                dat["status"],
                *timestamps,
                seconds,
            ]
        else:
            table[tracking_number] = [tracking_number, None, None, "not_found"]

    sh.get_worksheet_by_id(sheet).update(range_name="A1", values=list(table.values()))
    META.google_request_count += 1

    # Update the meta information
    META.google_request_count += 1
    sh.get_worksheet_by_id(meta_sheet).update(
        "A1", list(dataclasses.asdict(META).items())
    )
