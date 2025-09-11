import streamlit as st
from openai import OpenAI

# Show title and description.
st.title("📄 Rohan's Chatbot")

#checkbox
model=st.radio("Model",("Mini","Advanced Model"))
gptVersion="gpt-5"

if model=="Mini":
    gptVersion="gpt-4o-mini"
else:
    gptVersion="gpt-4o"

# Take user input.
# prompt=st.chat_input('Talk to me Goose')
# print(prompt,'hhhhh')


if 'client' not in st.session_state:
    openai_api_key = st.secrets["API_KEY"]
    st.session_state.client = OpenAI(api_key=openai_api_key)

if 'messages' not in st.session_state:
    st.session_state['messages']=[{'role':'assistant','content':'How can I help?'}]
if prompt:=st.chat_input('Talk to me Goose'):
    if len(st.session_state.messages) >2:
        st.session_state.messages.pop(0)
    st.session_state.messages.append({'role':'user','content':f'{prompt}'})

    for msg in st.session_state.messages:
        chat_msg=st.chat_message(msg['role'])
        chat_msg.write(msg['content'])
    st.session_state.messages.append({'role':'assistant','content':'do you want more info?'})
    

# Generate an answer using the OpenAI API.
if prompt:
    client=st.session_state.client
    stream = client.chat.completions.create(
        model=gptVersion,
        messages=st.session_state.messages,
        stream=True,
    )

    with st.chat_message('assistant'):
        response=st.write_stream(stream)

    st.session_state.messages.append({'role':'assistant','content':response})

print(st.session_state.messages,'kkk')

    
