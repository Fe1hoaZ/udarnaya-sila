import streamlit as st
import json
import random
import time

# --- Настройка страницы ---
st.set_page_config(page_title="Ударная Сила", page_icon="🎯")

# --- Загрузка базы данных ---
@st.cache_data
def load_data():
    with open('database.json', 'r', encoding='utf-8') as f:
        return json.load(f)

database = load_data()
words_list = list(database.keys())

# --- Инициализация экранов и переменных ---
if 'app_state' not in st.session_state:
    st.session_state.app_state = 'menu' # Экраны: 'menu', 'playing', 'results'
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'errors' not in st.session_state:
    st.session_state.errors = 0
if 'end_time' not in st.session_state:
    st.session_state.end_time = 0
if 'current_word' not in st.session_state:
    st.session_state.current_word = random.choice(words_list)
if 'feedback' not in st.session_state:
    st.session_state.feedback = ""

# --- Логика игры ---
def start_game():
    st.session_state.app_state = 'playing'
    st.session_state.score = 0
    st.session_state.errors = 0
    st.session_state.end_time = time.time() + 60 # Ровно 60 секунд от текущего момента
    st.session_state.current_word = random.choice(words_list)
    st.session_state.feedback = ""

def check_answer(is_correct, word_data):
    if is_correct:
        st.session_state.score += 1
        st.session_state.feedback = f"✅ Верно: {word_data['correct']}"
    else:
        st.session_state.errors += 1
        st.session_state.feedback = f"❌ Ошибка! Нужно: {word_data['correct']}"
    
    st.session_state.current_word = random.choice(words_list)

# ==========================================
# ОТОБРАЖЕНИЕ ЭКРАНОВ
# ==========================================

# 1. ЭКРАН МЕНЮ
if st.session_state.app_state == 'menu':
    st.markdown("<h1 style='text-align: center;'>🎯 Тренажер «Ударная Сила»</h1>", unsafe_allow_html=True)
    st.info("Проверь свои знания в режиме **Спринт**! У тебя есть **1 минута**, чтобы выбрать как можно больше слов с правильным ударением.")
    
    # Большая кнопка старта
    if st.button("🔥 НАЧАТЬ ИГРУ", use_container_width=True):
        start_game()
        st.rerun()

# 2. ЭКРАН ИГРОВОГО ПРОЦЕССА
elif st.session_state.app_state == 'playing':
    # Считаем, сколько времени осталось
    time_left = int(st.session_state.end_time - time.time())
    
    # Если время вышло — перекидываем на экран результатов
    if time_left <= 0:
        st.session_state.app_state = 'results'
        st.rerun()
        
    st.subheader("⏱️ Спринт: 1 минута")
    
    # Панель статистики наверху
    col1, col2, col3 = st.columns(3)
    col1.write(f"**⏳ Осталось:** {time_left} сек")
    col2.write(f"**✅ Верно:** {st.session_state.score}")
    col3.write(f"**❌ Ошибок:** {st.session_state.errors}")
    
    st.divider()
    
    # Получаем данные текущего слова
    current_word = st.session_state.current_word
    word_data = database[current_word]
    
    # Показываем слово (крупно)
    st.markdown(f"<h1 style='text-align: center;'>{current_word}</h1>", unsafe_allow_html=True)
    
    # Перемешиваем варианты
    options = [
        (word_data["correct"], True),
        (word_data["wrong"], False)
    ]
    random.shuffle(options)
    
    # Кнопки ответов
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button(options[0][0], use_container_width=True):
            check_answer(options[0][1], word_data)
            st.rerun()
    with col_btn2:
        if st.button(options[1][0], use_container_width=True):
            check_answer(options[1][1], word_data)
            st.rerun()
            
    # Показываем результат предыдущего клика
    if st.session_state.feedback:
        st.caption(st.session_state.feedback)

# 3. ЭКРАН РЕЗУЛЬТАТОВ
elif st.session_state.app_state == 'results':
    st.markdown("<h1 style='text-align: center;'>🏆 Время вышло!</h1>", unsafe_allow_html=True)
    st.divider()
    
    st.success(f"🎯 Правильных ответов: **{st.session_state.score}**")
    st.error(f"⚠️ Ошибок: **{st.session_state.errors}**")
    
    # Считаем процент правильных ответов
    total = st.session_state.score + st.session_state.errors
    if total > 0:
        accuracy = int((st.session_state.score / total) * 100)
        st.info(f"📊 Твоя точность: **{accuracy}%**")
    
    st.divider()
    if st.button("🔄 Сыграть еще раз", use_container_width=True):
        st.session_state.app_state = 'menu'
        st.rerun()
