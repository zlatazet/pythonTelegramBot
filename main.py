import os
import telebot
import requests
from io import BytesIO

# Retrieve the bot token from the environment variable
BOT_TOKEN = os.environ.get('base')
BOT_TOKEN = '6668212969:AAEjEx1SD8_a84usXMOL89HnDU4KcSdvVLY'


bot = telebot.TeleBot(BOT_TOKEN)
# print(f"BOT_TOKEN: {BOT_TOKEN}")

channel_id = '@academyOfGamesBot'


# API endpoint for fetching daily quotes
quote_api_url = 'https://api.quotable.io/random'


# Customization options for the image
image_width = 1080  # Instagram post width
image_height = 1080  # Instagram post height
background_color = (0, 0, 0)  # RGB value for black
text_color = (255, 255, 255)  # RGB value for white
font_size = 48
text_padding = 50  # Padding for left and right edges

# Logo customization
logo_text = "Your Logo"  # Replace with your logo text
logo_font_size = 64
logo_text_color = (255, 255, 255)  # RGB value for white


def get_daily_horoscope(sign: str, day: str) -> dict:
    """Get daily horoscope for a zodiac sign.
    Keyword arguments:
    sign:str - Zodiac sign
    day:str - Date in format (YYYY-MM-DD) OR TODAY OR TOMORROW OR YESTERDAY
    Return:dict - JSON data
    """
    url = "https://horoscope-app-api.vercel.app/api/v1/get-horoscope/daily"
    params = {"sign": sign, "day": day}
    response = requests.get(url, params)

    return response.json()


@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Hi! You\'ll receive daily quotes and horoscope from me :)")

@bot.message_handler(commands=['happy_birthday'])
def send_congratulation(message):
    # Replace 'path_to_your_photo.jpg' with the actual path to your photo file
    with open('./picture.jpeg', 'rb') as photo:
        bot.send_photo(message.chat.id, photo)

    # Send a text message as a reply
    text_message = "\fDear Mom,\n\nHappy Birthday! 🎂🎉\nI want to tell you how much you mean to me. Your birthday is a special day, and it's not just about getting older, but it's a day to celebrate all the love and kindness you give.\nYou are strong, kind, and loving. You've helped me become who I am today, and I'm so thankful for that.\nI wish you a day filled with happiness, laughter, and lots of special moments. You deserve all the best things in life.\nHappy Birthday, Mom! I love you very much.\n\nWith love, Anastasiia🤍"
    bot.send_message(message.chat.id, text_message)

# Add the /quote command handler
@bot.message_handler(commands=['quote'])
def quote_handler(message):
    quote = get_daily_quote()  # Call the function to retrieve the daily quote
    if quote:
        bot.send_message(message.chat.id, quote)  # Send the retrieved quote as a message
    else:
        bot.send_message(message.chat.id, "Unable to fetch daily quote.")


@bot.message_handler(commands=['horoscope'])
def sign_handler(message):
    text = "What's your zodiac sign?\nChoose one: *Aries*, *Taurus*, *Gemini*, *Cancer,* *Leo*, *Virgo*, *Libra*, *Scorpio*, *Sagittarius*, *Capricorn*, *Aquarius*, and *Pisces*."
    sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, day_handler)


def day_handler(message):
    sign = message.text
    text = "What day do you want to know?\nChoose one: *TODAY*, *TOMORROW*, *YESTERDAY*, or a date in format YYYY-MM-DD."
    sent_msg = bot.send_message(
        message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(
        sent_msg, fetch_horoscope, sign.capitalize())
 

def fetch_horoscope(message, sign):
    day = message.text
    horoscope = get_daily_horoscope(sign, day)
    data = horoscope["data"]
    horoscope_message = f'*Horoscope:* {data["horoscope_data"]}\n*Sign:* {sign}\n*Day:* {data["date"]}'
    bot.send_message(message.chat.id, "Here's your horoscope!")
    bot.send_message(message.chat.id, horoscope_message, parse_mode="Markdown")


#  Function to fetch a daily quote from the API
def get_daily_quote():
    response = requests.get(quote_api_url)
    if response.status_code == 200:
        quote_data = response.json()
        content = quote_data['content']
        author = quote_data['author']
        return f"{content}\n\n- {author}"
    return None


# Define the publish_daily_quote() function outside of quote_handler()
def publish_daily_quote():
    quote = get_daily_quote()
    if quote:
        with BytesIO() as bio:
            bio.seek(0)
            bot.send_photo(chat_id=channel_id, photo=bio)
    else:
        bot.send_message(chat_id=channel_id, text="Unable to fetch daily quote.")


bot.infinity_polling()