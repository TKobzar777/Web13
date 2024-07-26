from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config.db import get_db
from src.contacts.repo import ContactsRepository
from src.contacts.schemas import ContactsCreate, ContactsResponse

router = APIRouter()


@router.get("/ping")
async def ping():
    return {"message": "pong"}



@router.post("/", response_model=ContactsResponse)
async def create_contacts(contact: ContactsCreate, db: AsyncSession = Depends(get_db)):
    repo = ContactsRepository(db)
    return await repo.create_contacts(contact)


@router.delete("/{contact_id}")
async def delete_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
    repo = ContactsRepository(db)
    await repo.delete_contact(contact_id)
    return {"message": f"Contact {contact_id} deleted"}


@router.get("/", response_model=list[ContactsResponse])
async def get_contacts(
    limit: int = 10, offset: int = 0, db: AsyncSession = Depends(get_db)
):
    repo = ContactsRepository(db)
    return await repo.get_contacts(limit, offset)


@router.get("/search/", response_model=list[ContactsResponse])
async def search_contacts(query: str, db: AsyncSession = Depends(get_db)):
    repo = ContactsRepository(db)
    return await repo.search_contacts(query)
