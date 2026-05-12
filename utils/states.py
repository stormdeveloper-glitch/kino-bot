"""
Aiogram v3 FSM holatlari
"""
from aiogram.fsm.state import State, StatesGroup


class AddMovieState(StatesGroup):
    code = State()
    file = State()
    title = State()
    caption = State()
    post_media = State()


class AddChannelState(StatesGroup):
    channel = State()


class BroadcastState(StatesGroup):
    message = State()
    confirm = State()


class EditSettingState(StatesGroup):
    value = State()


class DeleteMovieState(StatesGroup):
    code = State()
