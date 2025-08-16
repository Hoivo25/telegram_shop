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
ADMIN_ID = 1802596609  # Replace with your Telegram user ID

# ----------------------------
# LOGGING
# ----------------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# ----------------------------
# BOT AND DISPATCHER
# ----------------------------
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Products with 40% of card values - Page 1 (1-10)
PRODUCTS_PAGE_1 = [
    {"name": "Card 1", "price": 127},  # 40% of $317.39
    {"name": "Card 2", "price": 124},  # 40% of $310.15
    {"name": "Card 3", "price": 121},  # 40% of $303.42
    {"name": "Card 4", "price": 121},  # 40% of $303.34
    {"name": "Card 5", "price": 120},  # 40% of $300.00
    {"name": "Card 6", "price": 120},  # 40% of $300.00
    {"name": "Card 7", "price": 118},  # 40% of $294.82
    {"name": "Card 8", "price": 118},  # 40% of $294.17
    {"name": "Card 9", "price": 117},  # 40% of $292.72
    {"name": "Card 10", "price": 117}, # 40% of $292.32
]

# Products with 40% of card values - Page 2 (1-10)
PRODUCTS_PAGE_2 = [
    {"name": "Card 1", "price": 13},   # 40% of $33.66
    {"name": "Card 2", "price": 13},   # 40% of $33.47
    {"name": "Card 3", "price": 13},   # 40% of $33.40
    {"name": "Card 4", "price": 13},   # 40% of $33.06
    {"name": "Card 5", "price": 13},   # 40% of $32.98
    {"name": "Card 6", "price": 13},   # 40% of $32.93
    {"name": "Card 7", "price": 13},   # 40% of $32.70
    {"name": "Card 8", "price": 13},   # 40% of $32.61
    {"name": "Card 9", "price": 13},   # 40% of $32.57
    {"name": "Card 10", "price": 13},  # 40% of $32.51
]

# Products with 40% of card values - Page 3 (1-10)
PRODUCTS_PAGE_3 = [
    {"name": "Card 1", "price": 62},   # 40% of $154.16
    {"name": "Card 2", "price": 60},   # 40% of $150.00
    {"name": "Card 3", "price": 60},   # 40% of $150.00
    {"name": "Card 4", "price": 59},   # 40% of $146.81
    {"name": "Card 5", "price": 58},   # 40% of $144.78
    {"name": "Card 6", "price": 57},   # 40% of $142.66
    {"name": "Card 7", "price": 57},   # 40% of $142.45
    {"name": "Card 8", "price": 57},   # 40% of $141.82
    {"name": "Card 9", "price": 63},   # 45% of $140.00
    {"name": "Card 10", "price": 56},  # 40% of $139.65
]

# Products with 40-45% of card values - Page 4 (1-10)
PRODUCTS_PAGE_4 = [
    {"name": "Card 1", "price": 55},   # 40% of $136.68
    {"name": "Card 2", "price": 61},   # 45% of $136.48
    {"name": "Card 3", "price": 61},   # 45% of $135.80
    {"name": "Card 4", "price": 53},   # 40% of $132.19
    {"name": "Card 5", "price": 52},   # 40% of $129.88
    {"name": "Card 6", "price": 57},   # 45% of $127.56
    {"name": "Card 7", "price": 50},   # 40% of $125.00
    {"name": "Card 8", "price": 49},   # 40% of $123.58
    {"name": "Card 9", "price": 49},   # 40% of $122.19
    {"name": "Card 10", "price": 49},  # 40% of $121.31
]

# Products with 40-45% of card values - Page 5 (1-10)
PRODUCTS_PAGE_5 = [
    {"name": "Card 1", "price": 54},   # 45% of $120.00
    {"name": "Card 2", "price": 47},   # 40% of $118.22
    {"name": "Card 3", "price": 47},   # 40% of $116.80
    {"name": "Card 4", "price": 46},   # 40% of $115.00
    {"name": "Card 5", "price": 44},   # 40% of $110.37
    {"name": "Card 6", "price": 44},   # 40% of $110.00
    {"name": "Card 7", "price": 44},   # 40% of $109.84
    {"name": "Card 8", "price": 44},   # 40% of $108.86
    {"name": "Card 9", "price": 45},   # 45% of $100.00
    {"name": "Card 10", "price": 45},  # 45% of $100.00
]

# Products with 40-45% of card values - Page 6 (1-10)
PRODUCTS_PAGE_6 = [
    {"name": "Card 1", "price": 45},   # 45% of $100.00
    {"name": "Card 2", "price": 40},   # 40% of $100.00
    {"name": "Card 3", "price": 45},   # 45% of $100.00
    {"name": "Card 4", "price": 40},   # 40% of $100.00
    {"name": "Card 5", "price": 45},   # 45% of $100.00
    {"name": "Card 6", "price": 45},   # 45% of $100.00
    {"name": "Card 7", "price": 40},   # 40% of $100.00
    {"name": "Card 8", "price": 45},   # 45% of $100.00
    {"name": "Card 9", "price": 45},   # 45% of $100.00
    {"name": "Card 10", "price": 45},  # 45% of $100.00
]

