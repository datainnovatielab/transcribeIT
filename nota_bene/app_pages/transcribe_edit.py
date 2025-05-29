"""Page to submit audio for transcription."""

import time
import os
import json
import streamlit as st
try:
    import whisper
except:
    print('pip install openai-whisper')

from nota_bene.utils import switch_page_button, create_audio_chunks, transcribe_audio_from_path, transcribe_local, save_session

#%%
@st.fragment
def run_main():
    # Ensure necessary session state variables are initialized
    st.session_state.setdefault('edit_transcript_mode', False)
    st.session_state.setdefault('transcript', '')

    # Header
    if st.session_state.get('project_name'):
        st.header(f"Transcribe Audio Files: {st.session_state['project_name']}", divider=True)
    else:
        with st.container(border=True):
            st.info('Each project starts with a name. Create your new project at the left sidepanel.')
        return

    st.write("**Transcript:**")

    if st.session_state['edit_transcript_mode']:
        # Edit mode
        edited_transcript = st.text_area(
            label="Edit Transcript",
            value=st.session_state['transcript'],
            height=400,
            label_visibility='collapsed',
            key="transcript_editor"
        )
        col1, col2 = st.columns([0.2, 0.8])
        with col1:
            if st.button("💾 Save Transcript"):
                st.session_state['transcript'] = edited_transcript
                st.session_state['edit_transcript_mode'] = False
                save_session(save_audio=True)
                st.success("Transcript updated.")
                st.rerun()
        with col2:
            if st.button("❌ Cancel"):
                st.session_state['edit_transcript_mode'] = False
                st.rerun()
    else:
        # View mode
        with st.container(border=True, height=400):
            st.markdown(st.session_state['transcript'], unsafe_allow_html=True)
        if st.button("✏️ Edit Transcript"):
            st.session_state['edit_transcript_mode'] = True
            st.rerun()

    # Navigation buttons
    with st.container(border=True):
        col1, col2 = st.columns([0.5, 0.5])
        with col1:
            switch_page_button("app_pages/transcribe.py", text='Vorige Stap: Transcribe Audio')
        with col2:
            switch_page_button("app_pages/model_instructions.py", text='Volgende stap: Set Model Instructions', button_type='primary')


# %%
run_main()
