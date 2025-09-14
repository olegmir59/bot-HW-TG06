import asyncio
import random

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from config import TELEGRAM_TOKEN
import sqlite3
import requests
import logging

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

button_registr = KeyboardButton(text="Регистрация в телеграм боте")
button_exchange_rates = KeyboardButton(text="Курс валют")
button_tips = KeyboardButton(text="Советы по экономии")
button_finances = KeyboardButton(text="Личные финансы")

keyboards = ReplyKeyboardMarkup(keyboard=[
    [button_registr, button_exchange_rates],
    [button_tips, button_finances]
], resize_keyboard=True)

conn = sqlite3.connect('user.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    telegram_id INTEGER UNIQUE,
    name TEXT,
    category1 TEXT,
    category2 TEXT,
    category3 TEXT,
    expenses1 REAL,
    expenses2 REAL,
    expenses3 REAL
)
''')

conn.commit()


class FinancesForm(StatesGroup):
    category1 = State()
    expenses1 = State()
    category2 = State()
    expenses2 = State()
    category3 = State()
    expenses3 = State()


@dp.message(Command('start'))
async def send_start(message: Message):
    # Сначала отправляем изображение
    with open("finance.png", "rb") as finance_image:
        image_bytes = BufferedInputFile(finance_image.read(), filename="finance.png")
        await bot.send_photo(chat_id=message.chat.id, photo=image_bytes)

    # Затем отправляем основное меню
    await message.answer("Привет! Я ваш личный финансовый помощник. Выберите одну из опций в меню:",
                         reply_markup=keyboards)


@dp.message(F.text == "Регистрация в телеграм боте")
async def registration(message: Message):
    telegram_id = message.from_user.id
    name = message.from_user.full_name
    cursor.execute('''SELECT * FROM users WHERE telegram_id = ?''', (telegram_id,))
    user = cursor.fetchone()
    if user:
        await message.answer("Вы уже зарегистрированы!")
    else:
        cursor.execute('''INSERT INTO users (telegram_id, name) VALUES (?, ?)''', (telegram_id, name))
        conn.commit()
        await message.answer("Вы успешно зарегистрированы!")


@dp.message(F.text == "Курс валют")
async def exchange_rates(message: Message):
    url = "https://v6.exchangerate-api.com/v6/09edf8b2bb246e1f801cbfba/latest/USD"
    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code != 200:
            await message.answer("Не удалось получить данные о курсе валют!")
            return
        usd_to_rub = data['conversion_rates'].get('RUB', 'N/A')
        eur_to_usd = data['conversion_rates'].get('EUR', 'N/A')

        if isinstance(eur_to_usd, str) or isinstance(usd_to_rub, str):
            await message.answer("Данные о валюте отсутствуют.")
            return

        euro_to_rub = round(eur_to_usd * usd_to_rub, 2)

        await message.answer(f"1 USD - {usd_to_rub:.2f} руб.\n"
                             f"1 EUR - {euro_to_rub:.2f} руб.")

    except requests.RequestException as e:
        await message.answer(f"Ошибка при получении курса валюты: {e}")


@dp.message(F.text == "Советы по экономии")
async def send_tips(message: Message):
    tips = [
        "Инвестируйте в душевное спокойствие:✅ Каждый рубль, сэкономленный на покупке ненужных вещей, приближает вас к счастью. Или хотя бы снижает уровень стресса!",
        "Экономьте на такси:😊 Иногда полезно пройтись пешком — ноги становятся крепче, мозг яснее, а кошелек толще!",
        "Научитесь готовить дома:☑️ Готовка собственных блюд экономит деньги и здоровье. Ну и никто не отменял кулинарные эксперименты с неожиданными результатами!",
        "Ищите скидки, акции и кэшбэк:🎯 Один клик может сэкономить сотни рублей. Главное — вовремя поймать выгодную акцию!",
        "Покупайте вкусные продукты:🍎 Продукты — это не только полезные для здоровья, но и экономичные. Покупайте только то, что вам действительно нужно!",
        "Пользуйтесь услугами совместно:🤝 Делите аренду жилья, машину или еду с друзьями — это весело и выгодно!",
        "Отложите покупку на завтра:🌍 Часто желание купить проходит быстрее, чем реклама успевает завладеть вами. Завтра мир покажется другим… и покупки тоже!",
        "Купите качественную обувь:👟 Хорошая пара обуви прослужит долго и спасёт ваши ноги от мозолей, нервов и лишних трат!",
        "Установите энергосберегающие лампочки:💡 Осветите вашу жизнь яркими впечатлениями, а не высокими счетами за электричество!",
        "Планируйте крупные покупки заранее:📆 Лучше копить постепенно, чем влезть в долги внезапно!",
        "Заботьтесь о своей технике:🛠️ Ремонт ноутбука обходится дешевле замены, а чай проливать легче, чем восстановить потерянные файлы!",
        "Используйте вещи повторно:🔥 Старую футболку можно превратить в тряпочку, а пластиковую бутылку — в кашпо. Так вы сократите отходы и найдете вдохновение!",
        "Будьте скромнее в развлечениях:🎭 Посещение кинотеатра или кафе — удовольствие дорогостоящее. Друзья, хорошая книга и уютный вечер дома сделают вас счастливее бесплатно!"
        "Ведите подробный бюджет и регулярно отслеживайте свои расходы.",
        "Откладывайте часть дохода на непредвиденные обстоятельства.",
        "Покупайте продукты питания и одежду по акционным ценам."
    ]
    await message.answer(random.choice(tips))


@dp.message(F.text == "Личные финансы")
async def finances(message: Message, state: FSMContext):
    await state.set_state(FinancesForm.category1)
    await message.reply("Введите первую категорию расходов:")


@dp.message(FinancesForm.category1)
async def finances_category1(message: Message, state: FSMContext):
    await state.update_data(category1=message.text)
    await state.set_state(FinancesForm.expenses1)
    await message.reply("Введите сумму расходов для первой категории:")


@dp.message(FinancesForm.expenses1)
async def finances_expenses1(message: Message, state: FSMContext):
    await state.update_data(expenses1=float(message.text))
    await state.set_state(FinancesForm.category2)
    await message.reply("Введите вторую категорию расходов:")


@dp.message(FinancesForm.category2)
async def finances_category2(message: Message, state: FSMContext):
    await state.update_data(category2=message.text)
    await state.set_state(FinancesForm.expenses2)
    await message.reply("Введите сумму расходов для второй категории:")


@dp.message(FinancesForm.expenses2)
async def finances_expenses2(message: Message, state: FSMContext):
    await state.update_data(expenses2=float(message.text))
    await state.set_state(FinancesForm.category3)
    await message.reply("Введите третью категорию расходов:")


@dp.message(FinancesForm.category3)
async def finances_category3(message: Message, state: FSMContext):
    await state.update_data(category3=message.text)
    await state.set_state(FinancesForm.expenses3)
    await message.reply("Введите сумму расходов для третьей категории:")


@dp.message(FinancesForm.expenses3)
async def finances_expenses3(message: Message, state: FSMContext):
    await state.update_data(expenses3=float(message.text))
    data = await state.get_data()
    await state.clear()
    await message.answer("Расходы введены и сохранены!")


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())