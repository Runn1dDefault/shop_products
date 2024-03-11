from fastapi import APIRouter, HTTPException

import schemas
from crud import product as crud
from dependencies import depends

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[schemas.ShortProductSchema])
async def products_list(
    db: depends.DBDepends,
    params: depends.PageDepends,
    category_id: str = None,
    ordering: str = 'id',
    min_avg_rating: float = None,
    min_discount: float = None
):
    errors = {}

    if isinstance(min_avg_rating, float) and min_avg_rating > 5.0:
        errors["min_avg_rating"] = "max available is 5"

    if isinstance(min_discount, float) and min_discount < 0:
        errors["min_discount"] = "min_discount must be positive"

    if errors:
        raise HTTPException(
            status_code=400,
            detail=errors
        )

    limit, skip, search = params["limit"], params["skip"], params["search"]
    return await crud.products_list(
        async_db=db,
        limit=limit,
        offset=skip,
        filters={"activity": True, "category": category_id,  "search": search,
                 "popular": min_avg_rating, "discount": min_discount},
        ordering=list(ordering.replace(' ', '').split(','))
    )


@router.get("/{product_id}/detail", response_model=schemas.ProductDetailSchema)
async def product_detail(product_id: str, db: depends.DBDepends):
    return await crud.product_detail(async_db=db, product_id=product_id, activity=True)


@router.get("/{product_id}/reviews", response_model=list[schemas.ProductReviewSchema])
async def product_reviews(product_id: str, db: depends.DBDepends, params: depends.PageDepends):
    limit, skip, ordering = params["limit"], params["skip"], params["ordering"]
    return await crud.get_product_reviews(db, product_id=product_id, limit=limit, offset=skip, ordering=ordering)
