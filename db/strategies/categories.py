from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.sql import expression
from sqlalchemy.sql.selectable import Select
from sqlalchemy_utils.types.ltree import LQUERY

from db.models import Category
from .base import SelectStrategy, FilteringStrategy


class CategorySelectStrategy(SelectStrategy):
    """
    SELECT
        c.id,
        c.name,
        pc.id AS parent,
        nlevel(c.hierarchy) AS level
    FROM category AS c
    LEFT OUTER JOIN category pc ON pc.hierarchy = subpath(c.hierarchy, 0, -1);
    """

    def select(self) -> Select[Category]:
        return (
            select(
                self._alias.id,
                self._alias.name,
                Category.id.label("parent"),
                (func.nlevel(self._alias.hierarchy)).label("level")
            )
            .select_from(self._alias)
            .outerjoin(self._alias.parent)
        )


class CategoryDeactivatedFilteringStrategy(FilteringStrategy):
    def filter(self, deactivated: bool) -> Select[Category]:
        assert isinstance(deactivated, bool)
        return self.query.where(self._alias.deactivated.is_(deactivated))


class CategoryLevelFilteringStrategy(FilteringStrategy):
    def filter(self, level: int) -> Select[Category]:
        assert isinstance(level, int)
        return self.query.where(func.nlevel(self._alias.hierarchy) == level)


class CategoryHierarchyFilteringStrategy(FilteringStrategy):
    def filter(self, data) -> Select[Category]:
        assert isinstance(data, dict)

        match data:
            case {"descendants": bool() as descendants, "category_id": str() as category_id}:
                current_hierarchy = (
                    select(Category.hierarchy)
                    .where(Category.id == category_id)
                    .limit(1)
                    .scalar_subquery()
                )
                referral_method = "ancestor_of" if descendants is False else "descendant_of"
                return self.query.where(
                    getattr(self._alias.hierarchy, referral_method)(current_hierarchy),
                    self._alias.id != category_id
                )
            case {"category_id": str() | UUID() as category_id}:
                category_hex = UUID(category_id).hex if isinstance(category_id, str) else category_id.hex
                return self.query.where(self._alias.hierarchy.lquery(expression.cast("*.%s.*" % category_hex, LQUERY)))
        return self.query
