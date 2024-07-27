from datetime import date

from pydantic import BaseModel, EmailStr


class ContactsBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    birthday: date
    additional_info: str | None = None


class ContactsResponse(ContactsBase):
    id: int


class ContactsCreate(ContactsBase):
    pass


class ContactsUpdate(ContactsBase):
    pass
