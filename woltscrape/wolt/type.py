from typing import List


class Coordinates:
    lat: float
    lon: float

    def __init__(self, http_response: List[dict]) -> None:
        self.lat = http_response[0]["lat"]
        self.lon = http_response[0]["lon"]

    def __repr__(self):
        return f"lat={self.lat}&lon={self.lon}"


__all__ = ["Coordinates"]
