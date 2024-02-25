import os
import telebot
from telebot import types
import requests
from requests.exceptions import ReadTimeout
import time
import json


# Retrieve the bot token from the environment variable
BOT_TOKEN = os.environ.get('base')

bot = telebot.TeleBot("6668212969:AAEjEx1SD8_a84usXMOL89HnDU4KcSdvVLY")

channel_id = '@academyOfGamesBot'

# API endpoints
quote_api_url = 'https://api.quotable.io/random'
weather_api_url = 'https://api.openweathermap.org/data/2.5/weather'
currency_api_url = 'https://api.exchangerate-api.com/v4/latest/'
reminder_api = {}


# Function to fetch a daily quote from the API
def get_daily_quote():
    response = requests.get(quote_api_url)
    if response.status_code == 200:
        quote_data = response.json()
        content = quote_data['content']
        author = quote_data['author']
        return f"{content}\n\n- {author}"
    return None


# Function to get current weather and forecast
def get_question(category, difficulty):
    url = f"https://opentdb.com/api.php?amount=10&category={category}&difficulty={difficulty}&type=multiple"
    response = requests.get(url)
    if response.status_code == 200:
        data = json.loads(response.text)
        return data['results']
    else:
        return None


def get_weather_by_coordinates(latitude, longitude):
    api_key = "3cf69507917b652370ad2e810f0e4dfd"
    base_url = "https://api.openweathermap.org/data/2.5/weather"

    params = {
        'lat': latitude,
        'lon': longitude,
        'appid': api_key,
        'units': 'metric'
    }

    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        weather_description = data['weather'][0]['description']
        temperature = data['main']['temp']
        return f"Weather: {weather_description}\nTemperature: {temperature}°C"
    else:
        return "Unable to fetch weather information."


def get_coordinates_by_city(city_name):
    api_key = "a363ba0015974e6087945d49481f6846"
    base_url = "https://api.opencagedata.com/geocode/v1/json"

    params = {
        'q': city_name,
        'key': api_key
    }

    response = requests.get(base_url, params=params)

    print("URL:", response.url)
    print("Response:", response.text)

    if response.status_code == 200:
        data = response.json()
        if data['results']:
            latitude = data['results'][0]['geometry']['lat']
            longitude = data['results'][0]['geometry']['lng']
            return (latitude, longitude)
        else:
            return None
    else:
        print("Error getting coordinates:", response.text)
        return None


def process_weather_command(message):
    city_name = message.text
    coordinates = get_coordinates_by_city(city_name)
    if coordinates:
        latitude, longitude = coordinates
        weather_info = get_weather_by_coordinates(latitude, longitude)
        if weather_info:
            bot.reply_to(message, weather_info)
        else:
            bot.reply_to(message, """Unable to fetch weather information.
                         Please try again later.""")
    else:
        bot.reply_to(message, """Unable to get coordinates for the city.
                     Please try again.""")


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text.startswith('/weather'):
        ask_for_city(message)
    else:
        pass


# Function to convert currency
def convert_currency(amount, source_currency, target_currency):
    url = f"{currency_api_url}{source_currency}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        exchange_rate = data['rates'].get(target_currency)
        if exchange_rate:
            converted_amount = amount * exchange_rate
            return f"""{amount} {source_currency} is
            {converted_amount} {target_currency}"""
        else:
            return """Unable to convert currency.
            Please check the currency codes."""
    else:
        return "Unable to convert currency at the moment."


def process_currency_command(message):
    try:
        amount, source_currency, target_currency = message.text.split()
        amount = float(amount)
        result = convert_currency(amount, source_currency.upper(),
                                  target_currency.upper())
        bot.send_message(message.chat.id, result)
    except Exception:
        bot.send_message(message.chat.id, """Invalid input. Please enter in
                         the format: amount source_currency target_currency""")


# Function to set a reminder
def process_reminder_command(message):
    reminder = message.text
    chat_id = message.chat.id
    reminder_api[chat_id] = reminder
    bot.send_message(chat_id, f"Reminder set: {reminder}")


# Function to send a message to all active users
def send_message_to_all(message):
    active_users = reminder_api.keys()
    for user_id in active_users:
        bot.send_message(user_id, message)


def process_send_to_all_command(message):
    message_to_send = message.text
    send_message_to_all(message_to_send)
    bot.send_message(message.chat.id, "Message sent to all active users.")


# Function to get recommendations for movies
def process_recommend_command(message):
    preferences = message.text
    bot.send_message(message.chat.id, f"""Recommendations for
                     {preferences}: Action, Comedy, Drama""")


