from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.orm import aliased

from db.models import Product
from db.strategies.products import (
    ProductListSelectStrategy, ProductDetailSelectStrategy,
    ProductActivityFilteringStrategy, ProductCategoryFilteringStrategy,
    ProductPopularFilteringStrategy, ProductDiscountFilteringStrategy,
    ProductPopularOrderingStrategy, ProductDiscountOrderingStrategy,
    ProductPriceOrderingStrategy
)
from tests.test_strategies.utils import normalize_sql


def test_product_list_select_strategy():
    strategy = ProductListSelectStrategy(alias=aliased(Product, name="p"))
    query = strategy.select()

    expected_sql = normalize_sql(
        """
        SELECT 
            p.id, 
            p.name, 
            p.category_id, 
            p.made_in, 
            max(product_image.image) AS image, 
            max(product_inventory.unit_price) AS price, 
            max(product_inventory.discount) AS discount, 
            coalesce(avg(product_reviews.rating), :coalesce_1) AS avg_rating, 
            count(product_reviews.id) AS reviews_count 
        FROM product AS p 
        LEFT OUTER JOIN product_image ON p.id = product_image.product_id 
        LEFT OUTER JOIN product_inventory ON p.id = product_inventory.product_id 
        LEFT OUTER JOIN product_reviews ON p.id = product_reviews.product_id 
        GROUP BY 
            p.id
        """
    )
    assert normalize_sql(str(query)) == expected_sql


def test_product_detail_select_strategy():
    strategy = ProductDetailSelectStrategy(alias=aliased(Product, name="p"))
    query = strategy.select()

    expected_sql = normalize_sql(
        """
        SELECT 
            p.id, 
            p.name, 
            p.category_id, 
            p.made_in, 
            p.description, 
            coalesce(array_agg(distinct(product_image.image)), :coalesce_1) AS images, 
            coalesce(
                array_agg(
                    distinct(
                        jsonb_build_object(
                            :jsonb_build_object_1, product_inventory.id, 
                            :jsonb_build_object_2, product_inventory.meta, 
                            :jsonb_build_object_3, CASE WHEN (product_inventory.quantity > :quantity_1) 
                                                        THEN :param_1 
                                                        ELSE :param_2  
                                                   END, 
                            :jsonb_build_object_4, product_inventory.unit_price, 
                            :jsonb_build_object_5, product_inventory.discount
                        )
                    )
                ), :coalesce_2
            ) AS inventories 
        FROM product AS p 
        LEFT OUTER JOIN product_image ON p.id = product_image.product_id 
        LEFT OUTER JOIN product_inventory ON p.id = product_inventory.product_id GROUP BY p.id
        """
    )
    assert normalize_sql(str(query)) == expected_sql


def test_product_activity_filtering_strategy():
    product_alias = aliased(Product, name="p")

    strategy = ProductActivityFilteringStrategy(
        query=select(product_alias.id),
        alias=product_alias
    )
    query = strategy.filter(True)

    expected_sql = "SELECT p.id FROM product AS p WHERE p.is_active IS true"
    assert normalize_sql(str(query)) == expected_sql

    with pytest.raises(AssertionError):
        strategy.filter(None)
        strategy.filter(1)
        strategy.filter(0.1)
        strategy.filter("1")
        strategy.filter(["1"])
        strategy.filter([True, False])


def test_product_category_filtering_strategy():
    product_alias = aliased(Product, name="p")

    strategy = ProductCategoryFilteringStrategy(
        query=select(product_alias.id),
        alias=product_alias
    )
    query = strategy.filter(uuid4())

    expected_sql = normalize_sql(
        """
        SELECT 
            p.id 
        FROM product AS p 
        JOIN category ON category.id = p.category_id 
        WHERE category.hierarchy ~ CAST(:param_1 AS LQUERY)
        """
    )
    assert normalize_sql(str(query)) == expected_sql

    query = strategy.filter(str(uuid4()))
    assert query is not None

    with pytest.raises((AssertionError, ValueError)):
        strategy.filter(None)
        strategy.filter(1)
        strategy.filter(0.1)
        strategy.filter(False)
        strategy.filter("1")


