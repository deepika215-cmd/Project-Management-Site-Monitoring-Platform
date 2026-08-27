from pydantic import BaseModel, ConfigDict


class VendorCreate(BaseModel):
    vendor_name: str
    contact_person: str | None = None
    contact_number: str | None = None
    email: str | None = None
    address: str | None = None
    category: str
    products_services: str | None = None
    status: str = "ACTIVE"


class VendorResponse(VendorCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)
