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
IPN_URL = "https://your-repl-url.repl.co/ipn"  # Replace with your actual Repl URL

MIN_DEPOSIT = 10  # Minimum deposit in USD

# Admin Configuration
ADMIN_ID = 123456789  # Replace with your Telegram user ID

# ----------------------------
# LOGGING
# ----------------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

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
# ADMIN FUNCTIONS
# ----------------------------
def is_admin(user_id):
    return user_id == ADMIN_ID

# ----------------------------
# START COMMAND
# ----------------------------
@dp.message(Command("start"))
async def start(message: types.Message):
    logging.info(f"Start command received from user {message.from_user.id}")
    user_id = message.from_user.id
    if user_id not in USERS:
        USERS[user_id] = {"balance": 0, "history": []}

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="View Products", callback_data="view_products"),
         InlineKeyboardButton(text="Deposit", callback_data="deposit")],
        [InlineKeyboardButton(text="Purchase History", callback_data="history")],
        [InlineKeyboardButton(text="Support", url="https://t.me/Legitplaysonly")]
    ])
    if is_admin(user_id):
        # Admin panel
        admin_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👥 User Stats", callback_data="admin_stats"),
             InlineKeyboardButton(text="💰 Revenue", callback_data="admin_revenue")],
            [InlineKeyboardButton(text="📊 Analytics", callback_data="admin_analytics"),
             InlineKeyboardButton(text="👤 User List", callback_data="admin_users")],
            [InlineKeyboardButton(text="🛒 Regular Shop", callback_data="regular_shop")]
        ])
        await message.answer("🔧 <b>Admin Panel</b>\n\nWelcome, Administrator!", reply_markup=admin_kb)
    else:
        await message.answer("Welcome to the Telegram Shop!", reply_markup=kb)

# ----------------------------
# CALLBACK HANDLERS
# ----------------------------
@dp.callback_query(F.data.in_(["view_products", "deposit", "history", "admin_stats", "admin_revenue", "admin_analytics", "admin_users", "regular_shop", "back_to_admin"]))
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
    
    # Admin Panel Callbacks
    elif call.data == "admin_stats" and is_admin(user_id):
        total_users = len(USERS)
        total_balance = sum(user_data["balance"] for user_data in USERS.values())
        active_users = len([u for u in USERS.values() if u["history"]])
        
        stats_text = f"📊 <b>Bot Statistics</b>\n\n"
        stats_text += f"👥 Total Users: {total_users}\n"
        stats_text += f"💰 Total Balance: ${total_balance}\n"
        stats_text += f"🔥 Active Users: {active_users}\n"
        
        await call.message.answer(stats_text)
    
    elif call.data == "admin_revenue" and is_admin(user_id):
        total_spent = 0
        for user_data in USERS.values():
            for transaction in user_data["history"]:
                if "Bought" in transaction:
                    # Extract price from transaction
                    price_start = transaction.find("$") + 1
                    price_end = transaction.find(" ", price_start)
                    if price_end == -1:
                        price_end = len(transaction)
                    try:
                        price = int(transaction[price_start:price_end])
                        total_spent += price
                    except:
                        pass
        
        revenue_text = f"💰 <b>Revenue Report</b>\n\n"
        revenue_text += f"💵 Total Revenue: ${total_spent}\n"
        revenue_text += f"🛒 Products Sold: {sum(len([h for h in u['history'] if 'Bought' in h]) for u in USERS.values())}\n"
        
        await call.message.answer(revenue_text)
    
    elif call.data == "admin_analytics" and is_admin(user_id):
        if not USERS:
            await call.message.answer("No user data available.")
        else:
            avg_balance = sum(u["balance"] for u in USERS.values()) / len(USERS)
            max_balance = max(u["balance"] for u in USERS.values())
            
            # Most popular product
            product_sales = {}
            for user_data in USERS.values():
                for transaction in user_data["history"]:
                    if "Bought" in transaction:
                        for idx, prod in enumerate(PRODUCTS):
                            if prod["name"] in transaction:
                                product_sales[prod["name"]] = product_sales.get(prod["name"], 0) + 1
            
            most_popular = max(product_sales.items(), key=lambda x: x[1]) if product_sales else ("None", 0)
            
            analytics_text = f"📈 <b>Analytics</b>\n\n"
            analytics_text += f"💰 Average Balance: ${avg_balance:.2f}\n"
            analytics_text += f"🔝 Highest Balance: ${max_balance}\n"
            analytics_text += f"🏆 Most Popular Product: {most_popular[0]} ({most_popular[1]} sales)\n"
            
            await call.message.answer(analytics_text)
    
    elif call.data == "admin_users" and is_admin(user_id):
        if not USERS:
            await call.message.answer("No users registered yet.")
        else:
            users_text = f"👤 <b>Registered Users</b>\n\n"
            for idx, (user_id_item, user_data) in enumerate(list(USERS.items())[:10]):  # Show first 10 users
                users_text += f"{idx+1}. ID: {user_id_item} | Balance: ${user_data['balance']} | Purchases: {len(user_data['history'])}\n"
            
            if len(USERS) > 10:
                users_text += f"\n... and {len(USERS) - 10} more users"
            
            await call.message.answer(users_text)
    
    elif call.data == "regular_shop" and is_admin(user_id):
        # Show regular shop interface for admin
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="View Products", callback_data="view_products"),
             InlineKeyboardButton(text="Deposit", callback_data="deposit")],
            [InlineKeyboardButton(text="Purchase History", callback_data="history")],
            [InlineKeyboardButton(text="🔧 Back to Admin", callback_data="back_to_admin")]
        ])
        await call.message.answer("🛒 Regular Shop Mode", reply_markup=kb)
    
    elif call.data == "back_to_admin" and is_admin(user_id):
        admin_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👥 User Stats", callback_data="admin_stats"),
             InlineKeyboardButton(text="💰 Revenue", callback_data="admin_revenue")],
            [InlineKeyboardButton(text="📊 Analytics", callback_data="admin_analytics"),
             InlineKeyboardButton(text="👤 User List", callback_data="admin_users")],
            [InlineKeyboardButton(text="🛒 Regular Shop", callback_data="regular_shop")]
        ])
        await call.message.answer("🔧 <b>Admin Panel</b>", reply_markup=admin_kb)

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
            await message.reply(f"💰 Deposit Invoice Created!\n\n💵 Amount: ${amount}\n🔗 Payment Link: {res_json['invoice_url']}\n\n⏰ Complete your payment to add funds to your balance.")
        else:
            logging.error(f"NOWPayments API Error: {res_json}")
            await message.reply("⚠️ Error creating payment invoice. Please try again later.")
    except Exception as e:
        logging.error(f"NOWPayments Request Error: {e}")
        await message.reply("⚠️ Error connecting to payment processor. Please try again later.")

# ----------------------------
# RUN BOT
# ----------------------------
async def main():
    try:
        logging.info("Starting bot...")
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Error running bot: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())