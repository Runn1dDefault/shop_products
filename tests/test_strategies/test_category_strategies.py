from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.orm import aliased

from db.models import Category
from db.strategies.categories import CategorySelectStrategy, CategoryDeactivatedFilteringStrategy, \
    CategoryLevelFilteringStrategy, CategoryHierarchyFilteringStrategy
from tests.test_strategies.utils import normalize_sql


def test_category_select_strategy():
    strategy = CategorySelectStrategy(aliased(Category, name="c"))
    query = strategy.select()

    expected_sql = normalize_sql(
        """
        SELECT 
            c.id, 
            c.name, 
            category.id AS parent, 
            nlevel(c.hierarchy) AS level 
        FROM category AS c 
        LEFT OUTER JOIN category ON category.hierarchy = subpath(c.hierarchy, :subpath_1, :subpath_2)
        """
    )
    assert normalize_sql(str(query)) == expected_sql


def test_category_deactivated_filtering_strategy():
    strategy = CategoryDeactivatedFilteringStrategy(
        query=select(Category.id),
        alias=aliased(Category, name="c")
    )

    query = strategy.filter(False)
    expected_sql = "SELECT category.id FROM category, category AS c WHERE c.deactivated IS false"
    assert normalize_sql(str(query)) == expected_sql

    query = strategy.filter(True)
    expected_sql = "SELECT category.id FROM category, category AS c WHERE c.deactivated IS true"
    assert normalize_sql(str(query)) == expected_sql

    with pytest.raises(AssertionError):
        strategy.filter(None)
        strategy.filter(0.1)
        strategy.filter(0)
        strategy.filter("1")


def test_category_level_filtering_strategy():
    strategy = CategoryLevelFilteringStrategy(
        query=select(Category.id),
        alias=aliased(Category, name="c")
    )
    query = strategy.filter(1)
    expected_sql = "SELECT category.id FROM category, category AS c WHERE nlevel(c.hierarchy) = :nlevel_1"
    assert normalize_sql(str(query)) == expected_sql

    with pytest.raises(AssertionError):
        strategy.filter(None)
        strategy.filter(0.1)
        strategy.filter("some-string")
        strategy.filter("1")


def test_category_hierarchy_filtering_strategy():
    category_alias = aliased(Category, name="c")
    strategy = CategoryHierarchyFilteringStrategy(
        query=select(category_alias.id),
        alias=category_alias
    )
    query = strategy.filter({"descendants": True, "category_id": "some-category-id"})
    expected_sql = normalize_sql(
        """
        SELECT 
            c.id 
        FROM category AS c 
        WHERE 
            (c.hierarchy <@ (SELECT category.hierarchy FROM category WHERE category.id = :id_1 LIMIT :param_1)) 
            AND c.id != :id_2
        """
    )
    assert normalize_sql(str(query)) == expected_sql

    query = strategy.filter({"descendants": False, "category_id": "some-category-id"})
    expected_sql = normalize_sql(
        """
        SELECT 
            c.id 
        FROM category AS c 
        WHERE 
            (c.hierarchy @> (SELECT category.hierarchy FROM category WHERE category.id = :id_1 LIMIT :param_1)) 
            AND c.id != :id_2
        """
    )
    assert normalize_sql(str(query)) == expected_sql

    query = strategy.filter({"category_id": uuid4()})
    expected_sql = "SELECT c.id FROM category AS c WHERE c.hierarchy ~ CAST(:param_1 AS LQUERY)"
    assert normalize_sql(str(query)) == expected_sql

    query = strategy.filter({"category_id": str(uuid4())})
    expected_sql = "SELECT c.id FROM category AS c WHERE c.hierarchy ~ CAST(:param_1 AS LQUERY)"
    assert normalize_sql(str(query)) == expected_sql

    query = strategy.filter({"category_id": uuid4(), "descendants": None})
    expected_sql = "SELECT c.id FROM category AS c WHERE c.hierarchy ~ CAST(:param_1 AS LQUERY)"
    assert normalize_sql(str(query)) == expected_sql

    with pytest.raises(AssertionError):
        strategy.filter(None)
        strategy.filter(1)
        strategy.filter(1.0)
        strategy.filter("some-string")
