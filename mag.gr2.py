import streamlit as st

# --- KOD CSS DLA MIKOŁAJA NA RENIFERZE ---
MIKOLAJ_URL = "https://i.imgur.com/39J6i7Z.png" # Przykładowy link do obrazka

christmas_css = f"""
<style>
    /* Klasa dla obrazka Mikołaja */
    .santa-fixed-image {{
        position: fixed; /* Stała pozycja względem okna przeglądarki */
        top: 20px;      /* 20px od góry */
        right: 20px;    /* 20px od prawej */
        z-index: 1000;  /* Upewnia się, że obrazek jest na wierzchu */
        width: 150px;   /* Ustawia szerokość obrazka */
        height: auto;
    }}
</style>
<div class="santa-fixed-image">
    <img src="{MIKOLAJ_URL}" style="width: 100%; height: 100%; object-fit: contain;">
</div>
"""

# Wstrzyknięcie CSS i HTML do strony
st.markdown(christmas_css, unsafe_allow_html=True)

# 📦 Tytuł i opis aplikacji
st.title("📦 Prosty Magazyn w Pythonie (Streamlit)")
st.write("Aplikacja do zarządzania listą towarów. Dane przechowywane są w pamięci sesji (bez zapisu do plików).")

# --- KLUCZOWY MECHANIZM: st.session_state ---
if 'magazyn' not in st.session_state:
    st.session_state['magazyn'] = ["Wiertarka", "Śruby M8", "Rękawice robocze"] # Przykładowe dane startowe

# -----------------------------------------------

# --- 1. WYŚWIETLANIE STANU MAGAZYNU ---
st.header("📋 Aktualny stan magazynu")

if st.session_state['magazyn']:
    lista_wyswietlana = [f"* {towar}" for towar in st.session_state['magazyn']]
    st.markdown("\n".join(lista_wyswietlana))
else:
    st.info("Magazyn jest pusty. Dodaj pierwszy towar!")

st.markdown("---")

# --- 2. DODAWANIE TOWARU ---
st.header("➕ Dodaj nowy towar")

with st.form("dodaj_formularz", clear_on_submit=True):
    nowy_towar = st.text_input("Wpisz nazwę towaru")
    dodaj_przycisk = st.form_submit_button("Dodaj do magazynu")

    if dodaj_przycisk:
        if nowy_towar.strip(): # Sprawdzenie, czy pole nie jest puste
            st.session_state['magazyn'].append(nowy_towar.strip())
            st.success(f"Dodano: **{nowy_towar.strip()}**")
            st.rerun() 
        else:
            st.warning("Nazwa towaru nie może być pusta.")

st.markdown("---")

# --- 3. USUWANIE TOWARU (POPRAWIONE) ---
st.header("❌ Usuń towar")

if st.session_state['magazyn']:
    towar_do_usuniecia = st.selectbox(
        "Wybierz towar z listy do usunięcia",
        st.session_state['magazyn'],
        index=None,
        placeholder="Wybierz towar..."
    )

    # Użycie JEDNEGO przycisku z unikalnym kluczem
    przycisk_usun = st.button("Usuń wybrany towar", key="usun_przycisk")

    if przycisk_usun:
        if towar_do_usuniecia:
            st.session_state['magazyn'].remove(towar_do_usuniecia)
            st.error(f"Usunięto: **{towar_do_usuniecia}**")
            st.rerun()
        else:
            st.warning("Proszę wybrać towar do usunięcia.")
else:
    st.write("Brak towarów w magazynie.")
