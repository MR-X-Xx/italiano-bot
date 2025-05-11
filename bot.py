from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "7610384761:AAESdxBmc8ok6IhlSjYdgBv4EEzuw4D0P2M"
WEBHOOK_URL = "https://italiano-bot.onrender.com/webhook"  # ← غيّره إذا اتغير الرابط بعد النشر

app = Flask(__name__)
application = ApplicationBuilder().token(TOKEN).build()

# قائمة الدروس
lessons = [
    ("📖 الدرس 1", "Ciao! = مرحبًا\nCome ti chiami? = ما اسمك؟\nMi chiamo... = اسمي..."),
    ("📖 الدرس 2", "Io = أنا\nTu = أنت\nLui/Lei = هو / هي"),
    ("📖 الدرس 3", "Essere (يكون):\nio sono = أنا أكون\nAvere (يمتلك):\nio ho = أنا أملك"),
    ("📖 الدرس 4", "Come stai? = كيف حالك؟\nSto bene = أنا بخير\nE tu? = وأنت؟"),
    ("📖 الدرس 5", "uno, due, tre, quattro, cinque, sei, sette, otto, nove, dieci"),
    ("📖 الدرس 6", "lunedì, martedì, mercoledì, giovedì, venerdì, sabato, domenica"),
    ("📖 الدرس 7", "Sono egiziano = أنا مصري\nAbito al Cairo = أعيش في القاهرة"),
    ("📖 الدرس 8", "madre = أم\npadre = أب\nfratello = أخ\nsorella = أخت"),
    ("📖 الدرس 9", "il, lo, la, l’, i, gli, le — أمثلة توضيحية حسب الكلمة"),
    ("📖 الدرس 10", "Che cos’è? = ما هذا؟\nÈ un libro = إنه كتاب")
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📘 دروس اللغة الإيطالية", callback_data="lessons")],
        [InlineKeyboardButton("🧠 كلمات ومفردات", callback_data="words")],
        [InlineKeyboardButton("📖 كتب تعليمية", callback_data="books")],
        [InlineKeyboardButton("ℹ️ عن البوت", callback_data="about")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    welcome_text = (
        f"👋 أهلاً وسهلاً *{update.effective_user.first_name}*!\n\n"
        "📚 هذا البوت مشروع مصري مجاني لتعليم اللغة الإيطالية من الصفر.\n\n"
        "اختر من القائمة 👇"
    )
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.callback_query.edit_message_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")

def lessons_menu():
    buttons = [[InlineKeyboardButton(title, callback_data=f"lesson_{i}")] for i, (title, _) in enumerate(lessons)]
    buttons.append([InlineKeyboardButton("🔙 العودة", callback_data="main_menu")])
    return InlineKeyboardMarkup(buttons)

def main_menu_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🏠 العودة إلى القائمة الرئيسية", callback_data="main_menu")]])

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "main_menu":
        await start(update, context)

    elif query.data == "lessons":
        await query.edit_message_text("📘 اختر درسًا من دروس المستوى A1:", reply_markup=lessons_menu())

    elif query.data.startswith("lesson_"):
        index = int(query.data.split("_")[1])
        title, content = lessons[index]
        await query.edit_message_text(f"*{title}*\n\n{content}", parse_mode="Markdown", reply_markup=lessons_menu())

    elif query.data == "words":
        await query.edit_message_text(
            "🧠 *كلمات شائعة:*\n- Ciao = مرحبًا\n- Grazie = شكرًا\n- Sì / No = نعم / لا\n- Come stai? = كيف حالك؟",
            parse_mode="Markdown", reply_markup=main_menu_keyboard()
        )

    elif query.data == "books":
        await query.edit_message_text(
            "📖 *كتب تعليمية:*\n- كتاب A1 (قريبًا)\n- دليل القواعد الأساسية (PDF قريبًا)",
            parse_mode="Markdown", reply_markup=main_menu_keyboard()
        )

    elif query.data == "about":
        await query.edit_message_text(
            "ℹ️ *عن البوت:*\n\n"
            "بوت تعليمي مجاني من *شاب مصري* لتعلم الإيطالية ببساطة وبالعربي.\n"
            "📌 محتوى متجدد تدريجيًا للمستويات A1 وأعلى.",
            parse_mode="Markdown", reply_markup=main_menu_keyboard()
        )

# تسجيل المعالجات
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(handle_buttons))

# نقطة استقبال من تليجرام
@app.post("/webhook")
async def webhook():
    data = request.get_json(force=True)
    print("📩 تم استلام تحديث من تليجرام:", data)  # <-- السطر الجديد
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return "ok"

# تشغيل السيرفر على Render مع إعداد الـ webhook
if __name__ == "__main__":
    import asyncio
    asyncio.run(application.bot.set_webhook(WEBHOOK_URL))
    app.run(host="0.0.0.0", port=10000)
