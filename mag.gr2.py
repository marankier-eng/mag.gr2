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

supabase = init_connection()

# --- FUNKCJE BAZY DANYCH ---
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

def update_item(item_id, column, value):
    """Aktualizuje konkretną komórkę"""
    supabase.table("magazyn").update({column: value}).eq("id", item_id).execute()

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
        new_cat = st.selectbox("Kategoria", ["Narzędzia", "Elektronika", "Akcesoria", "BHP", "Inne"])
        new_qty = st.number_input("Ilość", min_value=1, value=1)
        submitted = st.form_submit_button("Zapisz w chmurze ☁️")
        
        if submitted and new_name:
            try:
                add_item(new_name, new_cat, new_qty)
                st.success("Zapisano w Supabase!")
                time.sleep(1) # Czas na przeładowanie bazy
                st.rerun()
            except Exception as e:
                st.error(f"Błąd zapisu: {e}")

# --- GŁÓWNA STRONA ---
st.title("🏭 Magazyn Online (Supabase)")

# 1. POBRANIE DANYCH Z BAZY
df = get_data()

# --- PANEL STATYSTYK ---
if not df.empty:
    col1, col2, col3 = st.columns(3)
    col1.metric("📦 Łącznie sztuk", df['ilosc'].sum())
    col2.metric("📝 Unikalne produkty", len(df))
    col3.metric("🏆 Top Kategoria", df['kategoria'].mode()[0])
else:
    st.info("Baza jest pusta. Dodaj coś w panelu bocznym!")

st.markdown("---")

# --- EDYCJA DANYCH ---
st.subheader("📋 Stan magazynowy")

if not df.empty:
    # Dodajemy kolumnę "Usuń" do DataFrame, żeby obsłużyć to w edytorze
    df["Usuń"] = False

    # Konfiguracja edytora
    edited_df = st.data_editor(
        df,
        column_config={
            "id": st.column_config.NumberColumn("ID", disabled=True, width="small"), # ID nie edytujemy!
            "produkt": "Nazwa",
            "kategoria": st.column_config.SelectboxColumn("Kategoria", options=["Narzędzia", "Elektronika", "Akcesoria", "BHP", "Inne"]),
            "ilosc": st.column_config.NumberColumn("Ilość", min_value=0, format="%d 📦"),
            "Usuń": st.column_config.CheckboxColumn("Zaznacz aby usunąć", default=False)
        },
        hide_index=True,
        use_container_width=True,
        key="editor" # Klucz jest ważny do śledzenia zmian
    )

    # --- LOGIKA ZAPISYWANIA ZMIAN ---
    # Porównujemy oryginalne dane z edytowanymi, aby wykryć zmiany
    # UWAGA: W prostym podejściu robimy to przyciskiem "Zatwierdź zmiany" dla bezpieczeństwa

    col_btn1, col_btn2 = st.columns([1, 4])
    
    if col_btn1.button("💾 Zatwierdź zmiany", type="primary"):
        changes_count = 0
        
        # 1. Sprawdzanie usunięć
        rows_to_delete = edited_df[edited_df["Usuń"] == True]
        for index, row in rows_to_delete.iterrows():
            delete_item(row['id'])
            changes_count += 1
            
        # 2. Sprawdzanie edycji (tylko jeśli nie usunięto)
        # Iterujemy po wierszach, które NIE są zaznaczone do usunięcia
        rows_to_update = edited_df[edited_df["Usuń"] == False]
        
        # Aby nie aktualizować wszystkiego (co jest wolne), można by porównywać wiersze.
        # Dla uproszczenia w małej aplikacji: aktualizujemy tylko zmienione ilości/kategorie
        # Porównujemy z oryginałem 'df' po ID.
        
        for index, row in rows_to_update.iterrows():
            original_row = df[df['id'] == row['id']].iloc[0]
            
            if row['ilosc'] != original_row['ilosc']:
                update_item(row['id'], 'ilosc', row['ilosc'])
                changes_count += 1
            
            if row['kategoria'] != original_row['kategoria']:
                update_item(row['id'], 'kategoria', row['kategoria'])
                changes_count += 1

        if changes_count > 0:
            st.success(f"Zaktualizowano {changes_count} rekordów w bazie!")
            time.sleep(1)
            st.rerun()
        else:
            st.info("Nie wykryto zmian do zapisania.")

st.markdown("---")

# --- WYKRESY ---
if not df.empty:
    st.subheader("📊 Analiza")
    chart_data = df.groupby("kategoria")["ilosc"].sum()
    st.bar_chart(chart_data)
