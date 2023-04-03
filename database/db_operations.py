import sqlite3
import random
import re

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(e)

    return conn

def create_table(conn):
    try:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS questions (id INTEGER PRIMARY KEY, text TEXT NOT NULL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS answers (id INTEGER PRIMARY KEY, text TEXT NOT NULL, correct INTEGER NOT NULL, question_id INTEGER NOT NULL, FOREIGN KEY (question_id) REFERENCES questions (id))''')
        conn.commit()
    except sqlite3.Error as e:
        print(e)


def parse_ticket_data(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    filtered_lines = [x for x in lines if "билет" not in x.lower()]

    questions = []

    for question_idx in range(0, len(filtered_lines), 5):
        question_raw = filtered_lines[question_idx].strip()
        question = re.sub(r'^\d+[)\.]?\s*', '', question_raw)
        answers = [filtered_lines[i].strip() for i in range(question_idx + 1, question_idx + 5)]
        correct_answer_idx = [i for i, x in enumerate(answers) if x.startswith('*')]
        if len(correct_answer_idx) > 0:
            correct_answer_idx = correct_answer_idx[0]
            answers[correct_answer_idx] = answers[correct_answer_idx].replace('*', '')
        else:
            correct_answer_idx = -1

        questions.append((question, answers, correct_answer_idx))

    return questions




def load_questions_from_fixed_file_to_db(conn):
    fixed_file_path = '/Users/andrej/Downloads/1.txt'
    load_questions_from_file_to_db(fixed_file_path, conn)

def load_questions_from_file_to_db(file_path, conn):
    questions_data = parse_ticket_data(file_path)
    cursor = conn.cursor()
    for index, question in enumerate(questions_data):
        cursor.execute("INSERT INTO questions (text) VALUES (?)", (question[0],))
        question_id = cursor.lastrowid
        for i, answer_text in enumerate(question[1]):
            is_correct = 1 if '*' in answer_text else 0
            answer_text = answer_text.replace('(*)', '')
            cursor.execute("INSERT INTO answers (text, correct, question_id) VALUES (?, ?, ?)", (answer_text, is_correct, question_id))
        conn.commit()


def get_all_questions(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM questions")
    return cursor.fetchall()

def get_answers_for_question(conn, question_text):
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, text, correct FROM answers WHERE question_id = (SELECT id FROM questions WHERE text = ?)", (question_text,))
        return cursor.fetchall()


def get_random_question(db_file, answered_questions):
    conn = create_connection(db_file)
    cursor = conn.cursor()
    exclusion_str = "AND id NOT IN (" + ",".join("?" * len(answered_questions)) + ")" if answered_questions else ""
    cursor.execute(f"SELECT * FROM questions WHERE 1 {exclusion_str} ORDER BY RANDOM() LIMIT 1",
                   tuple(answered_questions))
    question = cursor.fetchone()  # добавьте эту строку
    cursor.execute("SELECT * FROM answers WHERE question_id=?", (question[0],))
    answers = cursor.fetchall()
    conn.close()
    return question[1], answers




def get_correct_answer_for_question(conn, question_text):
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM answers WHERE question_id = (SELECT id FROM questions WHERE text = ?) AND correct = 1", (question_text,))
        return cursor.fetchone()[0]

def get_question_id(conn, question_text):
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM questions WHERE text = ?", (question_text,))
        return cursor.fetchone()[0]

def get_total_questions_count(db_file):
    conn = create_connection(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM questions")
    total_questions = cursor.fetchone()[0]
    conn.close()
    return total_questions
