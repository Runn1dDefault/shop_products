from sqlalchemy import delete
from sqlalchemy.sql import expression
from sqlalchemy_utils import Ltree
from sqlalchemy_utils.types.ltree import LQUERY

from db.models import Category
from db.utils import get_first_value_from_rows


def test_category_creation(session):
    category1 = Category(name='Test Category 1')
    category2 = Category(name='Test Category 2', parent=category1, deactivated=True)
    category3 = Category(name='Test Category 3', parent=category2)
    category4 = Category(name='Test Category 4', parent=category2, deactivated=True)

    session.add_all([category1, category2, category3, category4])
    session.commit()

    assert category1.id is not None
    assert category1.name == "Test Category 1"
    assert category1.deactivated is False
    assert category1.hierarchy == category1.id.hex
    assert category1.parent is None

    assert category2.id is not None
    assert category2.name == "Test Category 2"
    assert category2.deactivated is True
    assert category2.hierarchy == category1.hierarchy + Ltree(category2.id.hex)
    assert category2.parent.id == category1.id

    assert category3.id is not None
    assert category3.name == "Test Category 3"
    assert category3.deactivated is False
    assert category3.hierarchy == category2.hierarchy + Ltree(category3.id.hex)
    assert category3.parent.id == category2.id

    assert category4.id is not None
    assert category4.name == "Test Category 4"
    assert category4.deactivated is True
    assert category4.hierarchy == category2.hierarchy + Ltree(category4.id.hex)
    assert category4.parent.id == category2.id


def test_category_update(session):
    category = Category(name='Test Category to update')
    category2 = Category(name='Test Category to update 2')

    session.add_all([category, category2])
    session.commit()

    category2.name = "Updated category"
    category2.hierarchy = category.hierarchy + Ltree(category2.id.hex)
    category2.deactivated = True
    session.commit()

    assert category2.name == "Updated category"
    assert category2.hierarchy == category.hierarchy + Ltree(category2.id.hex)
    assert category2.parent.id == category.id
    assert category2.deactivated is True


def test_category_delete(session):
    category = Category(name="Category to delete")
    session.add(category)
    session.commit()

    session.execute(delete(Category).where(Category.id == category.id))
    session.commit()

    category_query = session.query(Category).where(Category.id == category.id).first()
    assert category_query is None


def test_category_hierarchy_filtering(session):
    category1 = Category(name='Category 1')
    category2 = Category(name='Category 2', parent=category1)
    category3 = Category(name='Category 3', parent=category2)
    category4 = Category(name='Category 4', parent=category3)

    session.add_all([category1, category2, category3, category4])
    session.commit()

    category1_children_ids = get_first_value_from_rows(
        session.query(Category.id)
        .where(Category.hierarchy.lquery(expression.cast("%s.*" % category1.id.hex, LQUERY)))
        .all()
    )

    assert category2.id in category1_children_ids
    assert category3.id in category1_children_ids
    assert category4.id in category1_children_ids

    category4_parent_ids = get_first_value_from_rows(
        session.query(Category.id)
        .where(Category.hierarchy.ancestor_of(category4.hierarchy))
        .all()
    )

    assert category1.id in category4_parent_ids
    assert category2.id in category4_parent_ids
    assert category3.id in category4_parent_ids

    category2_tree = get_first_value_from_rows(
        session.query(Category.id)
        .where(Category.hierarchy.lquery(expression.cast("*.%s.*" % category1.id.hex, LQUERY)))
        .all()
    )

    assert category1.id in category2_tree
    assert category2.id in category2_tree
    assert category3.id in category2_tree
    assert category4.id in category2_tree
