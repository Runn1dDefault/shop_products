from typing import Literal

from sqlalchemy import select
from sqlalchemy.sql.selectable import Select

from db.models import ProductReview, Customer
from .base import SelectStrategy, FilteringStrategy, SortStrategy


class ReviewListSelectStrategy(SelectStrategy):
    """
    SELECT
        pr.id,
        u.fullname as fullname,
        pr.rating,
        pr.comment,
        pr.created_at
    FROM product_review AS pr
    JOIN customer as u;
    """
    def select(self) -> Select[ProductReview]:
        return (
            select(
                self._alias.id,
                Customer.fullname.label("fullname"),
                self._alias.rating,
                self._alias.comment,
                self._alias.created_at
            )
            .select_from(self._alias)
            .join(self._alias.customer)
        )


class ReviewProductIDFilteringStrategy(FilteringStrategy):
    def filter(self, product_id: str) -> Select[ProductReview]:
        return self.query.where(self._alias.product_id == product_id)


class ReviewCreatedOrderingStrategy(SortStrategy):
    def sort(self, sort_type: Literal["asc", "desc"]) -> Select[ProductReview]:
        return self.query.order_by(self._alias.created_at.desc())
