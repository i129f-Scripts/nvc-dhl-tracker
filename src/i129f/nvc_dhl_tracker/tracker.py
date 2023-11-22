import itertools

from .dhl import query_and_parse_responses
from .google import update_google_sheet


async def track(google_sheet_url, tracking_sheet_id, meta_sheet_id):
    jsons = await query_and_parse_responses(
        dhl_numbers=(f"JD0030110676223{n:03d}" for n in range(10)),
        delay=1.0,
    )
    update_google_sheet(
        google_sheet_url,
        tracking_sheet_id,
        meta_sheet_id,
        itertools.chain(*jsons),
    )
