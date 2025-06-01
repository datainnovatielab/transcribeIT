"""Page to show used prompt to user."""

import streamlit as st
from nota_bene.utils import switch_page_button

#%%
@st.fragment
def run_main():
    # Ensure session state variables are initialized
    st.session_state.setdefault('edit_mode', False)
    st.session_state.setdefault('instruction', '')

    # Header based on project name
    if st.session_state.get('project_name'):
        st.header(f"Model Instructions: {st.session_state['project_name']}", divider=True)
    else:
        with st.container(border=True):
            st.warning('Create a project first and then select! See left panel sidepanel.')
        return  # Stop execution if no project

    st.subheader(f"Het model {st.session_state['model']} krijgt de volgende instructies mee:")

    col1, col2 = st.columns(2)
    # Multiselect for choosing predefined instruction templates
    options = ["-- Selecteer een prompt --"] + list(st.session_state['instructions'].keys())
    col1.caption('Select The Prompt')

    selected_prompt = col1.selectbox("instructions", options=options, label_visibility='collapsed')
    col2.caption('Load the default prompt')
    load_button = col2.button('Load prompt', type='primary', use_container_width=True)
    if load_button and selected_prompt != '-- Selecteer een prompt --':
        instructions = st.session_state['instructions'][selected_prompt]['system'] + '\n' + st.session_state['instructions'][selected_prompt]['instructions'] + '\n\n' + st.session_state['instructions'][selected_prompt]['query']
        st.session_state['instruction'] = instructions
        st.session_state['instruction_name'] = selected_prompt

    # Toggle button logic
    if st.session_state['edit_mode']:
        # Edit mode
        edited_text = st.text_area(
            label='Edit Instructions',
            value=st.session_state['instruction'],
            label_visibility='collapsed',
            height=1000,
            key='instruction_editor'
        )
        col1, col2 = st.columns([0.2, 0.8])
        with col1:
            if st.button("💾 Save"):
                st.session_state['instruction'] = edited_text
                st.session_state['edit_mode'] = False
                st.success("Instructions updated.")
                st.rerun()
        with col2:
            if st.button("❌ Cancel"):
                st.session_state['edit_mode'] = False
                st.rerun()
    else:
        # View mode
        with st.container(border=True, height=1000):
            st.markdown('Load your prompt with the instructions of interest.' if st.session_state['instruction'] is None else st.session_state['instruction'])
        if st.button("✏️ Edit Instruction"):
            st.session_state['edit_mode'] = True
            st.rerun()

    # Navigation buttons
    with st.container(border=True):
        col1, col2 = st.columns([0.5, 0.5])
        with col1:
            switch_page_button("app_pages/transcribe_edit.py", text='Previous Step: Edit Transcription')
        with col2:
            switch_page_button("app_pages/create_minute_notes.py", text='Next Step: Create Minute Notes', button_type='primary')



# %%
run_main()
