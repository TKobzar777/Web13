from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_cache.decorator import cache
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter



from src.auth.models import User
from src.auth.schemas import RoleEnum
from src.contacts.schemas import ContactsCreate, ContactsUpdate, ContactsResponse
from src.contacts.repo import ContactRepository
from config.db import get_db
from src.auth.utils import get_current_user, RoleChecker
# from config.general import settings

router = APIRouter()

# Add new contacts
@router.post("/",
             response_model=ContactsResponse,
             dependencies=[Depends(RateLimiter(times=2, seconds=59)), Depends(RoleChecker([RoleEnum.USER, RoleEnum.ADMIN]))]
             )
async def create_contact(
    contact_create: ContactsCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    contact_repo = ContactRepository(db)
    return await contact_repo.create_contact(contact_create, current_user.id)

# find contact by id
@router.get("/{contact_id}",
            response_model=ContactsResponse,
            dependencies=[Depends(RateLimiter(times=2, seconds=5))]
            )
async def get_contact(
    contact_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    contact_repo = ContactRepository(db)
    contact = await contact_repo.get_contact(contact_id, current_user.id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    return contact


@router.get("/", response_model=list[ContactsResponse])
@cache(expire=600, namespace="get_contacts")
async def get_contacts(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    contact_repo = ContactRepository(db)
    return await contact_repo.get_contacts(current_user.id, skip, limit)


@router.put("/{contact_id}", response_model=ContactsResponse)
async def update_contact(
    contact_id: int,
    contact_update: ContactsUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    contact_repo = ContactRepository(db)
    contact = await contact_repo.get_contact(contact_id, current_user.id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    return await contact_repo.update_contact(contact_id, contact_update, current_user.id)

@router.delete("/{contact_id}")
async def delete_contact(
    contact_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    contact_repo = ContactRepository(db)
    contact = await contact_repo.get_contact(contact_id, current_user.id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    await contact_repo.delete_contact(contact_id, current_user.id)
    return {"detail": "Contact deleted"}

@router.get("/birthdays/", response_model=list[ContactsResponse])
async def search_contacts_birthdays(days: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = ContactRepository(db)
    return await repo.search_contacts_birthdays(current_user.id, days)


@router.get("/all/", response_model=list[ContactsResponse], dependencies=[Depends(RoleChecker([RoleEnum.ADMIN]))], tags=['admin'])
async def get_contacts_admin(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    contact_repo = ContactRepository(db)
    return await contact_repo.get_contacts_admin(skip, limit)


# find contact by id
@router.get("/all/{contact_id}", response_model=ContactsResponse, dependencies=[Depends(RoleChecker([RoleEnum.ADMIN]))], tags=['admin'])
async def get_contact_admin(
    contact_id: int,
    db: AsyncSession = Depends(get_db)
):
    contact_repo = ContactRepository(db)
    contact = await contact_repo.get_contact_admin(contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    return contact


@router.get("/all/birthdays/", response_model=list[ContactsResponse], dependencies=[Depends(RoleChecker([RoleEnum.ADMIN]))], tags=['admin'])
async def search_contacts_birthdays_admin(days: int,
    db: AsyncSession = Depends(get_db)
):
    repo = ContactRepository(db)
    return await repo.search_contacts_birthdays_admin(days)



