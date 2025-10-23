import streamlit as st
import os
import re
import pandas as pd
from openai import OpenAI
from langchain_core.tools import Tool
from langchain.memory import ConversationBufferMemory
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document

# Show title and description
st.title("📄 Rohan's Research Assistant")

# Model selection
model = st.radio("Model", ("Mini", "Advanced Model"))
gpt_version = "gpt-4o-mini" if model == "Mini" else "gpt-4o"

# Initialize session state
if 'lab6_vectorstore' not in st.session_state:
    st.session_state.lab6_vectorstore = None
if 'lab6_df' not in st.session_state:
    st.session_state.lab6_df = None
if 'lab6_messages' not in st.session_state:
    st.session_state.lab6_messages = []
if 'lab6_agent' not in st.session_state:
    st.session_state.lab6_agent = None

# Initialize vectorstore
@st.cache_resource
def initialize_vectorstore():
    """Initialize vector database from CSV"""
    CSV_PATH = "/workspaces/multi-page-streamlit-app/lab/arxiv_papers_extended_20251019_150748.csv"
    PERSIST_DIR = "LAB6_vector_db"

    os.makedirs(PERSIST_DIR, exist_ok=True)
    df = pd.read_csv(CSV_PATH)

    docs = []
    for _, row in df.iterrows():
        text = (
            f"Title: {row.get('title','')}\n"
            f"Authors: {row.get('authors','')}\n"
            f"Abstract: {row.get('abstract','')}\n"
            f"Year: {row.get('year','')}\n"
            f"Category: {row.get('category','')}\n"
            f"Venue: {row.get('venue','')}"
        )
        metadata = {
            'title': row.get('title', ''),
            'authors': row.get('authors', ''),
            'link': row.get('link', ''),
            'year': row.get('year', ''),
            'category': row.get('category', ''),
            'venue': row.get('venue', '')
        }
        docs.append(Document(page_content=text, metadata=metadata))

    embeddings = OpenAIEmbeddings(api_key=st.secrets["API_KEY"])
    vectorstore = Chroma.from_documents(docs, embeddings, persist_directory=PERSIST_DIR)
    return vectorstore, df

# Initialize vectorstore and data
if st.session_state.lab6_vectorstore is None:
    try:
        st.session_state.lab6_vectorstore, st.session_state.lab6_df = initialize_vectorstore()
    except Exception as e:
        st.error(f"Vectorstore Error: {e}")
        st.stop()

# Define custom tools
def search_papers(query: str) -> str:
    """Search for research papers by topic"""
    results = st.session_state.lab6_vectorstore.similarity_search(query, k=5)
    if not results:
        return f"No papers found about '{query}'"
    return "\n".join([
        f"{i+1}. {doc.metadata.get('title','')}\n"
        f"   Authors: {doc.metadata.get('authors','')}\n"
        f"   Link: {doc.metadata.get('link','')}\n"
        for i, doc in enumerate(results)
    ])

def compare_papers(query: str) -> str:
    """Compare two papers by title"""
    parts = re.split(r"\s+and\s+|\s+vs\.?\s+", query, flags=re.IGNORECASE)
    if len(parts) < 2:
        return "Please specify two papers: 'paper1 and paper2'"
    
    df = st.session_state.lab6_df
    
    def find(title):
        m = df[df["title"].str.contains(title.strip(), case=False, na=False)]
        if m.empty:
            return None
        r = m.iloc[0]
        return f"{r['title']}\nAuthors: {r['authors']}\nAbstract: {r['abstract'][:300]}..."
    
    p1, p2 = find(parts[0]), find(parts[1])
    if not p1 or not p2:
        return "Could not find one or both papers."
    return f"### Paper 1\n{p1}\n\n### Paper 2\n{p2}"

# Register tools
tools = [
    Tool(
        name="SearchPapers",
        func=search_papers,
        description="Find research papers on a topic. Input should be a search query string."
    ),
    Tool(
        name="ComparePapers",
        func=compare_papers,
        description="Compare two papers by title. Input should be 'paper1 and paper2' or 'paper1 vs paper2'."
    )
]

# Initialize LLM and Agent (only once)
if st.session_state.lab6_agent is None:
    try:
        # Initialize LLM
        llm = ChatOpenAI(
            model=gpt_version,
            api_key=st.secrets["openai_api_key"],
            temperature=0
        )
        
        # Initialize memory
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="output"
        )
        
        # Pull ReAct prompt
        prompt = hub.pull("hwchase17/react")
        
        # Create agent
        agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
        
        # Create agent executor
        st.session_state.lab6_agent = AgentExecutor(
            agent=agent,
            tools=tools,
            memory=memory,
            verbose=True,
            handle_parsing_errors=True
        )
    except Exception as e:
        st.error(f"Agent initialization error: {e}")
        st.stop()

# Display chat history
for message in st.session_state.lab6_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat interface
if user_input := st.chat_input("💬 Ask about research papers..."):
    # Add user message to history
    st.session_state.lab6_messages.append({"role": "user", "content": user_input})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Generate and display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = st.session_state.lab6_agent.invoke({
                    "input": user_input,
                    "chat_history": st.session_state.lab6_messages
                })
                output = response.get("output", str(response))
            except Exception as e:
                output = f"Error: {str(e)}"
            
            st.markdown(output)
            st.session_state.lab6_messages.append({"role": "assistant", "content": output})