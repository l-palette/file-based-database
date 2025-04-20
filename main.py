from pathlib import Path
from typing import List
from faker import Faker
import random
import logging
import re
from datetime import datetime
import socket

FILENAME = "home_library.txt"
HEADERS = [
    "id",
    "name",
    "year",
    "authors",
    "genres",
    "width",
    "height",
    "book_type",
    "source",
    "date_added",
    "date_read",
    "rating",
]

regex_schema = {
    "name": r"[А-Яа-яЁёA-Za-z0-9\s]{1,100}",
    "authors": r"[А-Яа-яЁёA-Za-z\s,]{1,130}",
    "genres": r"[А-Яа-яЁёA-Za-z\s,]{1,100}",
    "year": r"\d{4}",
    "width": r"\d+(\.\d+)?",
    "height": r"\d+(\.\d+)?",
    "book_type": r"мягкий|твердый",
    "source": r"покупка|подарок|наследство",
    "date_added": r"\d{2}-\d{2}-\d{4}",
    "date_read": r"\d{2}-\d{2}-\d{4}",
    "rating": r"([1-9]|10)/10 - .{1,200}",
}


def validate_regex(field: str, value) -> None:
    if not re.fullmatch(regex_schema[field], str(value)):
        raise ValueError(
            f"Значение {value} не соответствует регулярному выражению {regex_schema[field]}"
        )


def validate_year(year) -> None:
    validate_regex("year", year)
    if int(year) > datetime.now().year:
        raise ValueError("Год издания не может быть больше текущего года")


def validate_width(width) -> None:
    validate_regex("width", width)
    if float(width) > 1000:
        raise ValueError("Ширина книги не может быть больше 1 метра")
    elif float(width) < 0:
        raise ValueError("Ширина книги не может быть отрицательной")


def validate_height(height) -> None:
    validate_regex("height", height)
    if float(height) > 1000:
        raise ValueError("Высота книги не может быть больше 1 метра")
    elif float(height) < 0:
        raise ValueError("Высота книги не может быть отрицательной")


def validate_date_added(date_added, year) -> None:
    validate_regex("date_added", date_added)
    date_added_datetime = datetime.strptime(date_added, "%d-%m-%Y")
    if date_added_datetime >= datetime.now():
        raise ValueError("Дата добавления не может быть позже текущей даты")
    if date_added_datetime.year < int(year):
        raise ValueError("Год добавления не может быть раньше года издания")


def validate_date_read(date_read, date_added) -> None:
    validate_regex("date_read", date_read)
    if date_read:
        date_added_datetime = datetime.strptime(date_added, "%d-%m-%Y")
        date_read_datetime = datetime.strptime(date_read, "%d-%m-%Y")
        if date_read_datetime < date_added_datetime:
            raise ValueError("Дата чтения не может быть раньше даты добавления")


def dict_to_line(book: dict) -> str:
    return "|".join(str(book[header]) for header in HEADERS)


def line_to_dict(line: str) -> dict:
    parts = line.strip().split("|")
    return {
        "id": parts[0],
        "name": parts[1],
        "year": parts[2],
        "authors": parts[3],
        "genres": parts[4],
        "width": parts[5],
        "height": parts[6],
        "book_type": parts[7],
        "source": parts[8],
        "date_added": parts[9],
        "date_read": parts[10],
        "rating": parts[11],
    }


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s"
)

fake = Faker("ru_RU")


def authors_set():
    authors = set()
    while len(authors) < 100:
        authors.add(fake.name())
    return authors


genres_list = [
    "Фэнтези",
    "Биография",
    "Научная фантастика",
    "Детектив",
    "Приключения",
    "Романтика",
    "Ужасы",
    "Исторический",
    "Научный",
    "Мистика",
    "Комедия",
    "Триллер",
    "Драма",
    "Приключенческий роман",
    "Сказка",
    "Поэзия",
    "Классика",
    "Современная проза",
    "Философия",
    "Психология",
    "Социальная фантастика",
    "Мифология",
    "Спорт",
    "Кулинария",
    "Техническая литература",
    "Автобиография",
    "Справочная литература",
]

