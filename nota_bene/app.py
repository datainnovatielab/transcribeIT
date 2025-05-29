"""Main streamlit app."""
import streamlit as st
import sys
import os
import re
import subprocess
from nota_bene.utils import init_session_keys, list_subdirectories, file_to_bytesio, set_project_paths, save_session
import shutil
import pypickle

init_session_keys()
# https://streamlit-emoji-shortcodes-streamlit-app-gwckff.streamlit.app/

# %%
def main():
    # Debug
    # for key, value in st.session_state.items():
    #     if key=='instruction' or key=='audio':
    #         st.write(f"{key} = {value is None}")
    #     else:
    #         st.write(f"{key} = {value}")

    # Build the bottom-sidebar
    sidebar()

    pg = st.navigation(
        {
            "Main": [st.Page("app_pages/intro.py", title="📢 Introductie")],
            "Audio": [
                st.Page("app_pages/audio_recording.py", title=("✅ " if st.session_state.get('audio') else "❗") + "Record Audio"),
                st.Page("app_pages/audio_upload.py", title=("✅ " if st.session_state.get('audio_filepath') else "❗") + "Upload Recordings"),
                st.Page("app_pages/audio_playback.py", title=("✅ " if st.session_state.get('audio') else "❗") + "Playback Recordings"),
            ],
            "Transcription": [
                st.Page("app_pages/transcribe.py", title=("✅ " if st.session_state.get('context') else "❗") + "Run Transcription"),
                st.Page("app_pages/transcribe_edit.py", title=("✅ " if st.session_state.get('context') else "❗") + "Edit Transcription"),
            ],
            "Notuleren": [
                st.Page("app_pages/model_instructions.py", title=("✅ " if st.session_state.get('instruction') else "❗") + "Model Instruction"),
                st.Page("app_pages/create_minutes.py", title=("✅ " if st.session_state.get('minutes') else "❗") + "Create Minute Notes"),

            ],
            "Configurations": [
                st.Page("app_pages/configurations.py", title="⚙️ Configurations"),
                ]
        }
    )

    pg.run()

#%%
def sidebar():
    # @st.dialog("Key?")
    # def enter_api_key():
    #     """Enter OpenAI key in dialog window."""
    #     api_key = st.text_input("OpenAI API Key", value=st.session_state["openai_api_key"] or "", type="password")
    #     if st.button("Bevestigen"):
    #         st.session_state["openai_api_key"] = api_key
    #         st.rerun()

    @st.dialog("New Project Name")
    def enter_project_name():
        """Enter project name in dialog window."""
        project_name = st.text_input("New Project Name", value="", placeholder='Enter your project name')
        if st.button("Confirm"):
            # Set project paths
            set_project_paths(project_name.strip())
            # Refresh screen
            st.rerun()

    # Display in listbox if available
    col1, col2 = st.sidebar.columns([0.5, 0.5])
    # Selectbox
    col1.caption('Select Project (auto loaded)')
    options = list_subdirectories(st.session_state['temp_dir'])
    index = options.index(st.session_state["project_name"]) if st.session_state["project_name"]!='' in options else None
    project_name = col1.selectbox("Select a Project", options=options, index=index, label_visibility='collapsed', help='Select project')

    # If a different project is choosen, load the session parameters
    if project_name != st.session_state["project_name"]:
        # Set session states for paths
        set_project_paths(project_name)
        # Load the session states
        if os.path.isfile(st.session_state["save_path"]):
            # Load pickle file
            session_state = pypickle.load(st.session_state["save_path"])
            for key, value in session_state.items():
                st.session_state[key] = value
        # Refresh screen
        st.rerun()

    # col1, col2 = st.sidebar.columns([0.5, 0.5])
    col2.caption('Create New Project')
    if col2.button("Create New Project", use_container_width=True):
        enter_project_name()
        init_session_keys(overwrite=True)

    st.sidebar.caption(f"{st.session_state['project_path']}")
    st.sidebar.divider()

    cols = st.sidebar.columns([0.5, 0.5])
    if st.session_state['project_name'] is not None and st.session_state['project_name'] != '':
        if cols[0].button(f"Delete Project {st.session_state['project_name']}", type='primary'):
            cols[0].caption('Deleting audio files in {st.session_state["project_path"]}')
            shutil.rmtree(st.session_state['project_path'], ignore_errors=True)
            # st.session_state["project_name"] = ''
            # st.session_state["project_path"] = os.path.join(st.session_state['temp_dir'], '')
            # st.session_state["audio_filepath"] = ''
            cols[0].caption('Clearning cache..')
            st.cache_resource.clear()
            # Clear all session states
            init_session_keys(overwrite=True)
            # Show done
            cols[0].caption('Done.')
            st.rerun()
    else:
        cols[0].button(f"Delete Project", type='primary', disabled=True)


# %%
def main_run():
    """Function to run the Streamlit app from the command line."""
    module_path = os.path.abspath(os.path.dirname(__file__))

    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", os.path.join(module_path, 'app.py')])
    except subprocess.CalledProcessError as e:
        print(f"Failed to run Streamlit app: {e}")

# %%
if __name__ == "__main__":
    main()
