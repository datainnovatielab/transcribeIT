"""Page for creation of meeting minutes.

Module for creating meeting minutes from a transcript using OpenAI's API and Streamlit
framework. This module allows users to input a transcript, generate minutes in Markdown
format, and download them as either Markdown or PDF files. It also provides a user
interface to navigate back if no transcript is available.
"""

from io import BytesIO

import streamlit as st
from markdown_pdf import MarkdownPdf, Section
from openai import OpenAI
import requests
import json

from nota_bene.utils import switch_page_button

st.subheader('Create minutes.')

user_select = st.selectbox(label='Select model', options=["llama3.2:latest", "openhermes-2.5-mistral-7b", "OpenAI"], index=0)
if user_select != 'OpenAI':
    user_select_endpoint = st.selectbox(label='Select model', options=st.session_state['endpoints'], index=0, label_visibility='collapsed')
    if st.session_state['endpoint'] is None or user_select_endpoint != st.session_state['endpoint']:
        st.session_state['endpoint'] = user_select_endpoint
        st.info(f'Endpoint is updated to {st.session_state["endpoint"]}')

user_press = st.button("Maak notulen.")

if not st.session_state["transcript"]:
    switch_page_button("app_pages/transcribe.py", text="Er is nog geen transcript.")
elif user_press and user_select == 'OpenAI':
    client = OpenAI(api_key=st.session_state.openai_api_key)
    response = client.chat.completions.create(
        model=st.session_state.model,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": st.session_state.prompt,
            },
            {"role": "user", "content": st.session_state.transcript},
        ],
        stream=True,
    )
    with st.container(height=400):
        st.session_state["minutes"] = st.write_stream(response)
        st.rerun()

elif user_press and user_select != 'OpenAI':
    from nota_bene.utils import API_LLM

    # Get prompts
    system_prompt = st.session_state['prompt']
    prompt = st.session_state['transcript']

    # Initialize
    model = API_LLM(model_id=user_select, api_url=st.session_state['endpoint'], temperature=0.7)
    response = model.run(f"{system_prompt}\n\n{prompt}")

    # system_prompt = "You are an AI assistant"
    # prompt = "hi"
    # payload = {
    #     "model": user_select,
    #     "prompt": f"{system_prompt}\n\n{prompt}",
    #     "prompt": prompt,
    #     "stream": False
    #     }

    # response = requests.post('http://localhost:11434/api/generate', json=payload)

    # # st.write(response.text)
    # # print(response.text)
    # response = json.loads(response.text)
    # response = response['response']

    with st.container(height=400):
        st.session_state["minutes"] = response
        st.rerun()


if st.session_state["minutes"]:
    if st.button('Edit minutes'):
        minutes_update = st.text_area(label='minutes', value=st.session_state["minutes"], height=1000, label_visibility='collapsed')
        if st.session_state["minutes"] != minutes_update:
            st.session_state["minutes"] = minutes_update
            st.info('Notules zijn bijgewerkt.')

    with st.container(border=False):
        st.markdown(st.session_state["minutes"])

    st.download_button(
        "Download notulen (.md)",
        file_name="notulen.md",
        data=st.session_state["minutes"],
    )
    pdf = MarkdownPdf(toc_level=2)
    f = BytesIO()
    pdf.add_section(Section(st.session_state["minutes"]))
    pdf.save(f)
    st.download_button("Download notulen (.pdf)", file_name="notulen.pdf", data=f)