authors_list = list(authors_set())


# SINGLE BOOK
def generate_valid_book(authors_list, genres_list) -> dict:
    name = fake.sentence(nb_words=random.randint(1, 5)).rstrip(".")
    authors = ",".join(random.sample(authors_list, k=random.randint(1, 3)))
    genres = ",".join(random.sample(genres_list, k=random.randint(1, 4)))
    year = str(random.randint(1000, 2025))
    width = round(random.uniform(10.0, 200.0), 1)
    height = round(random.uniform(10.0, 200.0), 1)
    book_type = random.choice(["мягкий", "твердый"])
    source = random.choice(["покупка", "подарок", "наследство"])
    # date_added
    start_date = datetime(int(year), 1, 1)
    date_added = str(
        fake.date_between(start_date=start_date, end_date="today").strftime("%d-%m-%Y")
    )
    while True:
        try:
            validate_date_added(date_added, year)
            break
        except ValueError:
            date_added = str(
                fake.date_between(start_date=start_date, end_date="today").strftime(
                    "%d-%m-%Y"
                )
            )
    # date_read
    date_added_dt = datetime.strptime(date_added, "%d-%m-%Y")
    date_read = str(
        fake.date_between(start_date=date_added_dt, end_date="today").strftime(
            "%d-%m-%Y"
        )
    )
    while True:
        try:
            validate_date_read(date_read, date_added)
            break
        except ValueError:
            date_read = str(
                fake.date_between(start_date=date_added_dt, end_date="today").strftime(
                    "%d-%m-%Y"
                )
            )
    # rating
    rating_value = random.randint(1, 10)
    description = fake.sentence(nb_words=random.randint(3, 10), variable_nb_words=True)
    rating = f"{rating_value}/10 - {description}"

    return {
        "name": name,
        "authors": authors,
        "genres": genres,
        "year": year,
        "width": width,
        "height": height,
        "book_type": book_type,
        "source": source,
        "date_added": date_added,
        "date_read": date_read,
        "rating": rating,
    }


def get_next_id() -> int:
    if not Path(FILENAME).exists():
        return 1

    with open(FILENAME, "r", encoding="utf-8") as file:
        lines = file.readlines()
        if lines:
            last_book = line_to_dict(lines[-1])
            return int(last_book["id"]) + 1
    return 1


def is_unique_book(book: dict) -> bool:
    original_filename = Path(FILENAME)
    with original_filename.open("r") as file:
        for line in file:
            existing_book = line_to_dict(line)
            if (
                existing_book["name"] == book["name"]
                and existing_book["authors"] == book["authors"]
                and existing_book["year"] == book["year"]
                and existing_book["genres"] == book["genres"]
            ):

                return False
    return True


def add_book(book: dict):
    book_id = get_next_id()
    book["id"] = book_id
    original_filename = Path(FILENAME)
    if is_unique_book(book):
        with original_filename.open("a") as file:
            file.write(dict_to_line(book) + "\n")
        return f"Добавлена книга: {book['name']} (ID: {book_id})"
    else:
        return f"Книга уже добавлена: {book['name']}, написанная {book['authors']}"


# MULTIPLE BOOKS
def print_all_books():
    original_filename = Path(FILENAME)
    res = ""
    with original_filename.open("r") as file:
        for line in file:
            book = line_to_dict(line)
            res += (
                f"ID: {book['id']},\n"
                f"\tНазвание: {book['name']},\n"
                f"\tАвторы: {book['authors']},\n"
                f"\tГод: {book['year']},\n"
                f"\tЖанры: {book['genres']},\n"
                f"\tШирина: {book['width']},\n"
                f"\tВысота: {book['height']},\n"
                f"\tТип книги: {book['book_type']},\n"
                f"\tИсточник: {book['source']},\n"
                f"\tДата добавления: {book['date_added']},\n"
                f"\tДата прочтения: {book['date_read']},\n"
                f"\tРейтинг: {book['rating']}\n"
            )
    return res