# Products with 40-45% of card values - Page 7 (1-10)
PRODUCTS_PAGE_7 = [
    {"name": "Card 1", "price": 167},  # 40% of $417.45
    {"name": "Card 2", "price": 180},  # 45% of $400.00
    {"name": "Card 3", "price": 156},  # 45% of $346.61
    {"name": "Card 4", "price": 136},  # 40% of $340.00
    {"name": "Card 5", "price": 135},  # 45% of $300.00
    {"name": "Card 6", "price": 120},  # 40% of $300.00
    {"name": "Card 7", "price": 135},  # 45% of $300.00
    {"name": "Card 8", "price": 116},  # 40% of $288.93
    {"name": "Card 9", "price": 113},  # 40% of $281.37
    {"name": "Card 10", "price": 108}, # 40% of $270.00
]

# Products with 40-45% of card values - Page 8 (1-10)
PRODUCTS_PAGE_8 = [
    {"name": "Card 1", "price": 107},  # 40% of $267.08
    {"name": "Card 2", "price": 67},   # 40% of $167.08
    {"name": "Card 3", "price": 187},  # 40% of $467.04
    {"name": "Card 4", "price": 67},   # 40% of $167.00
    {"name": "Card 5", "price": 107},  # 40% of $266.95
    {"name": "Card 6", "price": 107},  # 40% of $266.50
    {"name": "Card 7", "price": 165},  # 45% of $366.40
    {"name": "Card 8", "price": 66},   # 40% of $166.11
    {"name": "Card 9", "price": 120},  # 45% of $265.98
    {"name": "Card 10", "price": 146}, # 40% of $365.85
]

# Products with 40% of card values - Page 9 (1-10)
PRODUCTS_PAGE_9 = [
    {"name": "Card 1", "price": 63},   # 40% of $156.49
    {"name": "Card 2", "price": 63},   # 40% of $156.43
    {"name": "Card 3", "price": 63},   # 40% of $156.42
    {"name": "Card 4", "price": 62},   # 40% of $155.22
    {"name": "Card 5", "price": 62},   # 40% of $155.13
    {"name": "Card 6", "price": 62},   # 40% of $155.07
    {"name": "Card 7", "price": 62},   # 40% of $155.02
    {"name": "Card 8", "price": 62},   # 40% of $155.01
    {"name": "Card 9", "price": 62},   # 40% of $155.00
    {"name": "Card 10", "price": 62},  # 40% of $155.00
]

# Products with 40-45% of card values - Page 10 (1-10)
PRODUCTS_PAGE_10 = [
    {"name": "Card 1", "price": 23},   # 45% of $50.00
    {"name": "Card 2", "price": 20},   # 40% of $50.00
    {"name": "Card 3", "price": 23},   # 45% of $50.00
    {"name": "Card 4", "price": 20},   # 40% of $50.00
    {"name": "Card 5", "price": 20},   # 40% of $50.00
    {"name": "Card 6", "price": 20},   # 40% of $50.00
    {"name": "Card 7", "price": 20},   # 40% of $50.00
    {"name": "Card 8", "price": 20},   # 40% of $50.00
    {"name": "Card 9", "price": 20},   # 40% of $50.00
    {"name": "Card 10", "price": 20},  # 40% of $50.00
]

# Combined products for backwards compatibility
PRODUCTS = PRODUCTS_PAGE_1 + PRODUCTS_PAGE_2 + PRODUCTS_PAGE_3 + PRODUCTS_PAGE_4 + PRODUCTS_PAGE_5 + PRODUCTS_PAGE_6 + PRODUCTS_PAGE_7 + PRODUCTS_PAGE_8 + PRODUCTS_PAGE_9 + PRODUCTS_PAGE_10

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
    user_balance = USERS[user_id]["balance"]
    
    if is_admin(user_id):
        # Admin panel
        admin_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👥 User Stats", callback_data="admin_stats"),
             InlineKeyboardButton(text="💰 Revenue", callback_data="admin_revenue")],
            [InlineKeyboardButton(text="📊 Analytics", callback_data="admin_analytics"),
             InlineKeyboardButton(text="👤 User List", callback_data="admin_users")],
            [InlineKeyboardButton(text="🛍️ Manage Products", callback_data="admin_products"),
             InlineKeyboardButton(text="🛒 Regular Shop", callback_data="regular_shop")]
        ])
        await message.answer(f"🔧 <b>Admin Panel</b>\n\nWelcome, Administrator!\n💰 Your Balance: ${user_balance}", reply_markup=admin_kb)
    else:
        await message.answer(f"Welcome to the Prepaids Shop!\n💰 Your Balance: ${user_balance}", reply_markup=kb)

