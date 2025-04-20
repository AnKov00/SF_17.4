import asyncio


from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from aiogram import F
from aiogram.utils.formatting import (Bold, as_list, as_marked_section)
from token_data import TOKEN
from recipes_handler import router

dp = Dispatcher()
dp.include_router(router)

@dp.message(CommandStart())
async def command_start_heandler(message: Message):
    kb = [[types.KeyboardButton(text="Команды"),
           types.KeyboardButton(text="Описание бота")]]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer(f'Привет, {hbold(message.from_user.full_name)}!\n'
                         f'Нажми на одну из кнопок, что бы узнать подробности', reply_markup=keyboard)

@dp.message(F.text.lower() == 'описание бота')
async def about(message: types.Message):
    await message.answer('Это приложение поможет приготовить какое-нибудь вкусное блюдо!🍔')

@dp.message(F.text.lower() == 'команды')
async def command(message: types.Message):
    resource = as_list(as_marked_section(Bold("Команды:"), 'Введите:\n/category_search_random *\n'
                                         'где "*" это количество случайных рецептов рецептов',marker='🧑‍🍳'))
    await message.answer(**resource.as_kwargs())


async def main():
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())