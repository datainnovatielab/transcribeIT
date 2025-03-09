"""Page to upload audio file."""

import streamlit as st
from nota_bene.utils import switch_page_button
import os
import shutil
import numpy as np
from nota_bene.utils import write_audio_to_disk, file_to_bytesio, combine_audio_files, compress_audio

# %%
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
        file_list = []
        for i, filename in enumerate(uploaded_files):
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
        output_file = combine_audio_files(file_list, temp_dir, bitrate, '.m4a')

    return output_file

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
    with st.container(border=True):
        st.subheader('Upload audio files')
        st.caption('Upload audio files and set the order.')

        # File uploader with support for .m4a files
        uploaded_files = st.file_uploader("Upload audio files", type=["mp3", "wav", "m4a"], accept_multiple_files=True)

        # Upload and process audio
        output_file = audio_processing(uploaded_files, st.session_state['temp_dir'], bitrate=st.session_state['bitrate'])

        # st.write(st.session_state['audio'])

        if output_file:
            # st.success('Processing Done. Audio files are merged.')
            # Create bytesIO
            st.session_state['audio'] = file_to_bytesio(output_file)
            st.session_state['audio_filepath'] = output_file
            # st.info(output_file)
            # switch_page_button("app_pages/upload_audio.py")
            # switch_page_button("app_pages/transcribe.py")

    if st.session_state['audio'] is not None:
        with st.container(border=True):
            st.subheader('Final audio fragment')
            # st.write("Je hebt dit audiobestand geüpload:")
            st.caption("This is the final combined audio fragment.")
            st.audio(st.session_state['audio'])
            switch_page_button("app_pages/transcribe.py")

    # with st.container(border=True):
    #     st.subheader('Use recording')
    #     st.caption('Upload audio files and set the order.')


# %%
run_main()