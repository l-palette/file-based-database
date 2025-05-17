from pathlib import Path
from typing import List
from faker import Faker
import random
import logging
import re
import time
import socket
import os
from contextlib import contextmanager
import shutil
from datetime import datetime
import threading

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
    "name": r"(?!.*([\s])\1)[А-Яа-яЁёA-Za-z0-9\s]{1,100}",
    "authors": r"(?!.*([\s,])\1)[А-Яа-яЁёA-Za-z\s,]{1,130}",
    "genres": r"^(?!.*([\s,])\1)[А-Яа-яЁёA-Za-z\s,]{1,100}",
    "year": r"\d{4}",
    "width": r"\d+(\.\d+)?",
    "height": r"\d+(\.\d+)?",
    "book_type": r"мягкий|твердый",
    "source": r"покупка|подарок|наследство",
    "date_added": r"\d{2}-\d{2}-\d{4}",
    "date_read": r"\d{2}-\d{2}-\d{4}",
    "rating": r"([1-9]|10)/10 - [А-Яа-яЁёA-Za-z0-9\s\,\.\!\?]{1,200}",
}

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

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s"
)

fake = Faker("ru_RU")

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


@contextmanager
def file_lock(filename, timeout=0.1):
    lockfile = Path(f"{filename}.lock")
    thread_name = threading.current_thread().name
    logging.info(f"[{thread_name}] Пытаюсь захватить блокировку...")

    start_time = time.time()
    while True:
        try:
            lockfile.touch(exist_ok=False)
            logging.info(f"[{thread_name}] ✅ Захватил блокировку!")
            break
        except FileExistsError:
            if time.time() - start_time > timeout:
                logging.error(f"[{thread_name}] ❌ Не успел за {timeout} сек!")
                raise TimeoutError("Не удалось захватить блокировку")
            time.sleep(0.01)

    try:
        yield
    finally:
        lockfile.unlink()
        logging.info(f"[{thread_name}] 🔓 Освободил блокировку")


def create_backup():
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    backups = list(backup_dir.glob("library_backup_*.txt"))
    if len(backups) >= 5:
        oldest_backup = min(backups, key=os.path.getmtime)
        oldest_backup.unlink()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"library_backup_{timestamp}.txt"
    shutil.copy2(FILENAME, backup_file)
    logging.info(f"Создана резервная копия: {backup_file}")


def recover_from_backup():
    backup_dir = Path("backups")
    if not backup_dir.exists():
        return False
    
    backups = sorted(backup_dir.glob("library_backup_*.txt"), key=os.path.getmtime)
    if backups:
        latest_backup = backups[-1]
        shutil.copy2(latest_backup, FILENAME)
        logging.info(f"Восстановлено из резервной копии: {latest_backup}")
        return True
    return False


def validate_regex(field: str, value) -> None:
    if not re.fullmatch(regex_schema[field], str(value)):
        raise ValueError(
            f"Значение {value} не соответствует регулярному выражению {regex_schema[field]}"
        )


def validate_year(year) -> None:
    validate_regex("year", year)
    if int(year) > datetime.now().year:
        raise ValueError("Год издания не может быть больше текущего года")
    if int(year) < 1500:
        raise ValueError("Год издания не может меньше 1500")



def validate_width(width) -> None:
    validate_regex("width", width)
    if float(width) > 1000:
        raise ValueError("Ширина книги не может быть больше 1 метра")
    elif float(width) <= 0:
        raise ValueError("Ширина книги не может быть отрицательной или равна 0")


def validate_height(height) -> None:
    validate_regex("height", height)
    if float(height) > 1000:
        raise ValueError("Высота книги не может быть больше 1 метра")
    elif float(height) <= 0:
        raise ValueError("Высота книги не может быть отрицательной или равна 0")


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


def authors_set():
    authors = set()
    while len(authors) < 100:
        authors.add(fake.name())
    return authors


