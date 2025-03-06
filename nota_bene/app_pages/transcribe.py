"""Page to submit audio for transcription."""

import streamlit as st
import whisper

from nota_bene.utils import switch_page_button, create_audio_chunks
from nota_bene.utils import transcribe_audio_from_path, transcribe_local


def transcribe_button():
    """Check for API key, and present transcribe button if present."""

    user_select = st.selectbox(label='Select Whisper model', options=["base", "tiny", "small", "medium", "large", "OpenAI"], index=0)
    user_press = st.button("Transcriberen.")
    # st.markdown(st.session_state['temp_dir'])

    if not st.session_state.openai_api_key:
        st.markdown(
            """
            ## **Missende OpenAI API key**

            Om te kunnen transcriberen is er een OpenAI API key nodig. Deze kan links
            in de sidebar worden ingevoerd.
            """
        )
    elif user_press:
        # 1. Cut the audio file in chunks of 30minutes
        # 2. Transcribe per chunk
        # 3. Stack all text together

        progress_text = f"Operation in progress using {user_select}.. Please wait."
        my_bar = st.progress(0, text=progress_text)

        # Create chunks of 30min
        segment_time = 300
        audio_chunks = create_audio_chunks(st.session_state['temp_dir'], st.session_state['audio_filepath'], segment_time=segment_time)

        transcripts = []
        for i, audio_path in enumerate(audio_chunks):
            # Progress bar
            # progress_text = f'Transcribing {max(i-1, 0) * {segment_time/60}}min-{max(i, 1)*{segment_time/60}}min'
            my_bar.progress(int((max(i, 1) / len(audio_chunks)) * 100), text=f'Working on audio chunk {max(i, 1)} / {len(audio_chunks)} using {user_select} model.')

            # Create transcript
            if user_select=='OpenAI':
                # large-v2
                transcript = transcribe_audio_from_path(audio_path)
                # Als het een streamlit object is, dan kan je deze ook gebruiken:
                # transcript = transcribe_audio_streamlit_object(audio)
            else:
                # Run local model
                transcript = transcribe_local(audio_path, user_select)

            transcripts.append(transcript.get('text', ''))

        # Create one big transcript
        st.session_state.transcript = ' '.join(transcripts)


st.subheader('Start Transcribing audio file')
if st.session_state.audio is None:
    switch_page_button("app_pages/upload_audio.py", text="Upload eerst een audio file.")
elif st.session_state.transcript is None:
    transcribe_button()

if st.session_state.transcript:
    st.write("**Transcript:**")
    with st.container(height=400, border=True):
        st.write(st.session_state.transcript)
    switch_page_button("app_pages/minutes_prompt.py")
