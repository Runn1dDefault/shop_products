import pytest
from sqlalchemy import select
from sqlalchemy.orm import aliased

from db.models import Product
from db.strategies.common import (
    NameSearchFilteringStrategy, IDFilteringStrategy, IDOrderingStrategy, CreatedOrderingStrategy
)
from tests.test_strategies.utils import normalize_sql


def test_name_search_strategy():
    product_alias = aliased(Product, name="p")

    strategy = NameSearchFilteringStrategy(
        query=select(product_alias.id),
        alias=product_alias
    )
    query = strategy.filter("some search term")

    expected_sql = "SELECT p.id FROM product AS p WHERE lower(p.name) LIKE lower(:name_1)"
    assert normalize_sql(str(query)) == expected_sql

    with pytest.raises(AssertionError):
        strategy.filter(None)
        strategy.filter(1)
        strategy.filter(0.1)
        strategy.filter("1")
        strategy.filter(["1"])
        strategy.filter([True, False])


def test_id_filtering_strategy():
    product_alias = aliased(Product, name="p")

    strategy = IDFilteringStrategy(
        query=select(product_alias.id),
        alias=product_alias
    )
    for test_id in ("some string id", 1, 0.1):
        query = strategy.filter(test_id)

        expected_sql = "SELECT p.id FROM product AS p WHERE p.id = :id_1"
        assert normalize_sql(str(query)) == expected_sql

    query = strategy.filter(None)
    expected_sql = "SELECT p.id FROM product AS p WHERE p.id IS NULL"
    assert normalize_sql(str(query)) == expected_sql

    query = strategy.filter(True)
    expected_sql = "SELECT p.id FROM product AS p WHERE p.id = true"
    assert normalize_sql(str(query)) == expected_sql


def test_id_ordering_strategy():
    product_alias = aliased(Product, name="p")

    strategy = IDOrderingStrategy(
        query=select(product_alias.id),
        alias=product_alias
    )
    query = strategy.sort("asc")

    expected_sql = "SELECT p.id FROM product AS p ORDER BY p.id ASC"
    assert normalize_sql(str(query)) == expected_sql

    query = strategy.sort("desc")

    expected_sql = "SELECT p.id FROM product AS p ORDER BY p.id DESC"
    assert normalize_sql(str(query)) == expected_sql

    with pytest.raises(AssertionError):
        strategy.sort("")
        strategy.sort(1)
        strategy.sort(None)
        strategy.sort(False)
        strategy.sort("some random value")


def test_created_ordering_strategy():
    product_alias = aliased(Product, name="p")

    strategy = CreatedOrderingStrategy(
        query=select(product_alias.id),
        alias=product_alias
    )
    query = strategy.sort("asc")

    expected_sql = "SELECT p.id FROM product AS p ORDER BY p.created_at ASC"
    assert normalize_sql(str(query)) == expected_sql

    query = strategy.sort("desc")

    expected_sql = "SELECT p.id FROM product AS p ORDER BY p.created_at DESC"
    assert normalize_sql(str(query)) == expected_sql

    with pytest.raises(AssertionError):
        strategy.sort("")
        strategy.sort(1)
        strategy.sort(None)
        strategy.sort(False)
        strategy.sort("some random value")
