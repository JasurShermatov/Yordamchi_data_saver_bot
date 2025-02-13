from aiogram.fsm.state import StatesGroup, State


class ChannelStates(StatesGroup):
    add_channel = State()
    delete_channel = State()
