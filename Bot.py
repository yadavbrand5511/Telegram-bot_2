import os
import sqlite3
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("8759823115:AAFFlC154_LJ5wjQo7gIpBCGgnlB9mYu464")
ADMIN_ID = 8008313092
BOT_USERNAME = "methb0t"

conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 0,
    referred_by INTEGER
)
""")
conn.commit()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args

    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()

    if not user:
        ref = int(args[0]) if args else None
        cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (user_id, 10, ref))
        conn.commit()

        if ref and ref != user_id:
            cursor.execute("UPDATE users SET balance = balance + 5 WHERE user_id=?", (ref,))
            conn.commit()

        await update.message.reply_text("🎉 Welcome! ₹10 Bonus Added")
    else:
        await update.message.reply_text("👋 Welcome Back")

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    bal = cursor.fetchone()
    await update.message.reply_text(f"💰 Balance: ₹{bal[0]}")

async def ref(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
    await update.message.reply_text(f"🔗 Referral:\n{link}")

async def bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cursor.execute("UPDATE users SET balance = balance + 2 WHERE user_id=?", (user_id,))
    conn.commit()
    await update.message.reply_text("🎁 ₹2 Bonus Added")

async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    bal = cursor.fetchone()[0]

    if bal < 50:
        await update.message.reply_text("❌ Minimum ₹50 required")
    else:
        cursor.execute("UPDATE users SET balance = 0 WHERE user_id=?", (user_id,))
        conn.commit()

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"💸 Withdraw Request\nUser: {user_id}\nAmount: ₹{bal}"
        )

        await update.message.reply_text("✅ Withdraw Sent")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("balance", balance))
app.add_handler(CommandHandler("ref", ref))
app.add_handler(CommandHandler("bonus", bonus))
app.add_handler(CommandHandler("withdraw", withdraw))

print("RUNNING 🚀")
app.run_polling()