def print_books(books: List[dict]) -> str:
    """
    Печатает информацию о книгах.
    """
    if not books:
        return "Нет книг для отображения."
    res = ""
    res += f"Найдено {len(books)} книг(и):\n"
    for book in books:
        res += (
            f"ID: {book['id']},\n"
            + f"\tНазвание: {book['name']},\n"
            + f"\tАвторы: {book['authors']},\n"
            + f"\tГод: {book['year']},\n"
            + f"\tЖанры: {book['genres']},\n"
            + f"\tШирина: {book['width']},\n"
            + f"\tВысота: {book['height']},\n"
            + f"\tТип книги: {book['book_type']},\n"
            + f"\tИсточник: {book['source']},\n"
            + f"\tДата добавления: {book['date_added']},\n"
            + f"\tДата прочтения: {book['date_read']},\n"
            + f"\tРейтинг: {book['rating']}\n"
        )

    return res


def modify_books_file(new_books: List[dict] = None, update=False) -> str:
    res = ""
    temp_filename = Path("temp.txt")
    found = False
    original_filename = Path(FILENAME)

    with original_filename.open("r") as file, temp_filename.open("w") as temp_file:
        for line in file:
            book = line_to_dict(line)
            # Проверяем, есть ли книга в списке для обновления
            for new_book in new_books:
                if book["id"] == new_book["id"]:
                    found = True

                    # Обновляем поля книги
                    if update:
                        book.update(new_book)
                        if is_unique_book(book):
                            temp_file.write(dict_to_line(book) + "\n")
                            res += (
                                f"Обновлена книга: {book['name']} (ID: {book['id']})\n"
                            )
                            break
                        else:
                            res += f"Книга с именем {book['name']} уже есть, написанная {book['authors']}\n"
                    else:
                        res += f"Удалена книга: {book['name']} (ID: {book['id']})\n"
                        break
            else:
                # Если книга не обновляется, записываем её как есть
                temp_file.write(line)

    if found:
        original_filename.unlink()
        temp_filename.rename(original_filename)
    else:
        temp_filename.unlink()

    return res


def delete_books(client_socket, field: str, value: str) -> str:
    """
    Проходит по файлу, ищет в поле field совпадения с value.
    Если находит, то записывает все строки до нее и после нее в файл temp.txt,
    затем удаляет файл home_library.txt и переименовывает temp.txt в home_library.txt.
    """
    client_socket.send("Удалить? (д/н)".encode())
    choice = client_socket.recv(1024).decode().strip().lower()
    while choice not in ("д", "н", "y", "n"):
        client_socket.send("Некорректный ввод".encode())
    if choice == "д" or choice == "y":
        return modify_books_file(search_books(field, value))
    return ""


def search_books(field: str, value: str) -> List[dict]:
    """
    Ищет в поле field совпадения c value, возвращает список словарей книг
    """
    result = []
    with open(FILENAME, "r") as file:
        for line in file:
            book = line_to_dict(line)
            value_book = book[field]
            if str(value).lower() in value_book.lower():
                result.append(book)
                if field == "id":
                    return [book]
    return result


def update_books(client_socket, field: str, value: str, new_field, new_value) -> str:
    books = search_books(field, value)
    for book in books:
        book[new_field] = new_value
    results = "Найдены книги:\n"
    results += print_books(books)
    client_socket.send(str(results).encode())

    client_socket.send("Удалить? (д/н)".encode())
    choice = client_socket.recv(1024).decode().strip().lower()
    while choice not in ("д", "н", "y", "n"):
        client_socket.send("Некорректный ввод".encode())
    if choice == "д" or choice == "y":
        return modify_books_file(books, True)
    return ""


