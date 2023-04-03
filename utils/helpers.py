import os
import random
import sqlite3

from database.db_operations import get_random_question
from database.db_operations import get_all_questions



class ExitQuiz(Exception):
    pass


def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')


def get_user_input(prompt):
    user_input = input(prompt).strip().lower()
    if user_input == 'q':
        raise ExitQuiz
    return user_input


def start_quiz(conn):
    try:
        while True:
            clear_console()
            remaining_questions = len(get_all_questions(conn))
            print(f"Осталось вопросов: {remaining_questions}\n")
            question, answers = get_random_question(conn)

            print(question)
            random.shuffle(answers)
            for i, answer in enumerate(answers):
                print(f"{i + 1}. {answer[0]}")

            user_choice = int(get_user_input("Выберите ответ (1-4): ")) - 1

            correct_answer_index = None
            for i, answer in enumerate(answers):
                if answer[1] == 1:
                    correct_answer_index = i
                    break

            if user_choice == correct_answer_index:
                print("Правильно!")
            else:
                print(f"Неправильно. Правильный ответ: {answers[correct_answer_index][0]}")

            get_user_input("Enter или 'q' для выхода: ")

    except ExitQuiz:
        print("Выход из программы.")
