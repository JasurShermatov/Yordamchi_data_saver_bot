from aiogram.fsm.state import StatesGroup, State


class CategoryCreateState(StatesGroup):
    name_for_category = State()
