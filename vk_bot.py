import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

TOKEN = "vk1.a.k6lbgmiC8fGE7SeGzEsOs3t1Wh-ryV8aRCSRxa9W6bYDqQIRfmc1s6SbaR6G1NEV3iqAyzEnB7NaU_q3zNZjIRv6pL972DfkZW63keS0q6qDpeDEgzxmwsoU_9ycIGUk5LObHggtJkmnwE_Tj7of2YMshBZg2o1bvFRUPdSPWFAckNr6QTIevwOqKs7yMc64cQzWBAA97JZlmNQXGizFwg"
GROUP_ID = 211624296

# Команды
ALLOWED_COMMANDS = [
    "проверить",
    "доступ",
    "урок"
]

# =========================================
# ПОДКЛЮЧЕНИЕ VK
# =========================================

vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()

longpoll = VkLongPoll(vk_session)

print("VK бот запущен")


# =========================================
# ОТПРАВКА СООБЩЕНИЯ
# =========================================

def send_message(user_id, text):
    vk.messages.send(
        user_id=user_id,
        random_id=0,
        message=text
    )


# =========================================
# ОСНОВНОЙ ЦИКЛ
# =========================================
vk.messages.send(
    user_id=397627448,
    random_id=0,
    message="Тест от бота"
)

print("Сообщение отправлено")    

for event in longpoll.listen():

    if event.type == VkEventType.MESSAGE_NEW and event.to_me:

        user_id = event.user_id
        text = event.text.lower().strip()

        print(f"[{user_id}] -> {text}")

        # =========================================
        # ИГНОР ВСЕГО ЛИШНЕГО
        # =========================================

        if text not in ALLOWED_COMMANDS:
            continue

        # =========================================
        # ПРОВЕРКА ПОДПИСКИ
        # =========================================

        try:

            result = vk.groups.isMember(
                group_id=GROUP_ID,
                user_id=user_id
            )

            # =========================================
            # ПОДПИСАН
            # =========================================

            if result == 1:

                send_message(
                    user_id,
                    (
                        "✅ Подписка подтверждена\n\n"
                        "Вот ваш доступ:\n"
                        "https://your-link.com"
                    )
                )

            # =========================================
            # НЕ ПОДПИСАН
            # =========================================

            else:

                send_message(
                    user_id,
                    (
                        "❌ Вы не подписаны на сообщество\n\n"
                        "Подпишитесь и попробуйте снова."
                    )
                )

        except Exception as e:

            print("ERROR:", e)

