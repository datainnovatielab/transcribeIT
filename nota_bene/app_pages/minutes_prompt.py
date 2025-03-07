"""Page to show used prompt to user."""

import streamlit as st

from nota_bene.utils import switch_page_button

st.subheader(f"Het model {st.session_state['model']} krijgt de volgende instructies mee:")
if st.button('Edit instructions'):
    user_minutes_prompt = st.text_area(label='user_minutes_prompt', value=st.session_state['prompt'], label_visibility='collapsed', height=1000)
    if user_minutes_prompt != '' and user_minutes_prompt != st.session_state['prompt']:
        st.session_state['prompt'] = user_minutes_prompt
        st.info('Instructions are updated.')
        # st.rerun()

with st.container(border=True, height=1000):
    st.markdown(st.session_state['prompt'])


switch_page_button("app_pages/create_minutes.py")
