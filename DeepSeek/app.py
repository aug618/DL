# app.py
import streamlit as st
from file_processor import process_file
from chat_stream import chat_stream
from chat_history_manager import add_message_to_history
from openai import OpenAI


with st.sidebar:
    st.markdown(""" 
    <center>
    <img src="https://i.ibb.co/MgBss0Q/1.webp" alt="1" border="0" width="250" height="220">
    <h1><sup>极恶贝利亚💬</sup></h1>
    </center>""", unsafe_allow_html=True)

    system_message = st.text_area("定义角色", value="我是贝利亚, 你可以问我任何问题🤣")
    temperature = st.slider("Creativity", min_value=0.0, max_value=2.0, value=1.0, step=0.1)
    api_key = st.sidebar.text_input('OpenAI API Key', type='password')
    base_url = st.sidebar.text_input('OpenAI Base URL')

# 主界面设置
st.title("🐔邪恶贝利亚")


# 上传文件
uploaded_files = st.file_uploader("上传文件", type=["txt", "pdf", "docx"], accept_multiple_files=True)

# 处理上传的文件
documents = []
for file in uploaded_files:
    try:
        file_content = process_file(file)
        documents.append(file_content)
    except ValueError as e:
        st.warning(str(e))

# 使用 session_state 初始化聊天记录
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 显示聊天记录
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# openai 客户端初始化
client = OpenAI(api_key=api_key, base_url=base_url)

# 处理用户输入并显示
user_input = st.chat_input("你想问我什么问题?", key="user_input")
if user_input:
    with st.chat_message("user"):
        st.write(user_input)

    st.session_state.chat_history = add_message_to_history(st.session_state.chat_history, "user", user_input)

    context = "\n".join(documents) if documents else None

    with st.spinner("让我想一想先..."):
        response, st.session_state.chat_history = chat_stream(
            client, user_input, system_message, temperature, context, st.session_state.chat_history
        )
        message_placeholder = st.empty()
        full_response = ""

        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                message_placeholder.markdown(full_response + "...")

        message_placeholder.markdown(full_response)
        st.session_state.chat_history = add_message_to_history(st.session_state.chat_history, "assistant", full_response)