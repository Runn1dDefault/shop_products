from fastapi import APIRouter

import schemas
from crud import category as crud
from dependencies import depends

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[schemas.CategorySchema])
async def base_categories(db: depends.DBDepends):
    return await crud.category_list(
        async_db=db,
        filters={
            "deactivated": False,
            "hierarchy": {"category_id": None, "descendants": False},
            "level": 1
        }
    )


@router.get("/{category_id}/children/", response_model=list[schemas.CategorySchema])
async def category_children(category_id: str, db: depends.DBDepends, level: int = None):
    return await crud.category_list(
        async_db=db,
        filters={
            "deactivated": False,
            "hierarchy": {"category_id": category_id, "descendants": True},
            "level": level,
        }
    )


@router.get("/{category_id}/parents/", response_model=list[schemas.CategorySchema])
async def category_parents(category_id: str, db: depends.DBDepends, level: int = None):
    return await crud.category_list(
        async_db=db,
        filters={
            "deactivated": False,
            "hierarchy": {"category_id": category_id, "descendants": False},
            "level": level
        }
    )
