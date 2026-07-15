from typing import List, Optional
from datetime import datetime
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine


class ProductType(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    products: List["Product"] = Relationship(back_populates="type")


class Product(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    product_id: int
    title: str
    price_eur: float
    scraped_at: datetime
    type_id: int | None = Field(default=None, foreign_key="producttype.id")
    type: Optional[ProductType] = Relationship(back_populates="products")


sqlite_file_name = "prueba.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# engine es el objeto que maneja la comunicación con SQLite
engine = create_engine(sqlite_url, echo=False)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    create_db_and_tables()
