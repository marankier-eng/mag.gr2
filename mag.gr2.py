import streamlit as st
import time

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Świąteczny Magazyn", page_icon="📦")

# --- KOD CSS DLA MIKOŁAJA NA RENIFERZE ---
MIKOLAJ_URL = "https://i.imgur.com/39J6i7Z.png"

christmas_css = f"""
<style>
    .santa-fixed-image {{
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1000;
        width: 150px;
        height: auto;
    }}
    /* Dodatkowy styl dla metryk */
    div[data-testid="stMetric"] {{
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
    }}
</style>
<div class="santa-fixed-image">
    <img src="{MIKOLAJ_URL}" style="width: 100%; height: 100%; object-fit: contain;">
</div>
"""
st.markdown(christmas_css, unsafe_allow_html=True)

# 📦 Tytuł i opis aplikacji
st.title("📦 Świąteczny Magazyn")
st.caption("Aplikacja do zarządzania listą towarów w pamięci sesji.")

# --- INICJALIZACJA STANU ---
if 'magazyn' not in st.session_state:
    st.session_state['magazyn'] = ["Wiertarka", "Śruby M8", "Rękawice robocze", "Czapka Mikołaja"]

# --- FUNKCJE POMOCNICZE ---
def pobierz_dane_txt():
    return "\n".join(st.session_state['magazyn'])

# ==========================================
# 📊 SEKCJA 0: DASHBOARD (STATYSTYKI) - TO JEST NOWOŚĆ
# ==========================================
st.markdown("### 📊 Statystyki")
col1, col2, col3 = st.columns(3)

ilosc_towarow = len(st.session_state['magazyn'])
ostatni_towar = st.session_state['magazyn'][-1] if ilosc_towarow > 0 else "Brak"

col1.metric("Liczba produktów", ilosc_towarow, delta=None)
col2.metric("Ostatnio dodany", ostatni_towar)
# Przycisk pobierania listy
col3.download_button(
    label="📥 Pobierz listę (TXT)",
    data=pobierz_dane_txt(),
    file_name="stan_magazynu.txt",
    mime="text/plain"
)

st.markdown("---")

# ==========================================
# 🔎 SEKCJA 1: WYŚWIETLANIE I WYSZUKIWANIE
# ==========================================
st.header("📋 Stan magazynu")

# Wyszukiwarka
szukana_fraza = st.text_input("🔍 Szukaj towaru...", placeholder="Wpisz nazwę...")

if st.session_state['magazyn']:
    # Filtrowanie listy
    if szukana_fraza:
        lista_do_wyswietlenia = [t for t in st.session_state['magazyn'] if szukana_fraza.lower() in t.lower()]
    else:
        lista_do_wyswietlenia = st.session_state['magazyn']
    
    # Wyświetlanie w ładniejszy sposób (kontener)
    if lista_do_wyswietlenia:
        for idx, towar in enumerate(lista_do_wyswietlenia, 1):
            st.text(f"{idx}. {towar}")
    else:
        st.info("Nie znaleziono towaru o takiej nazwie.")
else:
    st.info("Magazyn jest pusty. Dodaj pierwszy towar!")

st.markdown("---")

# ==========================================
# ➕ SEKCJA 2: DODAWANIE TOWARU
# ==========================================
st.header("➕ Dodaj nowy towar")

with st.form("dodaj_formularz", clear_on_submit=True):
    nowy_towar = st.text_input("Wpisz nazwę towaru")
    cols = st.columns([1, 4]) # Układ przycisku
    dodaj_przycisk = cols[0].form_submit_button("Dodaj")
    
    if dodaj_przycisk:
        if nowy_towar.strip():
            st.session_state['magazyn'].append(nowy_towar.strip())
            st.success(f"Dodano: **{nowy_towar.strip()}**")
            # Efekt śniegu przy sukcesie! ❄️
            st.snow() 
            time.sleep(1) # Krótka pauza żeby zobaczyć komunikat przed odświeżeniem
            st.rerun() 
        else:
            st.warning("Nazwa towaru nie może być pusta.")

st.markdown("---")

# ==========================================
# ❌ SEKCJA 3: USUWANIE TOWARU
# ==========================================
st.header("❌ Usuń towar")

if st.session_state['magazyn']:
    with st.expander("Rozwiń, aby usunąć towar"): # Ukrywamy to w rozwijanym panelu, żeby było czyściej
        towar_do_usuniecia = st.selectbox(
            "Wybierz towar do usunięcia",
            st.session_state['magazyn'],
            key="select_usun"
        )

        if st.button("Usuń wybrany towar", type="primary"): # type="primary" robi czerwony/główny przycisk
            st.session_state['magazyn'].remove(towar_do_usuniecia)
            st.toast(f"Usunięto: {towar_do_usuniecia}", icon="🗑️") # Toast to małe powiadomienie w rogu
            time.sleep(1)
            st.rerun()
else:
    st.write("Brak towarów do usunięcia.")
