import asyncio
from aiogram import Bot, Dispatcher, types, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.filters import Command
import nest_asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client
from dotenv import dotenv_values
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import json

asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
nest_asyncio.apply()

secrets_file="/run/secrets/api_keys"
conf = dotenv_values(secrets_file)

TELEGRAM_BOT_TOKEN = conf.get("TELEGRAM_BOT_TOKEN")


bot = Bot(token=str(TELEGRAM_BOT_TOKEN))
dp = Dispatcher()

async def call_mcp_tool(tool_name, args):
    async with sse_client("http://mcp-server:8050/sse") as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            return await session.call_tool(tool_name, arguments=args)

class RecipeStates(StatesGroup):
    choosing_mode = State()
    choosing_dish = State()
    choosing_servings = State()
    surprise_servings = State()


@dp.message(Command("start"))
async def start_cmd(msg: types.Message, state: FSMContext):
    kb = [
        [KeyboardButton(text="Create Recipe")],
        [KeyboardButton(text="Surprise Me")]
    ]
    await msg.answer(
        "Hi! I am your Ground Beef RAG Chef.\nWhat do you want to do?",
        reply_markup=ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    )
    await state.set_state(RecipeStates.choosing_mode)

@dp.message(RecipeStates.choosing_mode)
async def choose_mode(msg: types.Message, state: FSMContext):
    if msg.text == "Create Recipe":
        await msg.answer("What kind of dish do you want to cook?", reply_markup=ReplyKeyboardRemove())
        await state.set_state(RecipeStates.choosing_dish)
    elif msg.text == "Surprise Me":
        await msg.answer("How many people are you cooking for?", reply_markup=ReplyKeyboardRemove())
        await state.set_state(RecipeStates.surprise_servings)
    else:
        await msg.answer("Please choose a valid option.")

@dp.message(RecipeStates.choosing_dish)
async def get_dish(msg: types.Message, state: FSMContext):
    dish = msg.text
    await state.update_data(dish=dish)
    await msg.answer("How many people are you cooking for?")
    await state.set_state(RecipeStates.choosing_servings)


@dp.message(RecipeStates.choosing_servings)
async def get_servings(msg: types.Message, state: FSMContext):
    try:
        servings = int(msg.text)
    except ValueError:
        await msg.answer("Please enter a number.")
        return

    data = await state.get_data()
    dish = data.get("dish")
    await msg.answer("Please wait...")
    response = await call_mcp_tool("create_recipe", {"dish": dish, "servings": servings})
    #print("Response:",response, flush=True)
    recipe = response.content[0].model_dump()
    #print("Recipe:", recipe, flush=True)
    if "error" in recipe['text']:
        await msg.answer("No recipe found for your input.")
        await state.clear()
        return

    try:
        recipe_data = json.loads(recipe['text'])
    except Exception as e:
        await msg.answer("Recipe was not in valid JSON format.")
        await state.clear()
        return

    text = (
        f"🍽 <b>{recipe_data['title']}</b>\n\n"
        f"<b>Ingredients:</b>\n" + recipe_data['ingredients'] +
        "\n\n<b>Steps:</b>\n" + recipe_data['steps']
    )
    await msg.answer(text, parse_mode="HTML")
    await state.clear()

@dp.message(RecipeStates.surprise_servings)
async def get_surprise_servings(msg: types.Message, state: FSMContext):
    try:
        servings = int(msg.text)
    except ValueError:
        await msg.answer("Please enter a number.")
        return
    await msg.answer("Please wait...")
    response = await call_mcp_tool("experimental", {"servings": servings})
    recipe = response.content[0].model_dump()

    if "error" in recipe['text']:
        await msg.answer("No recipe found for your input.")
        await state.clear()
        return

    try:
        recipe_data = json.loads(recipe['text'])
    except Exception as e:
        await msg.answer("Recipe was not in valid JSON format.")
        await state.clear()
        return

    text = (
        f"🍽 <b>{recipe_data['title']}</b>\n\n"
        f"<b>Ingredients:</b>\n" + recipe_data['ingredients'] +
        "\n\n<b>Steps:</b>\n" + recipe_data['steps']
    )
    await msg.answer(text, parse_mode="HTML")
    await state.clear()

def run_bot():
    dp.run_polling(bot)

if __name__ == "__main__":
    asyncio.run(run_bot())