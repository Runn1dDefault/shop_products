from typing import Literal
from uuid import UUID

from sqlalchemy import select, func, case as sql_case
from sqlalchemy.sql import expression
from sqlalchemy.sql.selectable import Select
from sqlalchemy_utils.types.ltree import LQUERY

from db.models import Category, Product, ProductInventory, ProductImage, ProductReview
from .base import SelectStrategy, FilteringStrategy, SortStrategy


class ProductListSelectStrategy(SelectStrategy):
    """
    SELECT
        p.id,
        p.name,
        p.category_id,
        p.made_in,
        max(p_img.image) AS image,
        max(inv.unit_price) AS price,
        max(inv.discount) AS discount,
        coalesce(avg(rv.rating), 0.0) AS avg_rating,
        count(rv.id) AS reviews_count
    FROM product AS p
    LEFT OUTER JOIN product_image p_img ON p.id = p_img.product_id
    LEFT OUTER JOIN product_inventory inv ON p.id = inv.product_id
    LEFT OUTER JOIN product_reviews rv ON p.id = rv.product_id
    GROUP BY
        p.id
    ORDER BY
        p.id ASC
    LIMIT 10 OFFSET 0;
    """
    def select(self) -> Select[Product]:
        return (
            select(
                self._alias.id,
                self._alias.name,
                self._alias.category_id,
                self._alias.made_in,
                func.max(ProductImage.image).label("image"),
                func.max(ProductInventory.unit_price).label("price"),
                func.max(ProductInventory.discount).label("discount"),
                func.coalesce(func.avg(ProductReview.rating), 0.0).label('avg_rating'),
                func.count(ProductReview.id).label("reviews_count")
            )
            .select_from(self._alias)
            .outerjoin(self._alias.images)
            .outerjoin(self._alias.inventories)
            .outerjoin(self._alias.reviews)
            .group_by(self._alias.id)
        )


class ProductDetailSelectStrategy(SelectStrategy):
    """
    SELECT
        p.id,
        p.name,
        p.category_id,
        p.made_in,
        p.description,
        coalesce(array_agg(distinct(product_image.image)), '{}') AS images,
        coalesce(
            array_agg(
                distinct(
                    jsonb_build_object(
                        'id', product_inventory.id,
                        'meta', product_inventory.meta,
                        'availability', CASE WHEN product_inventory.quantity > 0 THEN true ELSE false END,
                        'unit_price', product_inventory.unit_price,
                        'discount', product_inventory.discount
                    )
                )
            ), '{}'
        ) AS inventories
    FROM product AS p
    LEFT OUTER JOIN product_image ON p.id = product_image.product_id
    LEFT OUTER JOIN product_inventory ON p.id = product_inventory.product_id
    LEFT OUTER JOIN category ON p.category_id = category.id
    GROUP BY
        p.id
    LIMIT 1;
    """

    def select(self) -> Select[Product]:
        return (
            select(
                self._alias.id,
                self._alias.name,
                self._alias.category_id,
                self._alias.made_in,
                self._alias.description,
                func.coalesce(func.array_agg(func.distinct(ProductImage.image)), []).label('images'),
                func.coalesce(
                    func.array_agg(
                        func.distinct(
                            func.jsonb_build_object(
                                'id', ProductInventory.id,
                                'meta', ProductInventory.meta,
                                'availability', sql_case((ProductInventory.quantity > 0, True), else_=False),
                                'unit_price', ProductInventory.unit_price,
                                'discount', ProductInventory.discount
                            )
                        )
                    ), []
                ).label('inventories')
            )
            .select_from(self._alias)
            .outerjoin(self._alias.images)
            .outerjoin(self._alias.inventories)
            .group_by(self._alias.id)
        )


class ProductActivityFilteringStrategy(FilteringStrategy):
    def filter(self, activity: bool):
        assert isinstance(activity, bool)
        return self.query.where(self._alias.is_active.is_(activity))


class ProductCategoryFilteringStrategy(FilteringStrategy):
    def filter(self, category_id: UUID | str):
        assert isinstance(category_id, UUID) or isinstance(category_id, str)
        if isinstance(category_id, str):
            category_id = UUID(category_id)

        return (
            self.query
            .join(self._alias.category)
            .where(Category.hierarchy.lquery(expression.cast("*.%s.*" % category_id.hex, LQUERY)))
        )


class ProductPopularFilteringStrategy(FilteringStrategy):
    """this filter assumes a left outer join to Product.reviews in the query"""

    def filter(self, min_avg_rating: float):
        assert isinstance(min_avg_rating, float)
        avg_rating = func.avg(ProductReview.rating)
        return self.query.having(avg_rating >= min_avg_rating)


class ProductPopularOrderingStrategy(SortStrategy):
    """this filter assumes a left outer join to Product.reviews in the query"""

    def sort(self, sort_type: Literal["asc", "desc"]):
        assert isinstance(sort_type, str) and sort_type in ("asc", "desc")
        avg_rating = func.avg(ProductReview.rating)
        return self.query.order_by(self._get_sort_method(avg_rating, sort_type)())


class ProductDiscountFilteringStrategy(FilteringStrategy):
    """this filter assumes a left outer join to Product.inventories in the query"""

    def filter(self, min_discount: float):
        assert isinstance(min_discount, float)
        if min_discount == 0:
            return self.query
        return self.query.having(func.sum(ProductInventory.discount) > min_discount)


class ProductDiscountOrderingStrategy(SortStrategy):
    """this filter assumes a left outer join to Product.inventories in the query"""

    def sort(self, sort_type: Literal["asc", "desc"]):
        assert isinstance(sort_type, str) and sort_type in ("asc", "desc")
        return self.query.order_by(self._get_sort_method(func.sum(ProductInventory.discount), sort_type)())


class ProductPriceOrderingStrategy(SortStrategy):
    """this filter assumes a left outer join to Product.inventories in the query"""

    def sort(self, sort_type: Literal["asc", "desc"]):
        assert isinstance(sort_type, str) and sort_type in ("asc", "desc")
        return self.query.order_by(self._get_sort_method(func.max(ProductInventory.unit_price), sort_type)())
