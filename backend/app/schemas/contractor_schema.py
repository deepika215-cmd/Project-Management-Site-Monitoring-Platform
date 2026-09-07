from pydantic import BaseModel, ConfigDict


class ContractorCreate(BaseModel):
    name: str
    company_name: str | None = None
    phone: str | None = None
    email: str | None = None
    status: str = "Active"


class ContractorResponse(ContractorCreate):
    id: int

    model_config = ConfigDict(
        from_attributes=True
    )