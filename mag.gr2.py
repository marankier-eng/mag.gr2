import streamlit as st
import pandas as pd
from supabase import create_client, Client
import time

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Magazyn w Chmurze", page_icon="☁️", layout="wide")

# --- POŁĄCZENIE Z SUPABASE ---
# Używamy @st.cache_resource, żeby nie łączyć się przy każdym kliknięciu
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase = init_connection()
except FileNotFoundError:
    st.error("Brakuje pliku .streamlit/secrets.toml z kluczami API!")
    st.stop()

# --- FUNKCJE BAZY DANYCH (CRUD) ---
def get_data():
    """Pobiera wszystkie dane z tabeli 'magazyn'"""
    response = supabase.table("magazyn").select("*").order("id").execute()
    return pd.DataFrame(response.data)

def add_item(produkt, kategoria, ilosc):
    """Dodaje nowy wiersz"""
    data = {"produkt": produkt, "kategoria": kategoria, "ilosc": ilosc}
    supabase.table("magazyn").insert(data).execute()

def delete_item(item_id):
    """Usuwa wiersz po ID"""
    supabase.table("magazyn").delete().eq("id", item_id).execute()

def update_item(item_id, updates):
    """Aktualizuje konkretny wiersz (słownik zmian)"""
    supabase.table("magazyn").update(updates).eq("id", item_id).execute()

# --- CSS: ŚNIEG I WYGLĄD ---
snow_css = """
<style>
    .santa-fixed-image { position: fixed; top: 10px; right: 10px; z-index: 1000; width: 120px; }
    .snowflake { color: #fff; font-size: 1em; text-shadow: 0 0 1px #000; }
    @-webkit-keyframes snowflakes-fall{0%{top:-10%}100%{top:100%}}
    @-webkit-keyframes snowflakes-shake{0%{-webkit-transform:translateX(0px)}50%{-webkit-transform:translateX(80px)}100%{-webkit-transform:translateX(0px)}}
    .snowflake{position:fixed;top:-10%;z-index:9999;-webkit-user-select:none;user-select:none;cursor:default;
    animation-name:snowflakes-fall,snowflakes-shake;animation-duration:10s,3s;animation-timing-function:linear,ease-in-out;animation-iteration-count:infinite,infinite;animation-play-state:running,running}
    .snowflake:nth-of-type(1){left:10%;animation-delay:1s,1s} .snowflake:nth-of-type(2){left:20%;animation-delay:6s,.5s}
    .snowflake:nth-of-type(3){left:30%;animation-delay:4s,2s} .snowflake:nth-of-type(4){left:40%;animation-delay:2s,2s}
    .snowflake:nth-of-type(5){left:50%;animation-delay:8s,3s} .snowflake:nth-of-type(6){left:60%;animation-delay:6s,2s}
</style>
<div class="snowflakes" aria-hidden="true">
  <div class="snowflake">❅</div><div class="snowflake">❆</div><div class="snowflake">❄</div>
  <div class="snowflake">❅</div><div class="snowflake">❆</div><div class="snowflake">❄</div>
</div>
<div class="santa-fixed-image">
    <img src="https://i.imgur.com/39J6i7Z.png" style="width: 100%; height: 100%; object-fit: contain;">
</div>
"""
st.markdown(snow_css, unsafe_allow_html=True)

# --- SIDEBAR: DODAWANIE TOWARU ---
with st.sidebar:
    st.header("➕ Dodaj do Bazy")
    with st.form("add_form", clear_on_submit=True):
        new_name = st.text_input("Nazwa produktu")
        new_cat = st.selectbox
