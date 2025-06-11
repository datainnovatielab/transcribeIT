"""Page for creation of meeting minute notes.

Module for creating meeting minute notes from a transcript using OpenAI's API and Streamlit
framework. This module allows users to input a transcript, generate minute notes in Markdown
format, and download them as either Markdown or PDF files. It also provides a user
interface to navigate back if no transcript is available.
"""

from io import BytesIO
import streamlit as st
from markdown_pdf import MarkdownPdf, Section
from openai import OpenAI
from nota_bene.utils import switch_page_button, save_session, load_llm_model
import numpy as np
import time
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
        st.header('Create minute notes: ' + st.session_state['project_name'], divider=True)

    if st.session_state['context']:
        # switch_page_button("app_pages/transcribe.py", text="The Transcripts are a must to create minute notes.")

        with st.container(border=True):
            col1, col2 = st.columns([0.5, 0.5])

            # Selectionbox
            col1.caption('Select Large Language Model')
            options = st.session_state['model_names']
            try:
                index = options.index(st.session_state['model'])
            except:
                index = None

            user_model = col1.selectbox(label='Select model', options=options, index=index, label_visibility='collapsed')
            if user_model != st.session_state['model']:
                st.session_state['model'] = user_model
                st.rerun()

            # Button
            col2.caption('Create Minute Notes')
            user_press = col2.button(f"Run LLM!", type='primary', use_container_width=True)

            if user_model=='gpt-4o-mini':
                load_openai_modules(col1, col2)
            else:
                preprocessing, user_summarize, user_chunk_size = load_local_modules(col1)

            # Run local LLM
            if user_press and st.session_state['model'] == 'gpt-4o-mini':
                run_openai()
            elif user_press:
                run_local_llm(preprocessing=preprocessing, summarize=user_summarize, chunk_size=user_chunk_size)

    # Show minute_notes
    show_minute_notes()
    # Show Back-Download button
    navigation()

#%%
def load_local_modules(col1):
    user_method = col1.radio('Approach', options=['Unlimited', 'Global-reasoning', 'Chunk-Wise'], label_visibility='visible')
    user_summarize = True
    user_chunk_size = 8192

    # if user_method != 'Full':
        # user_summarize = col2.checkbox('Summarize results', value=True, label_visibility='visible')
        # user_chunk_size = col2.slider('Context Window', min_value=4096, max_value=16384, step=2048, value=8192)

    if user_method=='Global-reasoning':
        preprocessing='global-reasoning'
        user_chunk_text = user_chunk_size
    elif user_method=='Chunk-Wise':
        preprocessing='chunk-wise'
        user_chunk_text = user_chunk_size
    else:
        preprocessing=None
        user_chunk_text = 'Unlimited'
        user_chunk_size = None

    st.markdown(
        f"""
        <div style="padding: 1em; border-radius: 8px; background-color: #F3F4F6; color: #111827; font-size: 0.95em;">
            ✅ Instructions loaded: <strong>{st.session_state.get('instruction_name', 'N/A')}</strong><br>
            ✅ Model loaded: <strong>{st.session_state.get('model', 'N/A')}</strong><br>
            ✅ Method: <strong>{preprocessing}</strong> | Summarization: <strong>{user_summarize}</strong><br>
            ✅ Chunk size: <strong>{user_chunk_text}</strong>
        </div>
        """,
        unsafe_allow_html=True
    )

    return preprocessing, user_summarize, user_chunk_size

#%%
def load_openai_modules(col1, col2):
    # Show key
    if st.session_state['model'] == 'gpt-4o-mini':
        if col1.button("OpenAI-key invoeren", use_container_width=True):
            enter_api_key()
        if st.session_state['model'] == 'gpt-4o-mini':
            if st.session_state["openai_api_key"]:
                col2.write("✅ API-key found")
            else:
                col2.write("❌ API-key not found")

