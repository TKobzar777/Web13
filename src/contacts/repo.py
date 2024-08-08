from sqlalchemy import select,  Date, func
from datetime import datetime, timedelta, date

from sqlalchemy.sql.functions import now

from src.contacts.models import Contact
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from src.contacts.models import Contact
from src.contacts.schemas import ContactsCreate, ContactsUpdate


class ContactRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_contact(self, contact_create: ContactsCreate, owner_id: int) -> Contact:
        new_contact = Contact(
            **contact_create.model_dump(),
            owner_id=owner_id
        )
        self.session.add(new_contact)
        await self.session.commit()
        await self.session.refresh(new_contact)
        return new_contact

    async def get_contact(self, contact_id: int, owner_id: int) -> Contact:
        query = select(Contact).where(Contact.id == contact_id, Contact.owner_id == owner_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_contacts(self, owner_id: int, skip: int = 0, limit: int = 10) -> list[Contact]:
        query = select(Contact).where(Contact.owner_id == owner_id).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()



    async def update_contact(self, contact_id: int, contact_update: ContactsUpdate, owner_id: int) -> Contact:
        contact = await self.get_contact(contact_id, owner_id)
        if contact:
            for key, value in contact_update.model_dump().items():
                setattr(contact, key, value)
            await self.session.commit()
            await self.session.refresh(contact)
        return contact

    async def delete_contact(self, contact_id: int, owner_id: int):
        contact = await self.get_contact(contact_id, owner_id)
        if contact:
            await self.session.delete(contact)
            await self.session.commit()


    async def search_contacts_birthdays(self, owner_id: int, days: int = 7):
        today = date.today()
        query = select(Contact).where(
            (Contact.owner_id == owner_id) &
            (func.date_part('doy', Contact.birthday).between(
            func.date_part('doy', func.now()),
            func.date_part('doy', func.now()) + days
            )
            )
        )

        # Выполнение запроса
        results = await self.session.execute(query)
        return results.scalars().all()

    # get_contacts_by_id
    async def get_contact_admin(self, contact_id: int) -> Contact:
        query = select(Contact).where(Contact.id == contact_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    # get_contacts_admin
    async def get_contacts_admin(self, skip: int = 0, limit: int = 10) -> list[Contact]:
        query = select(Contact).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()



    async def search_contacts_birthdays_admin(self, days: int = 7):
        today = date.today()
        query = select(Contact).filter(
            func.date_part('doy', Contact.birthday).between(
                func.date_part('doy', today) - 1,
                func.date_part('doy', today) + days
            )
        )
        # Выполнение запроса
        results = await self.session.execute(query)
        return results.scalars().all()

#

