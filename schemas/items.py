from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class OrmSchema(BaseModel):
    id: UUID

    class Config:
        orm_mode = True


class BaseCategorySchema(OrmSchema):
    name: str


class CategorySchema(BaseCategorySchema):
    parent: UUID | None = None
    level: int | None = None


class ProductSchema(OrmSchema):
    name: str
    category_id: UUID
    made_in: str | None = None


class ShortProductSchema(ProductSchema):
    image: str = ""
    price: float = 0.0
    avg_rating: float = 0.0
    reviews_count: int = 0
    discount: float | None = None


class ProductInventorySchema(OrmSchema):
    availability: bool
    unit_price: float
    discount: float | None = None
    meta: dict | list | None = None


class ProductDetailSchema(ProductSchema):
    description: str | None = None
    images: list[str] = []
    inventories: list[ProductInventorySchema] = []


class ProductReviewSchema(OrmSchema):
    fullname: str
    rating: float = 0.0
    comment: str | None = None
    created_at: datetime = None
