import os
import telebot
import requests
import json
from telebot import types
# from datetime import datetime, timedelta
# import schedule
# import time
# import threading


# Retrieve the bot token from the environment variable
BOT_TOKEN = os.environ.get('base')

bot = telebot.TeleBot(BOT_TOKEN)

channel_id = '@academyOfGamesBot'

# Store reminders in a dictionary {chat_id: reminder_text}


# API endpoints
quote_api_url = 'https://api.quotable.io/random'
weather_api_url = 'https://api.openweathermap.org/data/2.5/weather'
currency_api_url = 'https://api.exchangerate-api.com/v4/latest/'

# Store reminders in a dictionary {chat_id: reminder_text}
reminder_jobs = {}


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
            bot.send_message(message.chat.id, weather_info)
        else:
            bot.reply_to(message, """Unable to fetch weather information.
                         Please try again later.""")
    else:
        bot.reply_to(message, """Unable to get coordinates for the city.
                     Please try again.""")


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
# def remind_user(message, text, delay):
#     bot.send_message(message.chat.id, text)
#     del reminder_jobs[message.chat.id]


# def process_reminder_command(message):
#     try:
#         reminder_text = message.text

#         # Split the input to get the time and day
#         parts = reminder_text.split(" at ")

#         if len(parts) != 2:
#             raise ValueError("Invalid input")

#         time_str = parts[1].strip()
#         day_str = parts[0].strip()

#         # Convert day string to datetime object
#         today = datetime.today()
#         days_dict = {
#             "monday": 0,
#             "tuesday": 1,
#             "wednesday": 2,
#             "thursday": 3,
#             "friday": 4,
#             "saturday": 5,
#             "sunday": 6,
#         }
#         day_of_week = days_dict.get(day_str.lower())
#         if day_of_week is None:
#             raise ValueError("Invalid day")

#         day_difference = (day_of_week - today.weekday()) % 7
#         reminder_day = today + timedelta(days=day_difference)

#         # Convert time string to datetime object
#         reminder_time = datetime.strptime(time_str, "%I:%M %p").time()

#         # Combine date and time to create reminder datetime
#         reminder_datetime = datetime.combine(reminder_day, reminder_time)

#         # Calculate delay in seconds
#         current_time = datetime.now()
#         delay = (reminder_datetime - current_time).total_seconds()

#         # Check if delay is less than one second, cancel reminder
#         if delay < 1:
#             raise ValueError("Invalid delay")

#         # Schedule the reminder
#         reminder_jobs[message.chat.id] = schedule.every().seconds.do(
#             remind_user, message, "Reminder: " + parts[0].strip(), delay
#         )

#         bot.send_message(message.chat.id, f"Reminder set: {reminder_text}")
#     except Exception as e:
#         bot.send_message(
#             message.chat.id, f"""Invalid input for reminder.
#        Please try again. Error: {e}"""
#         )


# # Function to schedule sending the reminder message
# def schedule_message(reminder_time, chat_id):
#     def send_reminder():
#         try:
#             reminder_text = reminder_jobs[chat_id]
#             bot.send_message(chat_id, f"🕒 Reminder: {reminder_text}")
#         except KeyError:
#             # Handle case where reminder is deleted before it's sent
#             pass

#     # Calculate the delay until the reminder time
#     now = datetime.now()
#     delay = (reminder_time - now).total_seconds()

#     # Check if the delay is less than one second
#     if delay < 1:
#         bot.send_message(chat_id, """Reminder canceled.
#                          The specified time is too soon.""")
#         return

#     # Schedule the reminder message
#     schedule.every().seconds.do(send_reminder).at(reminder_time
#                                                   .strftime("%H:%M:%S"))

#     # Start the scheduler in a separate thread (non-blocking)
#     schedule_thread = threading.Thread(target=schedule.run_continuously)
#     schedule_thread.start()


# def check_reminder_jobs():
#     while True:
#         schedule.run_pending()
#         time.sleep(1)


