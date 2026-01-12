import streamlit as st
import pandas as pd
from supabase import create_client
import time

# --- 1. USTAWIENIA STRONY ---
st.set_page_config(page_title="Magazyn Supabase", page_icon="🏭", layout="wide")

# =========================================================
# ⚙️ KONFIGURACJA (TUTAJ DOPASUJ NAZWY DO SWOJEJ BAZY!)
# =========================================================

# Nazwy tabel w Supabase
TABLE_PRODUKTY = "produkty"
TABLE_KATEGORIE = "kategorie"

# Nazwy kolumn w tabeli 'produkty'
COL_ID = "id"
COL_NAZWA = "nazwa"       # np. "name", "produkt", "title"
COL_ILOSC = "ilosc"       # <--- TU BYŁ BŁĄD. Sprawdź czy masz "ilosc", "quantity" czy "liczba"
COL_KAT = "kategoria"     # nazwa kolumny, która przechowuje kategorię

# Nazwy kolumn w tabeli 'kategorie'
COL_KAT_NAZWA = "nazwa"   # np. "name", "category_name"

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
    st.error("❌ Brak pliku .streamlit/secrets.toml lub błędne klucze API!")
    st.stop()

# --- 3. FUNKCJE (OPERACJE NA BAZIE) ---

def get_categories():
    """Pobiera listę kategorii"""
    try:
        response = supabase.table(TABLE_KATEGORIE).select(COL_KAT_NAZWA).execute()
        return [item[COL_KAT_NAZWA] for item in response.data]
    except Exception as e:
        st.error(f"❌ Błąd pobierania kategorii. Sprawdź czy tabela '{TABLE_KATEGORIE}' ma kolumnę '{COL_KAT_NAZWA}'.")
        return []

def add_category(nazwa):
    """Dodaje nową kategorię"""
    supabase.table(TABLE_KATEGORIE).insert({COL_KAT_NAZWA: nazwa}).execute()

def get_products():
    """Pobiera produkty"""
    try:
        response = supabase.table(TABLE_PRODUKTY).select("*").order(COL_ID).execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        msg = str(e)
        if "Could not find the" in msg:
            st.error(f"🚨 BŁĄD KOLUMN: Supabase nie widzi kolumny zdefiniowanej w kodzie. Sprawdź sekcję KONFIGURACJA na górze pliku.\nSzczegóły: {msg}")
        else:
            st.error(f"Błąd pobierania produktów: {msg}")
        return pd.DataFrame()

def add_product(nazwa, kat, ilosc):
    """Dodaje produkt (używając nazw kolumn z konfiguracji)"""
    data = {
        COL_NAZWA: nazwa,
        COL_KAT: kat,
        COL_ILOSC: ilosc
    }
    supabase.table(TABLE_PRODUKTY).insert(data).execute()

def update_product(item_id, updates):
    """Aktualizuje produkt"""
    supabase.table(TABLE_PRODUKTY).update(updates).eq(COL_ID, item_id).execute()

def delete_product(item_id):
    """Usuwa produkt"""
    supabase.table(TABLE_PRODUKTY).delete().eq(COL_ID, item_id).execute()

# --- 4. WYGLĄD (CSS + ŚNIEG) ---
st.markdown("""
<style>
    .santa-fixed-image { position: fixed; top: 10px; right: 10px; z-index: 1000; width: 100px; }
    div[data-testid="stMetric"] { background-color: #f0f2f6; border-radius: 10px; padding: 10px; }
</style>
<div class="santa-fixed-image">
    <img src="https://i.imgur.com/39J6i7Z.png" style="width: 100%;">
</div>
""", unsafe_allow_html=True)

# --- 5. LOGIKA APLIKACJI ---

st.title("🏭 System Magazynowy")

# Pobranie danych na start
lista_kat = get_categories()
df = get_products()

# --- PANEL BOCZNY (DODAWANIE) ---
with st.sidebar:
    st.header("🛠️ Panel Sterowania")
    
    # Zakładki w sidebarze dla porządku
    tab_prod, tab_kat = st.tabs(["📦 Produkt", "📂 Kategoria"])
    
    with tab_kat:
        st.write("**Dodaj nową kategorię**")
        new_cat_name = st.text_input("Nazwa kategorii", key="cat_in")
        if st.button("Dodaj kategorię"):
            if new_cat_name:
                try:
                    add_category(new_cat_name)
                    st.success("Dodano!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Błąd: {e}")
            else:
                st.warning("Wpisz nazwę.")

    with tab_prod:
        st.write("**Dodaj produkt**")
        if not lista_kat:
            st.error("⚠️ Brak kategorii! Dodaj je w zakładce obok.")
        else:
            with st.form("add_prod_form", clear_on_submit=True):
                p_name = st.text_input("Nazwa")
                p_cat = st.selectbox("Kategoria", lista_kat)
                p_qty = st.number_input("Ilość", min_value=1, value=1)
                
                if st.form_submit_button("Zapisz"):
                    if p_name:
                        try:
                            add_product(p_name, p_cat, p_qty)
                            st.toast("Produkt dodany!", icon="✅")
                            time.sleep(0.5)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Błąd zapisu: {e}")
                    else:
                        st.warning("Nazwa wymagana.")

# --- DASHBOARD ---
if not df.empty and COL_ILOSC in df.columns:
    c1, c2, c3 = st.columns(3)
    c1.metric("📦 Produkty", len(df))
    c2.metric("🔢 Łączna Ilość", df[COL_ILOSC].sum())
    c3.metric("📂 Kategorie", len(lista_kat))
elif df.empty:
    st.info("Baza jest pusta. Użyj panelu po lewej, aby dodać dane.")

st.divider()

# --- EDYCJA TABELI ---
st.subheader("📋 Stan Magazynowy")

if not df.empty:
    # Dodanie kolumny technicznej do usuwania
    df["delete"] = False
    
    # Konfiguracja kolumn dla data_editora
    column_config = {
        COL_ID: st.column_config.
