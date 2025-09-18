import streamlit as st
from openai import OpenAI
from pathlib import Path
from PyPDF2 import PdfReader
import sys 
import pysqlite3
sys.modules['sqlite3']=pysqlite3
import chromadb

# Show title and description.
st.title("📄 Rohan's Chatbot")

chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="lab4Collection")

if 'openai_client' not in st.session_state:
    openai_api_key = st.secrets["API_KEY"]
    st.session_state.openai_client = OpenAI(api_key=openai_api_key)

def add_to_collection(collection, text, filename):
    openai_client = st.session_state.openai_client
    response = openai_client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    embedding = response.data[0].embedding

    collection.add(
        documents=[text],
        ids=[filename],
        embeddings=[embedding]
    )

pdf_dir = Path("pdfFiles")
txt_dir = Path("dataFiles")
txt_dir.mkdir(exist_ok=True)

for pdf_file in pdf_dir.glob("*.pdf"):
    reader = PdfReader(str(pdf_file))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    txt_file = txt_dir / (pdf_file.stem + ".txt")
    with open(txt_file, "w", encoding="utf-8") as f:
        f.write(text)
    add_to_collection(collection, text, pdf_file.stem)

if 'messages' not in st.session_state:
    st.session_state['messages']=[{'role':'assistant','content':'Hi how can I help?'}]



#chat input
if prompt:=st.chat_input('Talk to me Goose'):
    st.session_state.messages = st.session_state.messages[-12:]

    # Append user message
    st.session_state.messages.append({'role':'user','content':prompt})

for msg in st.session_state.messages:
    chat_msg=st.chat_message(msg['role'])
    chat_msg.write(msg['content'])

topic=st.sidebar.selectbox('Topic',('Text Mining','GenAI'))
openai_client = st.session_state.openai_client
response=openai_client.embeddings.create(
    input=topic,
    model="text-embedding-3-small"
)

query_embedding = response.data[0].embedding

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=3
)

for i in range(len(results['documents'][0])):
    doc=results['documents'][0][i]
    doc_id=results['ids'][0][i]
    st.write(f"The following file might be helpfu;l: {doc_id}")

# Generate an answer using the OpenAI API.
# if prompt:
#     client=st.session_state.client
#     stream = client.chat.completions.create(
#         model=gptVersion,
#         messages=st.session_state.messages,
#         stream=True,
#     )

    # with st.chat_message('assistant'):
    #     response=st.write_stream(response)

    #st.session_state.messages.append({'role':'assistant','content':f'{response}'})

    
