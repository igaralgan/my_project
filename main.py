import random

from database.db_operations import create_table, load_questions_from_file_to_db, get_all_questions, get_answers_for_question, create_connection, load_questions_from_fixed_file_to_db, get_random_question
from utils.helpers import clear_console, get_user_input, start_quiz

def main_menu():
    print("Выберите команду:")
    print("1. Создать таблицы базы данных")
    print("2. Загрузить вопросы из файла")
    print("3. Просмотреть все вопросы")
    print("4. Выйти")
    print("5. Пройти тест")

def main():
    database = "qa_database.db"
    conn = create_connection(database)

    if conn is not None:
        while True:
            clear_console()
            main_menu()
            user_choice = int(get_user_input("Введите номер команды (1-5): "))

            if user_choice == 1:
                create_table(conn)
                print("Таблицы созданы")
                get_user_input("Нажмите Enter, чтобы продолжить")
            elif user_choice == 2:
                load_questions_from_fixed_file_to_db(conn)
                print("Вопросы загружены")
                get_user_input("Нажмите Enter, чтобы продолжить")
            elif user_choice == 3:
                questions = get_all_questions(conn)
                for question in questions:
                    print(question)
                get_user_input("Нажмите Enter, чтобы продолжить")
            elif user_choice == 4:
                print("Выход из программы")
                break
            elif user_choice == 5:
                start_quiz(conn)
            else:
                print("Неверный выбор, попробуйте еще раз")
                get_user_input("Нажмите Enter, чтобы продолжить")
    else:
        print("Error! Cannot create the database connection.")

if __name__ == '__main__':
    main()