# SINGLE BOOK
def generate_valid_book(authors_list, genres_list) -> dict:
    name = fake.sentence(nb_words=random.randint(1, 5)).rstrip(".")
    authors = ",".join(random.sample(authors_list, k=random.randint(1, 3)))
    genres = ",".join(random.sample(genres_list, k=random.randint(1, 4)))
    year = str(random.randint(1500, 2025))
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
    """Генерация ID"""
    if not Path(FILENAME).exists():
        return 1

    with open(FILENAME, "r", encoding="utf-8") as file:
        lines = file.readlines()
        if lines:
            last_book = line_to_dict(lines[-1])
            id = int(last_book["id"]) + 1
            return id
    return 1


def is_unique_book(book: dict) -> bool:
    """Проверка на уникальность книги"""
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
    """ Операция добавление книги - добавление ID + проверка на уникальность"""
    create_backup()
    book_id = get_next_id()
    book["id"] = book_id
    try:
        with file_lock(FILENAME):
            if is_unique_book(book):
                with open(FILENAME, ("a")) as file:
                    time.sleep(0.3)
                    file.write(dict_to_line(book) + "\n")
                res = f"Добавлена книга: {book['name']} (ID: {book_id})"
                return res
            else:
                res = f"Книга уже добавлена: {book['name']}, написанная {book['authors']}"
                return res
    except TimeoutError:
        return "Ошибка: не удалось выполнить обновление - система занята, попробуйте позже"


# MULTIPLE BOOKS
def modify_books_file(new_books: List[dict] = None, update=False) -> str:
    """
    Редактируем файл базы данных для операций удаления и редактирования
    Функция обеспечивает атомарность операций - изменения либо применяются полностью, либо не применяются вообще.
    """
    res = ""
    temp_filename = Path("temp.txt")
    found = False
    original_filename = Path(FILENAME)
    try:
        with file_lock(original_filename):
            with original_filename.open("r") as file, temp_filename.open("w") as temp_file:
                time.sleep(0.3)
                for line in file:
                    book = line_to_dict(line)
                    # Проверяем, есть ли книга в списке для обновления
                    for new_book in new_books:
                        if book["id"] == new_book["id"]:
                            found = True

                            # Обновляем поля книги
                            if update:
                                book.update(new_book)
                                temp_file.write(dict_to_line(book) + "\n")
                                res += (
                                    f"Обновлена книга: {book['name']} (ID: {book['id']})\n"
                                )
                                break
                            else:
                                res += f"Удалена книга: {book['name']} (ID: {book['id']})\n"
                                break
                    else:
                        temp_file.write(line)

            if found:
                original_filename.unlink()
                temp_filename.rename(original_filename)
            else:
                temp_filename.unlink()

        return res
    except TimeoutError:
        return "Ошибка: не удалось выполнить обновление - система занята, попробуйте позже"


def update_books(client_socket, field: str, value: str, new_field, new_value) -> str:
    """ Обновление поля в строке"""
    books = search_books(field, value)
    for book in books:
        book[new_field] = new_value
    results = "Обновленные книги:\n"
    results += print_books(books)
    if not books:
        return ""
    client_socket.send(str(results).encode())


    client_socket.send("Обновить? (д/н): ".encode())
    choice = client_socket.recv(1024).decode().strip().lower()
    while choice not in ("д", "н", "y", "n"):
        client_socket.send("Некорректный ввод\n".encode())
        client_socket.send("Обновить? (д/н): ".encode())
        choice = client_socket.recv(1024).decode().strip().lower()
    if choice == "д" or choice == "y":
        return modify_books_file(books, True)
    return ""


def delete_books(client_socket, field: str, value: str) -> str:
    """
    Проходит по файлу, ищет в поле field совпадения с value.
    Если находит, то записывает все строки до нее и после нее в файл temp.txt,
    затем удаляет файл home_library.txt и переименовывает temp.txt в home_library.txt.
    """
    books = search_books(field, value)
    results = "Найденные книги:\n"
    results += print_books(books)
    client_socket.send(str(results).encode())
    if not books:
        return ""
    client_socket.send("Удалить? (д/н): \n".encode())
    choice = client_socket.recv(1024).decode().strip().lower()
    while choice not in ("д", "н", "y", "n"):
        client_socket.send("Некорректный ввод\n".encode())
        client_socket.send("Удалить? (д/н): ".encode())
        choice = client_socket.recv(1024).decode().strip().lower()
    if choice == "д" or choice == "y":
        return modify_books_file(books)
    return ""


