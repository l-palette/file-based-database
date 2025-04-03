from datetime import datetime
from typing import List, Optional
from validate import validate_name, validate_authors, validate_genres, validate_year, validate_width, validate_height, validate_book_type, validate_source, validate_date_added, validate_date_read, validate_rating, validate_search_field, validate_update_name, validate_update_field
from validate import validation_functions, db_schema

FILENAME = 'home_library.txt'
HEADERS = ['name', 'year', 'authors', 'genres', 'width', 'height', 'book_type', 'source', 'date_added', 'date_read', 'rating']

class Book:
    _last_id = 0

    def __init__(self, name: str, year: int, width: float, height: float, 
                 book_type: str, source: str, 
                 date_added: str, date_read: Optional[str], rating: str, 
                 authors: List[str], genres: List[str]) -> None:
        
        Book._last_id += 1
        self.id = Book._last_id
        self.name = name
        self.authors = ','.join(authors)
        self.genres = ','.join(genres) 
        self.year = year
        self.width = width
        self.height = height
        self.book_type = book_type
        self.source = source
        self.date_added = date_added
        self.date_read = date_read if date_read else None
        self.rating = rating if rating else None

        self.validate_data()

    def validate_data(self):
        validate_name(self.name)
        validate_authors(self.authors)
        validate_genres(self.genres)
        validate_year(self.year)
        validate_width(self.width)
        validate_height(self.height)
        validate_book_type(self.book_type)
        validate_source(self.source)
        validate_date_added(self.date_added, self.year)
        validate_date_read(self.date_read, self.date_added)
        validate_rating(self.rating)

class HomeLibrary:
    def __init__(self):
        self.books = []
        self.load_books_from_file()

    def add_book(self, book: Book) -> None:
        self.books.append(book)

    def select_books(self) -> List[str]:
        return [book.name for book in self.books]
    
    def search_books(self, field: str, value: str) -> List[str]:
        return [book.name for book in self.books if value in str(getattr(book, field, ''))]

    def delete_book(self, name: str) -> None:
        self.books = [book for book in self.books if book.name != name]

    def update_book(self, name: str, field: str, new_value: str) -> None:
        for book in self.books:
            if book.name == name:
                try:
                    setattr(book, field, new_value)
                    print(f"Книга '{name}' успешно обновлена.")
                except (ValueError, TypeError) as e:
                    print(f"Ошибка при обновлении книги: {e}")
                break

    def load_books_from_file(self):
        try:
            with open(FILENAME, 'r', encoding='utf-8') as file:
                for line in file:
                    data = line.strip().split('|')
                    if len(data) == len(HEADERS):
                        name, year, authors, genres, width, height, book_type, source, date_added, date_read, rating = data
                        book = Book(
                            name=name,
                            authors=authors.split(","),
                            genres=genres.split(","),
                            year=int(year),
                            width=float(width),
                            height=float(height),
                            book_type=book_type,
                            source=source,
                            date_added=date_added,
                            date_read=date_read if date_read else None,
                            rating=rating if rating else None,
                        )
                        self.add_book(book)
        except FileNotFoundError:
            print("Файл не найден, создается новая библиотека.")
        except Exception as e:
            print(f"Ошибка при загрузке книг: {e}")

    def save_books_to_file(self):
        with open(FILENAME, 'w', encoding='utf-8') as file:
            for book in self.books:
                file.write(f"{book.name}|{book.year}|{book.authors}|{book.genres}|{book.width}|{book.height}|{book.book_type}|{book.source}|{book.date_added}|{book.date_read}|{book.rating}\n")

def get_input(prompt, field, validation_method, extra_field=None):
    while True:
        value = input(prompt).strip()
        try:
            value = make_correct_type(value, db_schema[field]['type'])
            if validation_method:
                if extra_field:
                    validation_method(value, extra_field)
                else:
                    validation_method(value)
            return value
        except (ValueError, TypeError) as e:
            print(f"Ошибка: {e}")

def display_menu():
    print("\n--- Меню Библиотеки ---")
    print("1. Добавить книгу")
    print("2. Показать все книги")
    print("3. Искать книги")
    print("4. Обновить книгу")
    print("5. Удалить книгу")
    print("6. Выход")

def make_correct_type(value, expected_type):
    if not isinstance(value, expected_type):
        value = expected_type(value)
    return value

def main():
    library = HomeLibrary()
    
    while True:
        display_menu()
        choice = input("Выберите опцию (1-6): ")

        if choice == '1':
            try:
                name = get_input("Введите название книги: ", 'name', validate_name)
                authors = get_input("Введите авторов (через запятую): ", 'authors', validate_authors)
                genres = get_input("Введите жанры (через запятую): ", 'genres', validate_genres)
                year = int(get_input("Введите год издания: ", 'year', validate_year))
                width = float(get_input("Введите ширину книги (в мм, например 200.0): ", 'width', validate_width))
                height = float(get_input("Введите высоту книги (в мм, например 200.0): ", 'height', validate_height))
                book_type = get_input("Введите тип книги (мягкий/твердый): ", 'book_type', validate_book_type)
                source = get_input("Введите источник (покупка/подарок/наследство): ", 'source', validate_source)
                date_added = get_input("Введите дату добавления (дд-мм-гггг): ", 'date_added', validate_date_added, year)
                date_read = get_input("Введите дату чтения (дд-мм-гггг, оставьте пустым, если не читали): ", 'date_read', validate_date_read, date_added)
                rating = get_input("Введите оценку книги (n/10 - комментарий, оставьте пустым, если не читали): ", 'rating', validate_rating)

                book = Book(
                    name=name,
                    authors=authors.split(","),
                    genres=genres.split(","),
                    year=year,
                    width=width,
                    height=height,
                    book_type=book_type,
                    source=source,
                    date_added=date_added,
                    date_read=date_read,
                    rating=rating,
                )

                library.add_book(book)
                print("Книга успешно добавлена:", book.name)
            except (ValueError, TypeError) as e:
                print("Ошибка при добавлении книги:", e)

        elif choice == '2':
            print("Книги в библиотеке:", library.select_books())

        elif choice == '3':
            field = get_input("Введите поле для поиска (name/authors/genres): ", 'search_field', validate_search_field)
            value = get_input("Введите значение для поиска: ", field, validation_functions[field])
            results = library.search_books(field, value)
            print("Результаты поиска:", results)

        elif choice == '4':
            name = get_input("Введите название книги для обновления: ", 'update_name', validate_update_name, library)
            field = get_input("Введите поле для обновления (name/authors/genres/year/width/height/book_type/source/date_added/date_read/rating):", 'update_field', validate_update_field)
            new_value = get_input("Введите новое значение: ", field, validation_functions[field])
            library.update_book(name, field, new_value)

        elif choice == '5':
            name = get_input("Введите название книги для удаления: ", 'name', validate_update_name, library)
            library.delete_book(name)
            print("Книга удалена.")

        elif choice == '6':
            library.save_books_to_file()  # Сохраняем книги в файл перед выходом
            print("Выход из программы.")
            break

        else:
            print("Неверный выбор. Пожалуйста, выберите опцию от 1 до 6.")

if __name__ == "__main__":
    main()
