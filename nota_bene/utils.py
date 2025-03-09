"""
Utility functions for handling audio transcription and processing using OpenAI's API.

This module provides functionality to transcribe audio files, manage session states
and handle page switching in Streamlit applications. It also includes constants for the
full prompt template used in generating structured meeting minutes.
"""

from io import BytesIO
import os
import subprocess
from pathlib import Path
try:
    import whisper
except:
    print('pip install openai-whisper')

import streamlit as st
from openai import OpenAI
import tempfile

FULL_PROMPT = """Je bent een AI-assistent gespecialiseerd in het omzetten van
transcripties naar gestructureerde en overzichtelijke notulen. Jouw taak is om van een
transcriptie een professioneel verslag te maken, zelfs als de transcriptie afkomstig is
van automatische spraak-naar-tekst software en fouten kan bevatten.

Bij het verwerken van de transcriptie, houd je rekening met het volgende:
1. **Corrigeren van fouten:** Je corrigeert duidelijke fouten in de transcriptie (zoals
verkeerde woorden, grammaticale fouten en onduidelijke zinnen) op basis van de context.
Als iets onzeker blijft, markeer je dit met '[?]'.
2. **Heldere structuur:** Je formatteert de notulen volgens de volgende opbouw:
   - **Titel en datum van de bijeenkomst** (haal dit uit de context van de
   transcriptie, indien mogelijk, anders laat het leeg).
   - **Aanwezigen en afwezigen** (indien vermeld).
   - **Samenvatting:** Een beknopte samenvatting van de belangrijkste besproken
   onderwerpen en uitkomsten.
   - **Details per agendapunt:** Geef de belangrijkste punten en discussies weer per
   onderwerp.
   - **Actiepunten en besluiten:** Noteer actiepunten en besluiten genummerd en
   duidelijk geordend.
3. **Samenvatten en structureren:** Behoud de kern van de informatie, verwijder
irrelevante details en vermijd herhaling. Gebruik bondige, professionele taal.
4. **Neutraliteit:** Schrijf in een objectieve, neutrale toon en geef geen subjectieve
interpretaties.
5. **Tijdsaanduidingen:** Voeg waar nodig tijdsaanduidingen toe om de volgorde van de
bespreking te verduidelijken. Laat irrelevante tijdsaanduidingen weg.

Je ontvangt een transcriptie van de gebruiker als input. Zet deze direct om in volledig
gestructureerde en gepolijste notulen volgens de bovenstaande richtlijnen.

Wanneer je klaar bent, geef je alleen het uiteindelijke verslag als output, zonder
verdere uitleg.

"""
def switch_page_button(page: st.Page, text: str | None = None):
    """
    Generate a button in the Streamlit app to switch to another page.

    Parameters
    ----------
    page : st.Page
        The identifier of the target page.
    text : str or None, optional
        The label displayed on the button. If None, defaults to "Volgende".
    """
    if st.button(text or "Volgende"):
        st.switch_page(page)

@st.cache_data(persist=True)
def transcribe_local(audio_path, user_select):
    # Load model: Can be "tiny", "small", "medium", "large"
    model = whisper.load_model(user_select).to("cpu")  # Explicitly set CPU
    # Create transcript
    transcript = model.transcribe(audio_path)
    return transcript


@st.cache_data(persist=True)
def transcribe_audio_from_path(audio_path) -> str:
    client = OpenAI(api_key=st.session_state.openai_api_key)

    with open(audio_path, 'rb') as audio_file:
        transcription = client.audio.transcriptions.create(model="whisper-1", file=audio_file)

    return transcription.text


@st.cache_data(persist=True)
def transcribe_audio_streamlit_object(audio_file: BytesIO) -> str:
    """
    Transcribe an audio file using the Whisper-1 model provided by OpenAI.

    Parameters
    ----------
    audio_file : BytesIO
        The audio file as buffer or UploadedFile to be transcribed.

    Returns
    -------
    str
        Text transcription of the audio file.
    """
    client = OpenAI(api_key=st.session_state.openai_api_key)

    transcription = client.audio.transcriptions.create(
        model="whisper-1", file=audio_file
    )
    return transcription.text


def init_session_key(key: str, default_value: str | None = None):
    """
    Initialize a session state key with an optional default value.

    Parameters
    ----------
    key : str
        The key to be set in the session state.
    default_value : str or None, optional
        The default value for the key if it doesn't exist yet.
    """
    if key not in st.session_state:
        st.session_state[key] = default_value

def init_session_keys():
    """Initialize multiple session state keys with default values."""
    temp_dir = os.path.join(tempfile.gettempdir(), "notabena")
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    init_session_key("audio")
    init_session_key("transcript")
    init_session_key("model", default_value="gpt-4o-mini")
    init_session_key("prompt", default_value=FULL_PROMPT)
    init_session_key("openai_api_key", default_value=st.secrets["openai"]["key"])
    init_session_key("minutes")
    init_session_key("temp_dir", default_value=temp_dir)
    init_session_key("audio_filepath", default_value=None)
    init_session_key("endpoints", default_value=['http://localhost:1234/v1/chat/completions', 'http://localhost:11434/api/generate'])
    init_session_key("endpoint", default_value=None)
    init_session_key("audio_recording", default_value={})
    init_session_key("audio_order", default_value=[])
    init_session_key("bitrate", default_value='24k')


def write_audio_to_disk(audio, filepath):
    if filepath is not None:
        # Write the uploaded file to the temporary directory
        with open(filepath, "wb") as f:
            f.write(audio.getbuffer())


