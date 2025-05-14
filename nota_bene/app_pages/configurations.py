"""Configurations."""

import streamlit as st
import time
import numpy as np
import copy
import os
from nota_bene.utils import set_project_paths

if st.session_state['project_name']:
    st.header('Configurations For ' + st.session_state['project_name'], divider=True)
else:
    with st.container(border=True):
        st.info('Each project starts with a name. Create your new project at the left sidepanel.')

# colm1, colm2 = st.columns([1, 1])
# with colm1:
with st.container(border=True):
    st.subheader('API Endpoint', divider='gray')
    st.caption('Add new API-endpoint.')

    user_endpoint = st.text_input(label='End points', label_visibility='collapsed').strip()
    # Only update if on_change.
    if user_endpoint != st.session_state['endpoint'] and user_endpoint != '':
        st.session_state['endpoints'].append(user_endpoint)
        st.success('New end point is added.')

    # user_model = st.selectbox(label='Select model', options=st.session_state['model_names'], index=0)
    # if user_model != st.session_state['model']:
    #     st.session_state['model'] = user_model

    if st.session_state['model'] != 'gpt-4o-mini':
        index = st.session_state['endpoints'].index(st.session_state['endpoint'])
        user_select_endpoint = st.selectbox(label='Select model', options=st.session_state['endpoints'], index=index, label_visibility='collapsed')
        if st.session_state['endpoint'] is None or user_select_endpoint != st.session_state['endpoint']:
            st.session_state['endpoint'] = user_select_endpoint
            # st.info(f'Endpoint is updated to {st.session_state["endpoint"]}')


# with colm1:
with st.container(border=True):
    st.subheader('Temp directory', divider='gray')
    col1, col2 = st.columns([5, 2])
    col1.caption('Temp directory where thumbnails are stored for faster loading')
    temp_dir = col1.text_input(label='temp_dir', value=st.session_state['temp_dir'], label_visibility='collapsed').strip()
    col2.caption('Project name')
    project_name = col2.text_input(label='project_name', value=st.session_state['project_name'], label_visibility='collapsed')
    if project_name is None:
        project_name = ''
    else:
        project_name = project_name.strip()

    # Store
    project_path = os.path.join(temp_dir, project_name)
    if project_path != st.session_state['project_path']:
        st.session_state['temp_dir'] = temp_dir
        # st.session_state['project_name'] = project_name
        # st.session_state['project_path'] = project_path
        # st.session_state["save_path"] = os.path.join(st.session_state['project_path'], 'session_states.pkl')
        set_project_paths(project_name)

        if not os.path.exists(st.session_state['project_path']):
            os.makedirs(st.session_state['project_path'])
            st.success(f"Project directory: {st.session_state['project_path']}")
            st.rerun()
        else:
            st.success(f"Project directory: {st.session_state['project_path']}")

with st.container(border=True):
    st.subheader('Bitrate', divider='gray')
    st.caption('Set the bitrate of the audio files. Note that Whisper uses 16k bitrate and is therefore recommend for usage.')
    set_user_bitrate = st.slider("bitrate", min_value=16, max_value=128, value=24, step=8)
    set_user_bitrate_str = str(set_user_bitrate) + 'k'
    # Store
    if st.session_state['bitrate'] != set_user_bitrate_str:
        st.session_state['bitrate'] = set_user_bitrate_str
        # st.info(f"Bitrate is udpated to {st.session_state['bitrate']}")
