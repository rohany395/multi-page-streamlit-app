import streamlit as st
from openai import OpenAI

#sidebar
add_sidebar=st.sidebar.selectbox("Summary options",("Summarize the document in 100 words","Summarize the document in 2 connecting paragraphs","Summarize the document in 5 bullet points"))

# Show title and description.
st.title("📄 Rohan's Document question answering app")
st.write(
    "Upload a document below and ask a question about it – GPT will answer! "
)

openai_api_key = st.secrets["API_KEY"]
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:

    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Let the user upload a file via `st.file_uploader`.
    uploaded_file = st.file_uploader(
        "Upload a document (.txt or .md)", type=("txt", "md")
    )

    #checkbox
    model=st.radio("Model",("Mini","Advanced Model"))
    gptVersion="gpt-5"

    if model=="Mini":
        gptVersion="gpt-4o-mini"
    else:
        gptVersion="gpt-4o"

    # # Ask the user for a question via `st.text_area`.
    # question = st.text_area(
    #     "Now ask a question about the document!",
    #     placeholder="Can you give me a short summary?",
    #     disabled=not uploaded_file,
    # )

    if uploaded_file and add_sidebar:

        # Process the uploaded file and question.
        document = uploaded_file.read().decode()
        messages = [
            {
                "role": "user",
                "content": f"Here's a document: {document} \n\n---\n\n {add_sidebar}",
            }
        ]

        # Generate an answer using the OpenAI API.
        stream = client.chat.completions.create(
            model=gptVersion,
            messages=messages,
            stream=True,
        )

        # Stream the response to the app using `st.write_stream`.
        st.write_stream(stream)