# ----------------------------
# CALLBACK HANDLERS
# ----------------------------
@dp.callback_query(F.data.in_(["view_products", "deposit", "history", "admin_stats", "admin_revenue", "admin_analytics", "admin_users", "regular_shop", "back_to_admin", "admin_products", "admin_add_product", "admin_edit_product", "admin_delete_product", "cards_page_2", "cards_page_3", "cards_page_4", "cards_page_5", "cards_page_6", "cards_page_7", "cards_page_8", "cards_page_9", "cards_page_10"]))
async def callbacks(call: types.CallbackQuery):
    user_id = call.from_user.id
    if user_id not in USERS:
        USERS[user_id] = {"balance": 0, "history": []}

    if call.data == "view_products":
        # Card listings - Page 1
        card_text = "🏦 <b>Available Cards - Page 1</b>\n\n"
        card_text += "1. 435880xx:US$317.39: 🔒 at 40%\n"
        card_text += "2. 435880xx:US$310.15: 🔒 at 40%\n"
        card_text += "3. 435880xx:US$303.42: 🔒 at 40%\n"
        card_text += "4. 435880xx:US$303.34: 🔒 at 40%\n"
        card_text += "5. 435880xx:US$300.00: 🔒 at 40%\n"
        card_text += "6. 435880xx:US$300.00: 🔒 at 40%\n"
        card_text += "7. 511332xx:US$294.82: 🔒 at 40%\n"
        card_text += "8. 435880xx:US$294.17: 🔒 at 40%\n"
        card_text += "9. 435880xx:US$292.72: 🔒 at 40%\n"
        card_text += "10. 435880xx:US$292.32: 🔒 at 40%\n\n"
        card_text += "<b>Legend:</b>\n"
        card_text += "🔒 - Card is registered\n"
        card_text += "✅ - Card is not registered\n"
        card_text += "⚠️ - Card has been used on Google\n\n"
        
        card_text += "<b>Products (1-10):</b>"
        
        # Create keyboard with only page 1 products
        product_buttons = [
            [InlineKeyboardButton(text=f"{idx+1}. {prod['name']} - ${prod['price']}", callback_data=f"buy_page1_{idx}")]
            for idx, prod in enumerate(PRODUCTS_PAGE_1)
        ]
        # Add pagination button
        product_buttons.append([InlineKeyboardButton(text="➡️ Next Page", callback_data="cards_page_2")])
        
        kb = InlineKeyboardMarkup(inline_keyboard=product_buttons)
        await call.message.answer(card_text, reply_markup=kb)

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

    elif call.data == "admin_products" and is_admin(user_id):
        # Product management interface
        product_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Add Product", callback_data="admin_add_product"),
             InlineKeyboardButton(text="📝 Edit Product", callback_data="admin_edit_product")],
            [InlineKeyboardButton(text="🗑️ Delete Product", callback_data="admin_delete_product")],
            [InlineKeyboardButton(text="🔙 Back to Admin Panel", callback_data="back_to_admin")]
        ])
        await call.message.answer("🛍️ <b>Product Management</b>", reply_markup=product_kb)

    elif call.data == "admin_add_product" and is_admin(user_id):
        await call.message.answer("➕ <b>Add New Product</b>\n\nSend product details in this format:\nADD:Product Name:Price\n\nExample: ADD:Premium Account:30")

    elif call.data == "admin_edit_product" and is_admin(user_id):
        if not PRODUCTS:
            await call.message.answer("No products available to edit.")
        else:
            products_text = "📝 <b>Edit Product</b>\n\nCurrent Products:\n"
            for idx, prod in enumerate(PRODUCTS):
                products_text += f"{idx}. {prod['name']} - ${prod['price']}\n"
            products_text += "\nTo edit, send: EDIT:ProductIndex:NewName:NewPrice\nExample: EDIT:0:New Product Name:25"
            await call.message.answer(products_text)

    elif call.data == "admin_delete_product" and is_admin(user_id):
        if not PRODUCTS:
            await call.message.answer("No products available to delete.")
        else:
            products_text = "🗑️ <b>Delete Product</b>\n\nCurrent Products:\n"
            for idx, prod in enumerate(PRODUCTS):
                products_text += f"{idx}. {prod['name']} - ${prod['price']}\n"
            products_text += "\nTo delete, send: DELETE:ProductIndex\nExample: DELETE:0"
            await call.message.answer(products_text)

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
            [InlineKeyboardButton(text="🛍️ Manage Products", callback_data="admin_products"),
             InlineKeyboardButton(text="🛒 Regular Shop", callback_data="regular_shop")]
        ])
        await call.message.answer("🔧 <b>Admin Panel</b>", reply_markup=admin_kb)

    elif call.data == "cards_page_2":
        # Card listings - Page 2
        card_text = "🏦 <b>Available Cards - Page 2</b>\n\n"
        card_text += "1. 435880xx:US$33.66: ✅ at 40% ⚠️\n"
        card_text += "2. 403446xx:US$33.47: ✅ at 40%\n"
        card_text += "3. 403446xx:US$33.40: 🔒 at 40%\n"
        card_text += "4. 451129xx:US$33.06: 🔒 at 40% ⚠️\n"
        card_text += "5. 435880xx:US$32.98: 🔒 at 40%\n"
        card_text += "6. 435880xx:US$32.93: 🔒 at 40%\n"
        card_text += "7. 403446xx:US$32.70: ✅ at 40%\n"
        card_text += "8. 491277xx:US$32.61: ✅ at 40%\n"
        card_text += "9. 403446xx:US$32.57: ✅ at 40%\n"
        card_text += "10. 435880xx:US$32.51: 🔒 at 40%\n\n"
        card_text += "<b>Legend:</b>\n"
        card_text += "🔒 - Card is registered\n"
        card_text += "✅ - Card is not registered\n"
        card_text += "⚠️ - Card has been used on Google\n\n"
        
        card_text += "<b>Products (1-10):</b>"
        
        # Create keyboard with only page 2 products (numbered 1-10)
        product_buttons = [
            [InlineKeyboardButton(text=f"{idx+1}. {prod['name']} - ${prod['price']}", callback_data=f"buy_page2_{idx}")]
            for idx, prod in enumerate(PRODUCTS_PAGE_2)
        ]
        # Add navigation buttons
        nav_buttons = [
            InlineKeyboardButton(text="⬅️ Previous Page", callback_data="view_products"),
            InlineKeyboardButton(text="➡️ Next Page", callback_data="cards_page_3")
        ]
        product_buttons.append(nav_buttons)
        
        kb = InlineKeyboardMarkup(inline_keyboard=product_buttons)
        await call.message.answer(card_text, reply_markup=kb)

    elif call.data == "cards_page_3":
        # Card listings - Page 3
        card_text = "🏦 <b>Available Cards - Page 3</b>\n\n"
        card_text += "1. 435880xx:US$154.16: 🔒 at 40%\n"
        card_text += "2. 435880xx:US$150.00: 🔒 at 40%\n"
        card_text += "3. 435880xx:US$150.00: 🔒 at 40%\n"
        card_text += "4. 435880xx:US$146.81: 🔒 at 40%\n"
        card_text += "5. 511332xx:US$144.78: 🔒 at 40%\n"
        card_text += "6. 435880xx:US$142.66: 🔒 at 40%\n"
        card_text += "7. 403446xx:US$142.45: 🔒 at 40%\n"
        card_text += "8. 435880xx:US$141.82: 🔒 at 40%\n"
        card_text += "9. 511332xx:US$140.00: 🔒 at 45%\n"
        card_text += "10. 403446xx:US$139.65: 🔒 at 40%\n\n"
        card_text += "<b>Legend:</b>\n"
        card_text += "🔒 - Card is registered\n"
        card_text += "✅ - Card is not registered\n"
        card_text += "⚠️ - Card has been used on Google\n\n"
        
        card_text += "<b>Products (1-10):</b>"
        
        # Create keyboard with only page 3 products (numbered 1-10)
        product_buttons = [
            [InlineKeyboardButton(text=f"{idx+1}. {prod['name']} - ${prod['price']}", callback_data=f"buy_page3_{idx}")]
            for idx, prod in enumerate(PRODUCTS_PAGE_3)
        ]
        # Add navigation buttons
        nav_buttons = [
            InlineKeyboardButton(text="⬅️ Previous Page", callback_data="cards_page_2"),
            InlineKeyboardButton(text="➡️ Next Page", callback_data="cards_page_4")
        ]
        product_buttons.append(nav_buttons)
        
        kb = InlineKeyboardMarkup(inline_keyboard=product_buttons)
        await call.message.answer(card_text, reply_markup=kb)

    elif call.data == "cards_page_4":
        # Card listings - Page 4
        card_text = "🏦 <b>Available Cards - Page 4</b>\n\n"
        card_text += "1. 435880xx:US$136.68: 🔒 at 40%\n"
        card_text += "2. 435880xx:US$136.48: 🔒 at 45%\n"
        card_text += "3. 403446xx:US$135.80: 🔒 at 45%\n"
        card_text += "4. 435880xx:US$132.19: 🔒 at 40%\n"
        card_text += "5. 435880xx:US$129.88: 🔒 at 40%\n"
        card_text += "6. 403446xx:US$127.56: 🔒 at 45%\n"
        card_text += "7. 435880xx:US$125.00: 🔒 at 40%\n"
        card_text += "8. 435880xx:US$123.58: 🔒 at 40%\n"
        card_text += "9. 435880xx:US$122.19: 🔒 at 40%\n"
        card_text += "10. 403446xx:US$121.31: 🔒 at 40%\n\n"
        card_text += "<b>Legend:</b>\n"
        card_text += "🔒 - Card is registered\n"
        card_text += "✅ - Card is not registered\n"
        card_text += "⚠️ - Card has been used on Google\n\n"
        
        card_text += "<b>Products (1-10):</b>"
        
        # Create keyboard with only page 4 products (numbered 1-10)
        product_buttons = [
            [InlineKeyboardButton(text=f"{idx+1}. {prod['name']} - ${prod['price']}", callback_data=f"buy_page4_{idx}")]
            for idx, prod in enumerate(PRODUCTS_PAGE_4)
        ]
        # Add navigation buttons
        nav_buttons = [
            InlineKeyboardButton(text="⬅️ Previous Page", callback_data="cards_page_3"),
            InlineKeyboardButton(text="➡️ Next Page", callback_data="cards_page_5")
        ]
        product_buttons.append(nav_buttons)
        
        kb = InlineKeyboardMarkup(inline_keyboard=product_buttons)
        await call.message.answer(card_text, reply_markup=kb)

    elif call.data == "cards_page_5":
        # Card listings - Page 5
        card_text = "🏦 <b>Available Cards - Page 5</b>\n\n"
        card_text += "1. 435880xx:US$120.00: 🔒 at 45%\n"
        card_text += "2. 435880xx:US$118.22: 🔒 at 40%\n"
        card_text += "3. 435880xx:US$116.80: 🔒 at 40%\n"
        card_text += "4. 451129xx:US$115.00: 🔒 at 40%\n"
        card_text += "5. 403446xx:US$110.37: 🔒 at 40%\n"
        card_text += "6. 435880xx:US$110.00: 🔒 at 40%\n"
        card_text += "7. 435880xx:US$109.84: 🔒 at 40%\n"
        card_text += "8. 435880xx:US$108.86: 🔒 at 40%\n"
        card_text += "9. 403446xx:US$100.00: 🔒 at 45%\n"
        card_text += "10. 403446xx:US$100.00: 🔒 at 45%\n\n"
        card_text += "<b>Legend:</b>\n"
        card_text += "🔒 - Card is registered\n"
        card_text += "✅ - Card is not registered\n"
        card_text += "⚠️ - Card has been used on Google\n\n"
        
        card_text += "<b>Products (1-10):</b>"
        
        # Create keyboard with only page 5 products (numbered 1-10)
        product_buttons = [
            [InlineKeyboardButton(text=f"{idx+1}. {prod['name']} - ${prod['price']}", callback_data=f"buy_page5_{idx}")]
            for idx, prod in enumerate(PRODUCTS_PAGE_5)
        ]
        # Add navigation buttons
        nav_buttons = [
            InlineKeyboardButton(text="⬅️ Previous Page", callback_data="cards_page_4"),
            InlineKeyboardButton(text="➡️ Next Page", callback_data="cards_page_6")
        ]
        product_buttons.append(nav_buttons)
        
        kb = InlineKeyboardMarkup(inline_keyboard=product_buttons)
        await call.message.answer(card_text, reply_markup=kb)

    elif call.data == "cards_page_6":
        # Card listings - Page 6
        card_text = "🏦 <b>Available Cards - Page 6</b>\n\n"
        card_text += "1. 403446xx:US$100.00: 🔒 at 45%\n"
        card_text += "2. 451129xx:US$100.00: 🔒 at 40%\n"
        card_text += "3. 403446xx:US$100.00: 🔒 at 45%\n"
        card_text += "4. 451129xx:US$100.00: 🔒 at 40%\n"
        card_text += "5. 435880xx:US$100.00: 🔒 at 45%\n"
        card_text += "6. 435880xx:US$100.00: 🔒 at 45%\n"
        card_text += "7. 451129xx:US$100.00: 🔒 at 40%\n"
        card_text += "8. 403446xx:US$100.00: 🔒 at 45%\n"
        card_text += "9. 435880xx:US$100.00: 🔒 at 45%\n"
        card_text += "10. 403446xx:US$100.00: 🔒 at 45%\n\n"
        card_text += "<b>Legend:</b>\n"
        card_text += "🔒 - Card is registered\n"
        card_text += "✅ - Card is not registered\n"
        card_text += "⚠️ - Card has been used on Google\n\n"
        
        card_text += "<b>Products (1-10):</b>"
        
        # Create keyboard with only page 6 products (numbered 1-10)
        product_buttons = [
            [InlineKeyboardButton(text=f"{idx+1}. {prod['name']} - ${prod['price']}", callback_data=f"buy_page6_{idx}")]
            for idx, prod in enumerate(PRODUCTS_PAGE_6)
        ]
        # Add navigation buttons
        nav_buttons = [
            InlineKeyboardButton(text="⬅️ Previous Page", callback_data="cards_page_5"),
            InlineKeyboardButton(text="➡️ Next Page", callback_data="cards_page_7")
        ]
        product_buttons.append(nav_buttons)
        
        kb = InlineKeyboardMarkup(inline_keyboard=product_buttons)
        await call.message.answer(card_text, reply_markup=kb)

    elif call.data == "cards_page_7":
        # Card listings - Page 7
        card_text = "🏦 <b>Available Cards - Page 7</b>\n\n"
        card_text += "1. 435880xx:US$417.45: ✅ at 40%\n"
        card_text += "2. 435880xx:US$400.00: 🔒 at 45%\n"
        card_text += "3. 435880xx:US$346.61: 🔒 at 45%\n"
        card_text += "4. 511332xx:US$340.00: ✅ at 40%\n"
        card_text += "5. 435880xx:US$300.00: 🔒 at 45%\n"
        card_text += "6. 435880xx:US$300.00: 🔒 at 40%\n"
        card_text += "7. 435880xx:US$300.00: 🔒 at 45%\n"
        card_text += "8. 435880xx:US$288.93: 🔒 at 40%\n"
        card_text += "9. 435880xx:US$281.37: ✅ at 40%\n"
        card_text += "10. 435880xx:US$270.00: 🔒 at 40%\n\n"
        card_text += "<b>Legend:</b>\n"
        card_text += "🔒 - Card is registered\n"
        card_text += "✅ - Card is not registered\n"
        card_text += "⚠️ - Card has been used on Google\n\n"
        
        card_text += "<b>Products (1-10):</b>"
        
        # Create keyboard with only page 7 products (numbered 1-10)
        product_buttons = [
            [InlineKeyboardButton(text=f"{idx+1}. {prod['name']} - ${prod['price']}", callback_data=f"buy_page7_{idx}")]
            for idx, prod in enumerate(PRODUCTS_PAGE_7)
        ]
        # Add navigation buttons
        nav_buttons = [
            InlineKeyboardButton(text="⬅️ Previous Page", callback_data="cards_page_6"),
            InlineKeyboardButton(text="➡️ Next Page", callback_data="cards_page_8")
        ]
        product_buttons.append(nav_buttons)
        
        kb = InlineKeyboardMarkup(inline_keyboard=product_buttons)
        await call.message.answer(card_text, reply_markup=kb)

    elif call.data == "cards_page_8":
        # Card listings - Page 8
        card_text = "🏦 <b>Available Cards - Page 8</b>\n\n"
        card_text += "1. 511332xx:US$267.08: ✅ at 40%\n"
        card_text += "2. 435880xx:US$167.08: 🔒 at 40%\n"
        card_text += "3. 435880xx:US$467.04: 🔒 at 40%\n"
        card_text += "4. 403446xx:US$167.00: 🔒 at 40%\n"
        card_text += "5. 435880xx:US$266.95: ✅ at 40% ⚠️\n"
        card_text += "6. 435880xx:US$266.50: ✅ at 40%\n"
        card_text += "7. 435880xx:US$366.40: 🔒 at 45%\n"
        card_text += "8. 403446xx:US$166.11: 🔒 at 40%\n"
        card_text += "9. 403446xx:US$265.98: 🔒 at 45%\n"
        card_text += "10. 403446xx:US$365.85: 🔒 at 40%\n\n"
        card_text += "<b>Legend:</b>\n"
        card_text += "🔒 - Card is registered\n"
        card_text += "✅ - Card is not registered\n"
        card_text += "⚠️ - Card has been used on Google\n\n"
        
        card_text += "<b>Products (1-10):</b>"
        
        # Create keyboard with only page 8 products (numbered 1-10)
        product_buttons = [
            [InlineKeyboardButton(text=f"{idx+1}. {prod['name']} - ${prod['price']}", callback_data=f"buy_page8_{idx}")]
            for idx, prod in enumerate(PRODUCTS_PAGE_8)
        ]
        # Add navigation buttons
        nav_buttons = [
            InlineKeyboardButton(text="⬅️ Previous Page", callback_data="cards_page_7"),
            InlineKeyboardButton(text="➡️ Next Page", callback_data="cards_page_9")
        ]
        product_buttons.append(nav_buttons)
        
        kb = InlineKeyboardMarkup(inline_keyboard=product_buttons)
        await call.message.answer(card_text, reply_markup=kb)

    elif call.data == "cards_page_9":
        # Card listings - Page 9
        card_text = "🏦 <b>Available Cards - Page 9</b>\n\n"
        card_text += "1. 435880xx:US$156.49: 🔒 at 40%\n"
        card_text += "2. 403446xx:US$156.43: 🔒 at 40%\n"
        card_text += "3. 435880xx:US$156.42: 🔒 at 40%\n"
        card_text += "4. 435880xx:US$155.22: ✅ at 40%\n"
        card_text += "5. 435880xx:US$155.13: 🔒 at 40%\n"
        card_text += "6. 511332xx:US$155.07: ✅ at 40%\n"
        card_text += "7. 511332xx:US$155.02: ✅ at 40%\n"
        card_text += "8. 435880xx:US$155.01: ✅ at 40%\n"
        card_text += "9. 435880xx:US$155.00: ✅ at 40%\n"
        card_text += "10. 435880xx:US$155.00: ✅ at 40%\n\n"
        card_text += "<b>Legend:</b>\n"
        card_text += "🔒 - Card is registered\n"
        card_text += "✅ - Card is not registered\n"
        card_text += "⚠️ - Card has been used on Google\n\n"
        
        card_text += "<b>Products (1-10):</b>"
        
        # Create keyboard with only page 9 products (numbered 1-10)
        product_buttons = [
            [InlineKeyboardButton(text=f"{idx+1}. {prod['name']} - ${prod['price']}", callback_data=f"buy_page9_{idx}")]
            for idx, prod in enumerate(PRODUCTS_PAGE_9)
        ]
        # Add navigation buttons
        nav_buttons = [
            InlineKeyboardButton(text="⬅️ Previous Page", callback_data="cards_page_8"),
            InlineKeyboardButton(text="➡️ Next Page", callback_data="cards_page_10")
        ]
        product_buttons.append(nav_buttons)
        
        kb = InlineKeyboardMarkup(inline_keyboard=product_buttons)
        await call.message.answer(card_text, reply_markup=kb)

    elif call.data == "cards_page_10":
        # Card listings - Page 10
        card_text = "🏦 <b>Available Cards - Page 10</b>\n\n"
        card_text += "1. 403446xx:US$50.00: 🔒 at 45%\n"
        card_text += "2. 435880xx:US$50.00: 🔒 at 40%\n"
        card_text += "3. 435880xx:US$50.00: 🔒 at 45%\n"
        card_text += "4. 511332xx:US$50.00: ✅ at 40%\n"
        card_text += "5. 403446xx:US$50.00: ✅ at 40%\n"
        card_text += "6. 403446xx:US$50.00: ✅ at 40%\n"
        card_text += "7. 435880xx:US$50.00: 🔒 at 40%\n"
        card_text += "8. 511332xx:US$50.00: ✅ at 40%\n"
        card_text += "9. 403446xx:US$50.00: 🔒 at 40%\n"
        card_text += "10. 403446xx:US$50.00: 🔒 at 40%\n\n"
        card_text += "<b>Legend:</b>\n"
        card_text += "🔒 - Card is registered\n"
        card_text += "✅ - Card is not registered\n"
        card_text += "⚠️ - Card has been used on Google\n\n"
        
        card_text += "<b>Products (1-10):</b>"
        
        # Create keyboard with only page 10 products (numbered 1-10)
        product_buttons = [
            [InlineKeyboardButton(text=f"{idx+1}. {prod['name']} - ${prod['price']}", callback_data=f"buy_page10_{idx}")]
            for idx, prod in enumerate(PRODUCTS_PAGE_10)
        ]
        # Add back to page 9 button
        product_buttons.append([InlineKeyboardButton(text="⬅️ Previous Page", callback_data="cards_page_9")])
        
        kb = InlineKeyboardMarkup(inline_keyboard=product_buttons)
        await call.message.answer(card_text, reply_markup=kb)

    await call.answer()

