import streamlit as st
import json
import random

# --- Настройка страницы ---
st.set_page_config(page_title="Ударная Сила", page_icon="🎯")

# --- Загрузка базы данных ---
@st.cache_data
def load_data():
    with open('database.json', 'r', encoding='utf-8') as f:
        return json.load(f)

database = load_data()
words_list = list(database.keys())

# --- Инициализация переменных сессии ---
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'current_word' not in st.session_state:
    st.session_state.current_word = random.choice(words_list)
if 'feedback' not in st.session_state:
    st.session_state.feedback = ""

# --- Логика игры ---
def check_answer(is_correct, word_data):
    if is_correct:
        st.session_state.score += 1
        st.session_state.feedback = "✅ Правильно! +1 балл."
    else:
        # ОБНУЛЯЕМ СЧЕТЧИК ЗДЕСЬ
        st.session_state.score = 0 
        st.session_state.feedback = f"❌ Ошибка! Очки сгорели 😭\n\nПравильно: **{word_data['correct']}**.\n\n💡 *Подсказка: {word_data['rule']}*"
    
    # Сразу выбираем новое слово для следующего раунда
    st.session_state.current_word = random.choice(words_list)

# --- Интерфейс (UI) ---
st.title("🎯 Тренажер «Ударная Сила»")
st.write(f"**Твои очки:** {st.session_state.score}")

st.divider()

# Получаем данные текущего слова
current_word = st.session_state.current_word
word_data = database[current_word]

# Показываем слово (крупно)
st.markdown(f"<h1 style='text-align: center;'>{current_word}</h1>", unsafe_allow_html=True)

# Перемешиваем варианты ответов (чтобы правильный не всегда был слева)
options = [
    (word_data["correct"], True),
    (word_data["wrong"], False)
]
random.shuffle(options)

# Создаем две кнопки рядом
col1, col2 = st.columns(2)

with col1:
    if st.button(options[0][0], use_container_width=True):
        check_answer(options[0][1], word_data)
        st.rerun() # Обновляем страницу

with col2:
    if st.button(options[1][0], use_container_width=True):
        check_answer(options[1][1], word_data)
        st.rerun() # Обновляем страницу

st.divider()

# Вывод результата (если он есть)
if st.session_state.feedback:
    if "✅" in st.session_state.feedback:
        st.success(st.session_state.feedback)
    else:
        st.error(st.session_state.feedback)