import asyncio
import logging
import uuid
import requests
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties

# ----------------------------
# CONFIGURATION
# ----------------------------
API_TOKEN = "8314185541:AAFDFgYP5CHLA8HVwvJBjcz0iXquepM2VWc"
NOWPAYMENTS_API_KEY = "WEP7ZF7-MJ44V90-G433PT9-HGDER2Q"
IPN_URL = ""  # Replace with your Serveo URL

MIN_DEPOSIT = 10  # Minimum deposit in USD

# ----------------------------
# LOGGING
# ----------------------------
logging.basicConfig(level=logging.INFO)

# ----------------------------
# BOT AND DISPATCHER
# ----------------------------
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Dummy products
PRODUCTS = [
    {"name": "Product A", "price": 15},
    {"name": "Product B", "price": 25},
    {"name": "Product C", "price": 50},
]

# In-memory storage
USERS = {}

# ----------------------------
# START COMMAND
# ----------------------------
@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id
    if user_id not in USERS:
        USERS[user_id] = {"balance": 0, "history": []}

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="View Products", callback_data="view_products"),
         InlineKeyboardButton(text="Deposit", callback_data="deposit")],
        [InlineKeyboardButton(text="Purchase History", callback_data="history")],
        [InlineKeyboardButton(text="Support", url="https://t.me/YOUR_SUPPORT_USERNAME")]
    ])
    await message.answer("Welcome to the Telegram Shop!", reply_markup=kb)

# ----------------------------
# CALLBACK HANDLERS
# ----------------------------
@dp.callback_query(F.data.in_(["view_products", "deposit", "history"]))
async def callbacks(call: types.CallbackQuery):
    user_id = call.from_user.id
    if user_id not in USERS:
        USERS[user_id] = {"balance": 0, "history": []}

    if call.data == "view_products":
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"{prod['name']} - ${prod['price']}", callback_data=f"buy_{idx}")]
            for idx, prod in enumerate(PRODUCTS)
        ])
        await call.message.answer("Available Products:", reply_markup=kb)

    elif call.data == "history":
        history = USERS[user_id]["history"]
        if not history:
            await call.message.answer("No purchase history yet.")
        else:
            await call.message.answer("\n".join(history))

    elif call.data == "deposit":
        await call.message.answer(f"Minimum deposit: ${MIN_DEPOSIT}\nSend the amount in USD.")

    await call.answer()

@dp.callback_query(F.data.startswith("buy_"))
async def buy_product(call: types.CallbackQuery):
    user_id = call.from_user.id
    if user_id not in USERS:
        USERS[user_id] = {"balance": 0, "history": []}

    idx = int(call.data.split("_")[1])
    product = PRODUCTS[idx]
    if USERS[user_id]["balance"] >= product["price"]:
        USERS[user_id]["balance"] -= product["price"]
        USERS[user_id]["history"].append(f"Bought {product['name']} for ${product['price']}")
        await call.message.answer(f"You bought {product['name']}! Remaining balance: ${USERS[user_id]['balance']}")
    else:
        await call.message.answer(f"Not enough balance. Please deposit at least ${product['price'] - USERS[user_id]['balance']} more.")
    
    await call.answer()

# ----------------------------
# MESSAGE HANDLER FOR DEPOSITS
# ----------------------------
@dp.message(F.text.regexp(r'^\d+$'))
async def handle_deposit(message: types.Message):
    user_id = message.from_user.id
    if user_id not in USERS:
        USERS[user_id] = {"balance": 0, "history": []}
    
    amount = int(message.text)
    if amount < MIN_DEPOSIT:
        await message.reply(f"Minimum deposit is ${MIN_DEPOSIT}. Please enter a valid amount.")
        return

    # Add amount directly to user's balance
    USERS[user_id]["balance"] += amount
    USERS[user_id]["history"].append(f"Deposited ${amount}")
    
    await message.reply(f"✅ Successfully deposited ${amount}!\nYour balance: ${USERS[user_id]['balance']}")

# ----------------------------
# RUN BOT
# ----------------------------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())