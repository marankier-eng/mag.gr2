import streamlit as st
import pandas as pd
import time

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Magazyn PRO", page_icon="📦", layout="wide")

# --- KOD CSS: CIĄGŁY ŚNIEG + MIKOŁAJ ---
# Ten blok CSS tworzy animację padającego śniegu w tle
snow_css = """
<style>
    /* Mikołaj */
    .santa-fixed-image {
        position: fixed;
        top: 10px;
        right: 10px;
        z-index: 1000;
        width: 120px;
        height: auto;
    }
    
    /* Animacja śniegu */
    .snowflake {
        color: #fff;
        font-size: 1em;
        font-family: Arial;
        text-shadow: 0 0 1px #000;
    }
    @-webkit-keyframes snowflakes-fall{0%{top:-10%}100%{top:100%}}
    @-webkit-keyframes snowflakes-shake{0%{-webkit-transform:translateX(0px);transform:translateX(0px)}50%{-webkit-transform:translateX(80px);transform:translateX(80px)}100%{-webkit-transform:translateX(0px);transform:translateX(0px)}}
    .snowflake{position:fixed;top:-10%;z-index:9999;-webkit-user-select:none;-moz-user-select:none;-ms-user-select:none;user-select:none;cursor:default;-webkit-animation-name:snowflakes-fall,snowflakes-shake;-webkit-animation-duration:10s,3s;-webkit-animation-timing-function:linear,ease-in-out;-webkit-animation-iteration-count:infinite,infinite;-webkit-animation-play-state:running,running;animation-name:snowflakes-fall,snowflakes-shake;animation-duration:10s,3s;animation-timing-function:linear,ease-in-out;animation-iteration-count:infinite,infinite;animation-play-state:running,running}
    .snowflake:nth-of-type(0){left:1%;-webkit-animation-delay:0s,0s;animation-delay:0s,0s}
    .snowflake:nth-of-type(1){left:10%;-webkit-animation-delay:1s,1s;animation-delay:1s,1s}
    .snowflake:nth-of-type(2){left:20%;-webkit-animation-delay:6s,.5s;animation-delay:6s,.5s}
    .snowflake:nth-of-type(3){left:30%;-webkit-animation-delay:4s,2s;animation-delay:4s,2s}
    .snowflake:nth-of-type(4){left:40%;-webkit-animation-delay:2s,2s;animation-delay:2s,2s}
    .snowflake:nth-of-type(5){left:50%;-webkit-animation-delay:8s,3s;animation-delay:8s,3s}
    .snowflake:nth-of-type(6){left:60%;-webkit-animation-delay:6s,2s;animation-delay:6s,2s}
    .snowflake:nth-of-type(7){left:70%;-webkit-animation-delay:2.5s,1s;animation-delay:2.5s,1s}
    .snowflake:nth-of-type(8){left:80%;-webkit-animation-delay:1s,0s;animation-delay:1s,0s}
    .snowflake:nth-of-type(9){left:90%;-webkit-animation-delay:3s,1.5s;animation-delay:3s,1.5s}
</style>

<div class="snowflakes" aria-hidden="true">
  <div class="snowflake">❅</div>
  <div class="snowflake">❅</div>
  <div class="snowflake">❆</div>
  <div class="snowflake">❄</div>
  <div class="snowflake">❅</div>
  <div class="snowflake">❆</div>
  <div class="snowflake">❄</div>
  <div class="snowflake">❅</div>
  <div class="snowflake">❆</div>
  <div class="snowflake">❄</div>
</div>

<div class="santa-fixed-image">
    <img src="https://i.imgur.com/39J6i7Z.png" style="width: 100%; height: 100%; object-fit: contain;">
</div>
"""
st.markdown(snow_css, unsafe_allow_html=True)

# --- INICJALIZACJA DANYCH (Teraz używamy Pandas DataFrame w pamięci) ---
if 'data' not in st.session_state:
    # Tworzymy przykładowe dane jako listę słowników
    st.session_state['data'] = [
        {"Produkt": "Wiertarka", "Kategoria": "Narzędzia", "Ilość": 5, "Zaznacz": False},
        {"Produkt": "Śruby M8", "Kategoria": "Akcesoria", "Ilość": 200, "Zaznacz": False},
        {"Produkt": "Kask ochronny", "Kategoria": "BHP", "Ilość": 10, "Zaznacz": False},
    ]

