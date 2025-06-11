"""Configurations."""

import streamlit as st
import time
import numpy as np
import copy
import os
from nota_bene.utils import set_project_paths, load_llm_model

#%%
def run_main():
    st.header('⚙️ Configurations', divider=True)

    # API-End points
    _update_endpoint()
    # API-End points
    _update_model()
    # Set temp dir
    _update_tempdir()
    # Set bitrate
    _update_bitrate()

#%%
def _update_bitrate():
    with st.container(border=True):
        st.subheader('Bitrate', divider='gray')
        st.caption('Set the bitrate of the audio files. Note that Whisper uses 16k bitrate and is therefore recommend for usage.')
        set_user_bitrate = st.slider("bitrate", min_value=16, max_value=128, value=24, step=8)
        set_user_bitrate_str = str(set_user_bitrate) + 'k'
        # Store
        if st.session_state['bitrate'] != set_user_bitrate_str:
            st.session_state['bitrate'] = set_user_bitrate_str

#%%
def _update_tempdir():
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
            set_project_paths(project_name)

            if not os.path.exists(st.session_state['project_path']):
                os.makedirs(st.session_state['project_path'])
                st.success(f"Project directory: {st.session_state['project_path']}")
                st.rerun()
            else:
                st.success(f"Project directory: {st.session_state['project_path']}")


#%%
def _update_endpoint():
    with st.container(border=True):
        col1, col2 = st.columns([0.5, 0.5])
        col1.subheader('Add New API-endpoint', divider='gray')
        # st.caption('API-endpoint.')

        user_endpoint = col1.text_input(label='End points', label_visibility='collapsed').strip()

        # Only update if on_change.
        if user_endpoint != st.session_state['endpoint'] and user_endpoint != '' and not np.any(np.isin(st.session_state['endpoints'], user_endpoint)):
            st.session_state['endpoints'].append(user_endpoint)
            st.session_state['endpoints'] = list(set(st.session_state['endpoints']))
            st.success('New end point is added.')
            # st.rerun()

        col2.subheader('Select API-endpoint', divider='gray')
        index = st.session_state['endpoints'].index(st.session_state['endpoint']) if 'endpoint' in st.session_state and st.session_state['endpoint'] in st.session_state['endpoints'] else None

        user_select_endpoint = col2.selectbox(label='Select endpoint', options=st.session_state['endpoints'], index=index, label_visibility='collapsed')
        if st.session_state['endpoint'] is not None or user_select_endpoint != st.session_state['endpoint']:
            st.session_state['endpoint'] = user_select_endpoint
            # st.info(f'Endpoint is updated to {st.session_state["endpoint"]}')

        col1.caption('Selected API Endpoint')
        col1.text_input('Selected API Endpoint', value=st.session_state['endpoint'], disabled=True, label_visibility='collapsed')
        col2.caption('Validate')
        if col2.button('Validate API-endpoint', type='primary'):
            # Initialize local LLM with custom endpoint
            try:
                llm = load_llm_model()
                with st.spinner('Checking API endpoint by updating available models..'):
                    models = llm.get_available_models()
                    st.session_state['model_names'] = ['gpt-4o-mini'] + models
                    st.success('✅ Endpoint is updated and available models from API Endpoint can now be selected!')
            except Exception as e:
                st.error(f'❌ Endpoint not valid! Please select another one. {e}')

#%%
def _update_model():
    with st.container(border=True):
        st.subheader('Available LLM models', divider='gray')
        st.caption('Select the prefered LLM model')
        col1, col2 = st.columns([0.7, 0.3])
        # index = st.session_state['model_names'].index(st.session_state['model'])
        index = st.session_state['model_names'].index(st.session_state['model']) if 'model' in st.session_state and st.session_state['model'] in st.session_state['model_names'] else None

        modelname = col1.selectbox('llm models', options=st.session_state['model_names'], index=index, label_visibility='collapsed')

        if col2.button('Set LLM model', type='primary'):# and modelname != st.session_state['model']:
            llm = load_llm_model(modelname=modelname)
            with st.spinner(f'Checking: {llm.modelname}'):
                response = llm.prompt(f'Be extremely happy and promote yourself in one very short sentences!', system="You are a helpful and very happy assistant.")
                if '400' in response[0:30] or '404' in response[0:30]:
                    st.error(f'❌ {modelname} is not available. Please select a different one.')
                else:
                    st.success(f'✅ Model is updated to {modelname}!')
                    st.write(response)
                    st.session_state['model'] = modelname

# %%
run_main()
