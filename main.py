import logging
import asyncio
import nest_asyncio
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Loggingni o'rnatish
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Bot token va guruh ID
TOKEN = '7808265437:AAF3GuTMi5Phq4RoWTNJsis6AsMvGTzFp8k'  # <-- bu yerga o'zingizning tokeningizni qo'ying
GROUP_ID = -4517219499     # <-- bu yerga guruh ID sini yozing

# Tugmalar va ularga bog'langan foydalanuvchilar
button_to_user = {
    "LLK": "@Nizomxon_Hamidov",
    "GIGA_SAHARA": "@Malr1ne022",
    "SOF": "@Sarvarbek_Rakhmanovv",
    "MAL-DEV": "@Sarvarbek_Rakhmanovv",
    "JENS_REVEREM": "@Abduvohid1972",
    "APTEKA": "@Nizomxon_Hamidov",
    "ALL": "@Nizomxon_Hamidov, @Malr1ne022, @Sarvarbek_Rakhmanovv, @Abduvohid1972"
}

# Perevod rejimidagi foydalanuvchilarni kuzatish
perevod_mode_users = {}

# Start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("LLK"), KeyboardButton("GIGA_SAHARA")],
        [KeyboardButton("SOF"), KeyboardButton("MAL-DEV")],
        [KeyboardButton("APTEKA"), KeyboardButton("JENS_REVEREM")],
        [KeyboardButton("ALL"), KeyboardButton("Perevod")]  # ← bu yerda yonma-yon qo‘yildi
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False, resize_keyboard=True)
    await update.message.reply_text("Iltimos, brendni tanlang:", reply_markup=reply_markup)

# Tugma tanlanganda
async def handle_button_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    selected_button = update.message.text

    if selected_button == "Perevod":
        perevod_mode_users[user_id] = []
        await update.message.reply_text("Perevod rejimi: Iltimos, 2 ta brend tanlang.")
        return

    if user_id in perevod_mode_users:
        perevod_mode_users[user_id].append(selected_button)
        if len(perevod_mode_users[user_id]) < 2:
            await update.message.reply_text("Yana bir brend tanlang.")
        else:
            context.user_data['perevod_selected'] = perevod_mode_users.pop(user_id)
            await update.message.reply_text(
                f"Siz tanladingiz: {context.user_data['perevod_selected'][0]} va {context.user_data['perevod_selected'][1]}\nEndi xabaringizni yuboring.")
        return

    # Oddiy rejim
    context.user_data['selected_button'] = selected_button
    confirmation_message = await update.message.reply_text(
        f"Siz {selected_button} tugmasini tanladingiz. Endi xabaringizni yuboring.")
    context.user_data['confirmation_message_id'] = confirmation_message.message_id

# Xabarni yuborish
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    # Eski tasdiqlash xabarini o'chirish
    if 'confirmation_message_id' in context.user_data:
        await context.bot.delete_message(chat_id=user_id, message_id=context.user_data['confirmation_message_id'])
        del context.user_data['confirmation_message_id']

    # PEREVOD rejimi
    if 'perevod_selected' in context.user_data:
        selected_buttons = context.user_data.pop('perevod_selected')
        receivers = ", ".join([button_to_user.get(btn, "Noma'lum") for btn in selected_buttons])

        if update.message.text:
            caption = f"{update.message.text}\n\nYuboruvchi: @{update.message.from_user.username or 'Nomalum'}\nQabul qiluvchilar: {receivers}"
            await context.bot.send_message(chat_id=GROUP_ID, text=caption)
            confirmation_message = await update.message.reply_text("Xabaringiz yuborildi.")
            context.user_data['confirmation_message_id'] = confirmation_message.message_id
        elif update.message.photo:
            caption = f"Rasm\n\nYuboruvchi: @{update.message.from_user.username or 'Nomalum'}\nQabul qiluvchilar: {receivers}"
            await context.bot.send_photo(chat_id=GROUP_ID, photo=update.message.photo[-1].file_id, caption=caption)
            confirmation_message = await update.message.reply_text("Rasm yuborildi.")
            context.user_data['confirmation_message_id'] = confirmation_message.message_id
        else:
            await update.message.reply_text("Faqat matn yoki rasm yuboring.")
        return

    # Oddiy rejim
    if 'selected_button' not in context.user_data:
        await update.message.reply_text("Iltimos, avval tugmani tanlang.")
        return

    selected_button = context.user_data.pop('selected_button')
    receiver = button_to_user.get(selected_button, "Noma'lum")

    if update.message.text:
        caption = f"{update.message.text}\n\nYuboruvchi: @{update.message.from_user.username or 'Nomalum'}\nQabul qiluvchi: {receiver}"
        await context.bot.send_message(chat_id=GROUP_ID, text=caption)
        confirmation_message = await update.message.reply_text("Xabaringiz yuborildi.")
        context.user_data['confirmation_message_id'] = confirmation_message.message_id
    elif update.message.photo:
        caption = f"Rasm\n\nYuboruvchi: @{update.message.from_user.username or 'Nomalum'}\nQabul qiluvchi: {receiver}"
        await context.bot.send_photo(chat_id=GROUP_ID, photo=update.message.photo[-1].file_id, caption=caption)
        confirmation_message = await update.message.reply_text("Rasm yuborildi.")
        context.user_data['confirmation_message_id'] = confirmation_message.message_id
    else:
        await update.message.reply_text("Faqat matn yoki rasm yuboring.")

# Guruhdagi reply larni o'chirish
async def block_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.id == GROUP_ID:
        await update.message.delete()

# Main ishga tushirish
async def main():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(
        filters.TEXT & filters.Regex('^(LLK|GIGA_SAHARA|SOF|MAL-DEV|JENS_REVEREM|APTEKA|ALL|Perevod)$'), handle_button_selection))
    application.add_handler(MessageHandler(filters.TEXT, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_message))
    application.add_handler(MessageHandler(filters.REPLY & filters.ChatType.GROUP, block_reply))
    await application.run_polling()

nest_asyncio.apply()
asyncio.run(main())
