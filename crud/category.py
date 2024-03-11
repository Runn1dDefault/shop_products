from typing import Literal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from db.models import Category
from db.strategies import categories
from db.strategies.context import QueryContext


hierarchy_depends = dict[Literal["descendants", "category_id"], None | bool | str]
category_filters = Literal["hierarchy", "level", "deactivated"]


async def category_list(
    async_db: AsyncSession,
    filters: dict[category_filters, hierarchy_depends | None | bool | int] = None
):
    query_context = QueryContext(
        select_strategy=categories.CategorySelectStrategy(alias=aliased(Category, name="c")),
        filtering_strategies={
            "deactivated": categories.CategoryDeactivatedFilteringStrategy,
            "hierarchy": categories.CategoryHierarchyFilteringStrategy,
            "level": categories.CategoryLevelFilteringStrategy
        }
    )
    if filters:
        query_context.filtering(**filters)
    return await async_db.execute(query_context.query)