@dp.callback_query(F.data.startswith("buy_"))
async def buy_product(call: types.CallbackQuery):
    user_id = call.from_user.id
    if user_id not in USERS:
        USERS[user_id] = {"balance": 0, "history": []}

    # Parse the callback data
    parts = call.data.split("_")
    
    if len(parts) == 3:  # buy_page1_0 or buy_page2_0
        page = parts[1]
        idx = int(parts[2])
        
        if page == "page1":
            product = PRODUCTS_PAGE_1[idx]
            product_display_name = f"Page 1 - {product['name']}"
        elif page == "page2":
            product = PRODUCTS_PAGE_2[idx]
            product_display_name = f"Page 2 - {product['name']}"
        elif page == "page3":
            product = PRODUCTS_PAGE_3[idx]
            product_display_name = f"Page 3 - {product['name']}"
        elif page == "page4":
            product = PRODUCTS_PAGE_4[idx]
            product_display_name = f"Page 4 - {product['name']}"
        elif page == "page5":
            product = PRODUCTS_PAGE_5[idx]
            product_display_name = f"Page 5 - {product['name']}"
        elif page == "page6":
            product = PRODUCTS_PAGE_6[idx]
            product_display_name = f"Page 6 - {product['name']}"
        elif page == "page7":
            product = PRODUCTS_PAGE_7[idx]
            product_display_name = f"Page 7 - {product['name']}"
        elif page == "page8":
            product = PRODUCTS_PAGE_8[idx]
            product_display_name = f"Page 8 - {product['name']}"
        elif page == "page9":
            product = PRODUCTS_PAGE_9[idx]
            product_display_name = f"Page 9 - {product['name']}"
        elif page == "page10":
            product = PRODUCTS_PAGE_10[idx]
            product_display_name = f"Page 10 - {product['name']}"
        else:
            await call.answer("Invalid product selection")
            return
    else:  # Legacy format buy_0 (backwards compatibility)
        idx = int(parts[1])
        if idx < len(PRODUCTS):
            product = PRODUCTS[idx]
            product_display_name = product['name']
        else:
            await call.answer("Invalid product selection")
            return
    
    if USERS[user_id]["balance"] >= product["price"]:
        USERS[user_id]["balance"] -= product["price"]
        USERS[user_id]["history"].append(f"Bought {product_display_name} for ${product['price']}")
        await call.message.answer(f"✅ You bought {product_display_name}! Remaining balance: ${USERS[user_id]['balance']}")
    else:
        await call.message.answer(f"❌ Not enough balance. Please deposit at least ${product['price'] - USERS[user_id]['balance']} more.")

    await call.answer()

