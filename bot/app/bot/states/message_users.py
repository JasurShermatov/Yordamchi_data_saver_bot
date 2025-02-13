from aiogram.fsm.state import StatesGroup, State


class BroadcastStates(StatesGroup):
    waiting_message = State()
