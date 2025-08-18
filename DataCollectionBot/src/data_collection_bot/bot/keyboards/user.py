from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def user_keyboard(choice: list[str]) -> InlineKeyboardMarkup:
    buttons = []
    row = []
    for item in choice:
        row.append(InlineKeyboardButton(text=item, callback_data=f'answer:{item}'))
        if len(row) == 2:
            buttons.append(row.copy())
            row.clear()
    if len(row) > 0:
        buttons.append(row.copy())
        row.clear()
    return InlineKeyboardMarkup(inline_keyboard=buttons)