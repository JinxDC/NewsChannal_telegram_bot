import json
import os
import telebot
import requests
import xmltodict
import random
from apscheduler.schedulers.background import BackgroundScheduler
import re

BOT_TOKEN = "TOKEN"
CHANNEL = -1002816478267
bot = telebot.TeleBot(BOT_TOKEN)
FILE_NAME = "data.json"

feeds = [
    "https://elementy.ru/rss/news/physics",
    "https://www.techcult.ru/rss",
    "https://www.goha.ru/rss/videogames",
    "https://www.gastronom.ru/RSS",
    "https://nplus1.ru/rss",
    "https://www.computerra.ru/feed/",
    "https://holographica.space/feed/"
]

def get_all_news():
    all_items = []
    for url in feeds:
        try:
            response = requests.get(url, timeout=5)
            data = xmltodict.parse(response.text)
            items = data.get("rss", {}).get("channel", {}).get("item", [])
            all_items.extend(items)
        except Exception as e:
            print(f"Ошибка при загрузке {url}: {e}")
    return all_items

def clean_html(raw_html):
    # Удаляет все HTML-теги
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

def send_random_news():
    items = get_all_news()
    if not items:
        print("Нет новостей для отправки.")
        return

    if os.path.getsize(FILE_NAME):
        with open(FILE_NAME, "r") as file:
            old_news_list = json.load(file)
    else:
        old_news_list = []
    item = random.choice(items)
    title = item.get("title", "Без названия")
    if title in old_news_list:
        return
    old_news_list.append(title)
    link = item.get("link", "#")
    category = item.get("category", "Без категории")
    raw_description = item.get("description", "")
    description = clean_html(raw_description)
    pub_date = item.get("pubDate", "")[:11]
    enclosure = item.get("enclosure", {})
    image_url = enclosure.get("@url")

    text = f"<b>{title}</b>\n\nКатегория: {category}\nДата: {pub_date}\n\n{description}\n\n<a href='{link}'>Читать далее</a>"

    try:
        if image_url :
            bot.send_photo(CHANNEL, image_url, caption=text, parse_mode="HTML")
        else:
            bot.send_message(CHANNEL, text, parse_mode="HTML")
        print("Новость отправлена.")
        with open(FILE_NAME, "w") as file:
            json.dump(old_news_list, file)
    except Exception as e:
        print(f"Ошибка при отправке: {e}")

# Настройка планировщика
scheduler = BackgroundScheduler()
scheduler.add_job(send_random_news, "interval", minutes=30)  # каждые 30 минут
scheduler.start()

print("Бот работает. Новости будут публиковаться автоматически.")

bot.infinity_polling()
