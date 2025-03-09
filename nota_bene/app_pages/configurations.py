"""Configurations."""

import streamlit as st
import time
import numpy as np
import copy
import os

# colm1, colm2 = st.columns([1, 1])
# with colm1:
with st.container(border=True):
    st.subheader('API Endpoint', divider='gray')
    st.caption('Add new end point for the API.')

    user_endpoint = st.text_input(label='End points', label_visibility='collapsed').strip()
    # Only update if on_change.
    if user_endpoint != st.session_state['endpoint'] and user_endpoint != '':
        st.session_state['endpoints'].append(user_endpoint)
        st.success('New end point is added.')

# with colm1:
with st.container(border=True):
    st.subheader('Temp directory', divider='gray')
    st.caption('Temp directory where thumbnails are stored for faster loading.')
    temp_dir = st.text_input(label='temp_dir', value=st.session_state['temp_dir'], label_visibility='collapsed').strip()

    # Store
    if temp_dir != st.session_state['temp_dir']:
        st.session_state['temp_dir'] = temp_dir
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
            st.info(f'Directory is created: {temp_dir}')
        else:
            st.info('Temp directory is udpated.')

with st.container(border=True):
    st.subheader('Bitrate', divider='gray')
    st.caption('Set the bitrate of the audio files. Note that Whisper uses 16k bitrate and is therefore recommend for usage.')
    set_user_bitrate = st.slider("bitrate", min_value=16, max_value=128, value=24, step=8)
    set_user_bitrate_str = str(set_user_bitrate) + 'k'
    # Store
    if st.session_state['bitrate'] != set_user_bitrate_str:
        st.session_state['bitrate'] = set_user_bitrate_str
        # st.info(f"Bitrate is udpated to {st.session_state['bitrate']}")
