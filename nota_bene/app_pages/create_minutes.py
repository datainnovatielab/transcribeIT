"""Page for creation of meeting minutes.

Module for creating meeting minutes from a transcript using OpenAI's API and Streamlit
framework. This module allows users to input a transcript, generate minutes in Markdown
format, and download them as either Markdown or PDF files. It also provides a user
interface to navigate back if no transcript is available.
"""

from io import BytesIO
import streamlit as st
from markdown_pdf import MarkdownPdf, Section
from openai import OpenAI
from nota_bene.utils import switch_page_button, save_session
from LLMlight import LLMlight

#%% Create header
@st.dialog("Key?")
def enter_api_key():
    """Enter OpenAI key in dialog window."""
    api_key = st.text_input("OpenAI API Key", value=st.session_state["openai_api_key"] or "", type="password")
    if st.button("Proceed"):
        st.session_state["openai_api_key"] = api_key
        st.rerun()

@st.fragment
def run_main():
    if st.session_state['project_name']:
        st.header('Create Minutes: ' + st.session_state['project_name'], divider=True)

    if st.session_state['transcript']:
        # switch_page_button("app_pages/transcribe.py", text="The Transcripts are a must to create minute notes.")

        with st.container(border=True):
            col1, col2 = st.columns(2)

            # Selectionbox
            col1.caption('Select Large Language Model')
            options = st.session_state['model_names']
            user_model = col1.selectbox(label='Select model', options=options, index=options.index(st.session_state['model']), label_visibility='collapsed')
            if user_model != st.session_state['model']:
                st.session_state['model'] = user_model
                st.rerun()

            # Button
            col2.caption('Create Minute Notes')
            user_press = col2.button(f"Run LLM!", type='primary', use_container_width=True)

            # Show key
            if st.session_state['model'] == 'gpt-4o-mini':
                if col1.button("OpenAI-key invoeren", use_container_width=True):
                    enter_api_key()
                if st.session_state['model'] == 'gpt-4o-mini':
                    if st.session_state["openai_api_key"]:
                        col2.write("✅ API-key found")
                    else:
                        col2.write("❌ API-key not found")

            # Run LLM
            if user_press and st.session_state['model'] == 'gpt-4o-mini':
                run_openai()
            elif user_press:
                run_local_llm()

    # Show minutes
    show_minutes()
    # Show Back-Download button
    navigation()


# %%
@st.fragment
def show_minutes():
    st.session_state.setdefault("edit_mode_minutes", False)

    with st.container(border=True):
        if not st.session_state.get("minutes"):
            st.info("Minutes notes are not found.")
            return

        if st.session_state["edit_mode_minutes"]:
            # Editable mode
            updated_minutes = st.text_area(
                label="Edit Minutes",
                value=st.session_state["minutes"],
                height=1000,
                label_visibility="collapsed",
                key="minutes_editor"
            )
            col1, col2 = st.columns([0.2, 0.8])
            with col1:
                if st.button("💾 Save Minutes"):
                    st.session_state["minutes"] = updated_minutes
                    st.session_state["edit_mode_minutes"] = False
                    st.success("Notulen zijn bijgewerkt.")
                    st.rerun()
            with col2:
                if st.button("❌ Cancel"):
                    st.session_state["edit_mode_minutes"] = False
                    st.rerun()
        else:
            # View mode
            st.markdown(st.session_state["minutes"])
            if st.button("✏️ Edit Minutes"):
                st.session_state["edit_mode_minutes"] = True
                st.rerun()

# %%
def navigation():
    with st.container(border=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            switch_page_button("app_pages/model_instructions.py", text='Previous stap: Set Model Instructions')

        with col2:
            if st.session_state["minutes"]:
                st.download_button("Download notulen (.md)", file_name="notulen.md", data=st.session_state["minutes"], type='primary')
        with col3:
            if st.session_state["minutes"]:
                pdf = MarkdownPdf(toc_level=2)
                f = BytesIO()
                pdf.add_section(Section(st.session_state["minutes"]))
                pdf.save(f)
                st.download_button("Download notulen (.pdf)", file_name="notulen.pdf", data=f, type='primary')

# %%
def run_local_llm():
    from nota_bene.utils import API_LLM
    
    # Get prompts
    system_prompt = st.session_state['prompt']
    prompt = st.session_state['transcript']
    
    # Initialize
    model = API_LLM(model_id=st.session_state['model'], api_url=st.session_state['endpoint'], temperature=0.7)
    response = model.run(f"{system_prompt}\n\n{prompt}")
    
    # system_prompt = "You are an AI assistant"
    # prompt = "hi"
    # payload = {
    #     "model": user_select,
    #     "prompt": f"{system_prompt}\n\n{prompt}",
    #     "prompt": prompt,
    #     "stream": False
    #     }
    
    # response = requests.post('http://localhost:11434/api/generate', json=payload)
    
    # # st.write(response.text)
    # # print(response.text)
    # response = json.loads(response.text)
    # response = response['response']
    
    st.session_state["minutes"] = response
    save_session()

# %%
def run_openai():
    client = OpenAI(api_key=st.session_state['openai_api_key'])
    response = client.chat.completions.create(
        model=st.session_state['model'],
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": st.session_state['prompt'],
            },
            {"role": "user", "content": st.session_state['transcript']},
        ],
        stream=True,
    )

    st.session_state["minutes"] = st.write_stream(response)
    save_session()

# %%
run_main()