library = """


 -                   @-                          @-                   %
   -                -           @@@@@@@            @                @  
    @-            -          @@@@@@ @@@@@@           @            @-   
      @         +        @@@@@@@       @@@@@@@         =         -     
          @@          @@@@@@@             @@@@@@@          @@          
        @@@@@@     @@@@@@       @@@@@@@       @@@@@@     @@@@@@        
       @@@@@@@ @@@@@@@        @@@@   @@@@        @@@@@@@@@@@@@@        
         @@@@@@@@@            @@@     @@@            @@@@@@@@@         
        @@@@@@@@-             @@@     @@@              @@@@@@@@ *      
     @@@@@@      @             @@@@@@@@@              -     @@@@@@-    
   @@@@@           *             @@@@@              -          @@@@ -  
 @- @@@              -                            #             @@@  @-
-   @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@    
        @@@      @@@   @@@     @@@   @@@     @@@   @@@      @@@        
        @@@@@@@@@@@@   @@@@@@@@@@@   @@@@@@@@@@@   @@@@@@@@@@@@        
         @@@@@@@@@@    @@@@@@@@@@@   @@@@@@@@@@@    @@@@@@@@@@         
          @@@   @@@     @@@   @@@     @@@- =@@@     @@@   @@@          
          @@@   @@@     @@@   @@@    @@@@+= @@@     @@@   @@@          
          @@@   @@@     @@@   @@@  @*@@@@   @@@     @@@   @@@          
          @@@   @@@     @@@   @@@ -* -@@@   @@@     @@@   @@@          
          @@@   @@@     @@@   @@@--@- @@@   @@@     @@@   @@@          
          @@@   @@@     @@@   @@@ +@  @@@   @@@     @@@   @@@          
          @@@   @@@     @@@ @-@@@     @@@-  @@@     @@@   @@@          
          @@@   @@@     @@@-@-@@@     @@@  -@@@     @@@   @@@          
          @@@   @@@     @@@ *-@@@     @@@   @@@     @@@   @@@          
          @@@   @@@     @@@   @@@     @@@   @@@=    @@@   @@@          
          @@@   @@@    -@@@   @@@     @@@   @@@ @   @@@   @@@          
 -        @@@   @@@  =  @@@   @@@     @@@   @@@   = @@@   @@@         @
   -      @@@   @@@@    @@@   @@@     @@@   @@@     *@@   @@@       @= 
    @=    @@@   @@@     @@@   @@@     @@@   @@@     @@@   @@@      -   
      @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@-     
      @@@ @@                                               @@ @@@      
   @@@@@@@@@@@                                           @@@@@@@@@@@   
   @@@@@@@@@@@                                           @@@@@@@@@@@   
   @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@   
   @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@   
     -           @                                    -           @-   
   -               =                                +               @  
 =                   -                            @                   *

"""


def display_menu():
    return (
        "\n--- Меню Библиотеки ---\n"
        "1. Добавить книгу\n"
        "2. Показать все книги\n"
        "3. Искать книги\n"
        "4. Обновить книгу\n"
        "5. Удалить книгу\n"
        "6. Выход\n"
    )


def display_add_menu():
    return (
        "\n--- Меню Библиотеки ---\n"
        "1.1. Сгенерировать книгу\n"
        "1.2. Ввести книгу вручную\n"
        "1.3. Выход\n"
    )


"""
Обернуть в Netcat сервер
Реализованы функции:
1. Добавить книгу
1.1. Ввести книгу -  # TODO реализовать функцию ввода всех значений и запуска валидации
1.2. Сгенерировать книгу
1.3. Добавить книгу от словаря
book_example = {
    "name": "1984",
    "year": "1949",
    "authors": "George Orwell",
    "genres": "Dystopian, Political Fiction",
    "width": "5.5",
    "height": "8.0",
    "book_type": "Мягкий",
    "source": "Подарок",
    "date_added": "2023-10-01",
    "date_read": "2023-10-10",
    "rating": "5/10 - супер книга"
}
book1 = generate_valid_book(authors_list, genres_list)
add_book(book1)
add_book(book_example)
2. Показать все книги 
2.1. print_all_books()

3. Искать книгу
3.1. Ввести поле для поиска и значение
3.2. Вывести книги
a = search_books("source", "подарок")
print_books(a)

4. Обновить книгу
4.1. Ввести поле для поиска и значение
4.2. Ввести поле для изменения и значение
update_books("id", "1", "name", "Sleep")

5. Удалить книгу
5.1. Ввести поле для поиска и значение
delete_books("id", "1")
"""


