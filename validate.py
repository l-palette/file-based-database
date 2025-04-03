from datetime import datetime
import re
from typing import Optional, List, Literal

# Define the schema for validation
db_schema = {
    "name": {"type": str, "length": 51, "regex": r"[А-Яа-яЁёA-Za-z0-9\s]+"},
    "authors": {"type": str, "length": 51, "regex": r"[А-Яа-яЁёA-Za-z\s,]+"},
    "genres": {"type": str, "length": 71, "regex": r"[А-Яа-яЁёA-Za-z\s,]+"},
    "year": {"type": int, "length": 5, "regex": r"\d{4}"},
    "width": {"type": float, "length": 6, "regex": r"\d+\.\d+"},
    "height": {"type": float, "length": 6, "regex": r"\d+\.\d+"},
    "book_type": {"type": str, "length": 8, "regex": r"мягкий|твердый"},
    "source": {"type": str, "length": 11, "regex": r"покупка|подарок|наследство"},
    "date_added": {"type": str, "length": 11, "regex": r"\d{2}-\d{2}-\d{4}"},
    "date_read": {"type": Optional[str], "length": 11, "regex": r"\d{2}-\d{2}-\d{4}"},
    "rating": {"type": Optional[str], "length": 101, "regex": r"([1-9]|10)/10 - ."},
    "search_field": {"type": str, "length": 1000, "regex": r"authors|genres|name"},
    "update_name": {"type": str, "length": 1000, "regex": r".*"},
    "update_field": {
        "type": str,
        "length": 1000,
        "regex": r"name|year|authors|genres|width|height|book_type|source|date_added|date_read|rating",
    },
}


# Validation functions
def validate_field(field: str, value) -> None:
    if len(str(value)) > db_schema[field]["length"]:
        raise ValueError(f"Переменная {field} превышает лимит символов")
    if not re.match(db_schema[field]["regex"], str(value)):
        raise ValueError(f"Неверное значение для {field}: {value}")


def validate_name(name) -> None:
    validate_field("name", name)


def validate_authors(authors) -> None:
    validate_field("authors", authors)


def validate_genres(genres) -> None:
    validate_field("genres", genres)


def validate_year(year) -> None:
    validate_field("year", year)
    if int(year) > datetime.now().year:
        raise ValueError("Год издания не может быть больше текущего года")


def validate_width(width) -> None:
    validate_field("width", width)
    if float(width) > 1000:
        raise ValueError("Ширина книги не может быть больше 1 метра")
    elif float(width) < 0:
        raise ValueError("Ширина книги не может быть отрицательной")


def validate_height(height) -> None:
    validate_field("height", height)
    if float(height) > 1000:
        raise ValueError("Высота книги не может быть больше 1 метра")
    elif float(height) < 0:
        raise ValueError("Высота книги не может быть отрицательной")


def validate_book_type(book_type) -> None:
    validate_field("book_type", book_type)


def validate_source(source) -> None:
    validate_field("source", source)


def validate_date_added(date_added, year) -> None:
    validate_field("date_added", date_added)
    date_added_datetime = datetime.strptime(date_added, "%d-%m-%Y")
    if date_added_datetime >= datetime.now():
        raise ValueError("Дата добавления не может быть позже текущей даты")
    if date_added_datetime.year < year:
        raise ValueError("Год добавления не может быть раньше года издания")


def validate_date_read(date_read, date_added) -> None:
    if date_read:
        validate_field("date_read", date_read)
        date_added_datetime = datetime.strptime(date_added, "%d-%m-%Y")
        date_read_datetime = datetime.strptime(date_read, "%d-%m-%Y")
        if date_read_datetime < date_added_datetime:
            raise ValueError("Дата чтения не может быть раньше даты добавления")


def validate_rating(rating) -> None:
    if rating:
        validate_field("rating", rating)


def validate_search_field(search_field) -> None:
    validate_field("search_field", search_field)


def validate_update_name(update_name, library) -> None:
    validate_field("update_name", update_name)
    if update_name not in library.select_books():
        raise ValueError(f'Книга с названием "{update_name}" не найдена в библиотеке.')


def validate_update_field(update_field) -> None:
    validate_field("update_field", update_field)


validation_functions = {
    "name": validate_name,
    "authors": validate_authors,
    "genres": validate_genres,
    "year": validate_year,
    "width": validate_width,
    "height": validate_height,
    "book_type": validate_book_type,
    "source": validate_source,
    "date_added": validate_date_added,
    "date_read": validate_date_read,
    "rating": validate_rating,
    "search_field": validate_search_field,
    "update_name": validate_update_name,
    "update_field": validate_update_field,
}
