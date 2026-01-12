import streamlit as st
import pandas as pd
from supabase import create_client
import time

# --- 1. KONFIGURACJA STRONY ---
st.set_page_config(page_title="Magazyn i Kategorie", page_icon="📦", layout="wide")

# =========================================================
# ⚙️ KONFIGURACJA NAZW TABEL (Dostosuj jeśli masz inne!)
# =========================================================

# Nazwy tabel w Supabase
TABELA_PRODUKTY = "produkty"
TABELA_KATEGORIE = "kategorie"

# Nazwy kolumn w tabeli 'produkty'
COL_PROD_ID = "id"
COL_PROD_NAZWA = "nazwa"      # nazwa produktu
COL_PROD_ILOSC = "ilosc"      # ilość sztuk
COL_PROD_KAT = "kategoria"    # nazwa kategorii przypisanej do produktu

# Nazwy kolumn w tabeli 'kategorie'
COL_KAT_ID = "id"
COL_KAT_NAZWA = "nazwa"       # nazwa kategorii

# =========================================================

# --- 2. POŁĄCZENIE Z SUPABASE ---
@st.cache_resource
def init_connection():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception:
        return None

supabase = init_connection()

if not supabase:
    st.error("❌ Brak pliku .streamlit/secrets.toml lub błędne klucze!")
    st.stop()

# --- 3. FUNKCJE BAZY DANYCH ---

def get_categories():
    """Pobiera listę nazw kategorii"""
    try:
        response = supabase.table(TABELA_KATEGORIE).select("*").order(COL_KAT_NAZWA).execute()
        # Zwracamy listę samych nazw (np. ['Elektronika', 'Narzędzia'])
        return [item[COL_KAT_NAZWA] for item in response.data]
    except Exception as e:
        st.sidebar.error(f"Błąd tabeli {TABELA_KATEGORIE}: {e}")
        return []

def add_category_to_db(nazwa_kategorii):
    """Dodaje nową kategorię do bazy"""
    try:
        supabase.table(TABELA_KATEGORIE).insert({COL_KAT_NAZWA: nazwa_kategorii}).execute()
        return True
    except Exception as e:
        st.error(f"Błąd dodawania kategorii: {e}")
        return False

def get_products():
    """Pobiera produkty"""
    try:
        response = supabase.table(TABELA_PRODUKTY).select("*").order(COL_PROD_ID).execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Błąd tabeli {TABELA_PRODUKTY}: {e}")
        return pd.DataFrame()

def add_product(nazwa, kategoria, ilosc):
    """Dodaje produkt"""
    data = {
        COL_PROD_NAZWA: nazwa,
        COL_PROD_KAT: kategoria,
        COL_PROD_ILOSC: ilosc
    }
    supabase.table(TABELA_PRODUKTY).insert(data).execute()

def delete_product(item_id):
    supabase.table(TABELA_PRODUKTY).delete().eq(COL_PROD_ID, item_id).execute()

def update_product(item_id, updates):
    supabase.table(TABELA_PRODUKTY).update(updates).eq(COL_PROD_ID, item_id).execute()

# --- 4. CSS (Mikołaj i Śnieg) ---
st.markdown("""
<style>
    .santa-fixed-image { position: fixed; top: 10px; right: 10px; z-index: 1000; width: 100px; }
</style>
<div class="santa-fixed-image">
    <img src="https://i.imgur.com/39J6i7Z.png" style="width: 100%;">
</div>
""", unsafe_allow_html=True)

# --- 5. INTERFEJS APLIKACJI ---
