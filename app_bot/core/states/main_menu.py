from aiogram.fsm.state import State, StatesGroup


class MainMenuStateGroup(StatesGroup):
    menu = State()
    exhibit = State()