# Function for time to make API request
def make_api_request(url):
    retries = 3
    delay = 5  # seconds
    for _ in range(retries):
        try:
            response = requests.get(url, timeout=25)
            response.raise_for_status()
            return response.json()
        except ReadTimeout:
            print("Timeout occurred. Retrying...")
            time.sleep(delay)
            continue
        except Exception as e:
            print(f"An error occurred: {e}")
            break
    return None


@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    item_quote = types.InlineKeyboardButton('Get Quote', callback_data='quote')
    item_weather = types.InlineKeyboardButton('Check Weather',
                                              callback_data='weather')
    item_currency = types.InlineKeyboardButton('Convert Currency',
                                               callback_data='currency')
    item_reminder = types.InlineKeyboardButton('Set Reminder',
                                               callback_data='reminder')
    item_recommend = types.InlineKeyboardButton('Recommendations',
                                                callback_data='recommend')
    item_recipe = types.InlineKeyboardButton('Recipe Suggestions',
                                             callback_data='recipe')

    markup.row(item_quote, item_weather)
    markup.row(item_currency, item_reminder)
    markup.row(item_recommend, item_recipe)

    bot.reply_to(message, "Hi! Choose an option:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == 'quote':
        quote = get_daily_quote()
        if quote:
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id, quote)
    elif call.data == 'weather':
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id,
                         "Please enter the name of the city to get weather information:")
        bot.register_next_step_handler(call.message, process_weather_command)
    elif call.data == 'currency':
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id,
                         """Enter amount, source currency,
                         and target currency (e.g., 100 USD EUR):""")
        bot.register_next_step_handler(call.message, process_currency_command)
    elif call.data == 'reminder':
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id,
                         """Enter your reminder
                         (e.g., 'Meeting at 2 PM on Friday'):""")
        bot.register_next_step_handler(call.message, process_reminder_command)
    elif call.data == 'recommend':
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "Enter your preferences:")
        bot.register_next_step_handler(call.message, process_recommend_command)


@bot.message_handler(commands=['happy_birthday'])
def send_congratulation(message):
    with open('./picture.jpeg', 'rb') as photo:
        bot.send_photo(message.chat.id, photo)
    text_message = ("\fDear Mum,\n\nHappy Birthday! 🎂🎉\nI want to tell you how much you mean to me. Your birthday is a special day, and it's not just about getting older, but it's a day to celebrate all the love and kindness you give. You are strong, kind, and loving. You've helped me become who I am today, and I'm so thankful for that.\nI wish you a day filled with happiness, laughter, and lots of special moments. You deserve all the best things in life.Happy Birthday, Mom! I love you very much.\n\nWith love, Anastasiia🤍")
    bot.send_message(message.chat.id, text_message)


@bot.message_handler(commands=['currency'])
def currency_handler(message):
    bot.send_message(message.chat.id, """Enter amount, source currency,
                     and target currency (e.g., 100 USD EUR):""")
    bot.register_next_step_handler(message, process_currency_command)


@bot.message_handler(commands=['weather'])
def ask_for_city(message):
    text = "Please enter the name of the city to get weather information:"
    bot.reply_to(message, text)
    bot.register_next_step_handler(message, process_weather_command)


@bot.message_handler(commands=['reminder'])
def set_reminder_handler(message):
    bot.send_message(message.chat.id, """Enter your reminder
                     (e.g., 'Meeting at 2 PM on Friday'):""")
    bot.register_next_step_handler(message, process_reminder_command)


@bot.message_handler(commands=['send_to_all'])
def send_to_all_handler(message):
    if message.from_user.id == 1084139144:
        bot.send_message(message.chat.id,
                         "Enter the message to send to all users:")
        bot.register_next_step_handler(message, process_send_to_all_command)
    else:
        bot.send_message(message.chat.id,
                         "You are not authorized to use this command.")


@bot.message_handler(commands=['joke'])
def joke_handler(message):
    # Implement a function to fetch jokes from an API and send to user
    bot.send_message(message.chat.id, "Here's a joke for you!")


@bot.message_handler(commands=['quote'])
def quote_handler(message):
    quote = get_daily_quote()
    if quote:
        bot.send_message(message.chat.id, quote)
    else:
        bot.send_message(message.chat.id, "Unable to fetch daily quote.")


@bot.message_handler(commands=['recommend'])
def recommend_handler(message):
    bot.send_message(message.chat.id,
                     "Enter your movie or TV show preferences:")
    bot.register_next_step_handler(message, process_recommend_command)


# Function to handle all other messages
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    bot.send_message(message.chat.id,
                     """I'm sorry, I didn't understand that command.
                     Please use the available commands.""")


# Infinite polling to keep the bot running
bot.infinity_polling()
response_data = make_api_request("YOUR_API_ENDPOINT")
