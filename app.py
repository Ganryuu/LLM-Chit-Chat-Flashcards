import streamlit as st
import genanki
import random
from streamlit_chat import message as msg
from PIL import Image
from langchain.memory import ConversationBufferMemory
import base64
from langchain.llms import CerebriumAI
from langchain import PromptTemplate, LLMChain
import os 



os.environ["CEREBRIUMAI_API_KEY"] = "API_KEY" # your cerebruimAI api key
st.set_page_config(page_title='LLM Chit Chat', page_icon=":star2:")
st.markdown("<h1 style='text-align: center;'>FlashCard LLM Generator</h1>", unsafe_allow_html=True)

# Define your genanki Model and Deck
model = genanki.Model(
    model_id=random.randrange(1 << 30, 1 << 31),
    name='SimpleModel',
    fields=[
        {'name': 'Question'},
        {'name': 'Answer'},
    ],
    templates=[
        {
            'name': 'Card 1',
            'qfmt': '{{Question}}',
            'afmt': '{{Answer}}',
        },
    ])

deck = genanki.Deck(
    deck_id=random.randrange(1 << 30, 1 << 31),
    name='LLM Chit Chat')




template = """
You are a friendly chatbot assistant that responds in a conversational
manner to users questions. Keep the answers short, unless specifically
asked by the user to elaborate on something.
Question: {question}

Answer:"""

prompt = PromptTemplate(template=template, input_variables=["question"])
llm = CerebriumAI(
  endpoint_url="https://run.cerebrium.ai/gpt4-all-webhook/predict",
  max_length=100
)
llm_chain = LLMChain(prompt=prompt, llm=llm)
def get_binary_file_downloader_html(bin_file, file_label='File'):
    """
    
    the streamlit doesn't support download for the apkg files thus we 
    read  the file data, encode it to base64, and then create an HTML link with the encoded data
    
    """
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{bin_file}">Download {file_label}</a>'
    return href
  
  
def main():
    with st.sidebar: 
      st.title("Chat with Your LLM and Generate Flashcard Anki Decks")
      choice = st.radio("Navigation", ["Chat", "History"])
      st.info("""Have a Converstaion with ggml-gpt4all-j-v1.3-groovy
              and generate flashcards for Anki""")
      
      
      st.markdown('My Github  https://github.com/Ganryuu star the repo if you liked the demo :)')  
      
      
    if choice =='Chat' :
      chat = st.expander("Chat Box", expanded=True)

      if 'conversations' not in st.session_state:
          st.session_state['conversations'] = []
          st.session_state['selections'] = []

      if 'input_key' not in st.session_state:
          st.session_state['input_key'] = 0
       
      query = chat.text_input("Enter Prompt", key=f"user_input_{st.session_state['input_key']}")
       
      
      if chat.button("Enter"):
        if query:  # Add the message only if the query is not empty
            response = llm(query)
            st.session_state['conversations'].append((query, response))
            st.session_state['selections'].append(False)
        st.session_state['input_key'] += 1  
            
      for i, conversation in enumerate(st.session_state['conversations']):
          st.write(f"User: {conversation[0]}")
          st.write(f"Bot: {conversation[1]}")
          st.session_state['selections'][i] = st.checkbox('Select to add to Anki deck', value=st.session_state['selections'][i], key=str(i))

      if st.button("Generate Anki Deck"):
          for i, conversation in enumerate(st.session_state['conversations']):
              if st.session_state['selections'][i]:
                  note = genanki.Note(
                      model=model,
                      fields=[conversation[0], conversation[1]])
                  deck.add_note(note)

          genanki.Package(deck).write_to_file('output.apkg')
          st.markdown(get_binary_file_downloader_html('output.apkg', 'Anki Deck'), unsafe_allow_html=True)

    elif  choice == 'History':
      
      for i, conversation in enumerate(st.session_state['conversations']):
          msg(f"Prompt: {conversation[0]}" , is_user=True)
          msg(f"Response: {conversation[1]}") 
      
if __name__ == "__main__":
    main()
