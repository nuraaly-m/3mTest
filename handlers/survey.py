from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from config import database


survey_router = Router()


class BookSurvey(StatesGroup):
    name = State()
    age = State()
    occupation = State()
    salary_or_grade = State()


@survey_router.message(Command("stop"))
@survey_router.message(F.text.lower() == "стоп")
async def stop(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Спасибо за прохождение опроса!")


@survey_router.message(Command('survey'))
async def start_survey(message: types.Message, state: FSMContext):
    # await message.answer()
    await state.set_state(BookSurvey.name)
    await message.answer('как вас зовут?')


@survey_router.message(BookSurvey.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(BookSurvey.age)
    await message.answer(f'сколько вам лет, {message.text}?')


@survey_router.message(BookSurvey.age)
async def process_age(message: types.Message, state: FSMContext):
    age = message.text
    if not age.isdigit():
        await message.answer('введите число')
        return
    if int(age) < 10 or int(age) > 100:
        await message.answer('введите возраст от 10 до 100')
        return
    await state.update_data(age=age)
    await state.set_state(BookSurvey.occupation)
    await message.answer('ваш род занятий')

@survey_router.message(BookSurvey.occupation)
async def process_occupation(message: types.Message, state: FSMContext):
    age_user = (await state.get_data()).get('age', 0)
    if int(age_user)<18:
        await message.answer('какая ваша средняя оценка')
    else:
        await message.answer('какая у вас зарплата')
    await state.set_state(BookSurvey.salary_or_grade)
    await state.update_data(occupation=message.text)


@survey_router.message(BookSurvey.salary_or_grade)
async def process_salary_or_grade(message: types.Message, state: FSMContext):
    await state.update_data(salary_or_grade=message.text)
    data = await state.get_data()
    await database.execute(
        '''INSERT INTO survey (name, age, occupation, salary_or_grade) VALUES (?, ?, ?, ?)''',
        (data['name'], data['age'], data['occupation'], data['salary_or_grade'])
    )
    await message.answer('спасибо за опрос')
    await state.clear()