def file_to_bytesio(file_path):
    if file_path is not None:
        # Open the file and read it into a BytesIO object
        with open(file_path, 'rb') as file:
            file_data = file.read()
        # Create a BytesIO buffer with the file data
        bytes_io = BytesIO(file_data)
        return bytes_io


def create_audio_chunks(temp_dir, file_path, segment_time=1800, ext='m4a'):
    if not file_path:
        return None

    # Define output filename pattern for chunks
    output_pattern = os.path.join(temp_dir, "chunk_%03d.m4a")  # Example: chunk_000.m4a, chunk_001.m4a, ...

    # FFmpeg command to split audio into 30-minute chunks
    command = [
        'ffmpeg',
        '-i', file_path,  # Input file
        '-f', 'segment',         # Enable segmenting
        '-segment_time', str(segment_time), # Split into 30-minute chunks
        '-c', 'copy',            # Keep original codec
        '-reset_timestamps', '1',
        '-map', '0',             # Ensure all streams are copied
        output_pattern           # Output files (chunk_000.m4a, chunk_001.m4a, etc.)
    ]

    # Run FFmpeg
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    # Get all chunk file paths
    chunk_files = sorted(Path(temp_dir).glob("chunk_*.m4a"))

    # Convert to a list of file paths as strings
    chunk_file_paths = [str(chunk) for chunk in chunk_files]

    return chunk_file_paths

def combine_audio_files(audio_files, temp_dir, bitrate, ext='.m4a'):
    # Define the path for the uploaded audio file
    # output_file = os.path.join(temp_dir, f'audio_file_stacked_{bitrate}' + '.m4a')
    output_file = os.path.join(temp_dir, f'audio_file_stacked_{bitrate}' + ext)
    # file_txt = 'file_list.txt'
    file_txt = os.path.join(temp_dir, 'file_list.txt')
    if os.path.isfile(output_file):
        return output_file

    # Create a temporary text file to list the audio files
    with open(file_txt, 'w') as f:
        for file in audio_files:
            f.write(f"file '{file}'\n")

    # FFmpeg command to combine the files using the concat demuxer
    command = [
        'ffmpeg',
        '-f', 'concat',         # Use the concat demuxer
        '-safe', '0',           # Allow unsafe file paths (if necessary)
        '-i', file_txt,         # Input file list
        '-c', 'copy',           # Copy codecs (no re-encoding)
        output_file             # Output file
    ]

    # Run the FFmpeg command
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Clean up the temporary file list
    # os.remove('file_list.txt')
    return output_file


# @st.cache_data
def compress_audio(file_path, bitrate='16k'):
    #  https://github.com/openai/whisper/discussions/870
    if file_path is not None:
        # Command to compress the audio using FFmpeg
        filename_new = os.path.split(file_path)[1].split('.')[0] + '_compressed_' + f'{bitrate}' + '.' + os.path.split(file_path)[1].split('.')[1]
        output_file = os.path.join(os.path.split(file_path)[0], filename_new)

        if not os.path.isfile(output_file):
            with st.spinner("Wait for it... compressing audio.."):
                command = [
                    'ffmpeg',
                    '-i', file_path,  # Input file
                    '-b:a', bitrate,   # Set bitrate (e.g., '16k')
                    # '-vn',             # Disable video processing
                    output_file        # Output file
                ]

                # Run the command
                subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                # st.write(output_file)
                # st.write(os.path.getsize(output_file))
        return output_file


def convert_wav_to_m4a(wav_filepath, bitrate='128k'):
    """Convert a WAV file to M4A format using ffmpeg.

    Args:
        wav_filepath (str): Path to the input .wav file.

    Returns:
        str: Path to the converted .m4a file.
    """
    if not os.path.isfile(wav_filepath):
        raise FileNotFoundError(f"File not found: {wav_filepath}")

    # Create output filename with .m4a extension
    m4a_filepath = os.path.splitext(wav_filepath)[0] + ".m4a"

    # Construct the ffmpeg command
    command = [
        "ffmpeg",
        "-i", wav_filepath,  # Input file
        "-c:a", "aac",       # Convert to AAC codec
        "-b:a", bitrate,      # Set audio bitrate (adjust if needed)
        "-movflags", "+faststart",  # Optimize for streaming
        m4a_filepath         # Output file
    ]

    # Run the ffmpeg command
    # subprocess.run(command, check=True)
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)


    return m4a_filepath


#%% Define API-based Agent
class API_LLM:
    """ The Agent class.
    1. Go the LM-studio.
    2. Go to left panel and select developers mode
    3. On top select your model of interest
    4. Then go to settings in the top bar
    5. Enable "server on local network" if you need
    6. Enable Running

    Examples
    --------
    > model=API_LLM()
    > model=API_LLM(model_id="openhermes-2.5-mistral-7b", api_url="http://localhost:1234/v1/chat/completions")
    > model.run('hello who are you?')

    """
    def __init__(self, model_id="openhermes-2.5-mistral-7b", api_url="http://localhost:1234/v1/chat/completions", temperature=0.7):
        self.model_id = model_id
        self.api_url = api_url
        self.temperature = temperature
    
    def run(self, prompt):
        import requests
        
        headers = {"Content-Type": "application/json"}
        data = {
            "model": self.model_id,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature
        }

        response = requests.post(self.api_url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json().get('choices', [{}])[0].get('message', {}).get('content', "No response")
        else:
            return f"Error: {response.status_code} - {response.text}"

