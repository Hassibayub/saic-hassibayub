import streamlit as st
from llama_index.agent.openai import OpenAIAgent

from src.agent import chat_engine

st.title("AI Car Salesperson 🤖")


@st.cache_resource
def fetch_engine() -> dict[str, OpenAIAgent]:
    return chat_engine(verbose=False)


agents = fetch_engine()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "passed" not in st.session_state:
    st.session_state.passed = 0  # 0 for agentX and 1 for agentY

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


@st.cache_resource
def add_first_message():
    """Add first message to the chat."""
    first_message = "Hello, How can I help you selecting car. \
    Can you let me know the preference of car you are looking for?"
    st.chat_message("assistant").markdown(first_message)


add_first_message()


def main():
    if prompt := st.chat_input("What is up?"):
        if prompt == "exit":
            st.chat_message("user").markdown("Bye!")
            st.session_state.messages = []

        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        if st.session_state.passed == 0:
            response = agents["agentX"].chat(prompt)
        else:
            response = agents["agentY"].chat(prompt)

        if "</EXIT>" in str(response):
            response = "Agent (Y): Thank you for your time. Your car has been booked. \
            We will send you an email with the details."

        # Check if user has passed to agentY, and if so, check for the </PASS> token
        if "</PASS>" in str(response):
            response = "Hello I am agent Y. I am here to help you with purchase. May I know your name?"
            agents["agentY"].chat_history.append(agents["agentX"].chat_history[-3])
            agents["agentY"].chat_history.append(agents["agentX"].chat_history[-2])
            agents["agentY"].chat_history.append(agents["agentX"].chat_history[-1])
            st.session_state.passed = 1

        with st.chat_message("assistant"):
            st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()
