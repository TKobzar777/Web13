from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr


class ContactsBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    birthday: date
    additional_info: Optional[str] = None


class ContactsCreate(ContactsBase):
    pass


class ContactsUpdate(ContactsBase):
    pass


class ContactsResponse(ContactsBase):
    id: int

    class Config:
        from_attributes = True