def print_all_books():
    """ Вывести книги"""
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
    """ Вывести книгу"""
    if not books:
        res = "Нет книг для отображения.\n"
        return res
    res = ""
    res += f"Отображено {len(books)} книг(и):\n"
    for book in books:
        try:
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
        except KeyError:
            res += (f"\tНазвание: {book['name']},\n"
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


def search_books(field: str, value: str) -> List[dict]:
    """
    Ищет в поле field совпадения c value, возвращает список словарей книг
    """
    result = []
    with open(FILENAME, "r") as file:
        for line in file:
            book = line_to_dict(line)
            value_book = book[field]
            if field in ["year", "width", "height"]:
                if book[field] == value:
                    result.append(book)
            elif field == "id":
                if book[field] == value:
                    return [book]
            else:
                if str(value).lower() in value_book.lower():
                    result.append(book)
                    
    return result


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

authors_list = list(authors_set())


def handle_client(client_socket, addr):
    """ Меню ввода команд"""
    try:
        print(f"Подключен клиент {addr}")
        client_socket.sendall(library.encode())
        client_socket.sendall("Добро пожаловать в библиотеку!\n".encode())
        while True:
            client_socket.send(display_menu().encode())
            choice = client_socket.recv(1024).decode().strip()

            if choice == "1":
                while True:
                    client_socket.send(display_add_menu().encode())
                    choice_add = client_socket.recv(1024).decode().strip()
                    if choice_add == "1.1" or choice_add == "1" or choice_add == "1.1.":
                        book = generate_valid_book(authors_list, genres_list)
                        client_socket.send(print_books([book]).encode())
                        client_socket.send("Добавить? (д/н): \n".encode())
                        choice = client_socket.recv(1024).decode().strip().lower()
                        while choice not in ("д", "н", "y", "n"):
                            client_socket.send("Некорректный ввод!\n".encode())
                            client_socket.send("Добавить? (д/н): \n".encode())
                            choice = client_socket.recv(1024).decode().strip()
                        if choice == "д" or choice == "y":
                            logging.info(f"Добавление книги {book['name']} начато клиентом {addr}")
                            response = add_book(book)
                            logging.info(f"Добавление книги {book['name']} завершено клиентом {addr}")
                            client_socket.send(response.encode())
                            break
                    elif choice_add == "1.2" or choice_add == "2" or choice_add == "1.2.":
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
                        logging.info(f"Добавление книги {book['name']} начато клиентом {addr}")
                        response = add_book(book)
                        logging.info(f"Добавление книги {book['name']} завершено клиентом {addr}")
                        client_socket.send(response.encode())
                        break
                    elif choice_add == "1.3" or choice_add == "3" or choice_add == "1.3.":
                        break
                    else:
                        client_socket.send("Неверный выбор. Попробуйте снова.".encode())

            elif choice == "2":
                logging.info("Вывод книг начат")
                response = print_all_books()
                logging.info("Вывод книг завершен")
                client_socket.send(response.encode())

            elif choice == "3":
                client_socket.send(
                    "Введите поле для поиска (id/name/authors/genres/year/width/height/book_type/source/date_added/date_read/rating): ".encode()
                )
                search_field = client_socket.recv(1024).decode().strip().lower()
                while search_field not in HEADERS:
                    client_socket.send("Некорректный ввод!\n".encode())
                    client_socket.send(
                    "Введите поле для поиска (id/name/authors/genres/year/width/height/book_type/source/date_added/date_read/rating): ".encode()
                    )
                    search_field = client_socket.recv(1024).decode().strip().lower()
                client_socket.send("Введите поисковый запрос: ".encode())
                search_value = client_socket.recv(1024).decode().strip().lower()
                logging.info("Поиск книг начат")
                results = print_books(search_books(search_field, search_value))
                logging.info("Поиск книг завершен")
                client_socket.send(str(results).encode())

            elif choice == "4":
                client_socket.send(
                    "Введите поле для поиска (id/name/authors/genres/year/width/height/book_type/source/date_added/date_read/rating): ".encode()
                )
                search_field = client_socket.recv(1024).decode().strip().lower()
                while search_field not in HEADERS:
                    client_socket.send("Некорректный ввод!\n".encode())
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
                while update_field not in HEADERS:
                    client_socket.send("Некорректный ввод!\n".encode())
                    client_socket.send(
                    "Введите поле для поиска (id/name/authors/genres/year/width/height/book_type/source/date_added/date_read/rating): ".encode()
                    )
                    update_field = client_socket.recv(1024).decode().strip().lower()
                if update_field == "name":
                    while True:
                        try:
                            client_socket.send("Введите название книги: ".encode())
                            name = client_socket.recv(1024).decode().strip()
                            validate_regex("name", name)
                            response = update_books(
                                client_socket, search_field, search_value, update_field, name
                            )
                            client_socket.send(response.encode())
                            break
                        except ValueError as error:
                            client_socket.send(f"Неверный ввод: {error}\n".encode())
                elif update_field == "authors":
                    while True:
                        try:
                            client_socket.send(
                                "Введите авторов (через запятую): ".encode()
                            )
                            authors = client_socket.recv(1024).decode().strip()
                            validate_regex("authors", authors)
                            response = update_books(
                                client_socket, search_field, search_value, update_field, authors
                            )
                            client_socket.send(response.encode())
                            break
                        except ValueError as error:
                            client_socket.send(f"Неверный ввод: {error}\n".encode())
                elif update_field == "genres":
                    while True:
                        try:
                            client_socket.send(
                                "Введите жанр (через запятую): ".encode()
                            )
                            genres = client_socket.recv(1024).decode().strip()
                            validate_regex("genres", genres)
                            response = update_books(
                                client_socket, search_field, search_value, update_field, genres
                            )
                            client_socket.send(response.encode())
                            break
                        except ValueError as error:
                            client_socket.send(f"Неверный ввод: {error}\n".encode())
                elif update_field == "year":
                    while True:
                        try:
                            client_socket.send("Введите год издания: ".encode())
                            year = client_socket.recv(1024).decode().strip()
                            validate_year(year)
                            response = update_books(
                                client_socket, search_field, search_value, update_field, year
                            )
                            client_socket.send(response.encode())
                            break
                        except ValueError as error:
                            client_socket.send(f"Неверный ввод: {error}\n".encode())
                elif update_field == "width":
                    while True:
                        try:
                            client_socket.send("Введите ширину книги (мм): ".encode())
                            width = client_socket.recv(1024).decode().strip()
                            validate_width(width)
                            response = update_books(
                                client_socket, search_field, search_value, update_field, width
                            )
                            client_socket.send(response.encode())
                            break
                        except ValueError as error:
                            client_socket.send(f"Неверный ввод: {error}\n".encode())
                elif update_field == "height":
                    while True:
                        try:
                            client_socket.send("Введите высоту книги (мм): ".encode())
                            height = client_socket.recv(1024).decode().strip()
                            validate_height(height)
                            response = update_books(
                                client_socket, search_field, search_value, update_field, height
                            )
                            client_socket.send(response.encode())
                            break
                        except ValueError as error:
                            client_socket.send(f"Неверный ввод: {error}\n".encode())
                elif update_field == "book_type":
                    while True:
                        try:
                            client_socket.send(
                                "Введите тип обложки (мягкий/твердый): ".encode()
                            )
                            book_type = client_socket.recv(1024).decode().strip()
                            validate_regex("book_type", book_type)
                            response = update_books(
                                client_socket, search_field, search_value, update_field, book_type
                            )
                            client_socket.send(response.encode())
                            break
                        except ValueError as error:
                            client_socket.send(f"Неверный ввод: {error}\n".encode())
                elif update_field == "source":
                    while True:
                        try:
                            client_socket.send(
                                "Введите источник (покупка/подарок/наследство): ".encode()
                            )
                            source = client_socket.recv(1024).decode().strip()
                            validate_regex("source", source)
                            response = update_books(
                                client_socket, search_field, search_value, update_field, source
                            )
                            client_socket.send(response.encode())
                            break
                        except ValueError as error:
                            client_socket.send(f"Неверный ввод: {error}\n".encode())
                elif update_field == "date_added":
                    while True:
                        try:
                            client_socket.send(
                                "Введите дату добавления (DD-MM-YYYY): ".encode()
                            )
                            date_added = client_socket.recv(1024).decode().strip()
                            validate_date_added(date_added, year)
                            response = update_books(
                                client_socket, search_field, search_value, update_field, date_added
                            )
                            client_socket.send(response.encode())
                            break
                        except ValueError as error:
                            client_socket.send(f"Неверный ввод: {error}\n".encode())
                elif update_field == "date_read":
                    while True:
                        try:
                            client_socket.send(
                                "Введите дату прочтения (DD-MM-YYYY): ".encode()
                            )
                            date_read = client_socket.recv(1024).decode().strip()
                            validate_date_read(date_read, date_added)
                            response = update_books(
                                client_socket, search_field, search_value, update_field, date_read
                            )
                            client_socket.send(response.encode())
                            break
                        except ValueError as error:
                            client_socket.send(f"Неверный ввод: {error}\n".encode())
                elif update_field == "rating":
                    while True:
                        try:
                            client_socket.send(
                                "Введите рейтинг (X/10) - комментарий: ".encode()
                            )
                            rating = client_socket.recv(1024).decode().strip()
                            validate_regex("rating", rating)
                            logging.info(f"Обновление книг начато клиентом {addr}")
                            response = update_books(
                                client_socket, search_field, search_value, update_field, rating
                            )
                            logging.info(f"Обновление книг завершено клиентом {addr}")
                            client_socket.send(response.encode())
                            break
                        except ValueError as error:
                            client_socket.send(f"Неверный ввод: {error}\n".encode())

            elif choice == "5":
                client_socket.send(
                    "Введите поле для поиска (id/name/authors/genres/year/width/height/book_type/source/date_added/date_read/rating): ".encode()
                )
                search_field = client_socket.recv(1024).decode().strip().lower()
                while search_field not in HEADERS:
                    client_socket.send("Некорректный ввод!\n".encode())
                    client_socket.send(
                    "Введите поле для поиска (id/name/authors/genres/year/width/height/book_type/source/date_added/date_read/rating): ".encode()
                    )
                    search_field = client_socket.recv(1024).decode().strip().lower()
                client_socket.send("Введите поисковый запрос: ".encode())
                search_value = client_socket.recv(1024).decode().strip().lower()
                logging.info(f"Удаление книг начато клиентом {addr}")
                response = delete_books(client_socket, search_field, search_value)
                logging.info(f"Удаление книг завершено клиентом {addr}")
                client_socket.send(response.encode())

            elif choice == "6":
                client_socket.send("Выход из программы.".encode())
                break

            else:
                client_socket.send("Неверный выбор. Попробуйте снова.".encode())
    except Exception as e:
        print(f"Ошибка с клиентом {addr}: {e}")
    finally:
        client_socket.close()
        print(f"Клиент {addr} отключен")


def start_server(host="127.0.0.1", port=9999):
    lock_files = list(Path().glob("*.lock"))

    if not lock_files:
        logging.info("Нет файлов блокировки")
    else:
        for lock_file in lock_files:
            lock_file.unlink()
        print(f"Удалено {len(lock_files)} файлов блокировки")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(10)
    print(f"Сервер запущен на {host}:{port}")

    while True:
        client_socket, addr = server.accept()
        client_thread = threading.Thread(
            target=handle_client,
            args=(client_socket, addr),
            daemon=True
        )
        client_thread.start()


if __name__ == "__main__":
    start_server()