# Function to send a message to all active users
def send_message_to_all(message):
    active_users = reminder_jobs.keys()
    for user_id in active_users:
        bot.send_message(user_id, message)


def process_send_to_all_command(message):
    if message.from_user.id == 1084139144:
        message_to_send = message.text
        send_message_to_all(message_to_send)
        bot.send_message(message.chat.id, "Message sent to all active users.")
    else:
        bot.send_message(message.chat.id,
                         "You are not authorized to use this command.")


# Function to get recommendations for movies
# def process_recommend_command(message):
#     preferences = message.text
#     bot.send_message(message.chat.id, f"""Recommendations for
#                      {preferences}: Action, Comedy, Drama""")


@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    item_quote = types.InlineKeyboardButton('Get Quote', callback_data='quote')
    item_weather = types.InlineKeyboardButton('Check Weather',
                                              callback_data='weather')
    item_currency = types.InlineKeyboardButton('Convert Currency',
                                               callback_data='currency')
    # item_reminder = types.InlineKeyboardButton('Set Reminder',
    #                                            callback_data='reminder')
    # item_recommend = types.InlineKeyboardButton('Recommendations',
    #                                             callback_data='recommend')

    markup.row(item_quote, item_weather)
    markup.row(item_currency)
    # markup.row(item_recommend, item_reminder)

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
                         """Please enter the name of the city to get weather
                         information:""")
        bot.register_next_step_handler(call.message, process_weather_command)
    elif call.data == 'currency':
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id,
                         """Enter amount, source currency,
                         and target currency (e.g., 100 USD EUR):""")
        bot.register_next_step_handler(call.message, process_currency_command)
    # elif call.data == 'reminder':
    #     bot.answer_callback_query(call.id)
    #     bot.send_message(call.message.chat.id,
    #                      """Enter your reminder
    #                      (e.g., 'Meeting at 2 PM on Friday'):""")
    #     bot.register_next_step_handler(call.message,
    #    process_reminder_command)
    # elif call.data == 'recommend':
    #     bot.answer_callback_query(call.id)
    #     bot.send_message(call.message.chat.id, "Enter your preferences:")
    #     bot.register_next_step_handler(call.message,
    #    process_recommend_command)
    else:
        bot.send_message(call.message.chat.id,
                         "You are not authorized to use this command.")


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


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text.startswith('/weather'):
        ask_for_city(message)
    else:
        pass


# @bot.message_handler(commands=["reminder"])
# def set_reminder_handler(message):
#     bot.send_message(
#         message.chat.id,
#         """Enter your reminder in the format:
#         'Do at <time> on <day>' (e.g., 'Do at 5:57 AM on Sunday'):""",
#     )
#     bot.register_next_step_handler(message, process_reminder_command)


@bot.message_handler(commands=['send_to_all'])
def send_to_all_handler(message):
    if message.from_user.id == 1084139144:
        bot.send_message(message.chat.id,
                         "Enter the message to send to all users:")
        bot.register_next_step_handler(message, process_send_to_all_command)
    else:
        bot.send_message(message.chat.id,
                         "You are not authorized to use this command.")


# @bot.message_handler(commands=['joke'])
# def joke_handler(message):
#     # Implement a function to fetch jokes from an API and send to user
#     bot.send_message(message.chat.id, "Here's a joke for you!")


@bot.message_handler(commands=['quote'])
def quote_handler(message):
    quote = get_daily_quote()
    if quote:
        bot.send_message(message.chat.id, quote)
    else:
        bot.send_message(message.chat.id, "Unable to fetch daily quote.")


# @bot.message_handler(commands=['recommend'])
# def recommend_handler(message):
#     bot.send_message(message.chat.id,
#                      "Enter your movie or TV show preferences:")
#     bot.register_next_step_handler(message, process_recommend_command)


# Function to handle all other messages
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    bot.send_message(message.chat.id,
                     """I'm sorry, I didn't understand that command.
                     Please use the available commands.""")


# Infinite polling to keep the bot running
print("Starting polling...")
bot.infinity_polling()
print("Bot stopped.")
