# chat_stream.py
from chat_history_manager import trim_chat_history

def chat_stream(client, query, system_message=None, temperature=0.5, context=None, chat_history=None):
    if chat_history is None:
        chat_history = []

    if system_message:
        chat_history.append({"role": "system", "content": system_message})

    chat_history.append({"role": "user", "content": query})

    if context:
        chat_history.append({"role": "system", "content": context})

    chat_history = trim_chat_history(chat_history)

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=chat_history,
        stream=True,
        temperature=temperature
    )
    return response, chat_history