def test_product_popular_filtering():
    product_alias = aliased(Product, name="p")

    strategy = ProductPopularFilteringStrategy(
        query=(
            select(product_alias.id)
            .select_from(product_alias)
            .outerjoin(product_alias.reviews)
            .group_by(product_alias.id)
        ),
        alias=product_alias
    )
    query = strategy.filter(1.0)

    expected_sql = normalize_sql(
        """
        SELECT 
            p.id 
        FROM product AS p 
        LEFT OUTER JOIN product_reviews ON p.id = product_reviews.product_id 
        GROUP BY 
            p.id 
        HAVING 
            avg(product_reviews.rating) >= :avg_1
        """
    )
    assert normalize_sql(str(query)) == expected_sql

    with pytest.raises(AssertionError):
        strategy.filter(None)
        strategy.filter(1)
        strategy.filter(False)
        strategy.filter("1")


def test_product_discount_filtering():
    product_alias = aliased(Product, name="p")

    strategy = ProductDiscountFilteringStrategy(
        query=(
            select(product_alias.id)
            .select_from(product_alias)
            .outerjoin(product_alias.inventories)
            .group_by(product_alias.id)
        ),
        alias=product_alias
    )
    query = strategy.filter(1.0)

    expected_sql = normalize_sql(
        """
        SELECT 
            p.id 
        FROM product AS p 
        LEFT OUTER JOIN product_inventory ON p.id = product_inventory.product_id 
        GROUP BY 
            p.id 
        HAVING 
            sum(product_inventory.discount) > :sum_1
        """
    )
    assert normalize_sql(str(query)) == expected_sql

    with pytest.raises(AssertionError):
        strategy.filter(None)
        strategy.filter(1)
        strategy.filter(False)
        strategy.filter("1")


def test_product_popular_ordering():
    product_alias = aliased(Product, name="p")

    strategy = ProductPopularOrderingStrategy(
        query=(
            select(product_alias.id)
            .select_from(product_alias)
            .outerjoin(product_alias.reviews)
            .group_by(product_alias.id)
        ),
        alias=product_alias
    )
    query = strategy.sort(sort_type="asc")

    expected_sql = normalize_sql(
        """
        SELECT 
            p.id 
        FROM product AS p 
        LEFT OUTER JOIN product_reviews ON p.id = product_reviews.product_id 
        GROUP BY 
            p.id 
        ORDER BY 
            avg(product_reviews.rating) ASC
        """
    )
    assert normalize_sql(str(query)) == expected_sql

    with pytest.raises(AssertionError):
        strategy.sort(None)
        strategy.sort(1)
        strategy.sort(False)
        strategy.sort("1")


def test_product_discount_ordering():
    product_alias = aliased(Product, name="p")

    strategy = ProductDiscountOrderingStrategy(
        query=(
            select(product_alias.id)
            .select_from(product_alias)
            .outerjoin(product_alias.inventories)
            .group_by(product_alias.id)
        ),
        alias=product_alias
    )
    query = strategy.sort(sort_type="asc")

    expected_sql = normalize_sql(
        """
        SELECT 
            p.id 
        FROM product AS p 
        LEFT OUTER JOIN product_inventory ON p.id = product_inventory.product_id 
        GROUP BY 
            p.id 
        ORDER BY 
            sum(product_inventory.discount) ASC
        """
    )
    assert normalize_sql(str(query)) == expected_sql

    with pytest.raises(AssertionError):
        strategy.sort(None)
        strategy.sort(1)
        strategy.sort(False)
        strategy.sort("1")


def test_product_price_ordering():
    product_alias = aliased(Product, name="p")

    strategy = ProductPriceOrderingStrategy(
        query=(
            select(product_alias.id)
            .select_from(product_alias)
            .outerjoin(product_alias.inventories)
            .group_by(product_alias.id)
        ),
        alias=product_alias
    )
    query = strategy.sort(sort_type="asc")

    expected_sql = normalize_sql(
        """
        SELECT 
            p.id 
        FROM product AS p 
        LEFT OUTER JOIN product_inventory ON p.id = product_inventory.product_id 
        GROUP BY 
            p.id 
        ORDER BY 
            max(product_inventory.unit_price) ASC
        """
    )
    assert normalize_sql(str(query)) == expected_sql

    with pytest.raises(AssertionError):
        strategy.sort(None)
        strategy.sort(1)
        strategy.sort(False)
        strategy.sort("1")
