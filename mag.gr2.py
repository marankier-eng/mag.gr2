import streamlit as st
import pandas as pd
from supabase import create_client
import time

# --- 1. KONFIGURACJA STRONY ---
st.set_page_config(page_title="System Produktów", page_icon="🏭", layout="wide")

# =========================================================
# ⚙️ KONFIGURACJA NAZW TABEL I KOLUMN (Zmień to tutaj!)
# =========================================================

# Jak nazywają się Twoje tabele w Supabase?
TABELA_PRODUKTY = "produkty"
TABELA_KATEGORIE = "kategorie"

# Jak nazywają się kolumny w tabeli 'produkty'?
COL_PROD_ID = "id"
COL_PROD_NAZWA = "nazwa"      # np. nazwa, name, produkt
COL_PROD_ILOSC = "ilosc"      # np. ilosc, quantity, stan
COL_PROD_KAT = "kategoria"    # Kolumna łącząca z kategorią (tekst)

# Jak nazywa się kolumna z nazwą w tabeli 'kategorie'?
COL_KAT_NAZWA = "nazwa"       # np. nazwa, title, name

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

# --- 3. FUNKCJE DO POBIERANIA DANYCH ---

def get_categories():
    """Pobiera listę kategorii z Twojej tabeli"""
    try:
        # Pobieramy tylko nazwę kategorii
        response = supabase.table(TABELA_KATEGORIE).select(COL_KAT_NAZWA).execute()
        # Wyciągamy samą listę nazw (np. ['Narzędzia', 'BHP'])
        return [item[COL_KAT_NAZWA] for item in response.data]
    except Exception as e:
        st.error(f"Błąd pobierania kategorii. Sprawdź czy tabela '{TABELA_KATEGORIE}' i kolumna '{COL_KAT_NAZWA}' istnieją.")
        st.error(e)
        return []

def get_products():
    """Pobiera listę produktów"""
    try:
        response = supabase.table(TABELA_PRODUKTY).select("*").order(COL_PROD_ID).execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Błąd pobierania produktów. Sprawdź czy tabela '{TABELA_PRODUKTY}' istnieje.")
        st.error(e)
        return pd.DataFrame()

def add_product(nazwa, kategoria, ilosc):
    """Dodaje produkt do tabeli produkty"""
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

# --- 4. CSS (Wygląd i Śnieg) ---
st.markdown("""
<style>
    .santa-fixed-image { position: fixed; top: 10px; right: 10px; z-index: 1000; width: 100px; }
    /* Ukrycie indeksu w tabelach */
    thead tr th:first-child {display:none}
    tbody th {display:none}
</style>
<div class="santa-fixed-image">
    <img src="https://i.imgur.com/39J6i7Z.png" style="width: 100%;">
</div>
""", unsafe_allow_html=True)

# --- 5. LOGIKA APLIKACJI ---

st.title(f"🏭 Zarządzanie: {TABELA_PRODUKTY}")

# A. POBIERANIE DANYCH
lista_kategorii = get_categories()
df = get_products()

# --- SIDEBAR: DODAWANIE ---
with st.sidebar:
    st.header("➕ Dodaj Produkt")
    
    if not lista_kategorii:
        st.warning(f"⚠️ Tabela '{TABELA_KATEGORIE}' jest pusta lub źle skonfigurowana. Dodaj tam najpierw jakieś kategorie w Supabase!")
        active_categories = ["Ogólne"] # Zabezpieczenie
    else:
        active_categories = lista_kategorii

    with st.form("add_form", clear_on_submit=True):
        new_name = st.text_input("Nazwa produktu")
        # Selectbox teraz pobiera dane z Twojej tabeli KATEGORIE
        new_cat = st.selectbox("Kategoria", active_categories)
        new_qty = st.number_input("Ilość", min_value=1, value=1)
        
        if st.form_submit_button("Zapisz w bazie"):
            if new_name:
                try:
                    add_product(new_name, new_cat, new_qty)
                    st.toast("Produkt dodany!", icon="✅")
                    time.sleep(0.5)
                    st.rerun()
                except Exception as e:
                    st.error(f"Nie udało się zapisać: {e}")
            else:
                st.warning("Podaj nazwę produktu.")

# --- DASHBOARD ---
if not df.empty:
    col1, col2 = st.columns(2)
    # Używamy nazw kolumn ze zmiennych
    col1.metric("📦 Wszystkie produkty", len(df))
    col2.metric("🔢 Łączna ilość sztuk", df[COL_PROD_ILOSC].sum() if COL_PROD_ILOSC in df.columns else 0)
else:
    st.info("Brak produktów w bazie.")

st.divider()

# --- EDYCJA TABELI ---
st.subheader("📋 Lista Produktów")

if not df.empty:
    # Dodajemy kolumnę do usuwania
    df["delete"] = False

    # Konfiguracja wyświetlania
    column_settings = {
        COL_PROD_ID: st.column_config.NumberColumn("ID", disabled=True, width="small"),
        COL_PROD_NAZWA: st.column_config.TextColumn("Nazwa"),
        COL_PROD_ILOSC: st.column_config.NumberColumn("Ilość", min_value=0),
        COL_PROD_KAT: st.column_config.SelectboxColumn("Kategoria", options=active_categories),
        "delete": st.column_config.CheckboxColumn("Usuń?", default=False)
    }

    edited_df = st.data_editor(
        df,
        column_config=column_settings,
        hide_index=True,
        use_container_width=True,
        key="editor"
    )

    # Przycisk zapisu
    if st.button("💾 Zapisz zmiany w bazie", type="primary"):
        changes = 0
        
        # 1. Usuwanie
        to_delete = edited_df[edited_df["delete"] == True]
        for idx, row in to_delete.iterrows():
            delete_product(row[COL_PROD_ID])
            changes += 1
        
        # 2. Aktualizacja (tylko to co nie usunięte)
        to_update = edited_df[edited_df["delete"] == False]
        for idx, row in to_update.iterrows():
            # Znajdź oryginał
            orig = df[df[COL_PROD_ID] == row[COL_PROD_ID]].iloc[0]
            
            updates = {}
            # Sprawdzamy czy zmieniła się ilość
            if row[COL_PROD_ILOSC] != orig[COL_PROD_ILOSC]:
                updates[COL_PROD_ILOSC] = row[COL_PROD_ILOSC]
            # Sprawdzamy czy zmieniła się kategoria
            if row[COL_PROD_KAT] != orig[COL_PROD_KAT]:
                updates[COL_PROD_KAT] = row[COL_PROD_KAT]
            # Sprawdzamy czy zmieniła się nazwa
            if row[COL_PROD_NAZWA] != orig[COL_PROD_NAZWA]:
                updates[COL_PROD_NAZWA] = row[COL_PROD_NAZWA]
                
            if updates:
                update_product(row[COL_PROD_ID], updates)
                changes += 1
        
        if changes > 0:
            st.success(f"Zaktualizowano rekordów: {changes}")
            time.sleep(1)
            st.rerun()
        else:
            st.info("Brak zmian do zapisania.")
