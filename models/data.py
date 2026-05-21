from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class GeolocationData(BaseModel):
    country: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    coordinates: Optional[str] = None
    timezone: Optional[str] = None
    isp: Optional[str] = None

class Data(BaseModel):
    address: str
    user: str
    time: datetime
    geolocation: GeolocationData