import os
import subprocess
import google.generativeai as genai
import telebot

# 1. Твой токен от главного бота (от @BotFather)
MAIN_BOT_TOKEN = "8709685556:AAGdpibGsdZyIvkBQqwORDnQ83h0ro881pY"

# 2. Твой API-ключ от Google AI Studio
GOOGLE_API_KEY = "AQ.Ab8RN6LDLl4DN8mwsVDLx8mIQT9qrDdiIcOdilYcNN43UxvPPw"

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

bot = telebot.TeleBot(MAIN_BOT_TOKEN)
user_data = {}


@bot.message_handler(commands=['start'])
def start(message):
  bot.reply_to(
      message,
      "🤖 **AI-Конструктор ботов (Render Free Cloud)**\n\nПришли мне **API Token**"
      " нового бота от @BotFather:",
  )
  user_data[message.chat.id] = {'step': 'get_token'}


@bot.message_handler(func=lambda msg: message.chat.id in user_data)
def process_creation(message):
  chat_id = message.chat.id
  state = user_data[chat_id]['step']

  if state == 'get_token':
    user_data[chat_id]['token'] = message.text.strip()
    user_data[chat_id]['step'] = 'get_prompt'
    bot.reply_to(
        message,
        "✅ Токен принят!\n\nТеперь напиши **описание/задачу** для бота (что он"
        " должен делать):",
    )

  elif state == 'get_prompt':
    user_prompt = message.text.strip()
    bot_token = user_data[chat_id]['token']

    bot.reply_to(
        message,
        "🧠 **Gemini пишeт код...** Разворачиваю бота в облаке Render...",
    )

    system_instruction = f"""
    Ты — профессиональный Python разработчик. Напиши ПОЛНЫЙ, рабочий код Telegram-бота на базе `pyTelegramBotAPI` (telebot).
    Токен бота: `{bot_token}`.
    Задача и логика: {user_prompt}.
    Код должен быть полностью автономным, импортировать telebot и запускаться через `bot.infinity_polling()`.
    Верни ТОЛЬКО чистый код Python, без markdown-разметки ```python и без пояснений.
    """

    try:
      response = model.generate_content(system_instruction)
      generated_code = response.text.strip()

      if generated_code.startswith("```"):
        generated_code = generated_code.split("\n", 1)[1]
      if generated_code.endswith("```"):
        generated_code = generated_code.rsplit("\n", 1)[0]

      file_name = f"bot_user_{chat_id}.py"

      # Сохраняем сгенерированный файл локально в файловую систему контейнера
      with open(file_name, "w", encoding="utf-8") as f:
        f.write(generated_code)

      # Запускаем созданного бота в фоновом процессе внутри Render
      subprocess.Popen(["python3", file_name])

      bot.reply_to(
          message,
          "🚀 **Успешно! Бот создан нейросетью и запущен в облаке"
          " Render!**\n\nМожешь заходить в Telegram и запускть созданного"
          " бота.",
      )

    except Exception as e:
      bot.reply_to(message, f"❌ Ошибка при генерации или запуске: {e}")

    del user_data[chat_id]


if __name__ == '__main__':
  print("Главный бот-конструктор запущен на Render...")
  bot.infinity_polling()