import asyncio
import logging
import uuid
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ----------------------------
# CONFIGURATION
# ----------------------------
API_TOKEN = "8314185541:AAFDFgYP5CHLA8HVwvJBjcz0iXquepM2VWc"
NOWPAYMENTS_API_KEY = "WEP7ZF7-MJ44V90-G433PT9-HGDER2Q"
IPN_URL = "https://8815990bfd405cb8cb93e8ea52d9ff2f.serveo.net/ipn"  # Replace with your Serveo URL

MIN_DEPOSIT = 10  # Minimum deposit in USD

# ----------------------------
# LOGGING
# ----------------------------
logging.basicConfig(level=logging.INFO)

# ----------------------------
# BOT AND DISPATCHER
# ----------------------------
bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
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
@dp.message(commands=["start"])
async def start(message: types.Message):
    user_id = message.from_user.id
    if user_id not in USERS:
        USERS[user_id] = {"balance": 0, "history": []}

    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("View Products", callback_data="view_products"),
        InlineKeyboardButton("Deposit", callback_data="deposit"),
        InlineKeyboardButton("Purchase History", callback_data="history"),
        InlineKeyboardButton("Support", url="https://t.me/YOUR_SUPPORT_USERNAME")
    )
    await message.answer("Welcome to the Telegram Shop!", reply_markup=kb)

# ----------------------------
# CALLBACK HANDLERS
# ----------------------------
@dp.callback_query(lambda c: True)
async def callbacks(call: types.CallbackQuery):
    user_id = call.from_user.id
    if user_id not in USERS:
        USERS[user_id] = {"balance": 0, "history": []}

    if call.data == "view_products":
        kb = InlineKeyboardMarkup()
        for idx, prod in enumerate(PRODUCTS):
            kb.add(InlineKeyboardButton(f"{prod['name']} - ${prod['price']}", callback_data=f"buy_{idx}"))
        await call.message.answer("Available Products:", reply_markup=kb)

    elif call.data.startswith("buy_"):
        idx = int(call.data.split("_")[1])
        product = PRODUCTS[idx]
        if USERS[user_id]["balance"] >= product["price"]:
            USERS[user_id]["balance"] -= product["price"]
            USERS[user_id]["history"].append(f"Bought {product['name']} for ${product['price']}")
            await call.message.answer(f"You bought {product['name']}! Remaining balance: ${USERS[user_id]['balance']}")
        else:
            await call.message.answer(f"Not enough balance. Please deposit at least ${product['price'] - USERS[user_id]['balance']} more.")

    elif call.data == "history":
        history = USERS[user_id]["history"]
        if not history:
            await call.message.answer("No purchase history yet.")
        else:
            await call.message.answer("\n".join(history))

    elif call.data == "deposit":
        await call.message.answer(f"Minimum deposit: ${MIN_DEPOSIT}\nSend the amount in USD.")

# ----------------------------
# MESSAGE HANDLER FOR DEPOSITS
# ----------------------------
@dp.message(lambda message: message.text.isdigit())
async def handle_deposit(message: types.Message):
    user_id = message.from_user.id
    amount = int(message.text)
    if amount < MIN_DEPOSIT:
        await message.reply(f"Minimum deposit is ${MIN_DEPOSIT}. Please enter a valid amount.")
        return

    order_id = str(uuid.uuid4())
    payment_data = {
        "price_amount": amount,
        "price_currency": "USD",
        "order_id": order_id,
        "ipn_callback_url": IPN_URL
    }

    headers = {
        "x-api-key": NOWPAYMENTS_API_KEY,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post("https://api.nowpayments.io/v1/invoice", json=payment_data, headers=headers)
        res_json = response.json()
        if response.status_code == 200 and "invoice_url" in res_json:
            await message.reply(f"Deposit created! Pay here: {res_json['invoice_url']}")
        else:
            logging.error(res_json)
            await message.reply("⚠️ Error creating payment. Try again later.")
    except Exception as e:
        logging.error(e)
        await message.reply("⚠️ Error creating payment. Try again later.")

# ----------------------------
# RUN BOT
# ----------------------------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())