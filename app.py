# ========== FLASK UPTIME ==========
from flask import Flask
from threading import Thread

flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Bot is alive!", 200

def keep_alive():
    Thread(target=lambda: flask_app.run(host='0.0.0.0', port=8080)).start()

# ========== TELEGRAM BOT ==========
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, MessageHandler, CallbackQueryHandler,
    ChatMemberHandler, filters, ContextTypes
)
import requests
import re
import os
import time

BOT_TOKEN = os.environ.get("BOT_TOKEN") or "ISI_TOKEN_BOT_LO"
TOPIC_THREAD_ID = 37

user_search_data = {}

def get_results(keyword, page=1, per_page=10):
    results = []
    for tipe in ["movies", "tvshows"]:
        try:
            url = f"https://decanime.rf.gd/wp-json/wp/v2/{tipe}?search={keyword}&per_page=100"
            res = requests.get(url, timeout=5)
            data = res.json()
            for item in data:
                title = re.sub(r"<[^>]+>", "", item.get("title", {}).get("rendered", "Tanpa Judul"))
                slug = item.get("slug", "")
                link = f"https://decanime.rf.gd/{tipe}/{slug}/"
                results.append((title, link))
        except:
            continue
    start = (page - 1) * per_page
    end = start + per_page
    return results, len(results), results[start:end]

async def handle_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text.startswith("?s "):
        return

    if update.message.message_thread_id != TOPIC_THREAD_ID:
        await update.message.reply_text(
            "❗ Bro, perintah `?s` cuma bisa dipakai di topik *#CARI* ya.",
            parse_mode="Markdown"
        )
        return

    keyword = update.message.text[3:].strip()
    results, total, page_data = get_results(keyword, page=1)

    if not page_data:
        await update.message.reply_text("❌ Gak ada hasil, bro.")
        return

    user_id = update.message.from_user.id
    user_search_data[user_id] = {
        "keyword": keyword,
        "total": total,
        "page": 1
    }

    user_mention = (
        f"@{update.message.from_user.username}"
        if update.message.from_user.username
        else update.message.from_user.first_name
    )

    msg = "\n".join(
        [f"👉 *{i+1}.* [{judul}]({link})" for i, (judul, link) in enumerate(page_data)]
    )

    buttons = []
    if total > 10:
        buttons = [[
            InlineKeyboardButton("▶ Selanjutnya", callback_data="next_1")
        ]]

    await update.message.reply_text(
        f"📢 {user_mention}, *hasil pencarian:*\n\n{msg}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons) if buttons else None
    )

async def next_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id not in user_search_data:
        await query.edit_message_text("❌ Sesi pencarian gak ditemukan.")
        return

    session = user_search_data[user_id]
    session["page"] += 1
    keyword = session["keyword"]
    page = session["page"]

    results, total, page_data = get_results(keyword, page)

    if not page_data:
        await query.edit_message_text("⚠ Sudah akhir halaman.")
        return

    start_num = (page - 1) * 10 + 1
    msg = "\n".join(
        [f"👉 *{i+start_num}.* [{judul}]({link})" for i, (judul, link) in enumerate(page_data)]
    )

    buttons = []
    if total > page * 10:
        buttons = [[
            InlineKeyboardButton("▶ Selanjutnya", callback_data=f"next_{page}")
        ]]

    await query.edit_message_text(
        f"*Hasil pencarian (halaman {page}):*\n\n{msg}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons) if buttons else None
    )

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    member = update.chat_member
    if member.new_chat_member.status == "member":
        user = member.new_chat_member.user
        name = f"@{user.username}" if user.username else user.first_name
        await context.bot.send_message(
            chat_id=update.chat_member.chat.id,
            text=(
                f"👋 Selamat datang {name}!\n\n"
                f"Ketik `?s judul` di thread *#CARI* buat cari film!"
            ),
            parse_mode="Markdown"
        )

# === RUN ===
keep_alive()

telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()
telegram_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_search))
telegram_app.add_handler(CallbackQueryHandler(next_page, pattern=r"next_\d+"))
telegram_app.add_handler(ChatMemberHandler(welcome_new_member, ChatMemberHandler.CHAT_MEMBER))

while True:
    try:
        telegram_app.run_polling(poll_interval=5, timeout=30)
    except Exception as e:
        time.sleep(5)