# %%
@st.fragment
def show_minute_notes():
    st.session_state.setdefault("edit_mode_minute_notes", False)

    if not st.session_state.get("minute_notes"):
        # st.info("Minute notes are not found.")
        return

    # Show some stats
    if len(st.session_state['timings_llm']) > 0:
        with st.container(border=True):
            st.markdown(f"""
            <div style="width: 100%; background-color: #E5E7EB; border-radius: 6px; margin-top: 1em;">
              <div style="width: {100}%; background-color: #3B82F6; height: 12px; border-radius: 6px;"></div>
            </div>
            """, unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Avg Time", f"{np.mean(st.session_state['timings_llm']):.1f} min")
            with col2:
                st.metric("Total Time", f"{np.sum(st.session_state['timings_llm']):.1f} min")
            with col3:
                try:
                    if st.session_state["minute_notes"] is not None:
                        st.metric("Words", f"{len(st.session_state['minute_notes'].split(' ')):.0f}")
                except:
                    st.metric("Words", 0)
                    # st.session_state["minute_notes"] = None

    with st.container(border=True):
        if st.session_state["edit_mode_minute_notes"]:
            # Editable mode
            if isinstance(st.session_state["minute_notes"], list):
                minute_notes =  "\n\n---\n\n".join([f"### Results {i+1}:\n{s}" for i, s in enumerate(st.session_state["minute_notes"])])
            else:
                minute_notes = st.session_state["minute_notes"]

            updated_minute_notes = st.text_area(
                label="Edit Minute notes",
                value=minute_notes,
                height=1000,
                label_visibility="collapsed",
                key="minute_notes_editor"
            )
            col1, col2 = st.columns([0.2, 0.8])
            with col1:
                if st.button("💾 Save Minute Notes"):
                    st.session_state["minute_notes"] = updated_minute_notes
                    st.session_state["edit_mode_minute_notes"] = False
                    st.success("Notulen zijn bijgewerkt.")
                    st.rerun()
            with col2:
                if st.button("❌ Cancel"):
                    st.session_state["edit_mode_minute_notes"] = False
                    st.rerun()
        else:
            # View mode
            st.markdown(st.session_state["minute_notes"])
            col1, col2 = st.columns(2)
            if col1.button("✏️ Edit Minute Notes"):
                st.session_state["edit_mode_minute_notes"] = True
                st.rerun()
            # if col2.button("Summarize"):
                # st.warning('do stuff')



# %%
def run_local_llm(preprocessing='Unlimited', summarize=True, chunk_size=8192):
    if st.session_state['instruction_name'] is None:
        st.warning('Instructions must be selected first.')
        return

    response = ''
    instruction_name = st.session_state['instruction_name']
    prompt = st.session_state['instructions'][instruction_name]

    # try:
    with st.spinner(f"Running {st.session_state['model']}"):
        start_time = time.time()
        st.warning("LLM model is running! Avoid navigating away or interacting with the app until it finishes.", icon="⚠️")

        # Initialize model
        overlap = int(0.25 * chunk_size) if isinstance(chunk_size, (int, float)) else None

        model = LLMlight(model=st.session_state['model'],
                         retrieval_method='RAG_basic',
                         embedding=None,
                         preprocessing=preprocessing,
                         alpha=None,
                         temperature=0.8,
                         top_p=1,
                         chunks={'method': 'chars', 'size': chunk_size, 'overlap': overlap},
                         n_ctx=16384,
                         endpoint=st.session_state['endpoint'],
                         verbose='info',
                         )

        # Run model
        response = model.prompt(prompt['query'],
                           instructions=prompt['instructions'],
                           context=st.session_state['context'],
                           system=prompt['system'],
                           stream=False,
                           )

        duration = (time.time() - start_time) / 60  # Convert to min
        st.session_state['timings_llm'].append(duration)
        st.session_state["minute_notes"] = response
        save_session()
        st.rerun()
    # except Exception as e:
    #     st.error(f'❌ Unexpected error. {e}')


# %%
def run_openai():
    client = OpenAI(api_key=st.session_state['openai_api_key'])
    response = client.chat.completions.create(
        model=st.session_state['model'],
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": st.session_state['instruction'],
            },
            {
                "role": "user",
                "content": st.session_state['context']},
        ],
        stream=True,
    )

    st.session_state["minute_notes"] = st.write_stream(response)
    save_session()

# %%
def navigation():
    with st.container(border=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            switch_page_button("app_pages/model_instructions.py", text='Previous stap: Set Model Instructions')

        with col2:
            if st.session_state["minute_notes"]:
                st.download_button("Download notulen (.md)", file_name="notulen.md", data=st.session_state["minute_notes"], type='primary')
        with col3:
            if st.session_state["minute_notes"] is not None and st.session_state["minute_notes"] != '':
                try:
                    pdf = MarkdownPdf(toc_level=1)
                    f = BytesIO()
                    pdf.add_section(Section(st.session_state["minute_notes"]))
                    pdf.save(f)
                    st.download_button("Download notulen (.pdf)", file_name="notulen.pdf", data=f, type='primary')
                except Exception as e:
                    st.error(f'❌ Unexpected error. {e}')
                    
# %%
run_main()