# ----------------------------
# MESSAGE HANDLERS FOR ADMIN PRODUCT MANAGEMENT
# ----------------------------
@dp.message(F.text.startswith("ADD:"))
async def handle_add_product(message: types.Message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return
    
    try:
        parts = message.text.split(":")
        if len(parts) != 3:
            await message.reply("❌ Invalid format. Use: ADD:Product Name:Price")
            return
        
        product_name = parts[1].strip()
        product_price = int(parts[2].strip())
        
        if product_price <= 0:
            await message.reply("❌ Price must be greater than 0.")
            return
        
        PRODUCTS.append({"name": product_name, "price": product_price})
        await message.reply(f"✅ Product '{product_name}' added successfully for ${product_price}!")
        
    except ValueError:
        await message.reply("❌ Invalid price. Please enter a valid number.")
    except Exception as e:
        await message.reply(f"❌ Error adding product: {e}")

@dp.message(F.text.startswith("EDIT:"))
async def handle_edit_product(message: types.Message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return
    
    try:
        parts = message.text.split(":")
        if len(parts) != 4:
            await message.reply("❌ Invalid format. Use: EDIT:ProductIndex:NewName:NewPrice")
            return
        
        product_index = int(parts[1].strip())
        new_name = parts[2].strip()
        new_price = int(parts[3].strip())
        
        if product_index < 0 or product_index >= len(PRODUCTS):
            await message.reply(f"❌ Invalid product index. Choose between 0 and {len(PRODUCTS)-1}.")
            return
        
        if new_price <= 0:
            await message.reply("❌ Price must be greater than 0.")
            return
        
        old_product = PRODUCTS[product_index]
        PRODUCTS[product_index] = {"name": new_name, "price": new_price}
        await message.reply(f"✅ Product updated!\nOld: {old_product['name']} - ${old_product['price']}\nNew: {new_name} - ${new_price}")
        
    except (ValueError, IndexError):
        await message.reply("❌ Invalid format or index. Use: EDIT:ProductIndex:NewName:NewPrice")
    except Exception as e:
        await message.reply(f"❌ Error editing product: {e}")

@dp.message(F.text.startswith("DELETE:"))
async def handle_delete_product(message: types.Message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return
    
    try:
        parts = message.text.split(":")
        if len(parts) != 2:
            await message.reply("❌ Invalid format. Use: DELETE:ProductIndex")
            return
        
        product_index = int(parts[1].strip())
        
        if product_index < 0 or product_index >= len(PRODUCTS):
            await message.reply(f"❌ Invalid product index. Choose between 0 and {len(PRODUCTS)-1}.")
            return
        
        deleted_product = PRODUCTS.pop(product_index)
        await message.reply(f"✅ Product '{deleted_product['name']}' deleted successfully!")
        
    except (ValueError, IndexError):
        await message.reply("❌ Invalid format or index. Use: DELETE:ProductIndex")
    except Exception as e:
        await message.reply(f"❌ Error deleting product: {e}")

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