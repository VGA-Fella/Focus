from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import asyncio
import nest_asyncio

TOKEN = 'Your token'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я таймер и правила мои просты. Я засекаю 30 минут, а ты за это время фокусируешься на своей задаче. Когда время заканчивается, ты можешь начать новую 30-минутную задачу или отправиться отдыхать.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("+30 минут", callback_data="add_30_minutes")], 
        ])
    )
    context.chat_data['total_time'] = 0
    context.chat_data['count'] = 0

async def callback_timer(context: ContextTypes.DEFAULT_TYPE):
    job_data = context.job.data
    total_time = job_data['total_time'] + 1800 
    chat_id = job_data['chat_id']
    await context.bot.send_message(chat_id, text='Ты справился, молодец. Теперь можно сделать небольшой перерыв на чашку кофе или просто провести время как тебе нравится. Или продолжить спринт.',
                             reply_markup=InlineKeyboardMarkup([
                                 [InlineKeyboardButton("+30 минут", callback_data="add_30_minutes")],
                                 [InlineKeyboardButton("Скажи сумму", callback_data="show_sum")],
                                 [InlineKeyboardButton("Закончить спринт", callback_data="finish")],
                             ]))
    job_data['total_time'] = total_time

def format_time(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours > 0:
        return f"{hours} часов {minutes} минут {seconds} секунд"
    else:
        return f"{minutes} минут {seconds} секунд"

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "add_30_minutes":
        context.chat_data['count'] += 1
        await query.message.reply_text("Счетчик таймеров +30 минут запущен. Сосредоточься!")
        job_data = {'total_time': context.chat_data['total_time'], 'chat_id': update.effective_chat.id}
        context.application.job_queue.run_once(callback_timer, 1800, data=job_data) 
        context.chat_data['total_time'] += 1800 
    elif query.data == "show_sum":
        formatted_time = format_time(context.chat_data['total_time'])
        await query.edit_message_text(
            text=f"Вы запустили таймер {context.chat_data['count']} раз(а). Время: {formatted_time}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("+30 минут", callback_data="add_30_minutes")],
                [InlineKeyboardButton("Скажи сумму", callback_data="show_sum")],
                [InlineKeyboardButton("Закончить спринт", callback_data="finish")]
            ])
        )
    elif query.data == "finish":
        await query.edit_message_text(
            text="Спринт завершен. Начнем заново?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("+30 минут", callback_data="add_30_minutes")]
            ])
        )
        context.chat_data['total_time'] = 0 
        context.chat_data['count'] = 0

async def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    await application.run_polling()

if __name__ == '__main__':
    nest_asyncio.apply()
    asyncio.run(main())