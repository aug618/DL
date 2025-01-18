# chat_history_manager.py
from token_counter import count_tokens

def trim_chat_history(chat_history, max_tokens=50000):
    total_tokens = 0
    trimmed_history = []
    for message in reversed(chat_history):
        tokens = count_tokens(message["content"])
        if total_tokens + tokens > max_tokens:
            break
        trimmed_history.append(message)
        total_tokens += tokens
    return list(reversed(trimmed_history))

def add_message_to_history(chat_history, role, content):
    chat_history.append({"role": role, "content": content})
    return chat_history