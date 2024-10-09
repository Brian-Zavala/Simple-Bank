import streamlit as st
import requests


def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()



def background_adjuster(img):
    st.markdown(
        f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background-image: url("{img}");
            background-size: cover;
            background-position: top 0px left -135px;           
            background-origin: border-box;
        }}
       </style>
        """,
        unsafe_allow_html=True
    )
