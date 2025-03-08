import streamlit as st
from datetime import datetime
from st_audiorec import st_audiorec

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
            st.caption('You can now save this audio fragment and use it for transcription.')

        if wav_audio_data is not None and st.button('Save this audio fragment for transcription'):
            audioname = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.write(audioname)
            st.session_state['audio_recording'][audioname] = wav_audio_data
            st.session_state['audio_order'].append(audioname)
            st.info(f"Audio fragment number {len(st.session_state['audio_recording'].keys())-1} audio fragment(s) is saved.")

    if len(st.session_state['audio_recording']) > 0:
        with st.container(border=True):
            st.subheader('Saved recordings')
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

if 'audio_recording' not in st.session_state:
    st.session_state['audio_recording'] = {}
    st.session_state['audio_order'] = []

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
main()
