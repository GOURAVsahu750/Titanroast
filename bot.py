import os
import time
import json
import urllib.request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ========== CONFIG ==========

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

AI_API_URL = "https://roast20-production.up.railway.app/roast"
MEMORY_TIME = 3600
TG_LIMIT = 4000

CREDIT = "DEVOLOPER @TITANCONTACT"
DEV_URL = "https://t.me/TITANCONTACT"
UPDATES_URL = "https://t.me/TITANBOTMAKING"

WELCOME_EMOJI = "😈"
LEAVE_EMOJI = "💀"

# ========== STORAGE (RAM) ==========

USERS = set()
GROUPS = {}
GROUP_MEMORY = {}
PRIVATE_MEMORY = {}

# ========== HELPERS ==========

def clean(mem):
    now = time.time()
    return [m for m in mem if now - m["time"] <= MEMORY_TIME]

def split_msg(text):
    return [text[i:i+TG_LIMIT] for i in range(0, len(text), TG_LIMIT)]

def ai_call(prompt):
    try:
        data = json.dumps({"message": prompt}).encode()
        req = urllib.request.Request(
            AI_API_URL,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode()).get("roast", "💀")
    except:
        return "💀 Roast engine thak gaya, thodi der baad aao."

def get_reply_text(update: Update):
    if update.message.reply_to_message:
        return update.message.reply_to_message.text
    return update.message.text.partition(" ")[2]

# ========== BOT ==========

app = ApplicationBuilder().token(BOT_TOKEN).build()

# ---------- START ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return

    user = update.effective_user
    is_new = user.id not in USERS
    USERS.add(user.id)

    if is_new:
        await context.bot.send_message(
            ADMIN_ID,
            f"🆕 New User\n👤 {user.first_name}\n🆔 {user.id}"
        )

    bot_username = context.bot.username or "YourBot"
    add_link = f"https://t.me/{bot_username}?startgroup=true"

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Me In Group", url=add_link)],
        [
            InlineKeyboardButton("👨‍💻 Developer", url=DEV_URL),
            InlineKeyboardButton("📢 Updates", url=UPDATES_URL)
        ]
    ])

    await update.message.reply_text(
        "🔥 Roast AI Bot 🔥\n\nPrivate + Groups dono me savage roast 💀",
        reply_markup=kb
    )

# ---------- STATS ----------

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    txt = f"📊 BOT STATS\n\n👤 Users: {len(USERS)}\n👥 Groups: {len(GROUPS)}\n"
    await update.message.reply_text(txt)

# ---------- BROADCAST ----------

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    text = get_reply_text(update)
    if not text:
        return

    ok = 0
    for uid in USERS:
        try:
            await context.bot.send_message(uid, text)
            ok += 1
        except:
            pass

    await update.message.reply_text(f"✅ Broadcast sent: {ok}")

async def gbroadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    text = get_reply_text(update)
    if not text:
        return

    ok = 0
    for gid in GROUPS:
        try:
            await context.bot.send_message(gid, text)
            ok += 1
        except:
            pass

    await update.message.reply_text(f"✅ Group broadcast: {ok}")

# ---------- ROAST ----------

async def roast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or update.message.from_user.is_bot:
        return

    chat = update.effective_chat

    if update.message.text:
        msg = update.message.text
    elif update.message.sticker:
        msg = f"[Sticker {update.message.sticker.emoji or '🤡'}]"
    else:
        return

    if chat.type in ("group", "supergroup"):
        GROUPS.setdefault(chat.id, {"title": chat.title})
        GROUP_MEMORY.setdefault(chat.id, [])
        GROUP_MEMORY[chat.id] = clean(GROUP_MEMORY[chat.id])
        GROUP_MEMORY[chat.id].append({"text": msg, "time": time.time()})

        context_text = "\n".join(m["text"] for m in GROUP_MEMORY[chat.id])
        prompt = f"Savage roast ONLY for last sender:\n{context_text}\n\nLast:\n{msg}"
    else:
        USERS.add(update.effective_user.id)
        PRIVATE_MEMORY.setdefault(update.effective_user.id, [])
        PRIVATE_MEMORY[update.effective_user.id] = clean(PRIVATE_MEMORY[update.effective_user.id])
        PRIVATE_MEMORY[update.effective_user.id].append({"text": msg, "time": time.time()})
        prompt = f"Savage private roast:\n{msg}"

    final = f"{ai_call(prompt)}\n\n{CREDIT}"
    for part in split_msg(final):
        await update.message.reply_text(part)

# ---------- JOIN / LEAVE ----------

async def join_leave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    GROUPS.setdefault(chat.id, {"title": chat.title})

    if update.message.new_chat_members:
        for u in update.message.new_chat_members:
            tag = f'<a href="tg://user?id={u.id}">{WELCOME_EMOJI}</a>'
            await context.bot.send_message(
                chat.id,
                f"{tag} Welcome!\n\n{ai_call('Short savage welcome roast')}",
                parse_mode="HTML"
            )

    if update.message.left_chat_member:
        tag = f'<a href="tg://user?id={update.message.left_chat_member.id}">{LEAVE_EMOJI}</a>'
        await context.bot.send_message(
            chat.id,
            f"{tag} Left 💀\n\n{ai_call('Short savage leave roast')}",
            parse_mode="HTML"
        )

# ========== HANDLERS ==========

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CommandHandler("broadcast", broadcast))
app.add_handler(CommandHandler("gbroadcast", gbroadcast))

app.add_handler(MessageHandler(
    (filters.ChatType.GROUPS | filters.ChatType.PRIVATE)
    & (filters.TEXT | filters.Sticker.ALL)
    & ~filters.COMMAND,
    roast
))

app.add_handler(MessageHandler(
    filters.StatusUpdate.NEW_CHAT_MEMBERS | filters.StatusUpdate.LEFT_CHAT_MEMBER,
    join_leave
))

print("🔥 Roast Bot Running on Railway...")
app.run_polling()