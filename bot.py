from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
import logging
import os
from database import db_operations
from dotenv import load_dotenv
from telegram import ParseMode
from telegram.ext import MessageHandler, Filters
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup


load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
db_file = "/Users/andrej/PycharmProjects/my_project/qa_database.db"
#db_file = "/root/project_folder/qa_database.db"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()


# В вашем основном файле бота
def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_data = context.user_data
    if 'answered_questions' not in user_data:
        user_data['answered_questions'] = []
    question, answers = db_operations.get_random_question(db_file,
                                                          user_data['answered_questions'])  # добавьте аргумент здесь
    answer_texts = [f"{i + 1}. {answer[1]}" for i, answer in enumerate(answers)]
    question_text = f"<b>{question}</b>\n\n" + "\n\n".join(answer_texts)
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(text=str(i + 1), callback_data=f'answer_{answer[0]}')] for i, answer in enumerate(answers)
    ])
    message = update.message.reply_html(text=question_text, reply_markup=reply_markup)
    context.user_data['question_message_id'] = message.message_id
    context.user_data['question'] = question
    context.user_data['answers'] = answers
    context.user_data['answered_current_question'] = False


def answer_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    answer_id = int(query.data.split('_')[1])
    conn = db_operations.create_connection(db_file)
    question_text = query.message.text.split('\n')[0].rstrip(':')
    question_id = db_operations.get_question_id(conn, question_text)

    if not context.user_data['answered_current_question']:
        context.user_data["answered_questions"].append(question_id)
        context.user_data['answered_current_question'] = True

    answers = db_operations.get_answers_for_question(conn, question_text)
    correct_answer_id = next((answer[0] for answer in answers if answer[2] == 1), None)

    if correct_answer_id == answer_id:
        text = 'Правильно!'
    else:
        correct_answer_text = next((answer[1] for answer in answers if answer[0] == correct_answer_id), None)
        text = f'Неправильно!\nПравильный ответ: {correct_answer_text}'

    # Добавьте статистику перед текстом кнопки "Следующий вопрос"
    total_questions = db_operations.get_total_questions_count(db_file)
    answered_questions_count = len(context.user_data["answered_questions"])
    remaining_questions = total_questions - answered_questions_count
    stats_text = f"Отвечено на {answered_questions_count} из {total_questions} вопросов. Осталось {remaining_questions}.\n\n"

    # Добавьте кнопку "Следующий вопрос"
    next_question_button = InlineKeyboardMarkup([
        [InlineKeyboardButton(text="Следующий вопрос", callback_data="next_question")]
    ])

    query.message.reply_text(text)
    query.message.reply_text(stats_text, reply_markup=next_question_button)
    conn.close()

def welcome(update: Update, context: CallbackContext):
    reply_markup = ReplyKeyboardMarkup(
        [["Старт"]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    welcome_text = "Привет! Я бот для опроса. Нажмите кнопку 'Старт', чтобы начать."
    update.message.reply_text(text=welcome_text, reply_markup=reply_markup)

def handle_text_message(update: Update, context: CallbackContext):
    text = update.message.text
    if text == "Старт":
        start(update, context)


def next_question_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    next_question, next_answers = db_operations.get_random_question(db_file, context.user_data["answered_questions"])
    if next_question is not None:
        answer_texts = [f"{i + 1}. {answer[1]}" for i, answer in enumerate(next_answers)]
        question_text = f"<b>{next_question}</b>\n\n" + "\n\n".join(answer_texts)
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(text=str(i + 1), callback_data=f'answer_{answer[0]}')] for i, answer in
            enumerate(next_answers)
        ])

        # Обновите текст сообщения с вопросом
        query.message.edit_text(question_text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
    else:
        query.message.reply_text("Это был последний вопрос. Спасибо за участие в тесте!")
    context.user_data['answered_current_question'] = False


def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", welcome))
    dp.add_handler(CallbackQueryHandler(answer_callback, pattern='^answer_'))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text_message))
    dp.add_handler(CallbackQueryHandler(next_question_callback, pattern='^next_question'))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
