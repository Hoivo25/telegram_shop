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

# Products with 40% of card values
PRODUCTS = [
    {"name": "1", "price": 127},  # 40% of $317.39
    {"name": "2", "price": 124},  # 40% of $310.15
    {"name": "3", "price": 121},  # 40% of $303.42
    {"name": "4", "price": 121},  # 40% of $303.34
    {"name": "5", "price": 120},  # 40% of $300.00
    {"name": "6", "price": 120},  # 40% of $300.00
    {"name": "7", "price": 118},  # 40% of $294.82
    {"name": "8", "price": 118},  # 40% of $294.17
    {"name": "9", "price": 117},  # 40% of $292.72
    {"name": "10", "price": 117}, # 40% of $292.32
    {"name": "1", "price": 13},   # 40% of $33.66 (Page 2)
    {"name": "2", "price": 13},   # 40% of $33.47 (Page 2)
    {"name": "3", "price": 13},   # 40% of $33.40 (Page 2)
    {"name": "4", "price": 13},   # 40% of $33.06 (Page 2)
    {"name": "5", "price": 13},   # 40% of $32.98 (Page 2)
    {"name": "6", "price": 13},   # 40% of $32.93 (Page 2)
    {"name": "7", "price": 13},   # 40% of $32.70 (Page 2)
    {"name": "8", "price": 13},   # 40% of $32.61 (Page 2)
    {"name": "9", "price": 13},   # 40% of $32.57 (Page 2)
    {"name": "10", "price": 13},  # 40% of $32.51 (Page 2)
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
@dp.callback_query(F.data.in_(["view_products", "deposit", "history", "admin_stats", "admin_revenue", "admin_analytics", "admin_users", "regular_shop", "back_to_admin", "admin_products", "admin_add_product", "admin_edit_product", "admin_delete_product", "cards_page_2"]))
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
        
        # Keep the original products as well
        card_text += "<b>Other Products:</b>"
        
        # Create keyboard with pagination and product buttons
        product_buttons = [
            [InlineKeyboardButton(text=f"{prod['name']} - ${prod['price']}", callback_data=f"buy_{idx}")]
            for idx, prod in enumerate(PRODUCTS)
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
        
        # Keep the original products as well
        card_text += "<b>Products (Page 2):</b>"
        
        # Create keyboard with Page 2 products (items 10-19, numbered 1-10)
        product_buttons = [
            [InlineKeyboardButton(text=f"{PRODUCTS[idx]['name']} - ${PRODUCTS[idx]['price']}", callback_data=f"buy_{idx}")]
            for idx in range(10, min(20, len(PRODUCTS)))
        ]
        # Add back to page 1 button
        product_buttons.append([InlineKeyboardButton(text="⬅️ Previous Page", callback_data="view_products")])
        
        kb = InlineKeyboardMarkup(inline_keyboard=product_buttons)
        await call.message.answer(card_text, reply_markup=kb)

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