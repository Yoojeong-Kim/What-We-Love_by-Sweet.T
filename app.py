import streamlit as st
import openai
import os

# add style
def local_css(file_name):
    # 파일 경로를 더 안정적으로 탐색합니다.
    p = Path(file_name)
    if p.exists():
        with p.open() as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css(".streamlit/style.css")

# Set a title for the Streamlit app
st.title("Nevertheless Chatbot")
st.markdown("---")

# The JavaScript `const apiKey = '...';` part
# We use st.secrets for secure key management, or environment variables
# You should store your key in `.streamlit/secrets.toml` or as an environment variable
# on your deployment service (like Streamlit Community Cloud).
# Example: api_key = os.getenv("OPENAI_API_KEY")
api_key = st.secrets["OPENAI_API_KEY"]

# --- 변경된 부분 시작 ---
# API 키를 openai 클라이언트 객체에 직접 전달하는 방식으로 변경
client = openai.OpenAI(api_key=api_key)
# openai.api_key = api_key # 이 코드는 더 이상 필요하지 않습니다.
# --- 변경된 부분 끝 ---

# The JavaScript `const initialMessages = [...]` part
initial_messages = [
    {"role": "system", "content": "Your name is 'Nevertheless'. You will return a score for keywords that people enter, based on a certain standard."},
    {"role": "system", "content": "People will enter various things like actions, objects, or people. So the keywords you receive will be very diverse."},
    {"role": "system", "content": "You must calculate a score based on how much it 'ruins the world'."},
    {"role": "system", "content": "Ruining the world can be based on various criteria, such as environmental pollution or the destruction of humanity."},
    {"role": "system", "content": "For example, if you receive the keyword 'coffee', you can calculate a score considering the environmental pollution from its production and the child labor exploited to pick coffee beans."},
    {"role": "system", "content": "The score is from -1 to -100. The more it ruins the world, the smaller the number you should give."},
    {"role": "system", "content": "If it's difficult to calculate a score for the destruction of humanity, use the Four Sprouts of Mencius as a standard."},
    {"role": "system", "content": "The Four Sprouts of Mencius are shame, right and wrong, compassion, and modesty. So the more it deviates from them, the lower the score."},
    {"role": "system", "content": "After stating the score, you must briefly explain why that score was given."},
    {"role": "system", "content": "Answer in English and always say '(your keyword) has ruined the world as (your score).' Where (your keyword) is the input keyword and (your score) is your calculated score. The reason should follow this sentence."},
]

# Initialize chat history in Streamlit's session state
# This is crucial for maintaining chat history in a stateful way
if "messages" not in st.session_state:
    st.session_state.messages = initial_messages.copy()

# The JavaScript `addMessage` and `chatMessages.prepend` parts
# We iterate through the messages in the session state to display them
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# The JavaScript `userInput` and `sendButton` parts
# Streamlit's chat_input handles both the text field and Enter key
if prompt := st.chat_input("What You Love"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call the OpenAI API and get the response
    with st.chat_message("assistant"):
        with st.spinner("Nevertheless is thinking..."):
            try:
                # --- 변경된 부분 시작 ---
                # openai.ChatCompletion.create()를 client.chat.completions.create()로 변경
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                    temperature=0.8,
                    max_tokens=1024,
                    top_p=1,
                    frequency_penalty=0.5,
                    presence_penalty=0.5,
                    stop=["대화종료"],
                )
                ai_response = response.choices[0].message.content
                st.markdown(ai_response)

                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
            except openai.OpenAIError as e:
                st.error(f"OpenAI API Error: {e}")
