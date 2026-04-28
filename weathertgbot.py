from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    Location
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import aiohttp

# Define the token for the bot
TOKEN = ""
# Initialize the bot with the token
bot = Bot(token=TOKEN)
# Create a dispatcher for the bot
dp = Dispatcher()

# Define a keyboard for sharing location
keyboard = ReplyKeyboardMarkup(
      keyboard=[[KeyboardButton(text="Share Location", request_location=True)]],
      resize_keyboard=True,
    )

# Define a function to handle the start command
@dp.message(Command("start"))
async def start(message: Message):
    # Handle the start command by sending a message to share location
    await message.answer("Hello! Please share your location", reply_markup=keyboard)

# Define a function to parse the location
@dp.message(F.location)
async def parse_location(message: Message):
    # Get the location from the message
    location = message.location
    # Define the URL for the weather API
    url = "https://api.open-meteo.com/v1/forecast"
    # Define the parameters for the API request
    params = {
        "latitude": location.latitude,
        "longitude": location.longitude,
        "daily": "temperature_2m_max,temperature_2m_min,weathercode,precipitation_probability_max",
        "timezone": "auto",
        "forecast_days": 7
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()
                if "daily" in data:
                    daily = data["daily"]
                    weather_info = "Weather forecast for the next 7 days:\n"
                    for i in range(len(daily["time"])):
                        date_str = daily['time'][i]
                        max_temp = daily['temperature_2m_max'][i]
                        min_temp = daily['temperature_2m_min'][i]
                        precip = daily['precipitation_probability_max'][i]
                        weather_code = daily['weathercode'][i]
                        weather_info += f"Date: {date_str}\n"
                        weather_info += f"Max Temp: {max_temp}°C\n"
                        weather_info += f"Min Temp: {min_temp}°C\n"
                        weather_info += f"Precipitation Probability: {precip}%\n"
                        weather_info += f"Weather Code: {weather_code}\n\n"
                    await message.answer(weather_info)
                else:
                    await message.answer("Failed to get weather data. Please try again.")
    except Exception as e:
        await message.answer(f"Error occurred while fetching weather data: {str(e)}")


# Define a function to handle other messages
@dp.message()
async def handle_other_messages(message: Message):
    # Send a message to share location
    await message.answer("Please share your location using the button below.", reply_markup=keyboard)

if __name__ == "__main__":
    print("Бот запустился!")
    dp.run_polling(bot)
