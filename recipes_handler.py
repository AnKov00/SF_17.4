import aiohttp

from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import  Router, types

from random import choices
from googletrans import  Translator


router = Router()
translator = Translator()

class RecipePath(StatesGroup):
    '''Класс для создания "цепочки" общения с ботом.
    Тут же переменная, которая хранит необходимое кол-во рецептов,
    и словарь выбранных рецептов'''
    wait_category = State()
    get_recept = State()
    recept_dict ={}
    quantity_recipes = 0


@router.message(Command('category_search_random'))
async def select_category(message: Message, command: CommandObject, state: FSMContext):
    try:#Если параметр введённый с командой - слово, символ или ноль, тогда выставляет переменной значение 1
        if command.args != "0":
            RecipePath.quantity_recipes = int(command.args)
        else:
            RecipePath.quantity_recipes = 1
    except Exception:
        RecipePath.quantity_recipes = 1
    async with aiohttp.ClientSession() as session:
        async with session.get('https://www.themealdb.com/api/json/v1/1/list.php?c=list') as response:
            if response.status == 200:
                category_data = await response.json()
                kb = ReplyKeyboardBuilder()
                for v in category_data['meals']:
                    kb.add(types.KeyboardButton(text=v['strCategory']))
                kb.adjust(4)
                await message.answer("Выберите категорию: ", reply_markup=kb.as_markup(resize_keyboard=True))
                await state.set_state(RecipePath.wait_category.state)
            else:
                await message.answer(f'Ошибка соединения с сервером')

@router.message(RecipePath.wait_category)
async def select_dish(message: types.Message, state: FSMContext):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://www.themealdb.com/api/json/v1/1/filter.php?c={message.text}') as resp:
            if resp.status == 200:
                menu_data = await resp.json()
                rec_len = choices(menu_data['meals'], k=RecipePath.quantity_recipes)
                rec_name=[]
                for item in rec_len:
                    RecipePath.recept_dict[item['strMeal']] = item['idMeal']
                    name = translator.translate(item['strMeal'], dest='ru')
                    rec_name.append(name.text)

                kb = [[types.KeyboardButton(text='Покажи Рецепты!')]]
                keyboard = types.ReplyKeyboardMarkup(keyboard=kb)
                await message.answer(f'Как вам такие варианты:\n{'\n'.join(rec_name)}', reply_markup=keyboard)
                await state.set_state(RecipePath.get_recept.state)

@router.message(RecipePath.get_recept)
async def get_recept(message: types.Message, state: FSMContext):
    data = RecipePath.recept_dict
    async with aiohttp.ClientSession() as session:
        for k, v in data.items():
            async with session.get(f'http://www.themealdb.com/api/json/v1/1/lookup.php?i={v}') as resp:
                rec = await resp.json()
                ru_rec = translator.translate(rec['meals'][0]['strInstructions'], dest='ru')
                await message.answer(f'Что бы приготовить {k} Вам потребуется:\n{ru_rec.text}\n{rec['meals'][0]['strMealThumb']}')







