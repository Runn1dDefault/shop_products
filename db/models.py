from datetime import datetime
from decimal import Decimal
from typing import Self
from uuid import UUID, uuid4

from sqlalchemy import MetaData, String, ForeignKey, DECIMAL, Column, Table, text, DateTime, Index, func
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship, remote, foreign
from sqlalchemy_utils import LtreeType, Ltree


convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata_obj = MetaData(naming_convention=convention)
DeclarativeBase = declarative_base(metadata=metadata_obj)


class BaseModel(DeclarativeBase):
    __abstract__ = True

    id: Mapped[UUID] = mapped_column(default=uuid4, server_default=text("uuid_generate_v4()"), primary_key=True)


class Category(BaseModel):
    __tablename__ = "category"

    name: Mapped[str] = mapped_column(String(50), nullable=False)
    deactivated: Mapped[bool] = mapped_column(default=False, server_default="false")
    hierarchy = Column(LtreeType, nullable=False)

    parent: Mapped['Category'] = relationship(
        primaryjoin=(remote(hierarchy) == foreign(func.subpath(hierarchy, 0, -1))),
        backref='children',
        viewonly=True
    )

    products: Mapped[list["Product"]] = relationship(back_populates="category")

    def __init__(self, name, parent: Self = None, deactivated: bool = False):
        obj_id = uuid4()
        self.id = obj_id
        ltree_id = Ltree(obj_id.hex)
        self.name = name
        self.hierarchy = ltree_id if parent is None else parent.hierarchy + ltree_id
        self.deactivated = deactivated

    __table_args__ = (
        Index('ix_categories_hierarchy', hierarchy, postgresql_using='gist'),
    )


product_tag_association = Table(
    "product_tag",
    BaseModel.metadata,
    Column("product_id", ForeignKey("product.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tag.id", ondelete="CASCADE"), primary_key=True)
)


class Tag(BaseModel):
    __tablename__ = "tag"

    id: Mapped[UUID] = mapped_column(default=uuid4, server_default=text("uuid_generate_v4()"), primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    group_id: Mapped[UUID] = mapped_column(ForeignKey("tag.id", ondelete="SET NULL"), nullable=True)
    group: Mapped["Tag"] = relationship(remote_side=[id], back_populates="tags")
    tags: Mapped[list["Tag"]] = relationship(back_populates="group")
    products: Mapped[list["Product"]] = relationship(
        secondary=product_tag_association,
        back_populates="tags"
    )


class Product(BaseModel):
    __tablename__ = "product"

    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, server_default="true")
    made_in: Mapped[str] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        server_default=text("CURRENT_TIMESTAMP")
    )

    category_id: Mapped[UUID] = mapped_column(ForeignKey("category.id", ondelete="CASCADE"), nullable=False)
    category: Mapped["Category"] = relationship(back_populates="products")
    images: Mapped[list["ProductImage"]] = relationship(back_populates="product")
    inventories: Mapped[list["ProductInventory"]] = relationship(back_populates="product")
    reviews: Mapped[list["ProductReview"]] = relationship(back_populates="product")
    tags: Mapped[list["Tag"]] = relationship(
        secondary=product_tag_association,
        back_populates="products"
    )


class ProductInventory(BaseModel):
    __tablename__ = "product_inventory"

    quantity: Mapped[int] = mapped_column(default=0, server_default="0", nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(DECIMAL(7, 3), nullable=False)
    discount: Mapped[float] = mapped_column(nullable=True)
    meta = Column(JSON, nullable=True)  # there may be product variations or anything else that might highlight the data

    product_id: Mapped[UUID] = mapped_column(ForeignKey("product.id", ondelete="CASCADE"), nullable=False)
    product: Mapped["Product"] = relationship(back_populates="inventories")


class ProductImage(BaseModel):
    __tablename__ = "product_image"

    image: Mapped[str] = mapped_column(String(100), nullable=False)

    product_id: Mapped[UUID] = mapped_column(ForeignKey("product.id", ondelete="CASCADE"), nullable=False)
    product: Mapped["Product"] = relationship(back_populates="images")


class Customer(BaseModel):
    __tablename__ = "customer"

    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    fullname: Mapped[str] = mapped_column(String(100), nullable=False)

    reviews: Mapped[list["ProductReview"]] = relationship(back_populates="customer")


class ProductReview(BaseModel):
    __tablename__ = "product_reviews"

    comment: Mapped[str] = mapped_column(nullable=True)
    rating: Mapped[float] = mapped_column(default=0.0, server_default="0")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        server_default=text("CURRENT_TIMESTAMP")
    )

    product_id: Mapped[UUID] = mapped_column(ForeignKey("product.id", ondelete="CASCADE"), nullable=False)
    product: Mapped["Product"] = relationship(back_populates="reviews")
    customer_id: Mapped[UUID] = mapped_column(ForeignKey("customer.id", ondelete="CASCADE"), nullable=False)
    customer: Mapped["Customer"] = relationship(back_populates="reviews")
