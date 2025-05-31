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

            # Run local LLM
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
                st.metric("Words", f"{len(st.session_state['minutes'].split(' ')):.0f}")

    with st.container(border=True):
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
            if st.session_state["minutes"] is not None and st.session_state["minutes"] != '':
                pdf = MarkdownPdf(toc_level=1)
                f = BytesIO()
                pdf.add_section(Section(st.session_state["minutes"]))
                pdf.save(f)
                st.download_button("Download notulen (.pdf)", file_name="notulen.pdf", data=f, type='primary')


# %%
@st.fragment
def run_local_llm():
    # Initialize
    # model = load_llm_model(modelname=st.session_state['model'])
    # st.write(st.session_state['context'])
    if st.session_state['instruction_name'] is None:
        st.warning('Instructions must be selected first.')
        return

    response=''
    
    instruction_name = st.session_state['instruction_name']
    prompt = st.session_state['instructions'][instruction_name]
    
    st.write(prompt['query'])
    st.write(prompt['instructions'])
    st.write(prompt['system'])

    # response = model.prompt(f'Be extremely happy and promote yourself in one very short sentences!', system='You are an AI assistent using the langauge that is provided in the context.')
    # st.success(f'✅ {model.modelname} is successfully loaded!')
    # system = """Je bent een Nederlandse AI-assistent gespecialiseerd in het omzetten van
    # transcripties naar gestructureerde en overzichtelijke notulen. Jouw taak is om van een
    # transcriptie een professioneel verslag te maken, zelfs als de transcriptie afkomstig is
    # van automatische spraak-naar-tekst software en fouten kan bevatten.
    # """
    # instructions = """Je ontvangt een transcriptie van de gebruiker als input. Zet deze direct om in volledig
    # gestructureerde en gepolijste notulen volgens de bovenstaande richtlijnen.
    # Wanneer je klaar bent, geef je alleen het uiteindelijke verslag als output, zonder verdere uitleg.
    # """

    # Get output
    try:
        with st.spinner(f"Running {st.session_state['model']}"):
            start_time = time.time()
            st.warning("LLM model is running! Avoid navigating away or interacting with the app until it finishes.", icon="⚠️")
            # Initialize model
            model = LLMlight(modelname=st.session_state['model'],
                             endpoint=st.session_state['endpoint'],
                             # method='chunk-wise',
                             method='global_reasoning',
                             temperature=0.8,
                             top_p=1,
                             chunks={'type': 'chars', 'size': 5000, 'overlap': 2000},
                             n_ctx=4096,
                             verbose='info',
                             )
    
            # Run model
            response = model.prompt(prompt['query'],
                               instructions=prompt['instructions'],
                               context=st.session_state['context'],
                               system=prompt['system'],
                               stream=False,
                               )
    
            duration = (time.time() - start_time) / 60  # Convert to minutes
    
            if (response is None) or ('400' in response[0:30]) or ('404' in response[0:30]) or (response.strip() == ''):
                st.error(f'❌ Model failed to generate output. Try a different model.')
                st.write(response)
            else:
                st.session_state['timings_llm'].append(duration)
                st.session_state["minutes"] = response
                save_session()
                st.rerun()
    except:
        st.write(response)

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