# --- SIDEBAR: PANEL STEROWANIA ---
with st.sidebar:
    st.header("➕ Dodaj towar")
    with st.form("add_form", clear_on_submit=True):
        new_name = st.text_input("Nazwa produktu")
        new_cat = st.selectbox("Kategoria", ["Narzędzia", "Elektronika", "Akcesoria", "BHP", "Inne"])
        new_qty = st.number_input("Ilość", min_value=1, value=1)
        submitted = st.form_submit_button("Zapisz w magazynie")
        
        if submitted and new_name:
            new_item = {"Produkt": new_name, "Kategoria": new_cat, "Ilość": new_qty, "Zaznacz": False}
            st.session_state['data'].append(new_item)
            st.success("Dodano!")
            st.rerun()

    st.markdown("---")
    st.info("💡 Wskazówka: Możesz edytować ilość sztuk bezpośrednio w głównej tabeli!")

# --- GŁÓWNA STRONA ---
st.title("🏭 Centrum Zarządzania Magazynem")

# Konwersja listy do DataFrame (tabeli)
df = pd.DataFrame(st.session_state['data'])

# --- PANEL STATYSTYK ---
col1, col2, col3 = st.columns(3)
total_items = df['Ilość'].sum()
unique_items = len(df)
top_category = df['Kategoria'].mode()[0] if not df.empty else "Brak"

col1.metric("📦 Łącznie sztuk", total_items)
col2.metric("📝 Unikalne produkty", unique_items)
col3.metric("🏆 Główna kategoria", top_category)

st.markdown("---")

# --- INTERAKTYWNA TABELA (DATA EDITOR) ---
st.subheader("📋 Stan magazynowy")

# st.data_editor pozwala użytkownikowi zmieniać dane w tabeli!
edited_df = st.data_editor(
    df,
    column_config={
        "Ilość": st.column_config.NumberColumn(
            "Ilość sztuk",
            help="Ile mamy tego na stanie?",
            min_value=0,
            step=1,
            format="%d 📦", # Dodaje ikonkę pudełka do liczb
        ),
        "Kategoria": st.column_config.SelectboxColumn(
            "Kategoria",
            options=["Narzędzia", "Elektronika", "Akcesoria", "BHP", "Inne"],
            required=True,
        ),
        "Zaznacz": st.column_config.CheckboxColumn(
            "Usuń?",
            help="Zaznacz, aby usunąć ten wiersz",
            default=False,
        )
    },
    hide_index=True,
    use_container_width=True,
    num_rows="dynamic" # Pozwala dodawać nowe wiersze na dole
)

# --- AKTUALIZACJA DANYCH ---
# Sprawdzamy, czy dane w tabeli różnią się od tych w sesji
# Jeśli tak, aktualizujemy sesję
if not edited_df.equals(df):
    # Filtrujemy usunięte (te gdzie Zaznacz == True) - to prosty sposób na usuwanie
    # Ale st.data_editor ma też wbudowane usuwanie wierszy, tutaj używamy kolumny "Zaznacz" jako przykładu
    tabela_po_usunieciu = edited_df[edited_df["Zaznacz"] == False].drop(columns=["Zaznacz"])
    
    # Dodajemy kolumnę Zaznacz z powrotem jako False dla przyszłych edycji
    tabela_po_usunieciu["Zaznacz"] = False
    
    # Zapisujemy do sesji
    st.session_state['data'] = tabela_po_usunieciu.to_dict('records')
    st.rerun()

# --- USUWANIE ZAZNACZONYCH (Przycisk pod tabelą) ---
# Jeśli ktoś zaznaczył "ptaszki" w kolumnie "Usuń?", ten przycisk wykona akcję
items_to_delete = edited_df[edited_df["Zaznacz"] == True]
if not items_to_delete.empty:
    if st.button(f"🗑️ Usuń zaznaczone ({len(items_to_delete)})", type="primary"):
        # Logika usuwania
        clean_df = edited_df[edited_df["Zaznacz"] == False]
        st.session_state['data'] = clean_df.to_dict('records')
        st.rerun()

st.markdown("---")

# --- WYKRESY ---
if not df.empty:
    st.subheader("📊 Analiza kategorii")
    # Grupujemy dane po kategorii, żeby zobaczyć ile sztuk jest w każdej
    chart_data = df.groupby("Kategoria")["Ilość"].sum()
    st.bar_chart(chart_data)
