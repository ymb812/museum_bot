from aiogram.fsm.state import State, StatesGroup


class CatalogStateGroup(StatesGroup):
    product_interaction = State()
    get_presentation = State()
