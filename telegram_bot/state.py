user_state = {}


def set_user_state(telegram_id: int, news_ids: list):
    user_state[telegram_id] = {
        "news_ids": news_ids,
        "index": 0
    }


def get_user_state(telegram_id: int):
    return user_state.get(telegram_id)


def update_index(telegram_id: int, index: int):
    if telegram_id in user_state:
        user_state[telegram_id]["index"] = index


def clear_user_state(telegram_id: int):
    if telegram_id in user_state:
        del user_state[telegram_id]