"""
Консольний асистент бот, який зберігає та управляє контактами 
у вигляді адресної книги за допомогою вбудованих класів.

Цей модуль надає класи для створення контактів, управління ними та зберігання
інформації в зручному форматі.
"""
from collections import UserDict
from typing import Optional, Dict
from datetime import datetime, date, timedelta
import pickle


class Field:
    """Базовий клас для всіх полів, що зберігають значення."""

    def __init__(self, value: str) -> None:
        self.value = value

    def __str__(self) -> str:
        return str(self.value)


class Name(Field):
    """Клас для зберігання імені контакту, наслідує від Field."""

    def __init__(self, name: str) -> None:
        super().__init__(name)


class Phone(Field):
    """Клас для зберігання номера телефону, наслідує від Field.
    Якщо номер телефону не пройшов перевірку на валідність, викликається виняток "ValueError"."""

    def __init__(self, phone: str) -> None:
        if len(phone) != 10 or not phone.isdigit():
            raise ValueError(f"Phone number {phone} is invalid")
        super().__init__(phone)


class Birthday(Field):
    """Клас для зберігання дати народження контакта у форматі date, наслідує від Field."""

    def __init__(self, value: str) -> None:
        try:
            datetime.strptime(value, "%d.%m.%Y").date()
            super().__init__(value)
        except ValueError as e:
            raise ValueError("Invalid date format. Use DD.MM.YYYY") from e


class Record:
    """Клас для зберігання контактної інформації, включаючи ім'я, 
    список телефонів та дату народження."""

    def __init__(self, name: str) -> None:
        self.name = Name(name)
        self.phones: list[Phone] = []
        self.birthday = None

    def add_phone(self, phone: str) -> None:
        """Додає новий номер телефону до запису."""
        for ph in self.phones:
            if ph.value == phone:
                raise ValueError("This phone is already exist.")
        self.phones.append(Phone(phone))

    def remove_phone(self, phone: str) -> None:
        """Видаляє номер телефону із запису, якщо він існує."""
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone: str, new_phone: str) -> None:
        """Редагує існуючий номер телефону на новий.
        Викликає ValueError, якщо старий номер не знайдено або новий номер не є валідним."""
        for index, p in enumerate(self.phones):
            if p.value == old_phone:
                new_phone_obj = Phone(new_phone)
                self.phones[index] = new_phone_obj
                return
        raise ValueError(f"Phone number {old_phone} not found.")

    def find_phone(self, phone: str) -> Optional[Phone]:
        """Шукає і повертає об'єкт Phone, якщо він існує, або None, якщо не знайдено."""
        return next((p for p in self.phones if p.value == phone), None)

    def add_birthday(self, birthday: str) -> None:
        """Додає дату народження до запису."""
        self.birthday = Birthday(birthday)

    def __str__(self) -> str:
        if self.birthday:
            return (
                f"Contact name: {self.name.value}, "
                f"phones: {'; '.join(p.value for p in self.phones)}, "
                f"birthday: {self.birthday.value}"
            )
        return (f"Contact name: {self.name.value}, "
                f"phones: {'; '.join(p.value for p in self.phones)}, "
                "birthday: None")


class AddressBook(UserDict):
    """Клас для зберігання контактів у вигляді словника, 
    де ключі — це імена, а значення — об'єкти Record."""

    data: Dict[str, Record]

    def add_record(self, record: Record) -> None:
        """Додає новий запис Record до адресної книги."""
        self.data[record.name.value] = record

    def find(self, name: str) -> Optional[Record]:
        """Шукає запис Record за ім'ям. Повертає Record або None, якщо запис не знайдено."""
        return self.data.get(name, None)

    def delete(self, name: str) -> None:
        """Видаляє запис Record за ім'ям, якщо він існує в адресній книзі."""
        self.data.pop(name, None)

    def show_birthday(self, name: str):
        """Знаходить дату народження за вказаним ім'ям."""
        if not name in self.data:
            raise KeyError(f"Contact {name} not found.")

        record = self.data.get(name)

        if record.birthday is None:
            return f"{name}'s birthday is not specified."

        return record.birthday.value

    def birthdays(self, days: int=7) -> list:
        """Збирає список найближчих днів народження користувачів у межах вказаних днів."""
        upcoming_birthdays = []
        today = date.today()

        for name, record in self.data.items():
            if record.birthday:
                birthday_obj = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
                birthday_this_year = birthday_obj.replace(year=today.year)
                days_until_birthday = (birthday_this_year - today).days

                if days_until_birthday < 0:
                    birthday_this_year = birthday_obj.replace(year=today.year + 1)
                    days_until_birthday = (birthday_this_year - today).days

                if 0 <= days_until_birthday <= days:
                    if birthday_this_year.weekday() == 5:
                        birthday_this_year += timedelta(days=2)
                    elif birthday_this_year.weekday() == 6:
                        birthday_this_year += timedelta(days=1)

                    upcoming_birthdays.append({
                        "name": name, 
                        "birthday": birthday_this_year.strftime("%d.%m.%Y")
                        })

        return upcoming_birthdays

    def __str__(self) -> str:
        """Повертає текстове представлення всіх записів у адресній книзі."""
        return '\n'.join(str(record) for record in self.data.values())


