import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties

# ----------------------------
# CONFIGURATION
# ----------------------------
API_TOKEN = os.getenv("BOT_TOKEN")  # Get from environment (Render/Windows)
if not API_TOKEN:
    raise ValueError("❌ BOT_TOKEN is not set in environment variables!")

# ----------------------------
# LOGGING
# ----------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# ----------------------------
# BOT AND DISPATCHER
# ----------------------------
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# ----------------------------
# PRODUCTS
# ----------------------------
PRODUCTS = {
    "prod1": {"name": "Premium Subscription", "price": 10},
    "prod2": {"name": "VIP Access", "price": 25},
    "prod3": {"name": "Special Item", "price": 50},
}

# ----------------------------
# HANDLERS
# ----------------------------
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍️ Shop", callback_data="open_shop")]
    ])
    await message.answer("👋 Welcome! Use the menu below to browse our products.", reply_markup=keyboard)

@dp.callback_query(lambda c: c.data == "open_shop")
async def open_shop(callback_query: types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup()
    for key, product in PRODUCTS.items():
        keyboard.add(
            types.InlineKeyboardButton(
                text=f"{product['name']} - ${product['price']}",
                callback_data=f"buy:{key}"
            )
        )
    await callback_query.message.answer("🛒 Available products:", reply_markup=keyboard)
    await callback_query.answer()

@dp.callback_query(lambda c: c.data.startswith("buy:"))
async def process_buy(callback_query: types.CallbackQuery):
    product_id = callback_query.data.split(":")[1]
    product = PRODUCTS.get(product_id)
    if not product:
        await callback_query.answer("❌ Product not found", show_alert=True)
        return
    await callback_query.message.answer(f"✅ You selected <b>{product['name']}</b> for <b>${product['price']}</b>.")
    await callback_query.answer()

# ----------------------------
# MAIN
# ----------------------------
async def main():
    logging.info("🚀 Starting bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logging.error(f"❌ Error running bot: {e}")