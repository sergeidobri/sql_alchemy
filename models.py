import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Publisher(Base):
    __tablename__ = "publisher"

    id = sq.Column(sq.Integer, primary_key=True)
    name = sq.Column(sq.String(length=120), nullable=False)

    book = relationship("Book", back_populates="publisher")

    def __str__(self):
        return f"Издатель {self.id}: {self.name}"
      
class Book(Base):
    __tablename__ = "book"

    id = sq.Column(sq.Integer, primary_key=True)
    title = sq.Column(sq.String(length=200), nullable=False)
    # у русских народных сказок - нет автора, NULL может быть
    id_publisher = sq.Column(sq.Integer, sq.ForeignKey("publisher.id"), nullable=True)

    publisher = relationship("Publisher", back_populates="book")
    stock = relationship("Stock", back_populates="book")

    def __str__(self):
        return f"Книга {self.id}: {self.title}"

class Shop(Base):
    __tablename__ = "shop"

    id = sq.Column(sq.Integer, primary_key=True)
    name = sq.Column(sq.String(length=200), nullable=False)

    stock = relationship("Stock", back_populates="shop")

    def __str__(self):
        return f"Магазин {self.id}: {self.name}"

class Sale(Base):
    __tablename__ = "sale"

    id = sq.Column(sq.Integer, primary_key=True)
    price = sq.Column(sq.Float, nullable=False)
    date_sale = sq.Column(sq.Date, nullable=False)
    id_stock = sq.Column(sq.Integer, sq.ForeignKey("stock.id"), nullable=False)
    count = sq.Column(sq.Integer, nullable=False)

    __table_args__ = (  # на уровне таблицы проверяем, что цена положительная или ноль (бесплатно)
        sq.CheckConstraint('price >= 0', name='check_price_positive'),
        sq.CheckConstraint('count >= 0', name='check_count_positive')
    )

    stock = relationship("Stock", back_populates="sale")

class Stock(Base):
    __tablename__ = "stock"

    id = sq.Column(sq.Integer, primary_key=True)
    id_book = sq.Column(sq.Integer, sq.ForeignKey("book.id"), nullable=False)
    id_shop = sq.Column(sq.Integer, sq.ForeignKey("shop.id"), nullable=False)
    count = sq.Column(sq.Integer, nullable=False)

    __table_args__ = (  # на уровне таблицы проверяем, что количество позиций в заказе > 0
        sq.CheckConstraint('count >= 0', name='check_count_positive'),
    )

    shop = relationship("Shop", back_populates="stock")
    book = relationship("Book", back_populates="stock")
    sale = relationship("Sale", back_populates="stock")


def create_tables(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
