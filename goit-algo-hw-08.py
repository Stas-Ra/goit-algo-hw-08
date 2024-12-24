from collections import UserDict
from datetime import datetime, date, timedelta
import pickle


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass
    
class Phone(Field): 
    def __init__(self, value):
        if len(value) == 10 and value.isdigit():
            super().__init__(value)
        else:
            raise ValueError

    def __str__(self):
        return str(self.value)
    
class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
            self.value = value
            super().__init__(value)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
    
    def add_phone(self, value):
        self.phones.append(Phone(value))

    def add_birthday(self, value):
        self.birthday = Birthday(value)

    def remove_phone(self, value):
        self.phones = [p for p in self.phones if p.value != value]

    def edit_phone(self, old_phone, new_phone):
        if old_phone in (p.value for p in self.phones):
            self.phones = [p if p.value != old_phone else Phone(new_phone) for p in self.phones]
        else:
            raise ValueError

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
            else:
                None
        
    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}, birthday: {self.birthday}"

class AddressBook(UserDict): 
    def add_record(self, record):
        self.data.update({record.name.value: record})

    def find(self, name) -> Record:
        return self.data.get(name)

    def delete(self, name):
        del self.data[name]

    @staticmethod
    def string_to_date(date_string):
        return datetime.strptime(date_string, "%d.%m.%Y").date()
    
    @staticmethod
    def date_to_string(date):
        return date.strftime("%d.%m.%Y")
    
    @staticmethod
    def find_next_weekday(start_date, weekday):
        days_ahead = weekday - start_date.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return start_date + timedelta(days=days_ahead)
    
    @classmethod
    def adjust_for_weekend(cls, birthday):
        if birthday.weekday() >= 5:
            return cls.find_next_weekday(birthday, 0)
        return birthday
    
    def get_upcoming_birthdays(self, days=7):
        upcoming_birthdays = []
        today = date.today()
        for record in self.data.values():
            try:
                birthday = str(record.birthday)
                birthday_this_year = self.string_to_date(birthday).replace(year=today.year)
                if birthday_this_year < today:
                    birthday_this_year = self.string_to_date(birthday).replace(year=today.year + 1)
                if 0 <= (self.adjust_for_weekend(birthday_this_year) - today).days <= days:
                    congratulation_date_str = self.date_to_string(self.adjust_for_weekend(birthday_this_year))
                    upcoming_birthdays.append({"name": record.name.value, "birthday": congratulation_date_str})
            except ValueError:
                pass    
        return upcoming_birthdays

    def show_birthday(self, name):
        return self.data.get(name).birthday
    
    def __str__(self):
        return f"Record in your AddressBook, amigo:\n{"\n".join(str(self.data.get(key)) for key in self.data)}"


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()
    
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Sorry, enter a relevant command or detalis"
        except KeyError:
            return "This key is not relevant for the command"
        except IndexError:
            return """
            I have no idea under what conditions the IndexError
            can be called in this bot, but so be it
            """
    return inner

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
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
def add_birthday(args, book: AddressBook):
    name, birthday, *_ = args
    record = book.find(name)
    message = "Birthday date added."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if birthday:
        record.add_birthday(birthday)
    return message

@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record is None:
        return "This contact does not exist. Add a contact first."
    else:
        record.edit_phone(old_phone, new_phone)
        return "Phone updated"

@input_error
def show_phone(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record is None:
        return "This contact does not exist. Add a contact first."
    else:
        return record
    
@input_error
def show_birthday(args, book: AddressBook):
    name, *_ = args
    return book.show_birthday(name)

@input_error
def show_all(book: AddressBook):     
    return book

@input_error
def get_birthdays(book: AddressBook):
    return book.get_upcoming_birthdays()

def main():
    book = load_data("addressbook.pkl")
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)
        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break
        elif command == "hello":
            print("Hola, amigo! How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(get_birthdays(book))
        else:
            print("I am a loser bot, and not understand this command.")

if __name__ == "__main__":
    main()
