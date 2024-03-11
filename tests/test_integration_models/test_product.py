from sqlalchemy import delete

from db.models import Category, Product, ProductInventory


def test_product_create(session):
    category = Category(name="Test product category")
    product = Product(category=category, name="Test product 1", is_active=True, made_in="China")
    inventory = ProductInventory(product=product, quantity=10, unit_price=5.0)
    session.add_all([category, product, inventory])
    session.commit()

    assert product.id is not None
    assert product.category is not None
    assert product.category.id == category.id
    assert product.name == "Test product 1"
    assert product.is_active is True
    assert product.made_in == "China"
    assert product.description is None

    assert inventory.id is not None
    assert inventory.product is not None
    assert inventory.product.id == product.id
    assert inventory.quantity == 10
    assert inventory.unit_price == 5.0


def test_product_update(session):
    category = Category(name="Test update product category")
    category2 = Category(name="Test category to update product")
    product = Product(category=category, name="Test product to update", is_active=True, made_in="China")
    session.add_all([category, product])
    session.commit()

    assert product.name == "Test product to update"
    assert product.category.id == category.id
    assert product.is_active is True
    assert product.made_in == "China"
    assert product.description is None

    product.name = "New product name"
    product.category = category2
    product.is_active = False
    product.made_in = "KZ"
    product.description = "New description"
    session.commit()

    assert product.name == "New product name"
    assert product.category.id == category2.id
    assert product.is_active is False
    assert product.made_in == "KZ"
    assert product.description == "New description"


def test_product_delete(session):
    category = Category(name="Test update product category")
    product = Product(category=category, name="Test product to update", is_active=True, made_in="China")
    session.add_all([category, product])
    session.commit()

    session.execute(delete(Product).where(Product.id == product.id))
    session.commit()

    query = session.query(Product).where(Product.id == product.id).first()
    assert query is None