def handle_client(client_socket):
    client_socket.sendall(library.encode())
    client_socket.sendall("Добро пожаловать в библиотеку!\n".encode())
    while True:
        client_socket.send(display_menu().encode())
        choice = client_socket.recv(1024).decode().strip()

        if choice == "1":
            while True:
                client_socket.send(display_add_menu().encode())
                choice_add = client_socket.recv(1024).decode().strip()
                if choice_add == "1.1":
                    book = generate_valid_book(authors_list, genres_list)
                    client_socket.send("Добавить? (д/н)".encode())
                    choice = client_socket.recv(1024).decode().strip().lower()
                    while choice not in ("д", "н", "y", "n"):
                        client_socket.send("Некорретный ввод".encode())
                    if choice == "д" or choice == "y":
                        response = add_book(book)
                        client_socket.send(response.encode())
                    break
                elif choice_add == "1.2":
                    while True:
                        try:
                            client_socket.send("Введите название книги: ".encode())
                            name = client_socket.recv(1024).decode().strip()
                            validate_regex("name", name)
                            break
                        except ValueError as error:
                            client_socket.send(f"Неверный ввод: {error}\n".encode())
                    # authors
                    while True:
                        try:
                            client_socket.send(
                                "Введите авторов (через запятую): ".encode()
                            )
                            authors = client_socket.recv(1024).decode().strip()
                            validate_regex("authors", authors)
                            break
                        except ValueError as error:
                            client_socket.send(f"Неверный ввод: {error}\n".encode())
                    # genres
                    while True:
                        try:
                            client_socket.send(
                                "Введите жанр (через запятую): ".encode()
                            )
                            genres = client_socket.recv(1024).decode().strip()
                            validate_regex("genres", genres)
                            break
                        except ValueError as error:
                            client_socket.send(f"Неверный ввод: {error}\n".encode())
                    # year
                    while True:
                        try:
                            client_socket.send("Введите год издания: ".encode())
                            year = client_socket.recv(1024).decode().strip()
                            validate_year(year)
                            break
                        except ValueError as error:
                            client_socket.send(f"Неверный ввод: {error}\n".encode())
                    # width
                    while True:
                        try:
                            client_socket.send("Введите ширину книги (мм): ".encode())
                            width = client_socket.recv(1024).decode().strip()
                            validate_width(width)
                            break
                        except ValueError as error:
                            client_socket.send(f"Неверный ввод: {error}\n".encode())
                    # height
                    while True:
                        try:
                            client_socket.send("Введите высоту книги (мм): ".encode())
                            height = client_socket.recv(1024).decode().strip()
                            validate_height(height)
                            break
                        except ValueError as error:
                            client_socket.send(f"Неверный ввод: {error}\n".encode())
                    # book_type
                    while True:
                        try:
                            client_socket.send(
                                "Введите тип обложки (мягкий/твердый): ".encode()
                            )
                            book_type = client_socket.recv(1024).decode().strip()
                            validate_regex("book_type", book_type)
                            break
                        except ValueError as error:
                            client_socket.send(f"Неверный ввод: {error}\n".encode())
                    # source
                    while True:
                        try:
                            client_socket.send(
                                "Введите источник (покупка/подарок/наследство): ".encode()
                            )
                            source = client_socket.recv(1024).decode().strip()
                            validate_regex("source", source)
                            break
                        except ValueError as error:
                            client_socket.send(f"Неверный ввод: {error}\n".encode())
                    # date_added
                    while True:
                        try:
                            client_socket.send(
                                "Введите дату добавления (DD-MM-YYYY): ".encode()
                            )
                            date_added = client_socket.recv(1024).decode().strip()
                            validate_date_added(date_added, year)
                            break
                        except ValueError as error:
                            client_socket.send(f"Неверный ввод: {error}\n".encode())
                    # date_read
                    while True:
                        try:
                            client_socket.send(
                                "Введите дату прочтения (DD-MM-YYYY): ".encode()
                            )
                            date_read = client_socket.recv(1024).decode().strip()
                            validate_date_read(date_read, date_added)
                            break
                        except ValueError as error:
                            client_socket.send(f"Неверный ввод: {error}\n".encode())
                    # rating
                    while True:
                        try:
                            client_socket.send(
                                "Введите рейтинг (X/10) - комментарий: ".encode()
                            )
                            rating = client_socket.recv(1024).decode().strip()
                            validate_regex("rating", rating)
                            break
                        except ValueError as error:
                            client_socket.send(f"Неверный ввод: {error}\n".encode())
                    book = {
                        "name": name,
                        "authors": authors,
                        "genres": genres,
                        "year": year,
                        "width": width,
                        "height": height,
                        "book_type": book_type,
                        "source": source,
                        "date_added": date_added,
                        "date_read": date_read,
                        "rating": rating,
                    }
                    response = add_book(book)
                    client_socket.send(response.encode())
                    break
                elif choice_add == "1.3":
                    break
                else:
                    client_socket.send("Неверный выбор. Попробуйте снова.".encode())

        elif choice == "2":
            response = print_all_books()
            client_socket.send(response.encode())

        elif choice == "3":
            client_socket.send(
                "Введите поле для поиска (id/name/authors/genres/year/width/height/book_type/source/date_added/date_read/rating): ".encode()
            )
            search_field = client_socket.recv(1024).decode().strip().lower()
            client_socket.send("Введите поисковый запрос: ".encode())
            search_value = client_socket.recv(1024).decode().strip().lower()
            results = print_books(search_books(search_field, search_value))
            client_socket.send(str(results).encode())

        elif choice == "4":
            client_socket.send(
                "Введите поле для поиска (id/name/authors/genres/year/width/height/book_type/source/date_added/date_read/rating): ".encode()
            )
            search_field = client_socket.recv(1024).decode().strip().lower()
            client_socket.send("Введите поисковый запрос: ".encode())
            search_value = client_socket.recv(1024).decode().strip().lower()
            client_socket.send(
                "Введите поле для обновления (id/name/authors/genres/year/width/height/book_type/source/date_added/date_read/rating): ".encode()
            )
            update_field = client_socket.recv(1024).decode().strip()
            client_socket.send("Введите обновленное значение: ".encode())
            update_value = client_socket.recv(1024).decode().strip()
            response = update_books(
                client_socket, search_field, search_value, update_field, update_value
            )
            client_socket.send(response.encode())

        elif choice == "5":
            client_socket.send(
                "Введите поле для поиска (id/name/authors/genres/year/width/height/book_type/source/date_added/date_read/rating): ".encode()
            )
            search_field = client_socket.recv(1024).decode().strip().lower()
            client_socket.send("Введите поисковый запрос: ".encode())
            search_value = client_socket.recv(1024).decode().strip().lower()
            response = delete_books(client_socket, search_field, search_value)
            client_socket.send(response.encode())

        elif choice == "6":
            client_socket.send("Выход из программы.".encode())
            break

        else:
            client_socket.send("Неверный выбор. Попробуйте снова.".encode())


def start_server(host="127.0.0.1", port=9978):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"Сервер запущен на {host}:{port}")

    while True:
        client_socket, addr = server.accept()
        print(f"Подключен к {addr}")
        handle_client(client_socket)
        client_socket.close()


if __name__ == "__main__":
    start_server()
