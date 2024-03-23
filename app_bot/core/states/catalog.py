from aiogram.fsm.state import State, StatesGroup


class CatalogStateGroup(StatesGroup):
    status = State()
    problem = State()
    exhibit = State()
