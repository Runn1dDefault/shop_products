from typing import Literal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from config import MAX_PRODUCTS_PER_PAGE, MAX_REVIEWS_PER_PAGE

from db.models import Product, ProductReview
from db.strategies import common, reviews, products
from db.strategies.context import QueryContext


async def products_list(
    async_db: AsyncSession,
    limit: int,
    offset: int = 0,
    filters: dict[Literal["activity", "category", "search", "popular", "discount"], str | bool | None] = None,
    ordering: list[Literal["id", "-id", "discount", "-discount", "popular", "-popular", "new", "-new"]] = None,
):
    if limit > MAX_PRODUCTS_PER_PAGE:
        limit = MAX_PRODUCTS_PER_PAGE

    query_context = QueryContext(
        select_strategy=products.ProductListSelectStrategy(alias=aliased(Product, name="p")),
        filtering_strategies={
            "activity": products.ProductActivityFilteringStrategy,
            "category": products.ProductCategoryFilteringStrategy,
            "search": common.NameSearchFilteringStrategy,
            "popular": products.ProductPopularFilteringStrategy,
            "discount": products.ProductDiscountFilteringStrategy
        },
        ordering_strategies={
            "id": common.IDOrderingStrategy,
            "popular": products.ProductPopularOrderingStrategy,
            "new": common.CreatedOrderingStrategy,
            "discount": products.ProductDiscountOrderingStrategy,
            "price": products.ProductPriceOrderingStrategy
        }
    )

    if filters:
        query_context.filtering(**filters)

    if ordering:
        query_context.ordering(ordering)
    return await async_db.execute(query_context.query.limit(limit).offset(offset))


async def product_detail(async_db: AsyncSession, product_id: str, activity: bool = None):
    query_context = QueryContext(
        select_strategy=products.ProductDetailSelectStrategy(alias=aliased(Product, name="p")),
        filtering_strategies={
            "id": common.IDFilteringStrategy,
            "activity": products.ProductActivityFilteringStrategy,
        }
    )
    query_context.filtering(id=product_id, activity=activity)
    return list(await async_db.execute(query_context.query.limit(1)))[0]


async def get_product_reviews(
    async_db: AsyncSession,
    product_id: str,
    limit: int,
    offset: int = 0,
    ordering: list[Literal["id", "-id", "created_at", "-created_at"]] = None
):
    if limit > MAX_REVIEWS_PER_PAGE:
        limit = MAX_REVIEWS_PER_PAGE

    query_context = QueryContext(
        select_strategy=reviews.ReviewListSelectStrategy(alias=aliased(ProductReview, name="pr")),
        filtering_strategies={"product_id": reviews.ReviewProductIDFilteringStrategy},
        ordering_strategies={"id": common.IDOrderingStrategy, "created_at": common.CreatedOrderingStrategy}
    )
    query_context.filtering(product_id=product_id)
    if ordering:
        query_context.ordering(ordering)
    return await async_db.execute(query_context.query.limit(limit).offset(offset))
