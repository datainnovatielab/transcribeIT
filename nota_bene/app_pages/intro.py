"""Page containing intro text for NotaBene."""

from nota_bene.utils import switch_page_button
import streamlit as st

#%%
def run_main():
    welcome_text="""
    # **Welkom bij NotaBene**
    De slimme oplossing voor moeiteloos notuleren en transcripties!
    
    ## **Wat is NotaBene?**
    NotaBene maakt gebruik van geavanceerde technologieën, zoals **OpenAI GPT-4o-mini** en
    **Whisper**, om jouw vergaderingen, interviews en gesprekken automatisch om te zetten
    in heldere notities en transcripties. Dit bespaart tijd, verhoogt de efficiëntie en
    helpt je om je volledig te focussen op de inhoud van het gesprek.
    
    ---
    
    ## **Hoe werkt het?**
    1. **Voer je OpenAI API-sleutel in**:
       Vul je persoonlijke OpenAI API-sleutel in om toegang te krijgen tot de app. Dit
       zorgt ervoor dat de app veilig en volledig op maat voor jou werkt.
    
    2. **Upload een audiobestand**:
       - Gebruik bestaande opnames
    
    3. **Automatische transcriptie**:
       Whisper zet je audio snel en nauwkeurig om in tekst.
    
    4. **Slimme samenvatting en inzichten**:
       Het grote taal model analyseert de transcriptie en levert overzichtelijke samenvattingen en
       belangrijke actiepunten.
    
    ---
    
    ## **Belangrijk: Let op bij het gebruik van vertrouwelijke gegevens!**
    - **OpenAI kan je data verwerken:** Hoewel NotaBene jouw gegevens niet opslaat, kan de
    OpenAI API de ingevoerde data verwerken om de transcriptie en samenvattingen te
    genereren.
    - **Gebruik daarom geen gevoelige of vertrouwelijke informatie:** Denk hierbij aan
    persoonlijke gegevens, financiële informatie of andere privacygevoelige inhoud.
    
    ---
    
    ## **Waarom NotaBene gebruiken?**
    - ✅ **Tijdsbesparing**: Laat technologie het zware werk doen.
    - ✅ **Heldere notities**: Directe samenvattingen en actiepunten zonder extra moeite.
    - ✅ **Gebruiksvriendelijk**: Intuïtieve interface, eenvoudig in gebruik.
    - ✅ **Flexibiliteit**: Geschikt voor vergaderingen, interviews, webinars en meer.
    
    ---
    
    ## **Hoe kan ik beginnen?**
    1. Zorg dat je een OpenAI API-sleutel hebt.
    2. Start de app en volg de eenvoudige stappen op het scherm.
    3. Upload je audiobestand of start een live sessie – en laat NotaBene de rest doen!
    
    ---
    
    ### **Veel plezier met NotaBene!**
    Heb je vragen, feedback of ideeën? Laat het ons weten. Samen maken we notuleren nóg
    slimmer en efficiënter.
    
    
    """
    
    st.markdown(welcome_text)
    navigation()

#%%
def navigation():
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            switch_page_button("app_pages/audio_recording.py", text='Next Step: Upload/ Record Audio', button_type='primary')

# %%
run_main()
