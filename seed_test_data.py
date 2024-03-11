from db.connections import db_session_manager
from db.models import *


async def seed_categories():
    async with db_session_manager.session() as session:
        async with session.begin():

            category1 = Category(name="Category 1")
            category2 = Category(name="Category 2", parent=category1)
            category3 = Category(name="Category 3", parent=category2)

            session.add_all([category1, category2, category3])
            await session.commit()

    await db_session_manager.close()


async def seed_products():
    async with db_session_manager.session() as session:
        async with session.begin():
            tag_group = Tag(name="colors")
            blue_tag = Tag(name="blue", group=tag_group)
            red_tag = Tag(name="red", group=tag_group)
            gray_tag = Tag(name="gray", group=tag_group)

            product1 = Product(
                name="product 1",
                description="test description",
                made_in="KG",
                category_id="f6ddce9a-f624-442a-bfa8-9bcd42be1883"
            )
            product1.tags.extend([blue_tag, red_tag])

            product_inventory1 = ProductInventory(
                product=product1,
                quantity=5,
                unit_price=10,
                meta={"name": "Blue"}
            )
            product_inventory2 = ProductInventory(
                product=product1,
                quantity=10,
                unit_price=11,
                meta={"name": "Red"}
            )

            product2 = Product(
                name="product 2",
                description="test description",
                made_in="KZ",
                category_id="cad7a747-d447-4b63-9b00-07ca75596d50"
            )
            product2.tags.append(gray_tag)

            product_inventory3 = ProductInventory(
                product=product2,
                quantity=0,
                unit_price=25,
                meta={"name": "Gray"}
            )

            product1_img = ProductImage(
                product=product1,
                image="products/product1.jpg"
            )

            product2_img = ProductImage(
                product=product2,
                image="products/product2.jpg"
            )
            product3_img = ProductImage(
                product=product2,
                image="products/product3.jpg"
            )

            session.add_all(
                [
                    tag_group, blue_tag, red_tag, gray_tag,
                    product1, product2,
                    product_inventory1, product_inventory2,
                    product_inventory3,
                    product1_img, product2_img, product3_img
             ]
            )
            await session.commit()


async def seed_reviews():
    async with db_session_manager.session() as session:
        async with session.begin():
            john = Customer(
                email="john@boogeyman.com",
                fullname="John Wick",
            )

            john_doe = Customer(
                email="john_doe@gmail.com",
                fullname="John Doe"
            )

            review1 = ProductReview(
                product_id="b8e0e2e6-ae14-42a6-8dd1-c1472580e1da",
                customer=john,
                comment="I liked",
                rating=5
            )
            review2 = ProductReview(
                product_id="b8e0e2e6-ae14-42a6-8dd1-c1472580e1da",
                customer=john_doe,
                comment="I hate this product",
                rating=1
            )

            review3 = ProductReview(
                product_id="64064223-a02b-4f52-aae6-9841d6b211bb",
                customer=john,
                comment="not bad",
                rating=4
            )
            review4 = ProductReview(
                product_id="64064223-a02b-4f52-aae6-9841d6b211bb",
                customer=john_doe,
                comment="i neven buy this again",
                rating=1
            )
            session.add_all([john, john_doe, review1, review2, review3, review4])
            await session.commit()


if __name__ == "__main__":
    import asyncio

    asyncio.run(seed_categories())
    asyncio.run(seed_products())
    asyncio.run(seed_reviews())
