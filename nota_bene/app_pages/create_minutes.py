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
        st.header('Create Minutes: ' + st.session_state['project_name'], divider=True)

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

            user_summarize = col1.checkbox('Summarize results', label_visibility='visible')
            user_method = col2.radio('Approach', options=['Global reasoning', 'Chunk-Wise'], label_visibility='visible')

            # Show key
            if st.session_state['model'] == 'gpt-4o-mini':
                if col1.button("OpenAI-key invoeren", use_container_width=True):
                    enter_api_key()
                if st.session_state['model'] == 'gpt-4o-mini':
                    if st.session_state["openai_api_key"]:
                        col2.write("✅ API-key found")
                    else:
                        col2.write("❌ API-key not found")

            # Run local LLM
            if user_press and st.session_state['model'] == 'gpt-4o-mini':
                run_openai()
            elif user_press:
                run_local_llm(method=user_method, summarize=user_summarize)

    # Show minutes
    show_minutes()
    # Show Back-Download button
    navigation()


# %%
@st.fragment
def show_minutes():
    st.session_state.setdefault("edit_mode_minutes", False)

    if not st.session_state.get("minutes"):
        # st.info("Minutes notes are not found.")
        return

    # Show some stats
    if len(st.session_state['timings_llm']) > 0:
        with st.container(border=True):
            st.markdown(f"""
            <div style="width: 100%; background-color: #E5E7EB; border-radius: 6px; margin-top: 1em;">
              <div style="width: {100}%; background-color: #3B82F6; height: 12px; border-radius: 6px;"></div>
            </div>
            <p style="font-size: 0.9em; color: #6B7280;">Creating minute notes is completed: {100:.1f}%</p>
            """, unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Avg Time", f"{np.mean(st.session_state['timings_llm']):.1f} min")
            with col2:
                st.metric("Total Time", f"{np.sum(st.session_state['timings_llm']):.1f} min")
            with col3:
                try:
                    if st.session_state['minutes'] is not None:
                        st.metric("Words", f"{len(st.session_state['minutes'].split(' ')):.0f}")
                except:
                    st.metric("Words", 0)
                    # st.session_state['minutes'] = None

    with st.container(border=True):
        if st.session_state["edit_mode_minutes"]:
            # Editable mode
            if isinstance(st.session_state["minutes"], list):
                minute_notes =  "\n\n---\n\n".join([f"### Results {i+1}:\n{s}" for i, s in enumerate(st.session_state["minutes"])])
            else:
                minute_notes = st.session_state["minutes"]

            updated_minutes = st.text_area(
                label="Edit Minutes",
                value=minute_notes,
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
            col1, col2 = st.columns(2)
            if col1.button("✏️ Edit Minutes"):
                st.session_state["edit_mode_minutes"] = True
                st.rerun()
            # if col2.button("Summarize"):
                # st.warning('do stuff')

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
            if st.session_state["minutes"] is not None and st.session_state["minutes"] != '':
                try:
                    pdf = MarkdownPdf(toc_level=1)
                    f = BytesIO()
                    pdf.add_section(Section(st.session_state["minutes"]))
                    pdf.save(f)
                    st.download_button("Download notulen (.pdf)", file_name="notulen.pdf", data=f, type='primary')
                except Exception as e:
                    st.error(f'❌ Unexpected error. {e}')

# %%
@st.fragment
def run_local_llm(method='Global reasoning', summarize=True):
    # Initialize
    st.write(f"✅ Instructions are loaded: **{st.session_state['instruction_name']}**")
    st.write(f"✅ Model is loaded: **{st.session_state['model']}**")
    st.write(f"✅ Method: **{method}** with summarization: **{summarize}**")

    # st.write(st.session_state['context'])
    if st.session_state['instruction_name'] is None:
        st.warning('Instructions must be selected first.')
        return

    response = ''
    instruction_name = st.session_state['instruction_name']
    prompt = st.session_state['instructions'][instruction_name]

    try:
        with st.spinner(f"Running {st.session_state['model']}"):
            start_time = time.time()
            st.warning("LLM model is running! Avoid navigating away or interacting with the app until it finishes.", icon="⚠️")
            # Initialize model
            model = LLMlight(modelname=st.session_state['model'],
                             endpoint=st.session_state['endpoint'],
                             # method='chunk-wise',
                             # method='global_reasoning',
                             temperature=0.8,
                             top_p=1,
                             chunks={'type': 'chars', 'size': 6000, 'overlap': 2000},
                             n_ctx=4096,
                             verbose='info',
                             )

            # Run model
            # response = model.prompt(prompt['query'],
            #                    context=st.session_state['context'],
            #                    instructions=prompt['instructions'],
            #                    system=prompt['system'],
            #                    stream=False,
            #                    )

            if method=='Global reasoning':
                response = model.global_reasoning(prompt['query'],
                                   context=st.session_state['context'],
                                   instructions=prompt['instructions'],
                                   system=prompt['system'],
                                   return_per_chunk=~summarize,
                                   stream=False,
                                   )
            else:
                response = model.chunk_wise(prompt['query'],
                                   context=st.session_state['context'],
                                   instructions=prompt['instructions'],
                                   system=prompt['system'],
                                   return_per_chunk=~summarize,
                                   top_chunks=0,
                                   stream=False,
                                   )

            duration = (time.time() - start_time) / 60  # Convert to minutes
            st.session_state['timings_llm'].append(duration)
            if isinstance(response, (str, list)):
                st.session_state["minutes"] = response
                save_session()
                st.rerun()
            else:
                st.write(response)
    except Exception as e:
        st.error(f'❌ Unexpected error. {e}')


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

    st.session_state["minutes"] = st.write_stream(response)
    save_session()

# %%
run_main()
