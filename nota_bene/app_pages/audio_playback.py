"""Page to upload audio file."""

import streamlit as st
from nota_bene.utils import switch_page_button


# %%
def run_main():
    """Run main file.

    1. Playback Audio

    """

    if st.session_state['project_name']:
        st.header('Audio Playback For ' + st.session_state['project_name'], divider=True)
    else:
        with st.container(border=True):
            st.info('Each project starts with a name. Create your new project at the left sidepanel.')
            return

    with st.container(border=True):
        if st.session_state['audio']:
            st.subheader('Final Audio File')
        else:
            st.warning('Audio file not found')
        st.caption("This is the final combined audio file.")
        st.audio(st.session_state['audio'])

    with st.container(border=True):
        col1, col2 = st.columns([0.5, 0.5])
        with col1:
            switch_page_button("app_pages/audio_upload.py", text='Vorige Stap: Upload Audio files')
        with col2:
            switch_page_button("app_pages/transcribe.py", text='Volgende Stap: Transcribe Audio', button_type='primary')



# %%
run_main()
