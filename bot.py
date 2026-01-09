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

# ================= CONFIG =================

BOT_TOKEN = "8551387537:AAHIIRZ6b8zxtq0zpncRH6Ha-XTnxDg79fY"
ADMIN_ID = 8188215655

AI_API_URL = "https://roast20-production.up.railway.app/roast"

MEMORY_TIME = 3600
TG_LIMIT = 4000

CREDIT = "DEVOLOPER @TITANCONTACT"
DEV_URL = "https://t.me/TITANCONTACT"
UPDATES_URL = "https://t.me/TITANBOTMAKING"

WELCOME_EMOJI = "😈"
LEAVE_EMOJI = "💀"

# ================= STORAGE =================

USERS = set()
GROUPS = {}
GROUP_MEMORY = {}
PRIVATE_MEMORY = {}

# ================= HELPERS =================

def clean(mem):
    now = time.time()
    return [m for m in mem if now - m["time"] <= MEMORY_TIME]

def split_msg(text):
    return [text[i:i+TG_LIMIT] for i in range(0, len(text), TG_LIMIT)]

def ai_call(prompt):
    data = json.dumps({"message": prompt}).encode()
    req = urllib.request.Request(
        AI_API_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode()).get("roast", "💀")

def get_reply_text(update: Update):
    if update.message.reply_to_message:
        return update.message.reply_to_message.text
    return update.message.text.partition(" ")[2]

# ================= APP =================

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

    add_link = f"https://t.me/{context.bot.username}?startgroup=true"

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Me In Group", url=add_link)],
        [
            InlineKeyboardButton("👨‍💻 Developer", url=DEV_URL),
            InlineKeyboardButton("📢 Updates", url=UPDATES_URL)
        ]
    ])

    await update.message.reply_text(
        "🔥 Roast AI Bot 🔥\n\nPrivate + Group savage roast 💀",
        reply_markup=kb
    )

# ---------- STATS ----------

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    txt = f"📊 BOT STATS\n\n👤 Users: {len(USERS)}\n👥 Groups: {len(GROUPS)}\n\n"
    for g in GROUPS.values():
        txt += f"• {g['title']} → {g['msgs']} msgs\n"

    await update.message.reply_text(txt)

# ---------- BROADCAST ----------

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    text = get_reply_text(update)
    if not text:
        return

    ok = 0
    for u in USERS:
        try:
            await context.bot.send_message(u, text)
            ok += 1
        except:
            pass

    await update.message.reply_text(f"✅ Sent to {ok} users")

async def gbroadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    text = get_reply_text(update)
    if not text:
        return

    ok = 0
    for g in GROUPS:
        try:
            await context.bot.send_message(g, text)
            ok += 1
        except:
            pass

    await update.message.reply_text(f"✅ Sent to {ok} groups")

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
        GROUPS.setdefault(chat.id, {"title": chat.title, "msgs": 0})
        GROUPS[chat.id]["msgs"] += 1

        GROUP_MEMORY.setdefault(chat.id, [])
        GROUP_MEMORY[chat.id] = clean(GROUP_MEMORY[chat.id])
        GROUP_MEMORY[chat.id].append({"text": msg, "time": time.time()})

        context_text = "\n".join(m["text"] for m in GROUP_MEMORY[chat.id])
        prompt = f"Roast only last sender brutally:\n{context_text}"
    else:
        USERS.add(update.effective_user.id)
        PRIVATE_MEMORY.setdefault(update.effective_user.id, [])
        PRIVATE_MEMORY[update.effective_user.id] = clean(PRIVATE_MEMORY[update.effective_user.id])
        PRIVATE_MEMORY[update.effective_user.id].append({"text": msg, "time": time.time()})
        prompt = f"Private savage roast:\n{msg}"

    try:
        r = ai_call(prompt)
        final = f"{r}\n\n{CREDIT}"
        for part in split_msg(final):
            await update.message.reply_text(part)
    except:
        pass

# ---------- JOIN / LEAVE ----------

async def join_leave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.new_chat_members:
        for u in update.message.new_chat_members:
            tag = f'<a href="tg://user?id={u.id}">{WELCOME_EMOJI}</a>'
            r = ai_call("Short savage welcome roast")
            await context.bot.send_message(update.effective_chat.id, f"{tag} Welcome\n\n{r}", parse_mode="HTML")

    if update.message.left_chat_member:
        tag = f'<a href="tg://user?id={update.message.left_chat_member.id}">{LEAVE_EMOJI}</a>'
        r = ai_call("Short savage roast for leaving")
        await context.bot.send_message(update.effective_chat.id, f"{tag} Left\n\n{r}", parse_mode="HTML")

# ================= HANDLERS =================

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CommandHandler("broadcast", broadcast))
app.add_handler(CommandHandler("gbroadcast", gbroadcast))

app.add_handler(
    MessageHandler(
        (filters.ChatType.GROUPS | filters.ChatType.PRIVATE)
        & (filters.TEXT | filters.Sticker.ALL)
        & ~filters.COMMAND,
        roast
    )
)

app.add_handler(
    MessageHandler(
        filters.StatusUpdate.NEW_CHAT_MEMBERS | filters.StatusUpdate.LEFT_CHAT_MEMBER,
        join_leave
    )
)

print("🔥 Roast Bot Running Successfully...")
app.run_polling(close_loop=False)
