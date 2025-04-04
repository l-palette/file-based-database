import logging
from faker import Faker
import random
import datetime
from validate import (
    validate_name,
    validate_authors,
    validate_genres,
    validate_year,
    validate_width,
    validate_height,
    validate_date_added,
    validate_date_read,
    validate_rating,
)
from main import Book, HomeLibrary

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

fake = Faker("ru_RU")


def authors_set():
    authors = set()
    while len(authors) < 100:
        authors.add(fake.name())
    return authors


authors_list = list(authors_set())


def generate_name():
    max_attempts = 10
    attempts = 0
    while attempts < max_attempts:
        name = fake.sentence(nb_words=random.randint(1, 5)).rstrip(".")
        try:
            validate_name(name)
            logging.info(f"Generated valid name: {name}")
            return name
        except ValueError:
            logging.warning(f"Invalid name generated: {name}")
            attempts += 1
    logging.error("Failed to generate a valid name after multiple attempts.")
    raise ValueError("Failed to generate a valid name after multiple attempts.")


def generate_authors():
    max_attempts = 10
    attempts = 0
    while attempts < max_attempts:
        authors = ",".join(random.sample(authors_list, k=random.randint(1, 3)))
        try:
            validate_authors(authors)
            logging.info(f"Generated valid authors: {authors}")
            return authors
        except ValueError:
            logging.warning(f"Invalid authors generated: {authors}")
            attempts += 1
    logging.error("Failed to generate valid authors after multiple attempts.")
    raise ValueError("Failed to generate valid authors after multiple attempts.")


def generate_genres():
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
        "Супергерои",
        "Классика",
        "Современная проза",
        "Философия",
        "Психология",
        "Социальная фантастика",
        "Киберпанк",
        "Постапокалипсис",
        "Мифология",
        "Спорт",
        "Кулинария",
        "Техническая литература",
        "Автобиография",
        "Справочная литература",
    ]
    max_attempts = 10
    attempts = 0
    while attempts < max_attempts:
        genres = ",".join(random.sample(genres_list, k=random.randint(1, 3)))
        try:
            validate_genres(genres)
            logging.info(f"Generated valid genres: {genres}")
            return genres
        except ValueError:
            logging.warning(f"Invalid genres generated: {genres}")
            attempts += 1
    logging.error("Failed to generate valid genres after multiple attempts.")
    raise ValueError("Failed to generate valid genres after multiple attempts.")


def generate_year():
    max_attempts = 10
    attempts = 0
    while attempts < max_attempts:
        year = str(random.randint(1000, 2023))
        try:
            validate_year(year)
            logging.info(f"Generated valid year: {year}")
            return year
        except ValueError:
            logging.warning(f"Invalid year generated: {year}")
            attempts += 1
    logging.error("Failed to generate a valid year after multiple attempts.")
    raise ValueError("Failed to generate a valid year after multiple attempts.")


def generate_width():
    max_attempts = 10
    attempts = 0
    while attempts < max_attempts:
        width = round(random.uniform(10.0, 200.0), 1)
        try:
            validate_width(width)
            logging.info(f"Generated valid width: {width}")
            return width
        except ValueError:
            logging.warning(f"Invalid width generated: {width}")
            attempts += 1
    logging.error("Failed to generate a valid width after multiple attempts.")
    raise ValueError("Failed to generate a valid width after multiple attempts.")


def generate_height():
    max_attempts = 10
    attempts = 0
    while attempts < max_attempts:
        height = round(random.uniform(10.0, 200.0), 1)
        try:
            validate_height(height)
            logging.info(f"Generated valid height: {height}")
            return height
        except ValueError:
            logging.warning(f"Invalid height generated: {height}")
            attempts += 1
    logging.error("Failed to generate a valid height after multiple attempts.")
    raise ValueError("Failed to generate a valid height after multiple attempts.")


def generate_book_type():
    book_type = random.choice(["мягкий", "твердый"])
    logging.info(f"Generated book type: {book_type}")
    return book_type


def generate_source():
    source = random.choice(["покупка", "подарок", "наследство"])
    logging.info(f"Generated source: {source}")
    return source


def generate_date_added(year):
    start_date = datetime.datetime(int(year), 1, 1)
    max_attempts = 10
    attempts = 0
    while attempts < max_attempts:
        date_added = str(
            fake.date_between(start_date=start_date, end_date="today").strftime(
                "%d-%m-%Y"
            )
        )
        try:
            validate_date_added(date_added, year)
            logging.info(f"Generated valid date added: {date_added}")
            return date_added
        except ValueError:
            logging.warning(f"Invalid date added generated: {date_added}")
            attempts += 1
    logging.error("Failed to generate a valid date added after multiple attempts.")
    raise ValueError("Failed to generate a valid date added after multiple attempts.")


def generate_date_read(date_added):
    date_added_dt = datetime.datetime.strptime(date_added, "%d-%m-%Y")
    max_attempts = 10
    attempts = 0
    while attempts < max_attempts:
        date_read = str(
            fake.date_between(start_date=date_added_dt, end_date="today").strftime(
                "%d-%m-%Y"
            )
        )
        try:
            validate_date_read(date_read, date_added)
            logging.info(f"Generated valid date read: {date_read}")
            return date_read
        except ValueError:
            logging.warning(f"Invalid date read generated: {date_read}")
            attempts += 1
    logging.error("Failed to generate a valid date read after multiple attempts.")
    raise ValueError("Failed to generate a valid date read after multiple attempts.")


def generate_rating():
    max_attempts = 10
    attempts = 0
    while attempts < max_attempts:
        rating_value = random.randint(1, 10)
        description = fake.sentence(
            nb_words=random.randint(3, 10), variable_nb_words=True
        )
        rating = f"{rating_value}/10 - {description}"
        try:
            validate_rating(rating)
            logging.info(f"Generated valid rating: {rating}")
            return rating
        except ValueError:
            logging.warning(f"Invalid rating generated: {rating}")
            attempts += 1
    logging.error("Failed to generate a valid rating after multiple attempts.")
    raise ValueError("Failed to generate a valid rating after multiple attempts.")


def generate_book():
    while True:
        try:
            name = generate_name()
            authors = generate_authors()
            genres = generate_genres()
            year = generate_year()
            width = generate_width()
            height = generate_height()
            book_type = generate_book_type()
            source = generate_source()
            date_added = generate_date_added(year)
            date_read = generate_date_read(date_added)
            rating = generate_rating()

            book = Book(
                name=name,
                authors=authors,
                genres=genres,
                year=year,
                width=width,
                height=height,
                book_type=book_type,
                source=source,
                date_added=date_added,
                date_read=date_read,
                rating=rating,
            )

            logging.info("Book generated.")
            return book
        except Exception as e:
            logging.error(f"An error occurred while generating data: {e}")
            continue


books = set()
library = HomeLibrary()
while len(books) < 10000:
    book = generate_book()
    if book not in books:
        books.add(book)
        library.add_book(book)
        library.save_books_to_file()
