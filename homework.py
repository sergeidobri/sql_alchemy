import sqlalchemy as sq
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from models import create_tables, Publisher, Book, Shop, Stock, Sale
import os
import json


def load_password(path_to_config):
    if os.path.exists(path_to_config):
        load_dotenv(path_to_config)
    else:
        raise FileNotFoundError("Файл не был найден")
    
    return os.getenv("PASSWORD")

def main():
    path_to_config = "config.env"               # путь до файла с паролем
    path_to_json = "tests_data.json"            # путь до json файла для 3 задания
    password = load_password(path_to_config)    # пароль от пользователя бд
    login = 'postgres'                          # логин пользователя бд
    db_name = 'bookshop_db'                     # название бд

    DSN = f"postgresql://{login}:{password}@localhost:5432/{db_name}"
    engine = sq.create_engine(DSN)

    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Задание №1 (см. models.py)
    create_tables(engine)

    # Задание №3
    with open(path_to_json) as file:
        data = json.load(file)

    model_name = {
        "publisher": Publisher,
        "book": Book,
        "shop": Shop,
        "stock": Stock,
        "sale": Sale
    }
    
    for data_dict in data:
        model = model_name.get(data_dict['model'])
        if not model:
            raise TypeError(f"{data_dict['model']}: данная модель не найдена")
        db_fields = {**data_dict["fields"]}  # не распаковываем pk чтобы бд сама инкрементила записи
        if "price" in db_fields.keys():      # в бд цена хранится вещественным числом, не строкой
            db_fields["price"] = float(db_fields["price"])
        session.add(model(**db_fields))
    
    session.commit()  # сохранение

    # Задание №2
    # добавляем авторов и их книги
    publisher1 = Publisher(name="А.С. Пушкин")
    publisher2 = Publisher(name="С.А. Есенин")
    publisher3 = Publisher(name="Л.Н. Толстой")

    p1_books = [
        "Капитанская дочка",
        "Руслан и Людмила",
        "Евгений Онегин",
    ]

    p2_books = [
        "Письмо матери",
        "Береза",
        "Сборник стихов С.А. Есенина",
    ]

    p3_books = [
        "Война и мир",
        "Анна Каренина",
        "Детство",
    ]
    books_objects = []

    for books_lst, author in zip([p1_books, p2_books, p3_books], 
                                 [publisher1, publisher2, publisher3]):
        for book_name in books_lst:
            books_objects.append(Book(title=book_name, publisher=author))
            session.add(books_objects[-1])

    # добавляем магазины
    shops = [
        "Буквоед", 
        "Лабиринт", 
        "Книжный дом"
    ]
    shops_objects = []

    for shop in shops:
        shops_objects.append(Shop(name=shop))
        session.add(shops_objects[-1])

    # добавляем книги в наличие
    stocks_objects = []
    stocks_objects.append(Stock(book=books_objects[0], shop=shops_objects[0], count=10))  # запас кап. дочки в буквоеде
    stocks_objects.append(Stock(book=books_objects[1], shop=shops_objects[0], count=15))  # запас рус. и л. в буквоеде
    stocks_objects.append(Stock(book=books_objects[0], shop=shops_objects[1], count=8))   # запас кап. дочки в лабиринте
    stocks_objects.append(Stock(book=books_objects[2], shop=shops_objects[1], count=11))  # запас евг. он. в лабиринте
    stocks_objects.append(Stock(book=books_objects[0], shop=shops_objects[2], count=6))   # запас евг. он. в книжн. доме
    for stock in stocks_objects:
        session.add(stock)

    # добавляем факты продаж книг
    sales_objects = []
    sales_objects.append(Sale(price=600, date_sale="09-11-2022", stock=stocks_objects[0], count=1))
    sales_objects.append(Sale(price=500, date_sale="08-11-2022", stock=stocks_objects[1], count=1))
    sales_objects.append(Sale(price=580, date_sale="05-11-2022", stock=stocks_objects[2], count=1))
    sales_objects.append(Sale(price=490, date_sale="02-11-2022", stock=stocks_objects[3], count=1))
    sales_objects.append(Sale(price=600, date_sale="26-10-2022", stock=stocks_objects[4], count=1))
    for sale in sales_objects:
        session.add(sale)

    session.commit()

    name = None
    while name != '0':
        name = input("Введите автора (или 0 для остановки): ")

        query = session.query(
            Book.title, 
            Shop.name, 
            Sale.price, 
            Sale.date_sale).join(
                Stock, Stock.id_book == Book.id).join(
                Sale, Sale.id_stock == Stock.id).join(
                Shop, Shop.id == Stock.id_shop).join(
                Publisher, Publisher.id == Book.id_publisher).filter(
                    Publisher.name.like(f"%{name}%")
                    ).all()
        
        if len(query):
            format_len_title, format_len_name, format_len_price, format_len_date = 0, 0, 0, 0
            for q_title, q_name, q_price, q_date in query:
                format_len_title = max(len(q_title), format_len_title)
                format_len_name = max(len(q_name), format_len_name)
                format_len_price = max(len(str(q_price)), format_len_price)
                format_len_date = max(len(str(q_date)), format_len_date)
                
            for q_title, q_name, q_price, q_date in query:
                print(str(q_title).ljust(format_len_title),
                    str(q_name).ljust(format_len_name),
                    str(q_price).ljust(format_len_price),
                    str(q_date).ljust(format_len_date),
                    sep=' | ')
        else:
            if name == '0': 
                print("Выход из режима поиска")
                continue
            print("У такого писателя никто книгу не покупал")

    session.close()

if __name__ == "__main__":
    main()
    