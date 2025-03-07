"""Main streamlit app."""

import streamlit as st
import sys
import os
import subprocess
from nota_bene.utils import init_session_keys
import shutil

init_session_keys()

def main():
    pg = st.navigation(
        {
            "Main": [st.Page("app_pages/intro.py", title="Introductie")],
            "Audio": [
                st.Page("app_pages/audio_preprocessing.py", title="Upload Audio"),
                st.Page("app_pages/transcribe.py", title="Transcriberen"),
            ],
            "Notuleren": [
                st.Page("app_pages/minutes_prompt.py", title="Instructies"),
                st.Page("app_pages/create_minutes.py", title="Resultaat"),
            ],
            "Configurations": [
                st.Page("app_pages/configurations.py", title="Configurations"),
                ]

        }
    )


    @st.dialog("Key?")
    def enter_api_key():
        """Enter OpenAI key in dialog window."""
        api_key = st.text_input(
            "OpenAI API Key",
            value=st.session_state["openai_api_key"] or "",
            type="password",
        )
        if st.button("Bevestigen"):
            st.session_state["openai_api_key"] = api_key
            st.rerun()
    
    
    if st.sidebar.button("OpenAI-key invoeren"):
        enter_api_key()

    if st.session_state["openai_api_key"]:
        st.sidebar.write("✅ Je hebt een API-key ingevoerd")
    else:
        st.sidebar.write("❌ Je hebt nog geen API-key ingevoerd")

    if st.sidebar.button("Cleanup files and cache", type='primary'):
        # Remove tempdir
        st.caption('Cleaning audio files in temp directory..')
        shutil.rmtree(st.session_state['temp_dir'], ignore_errors=True)
        st.caption('Clearning cache..')
        st.cache_resource.clear()
        st.caption('Done.')


    pg.run()


def main_run():
    """Function to run the Streamlit app from the command line."""
    module_path = os.path.abspath(os.path.dirname(__file__))

    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", os.path.join(module_path, 'app.py')])
    except subprocess.CalledProcessError as e:
        print(f"Failed to run Streamlit app: {e}")

if __name__ == "__main__":
    main()
