from aiogram import Router
from aiogram.filters import Filter
from utils.translator.translator import Translator
from aiogram.types import Message


class StartDialogFilter(Filter):
    def __init__(self, key: str) -> None:
        self.keyword = key

    async def __call__(self, msg: Message, translator: Translator):
        return msg.text == translator[self.keyword]
