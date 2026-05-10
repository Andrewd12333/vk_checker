import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from flask import Flask, request
import threading

# =========================================
# НАСТРОЙКИ
# =========================================

TOKEN = "vk1.a.k6lbgmiC8fGE7SeGzEsOs3t1Wh-ryV8aRCSRxa9W6bYDqQIRfmc1s6SbaR6G1NEV3iqAyzEnB7NaU_q3zNZjIRv6pL972DfkZW63keS0q6qDpeDEgzxmwsoU_9ycIGUk5LObHggtJkmnwE_Tj7of2YMshBZg2o1bvFRUPdSPWFAckNr6QTIevwOqKs7yMc64cQzWBAA97JZlmNQXGizFwg"

# Группы, на которые должна быть подписка
REQUIRED_GROUPS = [
    211624296,
    158699535
]

# Callback API
CONFIRMATION_TOKEN = "confirmation_token"
SECRET_KEY = "secret_key"

# Кодовое слово в комментариях
CODE_WORD = "доступ"

# Команды в ЛС
ALLOWED_COMMANDS = [
    "доступ"
]

# =========================================
# VK
# =========================================

vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()

longpoll = VkLongPoll(vk_session)

print("VK бот запущен")

# =========================================
# FLASK
# =========================================

app = Flask(__name__)

# =========================================
# ОТПРАВКА СООБЩЕНИЙ
# =========================================

def send_message(user_id, text):

    vk.messages.send(
        user_id=user_id,
        random_id=0,
        message=text
    )

# =========================================
# ПРОВЕРКА ПОДПИСОК
# =========================================

def check_subscriptions(user_id):

    for group_id in REQUIRED_GROUPS:

        result = vk.groups.isMember(
            group_id=group_id,
            user_id=user_id
        )

        if result != 1:
            return False

    return True

# =========================================
# CALLBACK API
# =========================================

@app.route("/", methods=["POST"])
def callback():

    data = request.json

    # Подтверждение сервера
    if data["type"] == "confirmation":
        return CONFIRMATION_TOKEN

    # Проверка secret key
    if data.get("secret") != SECRET_KEY:
        return "not ok"

    # Новый комментарий
    if data["type"] == "wall_reply_new":

        comment = data["object"]["text"].lower().strip()
        user_id = data["object"]["from_id"]

        print(f"Комментарий: {comment}")

        # Только кодовое слово
        if CODE_WORD in comment:

            try:

                send_message(
                    user_id,
                    (
                        "✅ Комментарий получен\n\n"
                        "Теперь напишите:\n"
                        "проверить"
                    )
                )

            except Exception as e:

                print("Ошибка отправки ЛС:", e)

    return "ok"

# =========================================
# FLASK В ОТДЕЛЬНОМ ПОТОКЕ
# =========================================

def run_callback():

    app.run(
        host="0.0.0.0",
        port=5000
    )

threading.Thread(target=run_callback).start()

# =========================================
# LONGPOLL
# =========================================

for event in longpoll.listen():

    if event.type == VkEventType.MESSAGE_NEW and event.to_me:

        user_id = event.user_id
        text = event.text.lower().strip()

        print(f"[{user_id}] -> {text}")

        # Игнор мусора
        if text not in ALLOWED_COMMANDS:
            continue

        try:

            is_subscribed = check_subscriptions(user_id)

            # =========================================
            # ВСЕ ПОДПИСКИ ЕСТЬ
            # =========================================

            if is_subscribed:

                send_message(
                    user_id,
                    (
                        "✅ Подписка подтверждена\n\n"
                        "Вот ваш доступ:\n"
                        "https://your-link.com"
                    )
                )

            # =========================================
            # НЕТ ПОДПИСОК
            # =========================================

            else:

                send_message(
                    user_id,
                    (
                        "❌ Вы подписаны не на все сообщества\n\n"
                        "Подпишитесь и попробуйте снова."
                    )
                )

        except Exception as e:

            print("ERROR:", e)