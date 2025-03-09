import streamlit as st
from datetime import datetime
from st_audiorec import st_audiorec
from nota_bene.utils import switch_page_button
from nota_bene.utils import write_audio_to_disk, file_to_bytesio, combine_audio_files, compress_audio
from nota_bene.utils import convert_wav_to_m4a
import os

# %%
def main():
    """
    Record audio from microphone and return the audio data while optionally saving to disk.
    """

    st.header('Record audio')

    if 'audio_recording' not in st.session_state:
        st.session_state['audio_recording'] = {}
    if 'audio_order' not in st.session_state:
        st.session_state['audio_order'] = []

    with st.container(border=True):
        st.caption('Use the buttons for navigation.')
        # Audio panel
        wav_audio_data = st_audiorec()

        # Show message after recording
        if wav_audio_data is not None:
            st.caption('Save this audio fragment in case you want to use it for transcription.')

        if wav_audio_data is not None and st.button('Save this audio fragment for transcription'):
            audioname = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state['audio_recording'][audioname] = wav_audio_data
            st.session_state['audio_order'].append(audioname)
            # st.info(f"Audio fragment number {len(st.session_state['audio_recording'].keys())-1} audio fragment(s) is saved.")

    # Set the order of the recordings
    user_button_process = set_order_recordings()
    # Process the audio recordings
    with st.spinner():
        output_file = process_audio_recordings(user_button_process, bitrate=st.session_state['bitrate'])

    if output_file:
        # st.success('Processing Done. Audio files are merged.')
        # Create bytesIO
        st.session_state['audio'] = file_to_bytesio(output_file)
        st.session_state['audio_filepath'] = output_file

    if st.session_state['audio'] is not None:
        with st.container(border=True):
            st.subheader('Final audio fragment')
            st.caption("This is the final combined audio fragment that will be used for the transcription.")
            st.audio(st.session_state['audio'])
            switch_page_button("app_pages/transcribe.py")


def set_order_recordings():
    if len(st.session_state['audio_recording']) > 0:
        with st.container(border=True):
            st.subheader('Sort recordings')
            st.caption(f"In total there are {len(st.session_state['audio_recording'])} audio recordings saved. You can remove or reorder them accordingly.")
            for key in st.session_state['audio_order']:  # Maintain order using the list
                col1, col2, col3, col4, col5 = st.columns([0.5, 0.3, 0.1, 0.1, 0.1])
                with st.container(border=False):
                    col1.audio(st.session_state['audio_recording'][key], format='audio/wav')
                    col2.write(key)
                    if col3.button("⬆️", key=f"up_{key}"):
                        move_audio(key, "up")
                    if col4.button("⬇️", key=f"down_{key}"):
                        move_audio(key, "down")
                    if col5.button(":x:", key=f"remove_{key}"):
                        remove_audio(key)

            # Create button
            user_button_process = st.button('Volgende stap: combineer de audio bestanden.')
        return user_button_process


def process_audio_recordings(user_button_process, bitrate='24k'):
    output_file = None

    if len(st.session_state['audio_recording']) > 0 and user_button_process:
        # st.info('process now')
        # st.write(st.session_state['audio_recording'].keys())
        # st.write(st.session_state['audio_order'])

        file_list = []
        ext = '.wav'
        for i, filename in enumerate(st.session_state['audio_order']):
            # st.write(f'Working on {filename}')
            # Get the correct order
            wav_audio = st.session_state['audio_recording'].get(filename)
            # Create filepath
            filepath = os.path.join(st.session_state['temp_dir'], f'audio_{i}{ext}')
            # Write audio to temp directory
            filepath = write_recording_to_disk(filepath, wav_audio, convert_to_m4a=True, bitrate=st.session_state['bitrate'])
            # Compress audio
            filepath_c = compress_audio(filepath, bitrate=bitrate)
            # Add the file path to list
            file_list.append(filepath_c)

        # Combine the audio files
        output_file = combine_audio_files(file_list, st.session_state['temp_dir'], bitrate, '.m4a')

    # Return
    return output_file


# %%
def write_recording_to_disk(filepath, wav_audio, convert_to_m4a=True, bitrate='128k'):
    # Save wav file to disk
    with open(filepath, "wb") as f:
        f.write(wav_audio)
    # Convert wav to m4a
    if convert_to_m4a:
        filepath = convert_wav_to_m4a(filepath, bitrate=bitrate)
    # Return
    return filepath

def remove_audio(key):
    if key in st.session_state['audio_recording']:
        del st.session_state['audio_recording'][key]
        st.session_state['audio_order'].remove(key)
        st.rerun()

def move_audio(key, direction):
    index = st.session_state['audio_order'].index(key)
    if direction == "up" and index > 0:
        st.session_state['audio_order'][index], st.session_state['audio_order'][index - 1] = (
            st.session_state['audio_order'][index - 1],
            st.session_state['audio_order'][index]
        )
    elif direction == "down" and index < len(st.session_state['audio_order']) - 1:
        st.session_state['audio_order'][index], st.session_state['audio_order'][index + 1] = (
            st.session_state['audio_order'][index + 1],
            st.session_state['audio_order'][index]
        )
    st.rerun()

# %%
# Run the main function. Kinda weird to do this in such manner but the st.navigations seems to force it in this way.
main()
