import dataclasses


@dataclasses.dataclass
class Meta:
    dhl_request_count: int = 0
    google_request_count: int = 0


META = Meta()
