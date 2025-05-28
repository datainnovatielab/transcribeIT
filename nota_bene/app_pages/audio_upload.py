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

    if st.session_state['project_name']:
        st.header('Audio Uploads For ' + st.session_state['project_name'], divider=True)
    else:
        with st.container(border=True):
            st.info('Each project starts with a name. Create your new project at the left sidepanel.')
            return

    with st.container(border=True):
        add_audio_from_path()
    #     st.caption('Upload audio files and set the order.')

    with st.container(border=True):
        # File uploader with support for .m4a files
        uploaded_files = st.file_uploader("Drag and Drop Audio Files", type=["mp3", "wav", "m4a"], accept_multiple_files=True)
        # Upload and process audio
        audio_processing(uploaded_files, st.session_state['project_path'], bitrate=st.session_state['bitrate'])

    # Show continue button
    with st.container(border=True):
        col1, col2 = st.columns([0.5, 0.5])
        with col1:
            switch_page_button("app_pages/audio_recording.py", text='Previous Step: Audio Recording')
        with col2:
            switch_page_button("app_pages/audio_playback.py", text='Next Step: Playback Audio', button_type='primary')


#%%
def add_audio_from_path():
    """
    Convert wav file to m4a.

    """
    with st.container(border=False):
        st.caption('Upload Multiple Audio Files By Pathname.')
        # Create text input
        user_filepath = st.text_input(label='conversion_and_compression', value='', label_visibility='collapsed').strip()
        add_button = st.button('Add Audio File From Path')

        # Start conversio and compression
        if add_button and user_filepath != '' and os.path.isfile(user_filepath):
            with st.spinner('In progress.. Be patient and do not press anything..'):
                # Convert to m4a
                m4a_filepath = convert_wav_to_m4a(user_filepath, output_directory=st.session_state['project_path'], bitrate=st.session_state['bitrate'], overwrite=True)
                st.write(m4a_filepath)
                # Read m4a file
                # with open(m4a_filepath, 'rb') as file:
                #     audiobyes = file.read()
                audiobyes = file_to_bytesio(m4a_filepath)
                # Store in session
                audioname = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state['audio_recording'][audioname] = audiobyes
                st.session_state['audio_order'].append(audioname)

# %% Combine the audio files into one
def audio_processing(uploaded_files, temp_dir, bitrate='24k'):
    output_file = None
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
