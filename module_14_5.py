from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from crud_functions import *

api = ""
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

choise_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Рассчитать норму калорий", callback_data="Calories")],
        [InlineKeyboardButton(text="Формулы расчёта", callback_data="Formulas")]
    ]
)

buy_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Product1", callback_data="product_buying"),
            InlineKeyboardButton(text="Product2", callback_data="product_buying"),
            InlineKeyboardButton(text="Product3", callback_data="product_buying"),
            InlineKeyboardButton(text="Product4", callback_data="product_buying")
        ]
    ]
)

start_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Информация'),
            KeyboardButton(text='Рассчитать'),
            KeyboardButton(text='Регистрация')
        ],
        [KeyboardButton(text='Купить')]
    ], resize_keyboard=True
)
initiate_db()
check_and_populate_products()
products = get_all_products()


@dp.message_handler(text='Купить')
async def get_buying_list(message):
    with open('../module_14/img1.jpg', "rb") as product_1:
        await message.answer_photo(product_1,
                                   f"Название: Product1 | Описание: NIKRITIN - Для работы мозга | Цена: {1 * 100}")
    with open("../module_14/img2.jpg", "rb") as product_2:
        await message.answer_photo(product_2,
                                   f"Название: Product2 | Описание: PAPAZOL - Антидепрессант  | Цена: {2 * 100}")
    with open("../module_14/img3.jpg", "rb") as product_3:
        await message.answer_photo(product_3,
                                   f"Название: Product3 | Описание: PERDOLAN - Парацетомол | Цена: {3 * 100}")
    with open("../module_14/img4.jpg", "rb") as product_4:
        await message.answer_photo(product_4,
                                   f"Название: Product4 | Описание: BILZOL - Успокоительное | Цена: {4 * 100}")
    await message.answer("Выберите продукт для покупки:", reply_markup=buy_menu)


@dp.callback_query_handler(text="product_buying")
async def send_confirm_message(call):
    await call.message.answer("Вы успешно приобрели продукт!")
    await call.answer()


@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer('Выберите опцию: ', reply_markup=choise_menu)


@dp.callback_query_handler(text='Formulas')
async def get_formulas(call):
    await call.message.answer(
        'Расчет по формуле Миффлина-Сан Жеора для мужчин = 10 * Вес(в кг) + 6.25 * Рост(в см) - 5 * Возраст + 5,\n '
        'Расчет по формуле Миффлина-Сан Жеора для женщин = 10 * Вес(в кг) + 6.25 * Рост(в см) - 5 * Возраст - 161')
    await call.answer()


@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer(f"Привет, {message.from_user.username}! Я бот помогающий твоему здоровью.",
                         reply_markup=start_menu)


@dp.message_handler(text='Информация')
async def info(message):
    await message.answer('Помогу тебе выбрать лекарства и следить за твоим здоровьем, доверься мне друг')
    with open('../module_14/img5.jpg', 'rb') as file:
        await message.answer_photo(file, reply_markup=choise_menu)


class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()
    balance = 1000


@dp.message_handler(text="Регистрация")
async def sing_up(message):
    await message.answer("Введите имя пользователя (только латинский алфавит):")
    await RegistrationState.username.set()


@dp.message_handler(state=RegistrationState.username)
async def set_username(message, state):
    username = message.text.strip()
    if not username.isalnum():
        await message.answer("Имя пользователя должно содержать только буквы и цифры. Попробуйте ещё раз:")
        return

    if is_included(username):
        await message.answer("Пользователь с таким именем уже существует. Введите другое имя:")
    else:
        await state.update_data(username=username)
        await message.answer("Введите свой email:")
        await RegistrationState.email.set()


@dp.message_handler(state=RegistrationState.email)
async def set_email(message: types.Message, state: FSMContext):
    email = message.text.strip()
    if "@" not in email or "." not in email:
        await message.answer("Введите корректный email.")
        return

    await state.update_data(email=email)
    await message.answer("Введите свой возраст:")
    await RegistrationState.age.set()


@dp.message_handler(state=RegistrationState.age)
async def set_age(message: types.Message, state: FSMContext):
    if not message.text.isdigit() or int(message.text) <= 0:
        await message.answer("Возраст должен быть положительным числом. Введите корректный возраст:")
        return

    age = int(message.text)
    data = await state.get_data()
    add_user(data['username'], data['email'], age)

    await message.answer(f"Регистрация завершена! Добро пожаловать, {data['username']}!")
    await state.finish()


class UserState(StatesGroup):
    sex = State()
    age = State()
    growth = State()
    weight = State()


@dp.callback_query_handler(text='Calories', state=None)
async def sex_form(call):
    sex_menu = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Мужской", callback_data="sex_male")],
            [InlineKeyboardButton(text="Женский", callback_data="sex_female")]
        ]
    )
    await call.message.answer('Выберите свой пол:', reply_markup=sex_menu)
    await call.answer()


@dp.callback_query_handler(lambda c: c.data.startswith('sex_'), state=None)
async def set_sex(call: types.CallbackQuery, state: FSMContext):
    sex = "мужской" if call.data == "sex_male" else "женский"
    await state.update_data(sex=sex)
    await call.message.answer(f"Вы выбрали: {sex}. Теперь введите свой возраст:")
    await UserState.age.set()
    await call.answer()


@dp.message_handler(state=UserState.sex)
async def set_age(message: types.Message, state: FSMContext):
    await state.update_data(sex=message.text)
    await message.reply('Введите свой возраст: ')
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.reply('Введите свой рост: ')
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    await state.update_data(growth=message.text)
    await message.reply('Введите свой вес:')
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    await state.update_data(weight=message.text)

    data = await state.get_data()
    age = int(data['age'])
    growth = int(data['growth'])
    weight = int(data['weight'])
    sex = str(data['sex'])
    if sex == 'мужской':
        calories = int(10 * weight + 6.25 * growth - 5 * age + 5)
    elif sex == 'женский':
        calories = int(10 * weight + 6.25 * growth - 5 * age - 161)

    await message.reply(f"Ваша норма калорий: {calories} ккал в день")
    await state.finish()


@dp.message_handler()
async def all_messages(message):
    print('Получено новое сообщение')
    await message.answer('Введите команду \start, чтобы начать общение')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
# connection.commit()
# connection.close()
