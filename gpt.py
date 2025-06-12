import telebot
import time
import json
import os
from openai import OpenAI

# 🔐 Токены
TELEGRAM_TOKEN = "7784364439:AAEIgbD1B29tTieUzSeesgXXsB5YxrG93HY"
OPENAI_API_KEY = "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"

# 📌 Настройки
DAILY_LIMIT = 30
LIMITS_FILE = "user_limits.json"

# 🔧 Инициализация
bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)

# 🔄 Загрузка и сохранение лимитов
def load_limits():
    if os.path.exists(LIMITS_FILE):
        with open(LIMITS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_limits(limits):
    with open(LIMITS_FILE, "w") as f:
        json.dump(limits, f)

# 🟢 Команда /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, "👋 Привет! Я GPT-4o бот. Напиши свой вопрос.")

# 💬 Обработка сообщений
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    user_id = str(message.chat.id)
    limits = load_limits()
    today = str(int(time.time()) // 86400)

    if user_id not in limits:
        limits[user_id] = {}
    if today not in limits[user_id]:
        limits[user_id][today] = 0

    if limits[user_id][today] >= DAILY_LIMIT:
        bot.reply_to(message, "🚫 Лимит исчерпан. Попробуйте завтра.")
        return

    limits[user_id][today] += 1
    save_limits(limits)

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Ты дружелюбный и умный помощник."},
                {"role": "user", "content": message.text}
            ],
            max_tokens=800,
            temperature=0.7
        )
        answer = response.choices[0].message.content.strip()
        bot.reply_to(message, answer)
    except Exception as e:
        print("❌ Ошибка:", e)
        bot.reply_to(message, "⚠️ Ошибка при обращении к OpenAI.")

# 🚀 Запуск
if __name__== "__main__":
    print("✅ Бот запущен!")
    bot.polling()
