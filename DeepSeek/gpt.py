import streamlit as st
from openai import OpenAI
import configparser
import PyPDF2
from docx import Document
import tiktoken

# 读取配置文件
config = configparser.ConfigParser()
config.read('config.ini')

# 获取 API 密钥和基础 URL
api_key = config['openai']['api_key']
base_url = config['openai']['base_url']

# 侧边栏 UI 配置
with st.sidebar:
    # 设置标题和图像
    st.markdown(f""" 
    <center>
    <img src="https://i.ibb.co/MgBss0Q/1.webp" alt="1" border="0" width="250" height="220">
    <h1>DeepSeek-V3<sup>💬</sup></h1>
    </center>""", unsafe_allow_html=True)
    
    # 系统消息配置，用户可以自定义系统消息
    system_message = st.text_area("定义角色", value="我是米塔, 你可以问我任何问题🤣")
    
    # 创造性调节器，调整生成内容的创意性
    temperature = st.slider("Creativity", min_value=0.0, max_value=2.0, value=1.0, step=0.1,
                            help="The higher the value, the more creative the text will be.")

# 主界面设置
st.title("🦜米塔助手")

# 上传文件
uploaded_files = st.file_uploader("上传文件", type=["txt", "pdf", "docx"], accept_multiple_files=True)

# 处理上传的文件
documents = []
for file in uploaded_files:
    if file.type == "text/plain":
        # 处理文本文件
        file_content = file.read().decode("utf-8")
        documents.append(file_content)
    elif file.type == "application/pdf":
        # 处理 PDF 文件
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        documents.append(text)
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        # 处理 Word 文件
        doc = Document(file)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        documents.append(text)
    else:
        st.warning(f"不支持的文件类型: {file.type}")

# 使用 session_state 初始化聊天记录
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{
        "role": "assistant",
        "content": "我是米塔, 你可以问我任何问题🤣"
    }]

# 显示聊天记录
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# openai 客户端初始化
client = OpenAI(api_key=api_key, base_url=base_url)
if "messageHistory" not in st.session_state:
    st.session_state.messageHistory = []

# 定义函数计算 token 数
def count_tokens(text, model="gpt-4"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

# 定义函数清理聊天历史记录
def trim_chat_history(chat_history, max_tokens=50000):
    encoding = tiktoken.encoding_for_model("gpt-4")
    total_tokens = 0
    trimmed_history = []
    for message in reversed(chat_history):
        tokens = count_tokens(message["content"])
        if total_tokens + tokens > max_tokens:
            break
        trimmed_history.append(message)
        total_tokens += tokens
    return list(reversed(trimmed_history))

# 定义聊天流处理函数
def chat_stream(query, system_message=None, temperature=0.5, context=None):
    if system_message:
        st.session_state.messageHistory.append({"role": "system", "content": system_message})
    
    # 添加用户消息到历史记录
    st.session_state.messageHistory.append({"role": "user", "content": query})

    # 将上传的文件内容作为上下文传递给模型
    if context:
        st.session_state.messageHistory.append({"role": "system", "content": context})

    # 清理聊天历史记录，确保不超过最大 token 数
    st.session_state.messageHistory = trim_chat_history(st.session_state.messageHistory)

    # 调用 DeepSeek API 获取聊天流数据
    response = client.chat.completions.create(
        model="deepseek-chat", 
        messages=st.session_state.messageHistory, 
        stream=True, 
        temperature=temperature
    )
    return response

# 处理用户输入并显示
user_input = st.chat_input("你想问我什么问题?", key="user_input")
if user_input:
    # 显示用户输入
    with st.chat_message("user"):
        st.write(user_input)

    # 将用户输入添加到聊天历史记录
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # 准备上下文
    context = "\n".join(documents) if documents else None

    # 显示加载状态并调用 DeepSeek 接口
    with st.spinner("让我想一想先..."):
        response = chat_stream(user_input, system_message, temperature, context)
        message_placeholder = st.empty()
        full_response = ""

        # 按流式数据获取内容并更新显示
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                message_placeholder.markdown(full_response + "...")

        # 完成所有内容后显示最终回答
        message_placeholder.markdown(full_response)

        # 将 AI 响应添加到聊天历史记录
        st.session_state.chat_history.append({"role": "assistant", "content": full_response})