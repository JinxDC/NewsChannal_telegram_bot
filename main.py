import telebot
import requests
import xmltodict
import json

BOT_TOKEN = "8102439813:AAGX32-F5OOB2RpW9DoxdRi9ir8zInnriTA"
bot = telebot.TeleBot(BOT_TOKEN)
BUTTONS = ["Предыдущий", "Ссылка", "Следующий"]
current_index = 0

r = requests.get("https://elementy.ru/rss/news/physics")
data = xmltodict.parse(r.text)
items = data.get("rss", {}).get("channel", {}).get("item", [])

def news_message(message, item):
    print(item)
    link = item.get("link")
    keyboard = menu_keyboard(link)
    category = item.get("category")
    description = item.get("description").replace("<p>", "").replace("</p>", "")
    pub_date = item.get("pubDate", "")[:11]
    title = item.get("title")
    enclosure = item.get("enclosure", {})
    image_url = enclosure.get("@url")

    bot.send_photo(message.chat.id, image_url, f"{title}\n\nКатегория: {category}\n\n{pub_date}\n\n{description}", reply_markup=keyboard)


def menu_keyboard(link):
    keyboard = telebot.types.InlineKeyboardMarkup()

    btn_prev = telebot.types.InlineKeyboardButton( BUTTONS[0], callback_data=json.dumps({"a": BUTTONS[0]}, ensure_ascii=False) )

    btn_link = telebot.types.InlineKeyboardButton( BUTTONS[1], link)

    btn_next = telebot.types.InlineKeyboardButton( BUTTONS[2], callback_data=json.dumps({"a": BUTTONS[2]}, ensure_ascii=False) )

    keyboard.row(btn_prev, btn_next)
    keyboard.row(btn_link)

    return keyboard



@bot.message_handler(commands=["start"])
def start(message):
    global current_index
    if items:
        news_message(message, items[current_index])

@bot.callback_query_handler(func=lambda call: True)
def menu_handler(call):
    global current_index
    data = json.loads(call.data)
    action = data.get("a")

    if action == "Предыдущий":
        if current_index > 0:
            current_index -= 1
    elif action == "Следующий":
        if current_index < len(items) - 1:
            current_index += 1

    bot.delete_message(call.message.chat.id, call.message.message_id)
    news_message(call.message, items[current_index])

bot.infinity_polling()
