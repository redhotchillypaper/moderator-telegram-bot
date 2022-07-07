from imports import TOKEN,WORDS,CHANNEL_ID,CHANNEL_URL,ADMIN_ID,CHAT_ID,WHITE_WORDS
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from db import DataBase
bot = Bot(token=TOKEN)  # бот
dp = Dispatcher(bot)  # диспетчер(мозг)
db = DataBase('dbase')  # база данных
greet_kb = ReplyKeyboardMarkup(resize_keyboard=True) # клавиатура

essage_handler(commands=['start','help'])
async def send_welcome(msg: types.Message):
    await msg.answer(f'Я Модератор-Бот. Приятно познакомиться, {msg.from_user.first_name}\nВот что я умею:\n1. Есть фильтр слов (Как пример - запрет матов)\n2. Белые ссылки, которые можно писать в чат\n3. Есть подключение к базам данных.\n4. Реализован мут пользователя средствами баз данных и постоянной проверки сообщений ')
async def help(msg: types.Message):
    await msg.reply('idi nahui')


@dp.message_handler(commands=['mute'])
async def mute(msg):
    if str(msg.from_user.id) in ADMIN_ID:
        if not msg.reply_to_message:
            await msg.reply('Ответьте на сообщение человека, которого хотите замутить')
        else:
            mute_sec = int(str(msg.text[6:]).strip())
            db.add_mute(msg.reply_to_message.from_user.id,mute_sec)
            await msg.answer(f'Успешно замутил {msg.reply_to_message.from_user.full_name}, на {mute_sec} секунд.')
            await msg.bot.restrictChatMember(chat_id=CHAT_ID,user_id=msg.reply_to_message.from_user.id,until_date=mute_sec)

@dp.message_handler(commands=['ban'])
async def ban(msg):
    if str(msg.from_user.id) in ADMIN_ID:
        if not msg.reply_to_message:
            await msg.reply('Ответьте на сообщение человека, которого хотите замутить')
        else:
            await msg.bot.delete_message(CHAT_ID, msg.message_id)
            await msg.bot.kick_chat_member(chat_id=CHAT_ID, user_id=msg.reply_to_message.from_user.id)


@dp.message_handler(content_types=['new_chat_members'])
async def on_user_join(msg: types.Message):
    await msg.delete()

# id for admins
@dp.message_handler(commands=['myid'])
async def send_welcome(msg: types.Message):
    await msg.answer(f'ID: {msg.from_user.id}')

def check_user_sub(chat_member):
    return chat_member['status'] != 'left'


@dp.message_handler(content_types=['new_chat_members'])
async def join_user(message: types.chat):
    await message.answer(f'Привет, {message.from_user.full_name}')



# check for WORDS in message and for subscribe
@dp.message_handler()
async def mess_handler(message: types.Message):
    if not db.user_exists(message.from_user.id):
        db.add_user(message.from_user.id)
    if db.mute(message.from_user.id):
        await message.delete()
    if check_user_sub(await bot.get_chat_member(chat_id=CHANNEL_ID,user_id=message.from_user.id)):
        text = message.text.lower()
        if ('http:' in text or 'https:' in text) and not text in WHITE_WORDS:
            await message.delete()
        for word in WORDS:
            if word in text:
                await message.delete()
    else:
        await message.answer(f'Чтобы отправить сообщ, подпишись на {CHANNEL_URL}')
        await message.delete()



if __name__ == '__main__':
   executor.start_polling(dp)