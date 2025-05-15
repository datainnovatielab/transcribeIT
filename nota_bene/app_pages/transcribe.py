"""Page to submit audio for transcription."""

import time
import os
import json
import streamlit as st
import numpy as np

try:
    import whisper
except:
    print('pip install openai-whisper')

from nota_bene.utils import switch_page_button, create_audio_chunks, transcribe_audio_from_path, transcribe_local, save_session


#%%
@st.fragment
def run_main():
    run_status = False
    if st.session_state['project_name']:
        st.header('Transcribe Audio Files For ' + st.session_state['project_name'], divider=True)
    else:
        with st.container(border=True):
            st.info('Each project starts with a name. Create your new project at the left sidepanel.')

    with st.container(border=True):
        if st.session_state['audio'] is None:
            st.markdown('Automatic transcription requires an audio file. There is no audio file here. Please go to the previous page to upload an audio file. Alternatively it is also possible to add your own transcripts in the next page.')
        else:
            # Run transcription
            run_status = run_transcription()
            # Refresh screen after run
            if run_status:
                st.rerun()

    # Show some stats
    if len(st.session_state['timings']) > 0:
        st.markdown(f"""
        <div style="width: 100%; background-color: #E5E7EB; border-radius: 6px; margin-top: 1em;">
          <div style="width: {100}%; background-color: #3B82F6; height: 12px; border-radius: 6px;"></div>
        </div>
        <p style="font-size: 0.9em; color: #6B7280;">Audio Transcription is completed: {100:.1f}%</p>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Avg Time / Chunk", f"{np.mean(st.session_state['timings']):.1f} min")
        with col2:
            st.metric("Total Time", f"{np.sum(st.session_state['timings']):.1f} min")
        with col3:
            st.metric("Words", f"{len(st.session_state['transcript'].split(' ')):.0f}")

    # Show continue button
    with st.container(border=True):
        col1, col2 = st.columns([0.5, 0.5])
        with col1:
            switch_page_button("app_pages/audio_playback.py", text='Previous Step: Playback Audio')
        with col2:
            switch_page_button("app_pages/transcribe_edit.py", text='Next Step: Edit Transcription', button_type='primary')


#%%
@st.fragment
def run_transcription():
    """Check for API key, and present transcribe button if present."""
    # Selectionbox
    col1, col2 = st.columns([0.5, 0.5])
    col1.caption('Select Whisper model')
    options = ["base", "tiny", "small", "medium", "large", "turbo", "OpenAI"]
    model_type = col1.selectbox(label='Select Whisper model', options=options, index=options.index(st.session_state['model_type']), label_visibility='collapsed')
    # Button
    col2.caption('Transcribe Audio file using the selected model')
    user_press = col2.button(f"Run Transcription!", type='primary')
    # Checkbox
    load_transcript_userselect = st.checkbox('Load processed audio transcripts.', value=True, help='Load previously transcribed transcriptions during run.')

    # Change model
    if model_type != st.session_state['model_type']:
        st.session_state['model_type'] = model_type
        st.rerun()

    if not st.session_state['openai_api_key']:
        st.markdown(
            """
            ## **Missende OpenAI API key**

            Om te kunnen transcriberen is er een OpenAI API key nodig. Deze kan links
            in de sidebar worden ingevoerd.
            """
        )
    elif not st.session_state['project_name']:
        st.markdown(
            """
            ## **Missing Project name**

            To Transcribe, you need to name your project at the sidebar.
            """
        )
    elif user_press:
        # 1. Cut the audio file in chunks of 30minutes
        # 2. Transcribe per chunk
        # 3. Stack all text together
        if load_transcript_userselect and st.session_state['transcript']:
            st.info("Transcription is loaded..")
            return
        else:
            st.warning("Transcription is running now. Avoid navigating away or interacting with the app until it finishes.", icon="⚠️")

        status_placeholder = st.empty()
        status_placeholder2 = st.empty()

        # Create chunks of 300sec
        segment_time = 300
        audio_chunks = create_audio_chunks(st.session_state['project_path'], st.session_state['audio_filepath'], segment_time=segment_time)

        transcripts = []
        timings = []
        envtype = 'OpenAI' if model_type.lower()=='openai' else 'local'
        # my_bar.progress(0, text=f'Working on the first audio chunk using Whisper-{model_type} model in the [{envtype}] environment.')

        status_placeholder2.markdown(f"""Operation {st.session_state['project_name']} in progress. Working on the first audio chunk using Whisper-{model_type} model in the [{envtype}] environment.""")

        # Run over all audio fragments
        for i, audio_path in enumerate(audio_chunks):
            # time
            # st.write(audio_path)
            start_time = time.time()
            # Create a unique cache filename for this chunk
            base_filename = os.path.splitext(os.path.basename(audio_path))[0]
            chunk_filename = f"{base_filename}.json"
            chunk_path = os.path.join(st.session_state['project_path'], chunk_filename)

            # Load transcript from textfile or run model
            if os.path.exists(chunk_path) and load_transcript_userselect:
                # Load cached transcript
                with open(chunk_path, "r", encoding="utf-8") as f:
                    cached_data = json.load(f)
                    transcript_text = cached_data.get('text', '')
                    duration = cached_data.get('duration', '')
                    if isinstance(duration, str):
                        duration = float(duration) if duration.isnumeric() else 0
            else:
                # Create transcript
                if model_type.lower() == 'openai':
                    # large-v2
                    transcript = transcribe_audio_from_path(audio_path)
                    # Als het een streamlit object is, dan kan je deze ook gebruiken:
                    # transcript = transcribe_audio_streamlit_object(audio)
                else:
                    # Run local model
                    transcript = transcribe_local(audio_path, model_type)

                # Get the transcript text
                transcript_text = transcript.get('text', '')
                # Store timings
                duration = (time.time() - start_time) / 60  # Convert to minutes

            # Save transcript to cache
            with open(chunk_path, "w", encoding="utf-8") as f:
                json.dump({'text': transcript_text, 'duration': round(duration, 4)}, f, ensure_ascii=False, indent=2)

            # Append transcripts
            transcripts.append(transcript_text)
            timings.append(duration)

            # Progress calculation
            progress_percent = int((max(i + 1, 1) / len(audio_chunks)) * 100)
            avg_time = sum(timings) / len(timings)
            remaining_chunks = len(audio_chunks) - (i + 1)
            estimated_time_left = round(avg_time * remaining_chunks, 1)
            estimated_time_left = 'To be estimated' if estimated_time_left < 0.1 else str(estimated_time_left) + ' min'

            # Show detailed progress text
            status_placeholder2.markdown(f"""
            <div style="width: 100%; background-color: #E5E7EB; border-radius: 6px; margin-top: 1em;">
              <div style="width: {progress_percent}%; background-color: #3B82F6; height: 12px; border-radius: 6px;"></div>
            </div>
            <p style="font-size: 0.9em; color: #6B7280;">Progress: {progress_percent:.1f}%</p>
            """, unsafe_allow_html=True)

            status_placeholder.markdown(
                f"""
                <div style="padding: 1em; border-radius: 8px; background-color: #F3F4F6; color: #111827;">
                    <strong>Chunk {i + 1} of {len(audio_chunks)}</strong><br>
                    Model: <span style="color:#2563EB;"><code>Whisper-{model_type}</code></span> |
                    Environment: <span style="color:#10B981;"><code>{envtype}</code></span><br>
                    Avg chunk time: <strong>{avg_time:.1f} min</strong><br>
                    Estimated time left: <strong>{estimated_time_left}</strong>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Timings
        if len(timings) > 0: st.session_state['timings'] = timings
        # Create one big transcript
        st.session_state['transcript'] = ' '.join(transcripts)
        # Save session
        save_session()
        return True

    return False


# %%
run_main()
