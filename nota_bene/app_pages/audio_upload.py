"""Page to upload audio file."""

import streamlit as st
from nota_bene.utils import switch_page_button
import os
import shutil
import numpy as np
from nota_bene.utils import write_audio_to_disk, file_to_bytesio, combine_audio_files, compress_audio, save_session
from nota_bene.utils import convert_wav_to_m4a
from datetime import datetime


# %%
def run_main():
    """Run main file.

    1. Upload all audio files and order accordingly.
    2. Store to disk and name to 01_ etc
    3. Resample to 16k
    4. Combine all audio files into one big audio file.
    5. Split audio file into parts of 20Mb
    6. Transcribe

    """

    if st.session_state['project_name'] == '' or st.session_state['project_name'] is None:
        with st.container(border=True):
            st.info('Each project starts with a name. Create your new project at the left sidepanel.')
            return
    else:
        st.header('Uploads Audio files: ' + st.session_state['project_name'], divider=True)

    with st.container(border=True):
        add_audio_from_path()
        # st.caption('Upload audio files and set the order.')

    # File uploader with support for .m4a files
    with st.container(border=True):
        uploaded_files = st.file_uploader("Drag and Drop Audio Files", type=["mp3", "wav", "m4a"], accept_multiple_files=True)

    # Upload and process audio
    with st.container(border=True):
        file_order = audio_ordering(uploaded_files, st.session_state['project_path'])

        if st.session_state['audio']:
            st.multiselect(label='Processed audio files', options=st.session_state['audio_names'], default=st.session_state['audio_names'], disabled=True)
            # st.write(st.session_state['audio_names'])
            # cols = st.columns(len(st.session_state['audio_names']))
            # for i, audio_name in enumerate(st.session_state['audio_names']):
            #     cols[i].button(audio_name, disabled=True)

            # st.write(st.session_state['audio_filepath'])
            # st.write(st.session_state['audio_names'])
            if st.button('Remove processed audio files'):
                st.session_state['audio'] = None
                st.session_state['audio_filepath'] = None
                st.session_state['audio_names'] = []
                st.rerun()

    # Show continue button
    with st.container(border=True):
        col1, col2 = st.columns([0.5, 0.5])
        with col1:
            switch_page_button("app_pages/audio_recording.py", text='Previous Step: Audio Recording')
        with col2:
            if not st.session_state['audio']:
                audio_processing(uploaded_files, file_order, st.session_state['project_path'], st.session_state['bitrate'])
            else:
                switch_page_button("app_pages/audio_playback.py", text='Next Step: Playback Audio', button_type='primary')



# %% Combine the audio files into one
def audio_ordering(uploaded_files, temp_dir):

    file_order = []
    # Ensure ffmpeg is installed and accessible
    if not shutil.which("ffmpeg"):
        st.error("ffmpeg is required but not found. Please install ffmpeg and ensure it's in your system PATH.")
        st.stop()

    # Create tempdir
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    if uploaded_files:
        file_order = st.multiselect(
            label="Select the order of audio files to process",
            options=[file.name for file in uploaded_files],
            default=[file.name for file in uploaded_files]
        )

    if uploaded_files and st.button('Volgende stap: Combineer de audio bestanden in deze volgorde.') and uploaded_files:
        progress_text = "Operation in progress. Please wait."
        my_bar = st.progress(0, text=progress_text)

        file_list = []
        for i, filename in enumerate(uploaded_files):
            # progressbar
            progress_percent = int((max(i + 1, 1) / len(uploaded_files)) * 100)
            my_bar.progress(progress_percent, text=f'Processing {filename.name}')
            # Get the correct order
            idx = np.where(np.isin(file_order, filename.name))[0][0]
            # Get file ext and file path
            _, ext = os.path.splitext(filename.name)
            filepath = os.path.join(temp_dir, f'audio_{i}{ext}')
            # Write audio to temp directory
            write_audio_to_disk(uploaded_files[idx], filepath)
            # Compress audio
            filepath_c = compress_audio(filepath, bitrate=bitrate)
            # Add the file path to list
            file_list.append(filepath_c)

        # Combine the audio files
        my_bar.progress(90, text=f'combining audio fragments.. Wait for it..')

        # Combine all audio files and return the filepath
        with st.spinner("Wait for it... combining audio fragments.."):
            st.session_state['audio_filepath'] = combine_audio_files(file_list, temp_dir, bitrate, '.m4a')

            if st.session_state['audio_filepath']:
                # Create bytesIO
                st.session_state['audio'] = file_to_bytesio(st.session_state['audio_filepath'])
                # Save
                my_bar.progress(95, text=f'Saving session states..')
                save_session(save_audio=True)
                my_bar.progress(100, text=f'Done!')


# %%
run_main()
