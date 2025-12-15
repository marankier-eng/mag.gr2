import streamlit as st

# Tytuł aplikacji
st.title("📦 Prosty Magazyn w Pythonie")
st.write("Aplikacja do zarządzania listą towarów (działa w pamięci podręcznej).")

# --- INICJALIZACJA STANU (SESSION STATE) ---
# Sprawdzamy, czy w pamięci sesji istnieje już lista towarów.
# Jeśli nie, tworzymy pustą listę. Dzięki temu dane nie znikają po kliknięciu przycisku.
if 'magazyn' not in st.session_state:
    st.session_state['magazyn'] = ["Jabłka", "Banany"] # Przykładowe dane startowe

# --- SEKCJA 1: WYŚWIETLANIE TOWARÓW ---
st.header("📋 Lista towarów")

if st.session_state['magazyn']:
    # Wyświetlamy towary jako listę punktowaną
    for i, towar in enumerate(st.session_state['magazyn'], 1):
        st.text(f"{i}. {towar}")
else:
    st.info("Magazyn jest pusty.")

st.markdown("---")

# --- SEKCJA 2: DODAWANIE TOWARU ---
st.header("➕ Dodaj towar")

# Pole tekstowe do wpisania nazwy
nowy_towar = st.text_input("Wpisz nazwę towaru do dodania")

if st.button("Dodaj do magazynu"):
    if nowy_towar:
        st.session_state['magazyn'].append(nowy_towar)
        st.success(f"Dodano: {nowy_towar}")
        # Rerun wymusza odświeżenie strony, aby nowy towar od razu pojawił się na liście
        st.rerun()
    else:
        st.warning("Wpisz nazwę towaru przed dodaniem.")

st.markdown("---")

# --- SEKCJA 3: USUWANIE TOWARU ---
st.header("❌ Usuń towar")

if st.session_state['magazyn']:
    # Selectbox pozwala wybrać towar z istniejącej listy, co eliminuje błędy w pisowni
    towar_do_usuniecia = st.selectbox("Wybierz towar do usunięcia", st.session_state['magazyn'])

    if st.button("Usuń wybrany towar"):
        st.session_state['magazyn'].remove(towar_do_usuniecia)
        st.error(f"Usunięto: {towar_do_usuniecia}")
        st.rerun()
else:
    st.write("Brak towarów do usunięcia.")
