from pywebio.input import input, textarea
from pywebio.output import put_text, put_html, put_buttons
from pywebio import start_server
import sqlite3
from contextlib import contextmanager

# Создание базы данных (если она не существует)
conn = sqlite3.connect('forum.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        message TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()


@contextmanager
def db_transaction():
    conn = sqlite3.connect('forum.db')
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    finally:
        conn.close()


def add_message(username, message):
    with db_transaction() as cursor:
        cursor.execute('INSERT INTO messages (username, message) VALUES (?, ?)', (username, message))


def edit_message(message_id, new_message):
    with db_transaction() as cursor:
        cursor.execute('UPDATE messages SET message = ? WHERE id = ?', (new_message, message_id))


def delete_message(message_id):
    with db_transaction() as cursor:
        cursor.execute('DELETE FROM messages WHERE id = ?', (message_id,))


def delete_all_messages():
    with db_transaction() as cursor:
        cursor.execute('DELETE FROM messages')


def get_messages():
    with db_transaction() as cursor:
        cursor.execute('SELECT id, username, message FROM messages')
        messages = cursor.fetchall()
        return messages


def forum_app():
    def action_handler(btn_value, msg_id):
        if btn_value == "[Редактировать]":
            new_message = textarea("Введите новое сообщение:")
            if new_message:
                edit_message(msg_id, new_message)
                put_text("Сообщение отредактировано.")
                put_html("<script>window.location.reload();</script>")
        elif btn_value == "[Удалить]":
            delete_message(msg_id)
            put_text("Сообщение удалено.")
            put_html("<script>window.location.reload();</script>")

    def delete_all_messages_handler(btn_value):
        if btn_value:
            delete_all_messages()
            put_text("Все сообщения на форуме удалены.")
            put_html("<script>window.location.reload();</script>")

    put_html("<h2>Добро пожаловать на форум!</h2>")
    messages = get_messages()

    if messages:
        put_text("Сообщения на форуме:")
        for idx, (message_id, username, message) in enumerate(messages):
            put_text(f"{idx + 1}. Пользователь {username}: {message}")
            edit_button = "[Редактировать]"
            delete_button = "[Удалить]"
            put_buttons([edit_button, delete_button],
                        onclick=lambda btn_value, msg_id=message_id: action_handler(btn_value, msg_id))

        delete_all_button = "[Удалить форум]"
        put_buttons([delete_all_button], onclick=delete_all_messages_handler)

    while True:
        username = input("Введите ваше имя:", type="text")
        message = textarea("Введите ваше сообщение:")

        if username and message:
            add_message(username, message)
            new_messages = get_messages()
            if new_messages:
                put_text("Новые сообщения на форуме:")
                for message_id, username, message in new_messages:
                    put_text(f"Пользователь {username}: {message}")
                    edit_button = "Редактировать"
                    delete_button = "Удалить"
                    put_buttons([edit_button, delete_button],
                                onclick=lambda btn_value, msg_id=message_id: action_handler(btn_value, msg_id))


if __name__ == '__main__':
    start_server(forum_app, port=8080)
