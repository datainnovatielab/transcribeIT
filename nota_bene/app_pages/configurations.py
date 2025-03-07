"""Configurations."""

import streamlit as st
import time
import numpy as np
import copy

colm1, colm2 = st.columns([1, 1])
with colm1:
    with st.container(border=True):
        st.subheader('API Endpoint', divider='gray')
        st.caption('Add new end point for the API.')

        user_endpoint = st.text_input(label='End points', label_visibility='collapsed').strip()
        # Only update if on_change.
        if user_endpoint != st.session_state['endpoint'] and user_endpoint != '':
            st.session_state['endpoints'].append(user_endpoint)
            st.success('New end point is added.')

    with colm2:
        with st.container(border=True):
            st.subheader('Temp directory', divider='gray')
            st.caption('Temp directory where thumbnails are stored for faster loading.')
            # tempdir = st.text_input(label='tempdir', value=st.session_state.get('tempdir', ''), label_visibility='collapsed').strip()
            # if tempdir != st.session_state['tempdir']:
            #     st.session_state['tempdir'] = tempdir
            #     st.info('Temp directory is udpated.')
