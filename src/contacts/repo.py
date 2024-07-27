from sqlalchemy import select

from src.contacts.models import Contact
from src.contacts.schemas import ContactsCreate


class ContactsRepository:
    def __init__(self, session):
        self.session = session

    async def get_contacts(self, limit: int = 10, offset: int = 0):
        query = select(Contact).offset(offset).limit(limit)
        results = await self.session.execute(query)
        return results.scalars().all()

    async def create_contacts(self, contact: ContactsCreate):
        new_contact = Contact(**contact.model_dump())
        self.session.add(new_contact)
        await self.session.commit()
        await self.session.refresh(new_contact)  # To get the ID from the database
        return new_contact

    async def search_contacts(self, query):
        q = select(Contact).filter(
            (Contact.first_name.ilike(query))
            | (Contact.last_name.ilike(query))
            | (Contact.email.icontains(query))
        )
        results = await self.session.execute(q)
        return results.scalars().all()

    async def delete_contact(self, contact_id):
        q = select(Contact).where(Contact.id == contact_id)
        result = await self.session.execute(q)
        contact = result.scalar_one()
        await self.session.delete(contact)
        await self.session.commit()



    async def update(self, contact: ContactsCreate, contact_id: int):
        q = select(Contact).where(Contact.id == contact_id)
        result = await self.session.execute(q)
        stored_contact = result.scalar_one()
        if stored_contact:
            stored_contact.first_name = contact.first_name
            stored_contact.last_name = contact.last_name
            stored_contact.email = contact.email
            stored_contact.phone_number = contact.phone_number
            stored_contact.birthday = contact.birthday
            await self.session.commit()
            await self.session.refresh(stored_contact)

        return stored_contact

