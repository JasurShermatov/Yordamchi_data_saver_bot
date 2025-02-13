from aiogram.fsm.state import StatesGroup, State


class FileCreateState(StatesGroup):
    waiting_for_files = State()
    waiting_for_category = State()


class FileDeleteState(StatesGroup):
    waiting_for_category = State()
    waiting_for_file = State()