def parse_input(user_input: str) -> tuple:
    """Парсує команду, введену користувачем, і розділяє її на команду та аргументи."""
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

def input_error(func):
    """Декоратор, що перевіряє чи не виникає винятків при виклику функції, а саме: 
    ValueError, KeyError та IndexError."""
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except KeyError as e:
            return str(e)
        except IndexError as e:
            return str(e)
        except Exception as e:
            return f"Unexpected error: {str(e)}"

    return inner

@input_error
def add_contact(args, book: AddressBook) -> str:
    """Додає контакт до екземпляру класу AddressBook."""
    if len(args) == 0 or len(args) > 2:
        raise IndexError("Arguments must be: <Name> (optional <Phone>).")

    name = args[0]
    phone = args[1] if len(args) > 1 else None

    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book: AddressBook) -> str:
    """Змінює номер телефону контакта в екземплярі класу AddressBook."""
    if len(args) <= 2 or len(args) > 3:
        raise IndexError("Arguments must be: <Name> <Old phone> <New phone>.")

    name, old_phone, new_phone = args

    record = book.find(name)
    if record is None:
        raise KeyError(f"Contact: {name} does not exist.")

    record.edit_phone(old_phone, new_phone)
    return "Phone changed successfully."

@input_error
def delete_contact(args, book: AddressBook) -> str:
    """Видаляє контакт за ім'ям"""
    if len(args) != 1:
        raise IndexError("Arguments must be: <Name>.")

    name = args[0]

    record = book.find(name)
    if record is None:
        raise KeyError(f"Contact: {name} does not exist.")

    book.delete(name)
    return "Contact deleted successfully."

@input_error
def find_phones(args, book: AddressBook) -> str:
    """Знаходить всі номери вказаного контакта."""
    if len(args) == 0 or len(args) > 1:
        raise IndexError("Arguments must be: <Name>.")

    name = args[0]

    record = book.find(name)
    if record is None:
        raise KeyError(f"Contact: {name} does not exist.")

    if record.phones == []:
        return "No phones yet."
    phones = ', '.join(phone.value for phone in record.phones)
    return phones

@input_error
def show_all_contacts(book: AddressBook) -> AddressBook:
    """Виводить список контактів."""
    if book.data == {}:
        return "No contacts yet."
    return book

@input_error
def add_birthday(args, book: AddressBook) -> str:
    """Вказує день народження контакту."""
    if len(args) <= 1 or len(args) > 2:
        raise IndexError("Arguments must be: <Name> <Birthday>.")

    name, birthday = args

    record = book.find(name)
    message = "Birthday updated."
    if record is None:
        raise KeyError(f"Contact: {name} does not exist.")
    if not record.birthday:
        message = "Birthday added."
    record.add_birthday(birthday)
    return message

@input_error
def show_birthday(args, book: AddressBook) -> str:
    """Виводить день народження вказаного контакта."""
    if len(args) == 0 or len(args) > 1:
        raise IndexError("Arguments must be: <Name>.")

    name = args[0]

    return book.show_birthday(name)

@input_error
def birthdays(book: AddressBook) -> list:
    """Виводить дати привітання контактів, у яких день народження в найближчі 7 днів."""
    if book.birthdays() == []:
        return "No upcoming birthdays yet."
    return book.birthdays()


def save_data(book: AddressBook, filename="addressbook.pkl") -> None:
    """Зберігає адресну книгу у бінарний файл 'addressbook' з розширенням '.pkl'."""
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl") -> AddressBook:
    """Завантажує дані адресної книги з бінарного файлу 'addressbook' з розширенням '.pkl'."""
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

def main():
    """Запуск програми у нескінченному циклі."""
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "delete":
            print(delete_contact(args, book))

        elif command == "phone":
            print(find_phones(args, book))

        elif command == "all":
            print(show_all_contacts(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
