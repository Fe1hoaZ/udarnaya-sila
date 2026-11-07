import streamlit as st
import streamlit.components.v1 as components
import json
import random
import time
import base64

st.set_page_config(page_title="Ударная Сила", page_icon="🎯")

# Стилизация стандартных кнопок Streamlit (вариантов ответа)
st.markdown("""
    <style>
    div.stButton > button {
        font-size: 1.8rem !important;
        font-weight: bold !important;
        padding: 18px 30px !important;
        border-radius: 14px !important;
        min-height: 70px !important;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    with open('database.json', 'r', encoding='utf-8') as f:
        return json.load(f)

database = load_data()
words_list = list(database.keys())

if 'app_state' not in st.session_state:
    st.session_state.app_state = 'menu'
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

def start_game():
    st.session_state.app_state = 'playing'
    st.session_state.score = 0
    st.session_state.errors = 0
    st.session_state.end_time = time.time() + 60
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

# 1. ЭКРАН МЕНЮ
if st.session_state.app_state == 'menu':
    st.markdown("<h1 style='text-align: center; font-size: 3rem;'>🎯 Тренажер «Ударная Сила»</h1>", unsafe_allow_html=True)
    st.info("Проверь свои знания в режиме **Спринт**! У тебя есть **1 минута**, чтобы выбрать как можно больше слов с правильным ударением.")
    
    if st.button("🔥 НАЧАТЬ ИГРУ", use_container_width=True):
        start_game()
        st.rerun()

# 2. ЭКРАН ИГРОВОГО ПРОЦЕССА
elif st.session_state.app_state == 'playing':
    time_left = int(st.session_state.end_time - time.time())
    
    if time_left <= 0:
        st.session_state.app_state = 'results'
        st.rerun()
        
    st.subheader("⏱️ Спринт: 1 минута")
    
    col1, col2, col3 = st.columns(3)
    col1.write(f"**⏳ Осталось:** {time_left} сек")
    col2.write(f"**✅ Верно:** {st.session_state.score}")
    col3.write(f"**❌ Ошибок:** {st.session_state.errors}")
    
    st.divider()
    
    current_word = st.session_state.current_word
    word_data = database[current_word]
    
    audio_path = f"audio/{current_word}.wav"
    try:
        with open(audio_path, "rb") as f:
            audio_b64 = base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        audio_b64 = ""

    # Увеличенная верстка слова и динамика
    html_code = f"""
    <html>
        <head>
            <style>
                body {{
                    margin: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    font-family: "Source Sans Pro", sans-serif;
                    color: #31333F;
                }}
                @media (prefers-color-scheme: dark) {{
                    body {{ color: #FAFAFA; }}
                }}
                .word-container {{
                    display: flex;
                    align-items: center;
                    gap: 20px;
                }}
                h1 {{
                    margin: 0;
                    font-size: 4.2rem;
                    font-weight: 800;
                    letter-spacing: 1px;
                }}
                .play-btn {{
                    background: #4285F4;
                    border: none;
                    border-radius: 50%;
                    width: 60px;
                    height: 60px;
                    cursor: pointer;
                    color: white;
                    font-size: 1.6rem;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    box-shadow: 0 3px 8px rgba(0,0,0,0.25);
                    transition: transform 0.1s, background 0.2s;
                }}
                .play-btn:hover {{ background: #3367D6; }}
                .play-btn:active {{ transform: scale(0.92); }}
            </style>
        </head>
        <body>
            <div class="word-container">
                <button class="play-btn" onclick="document.getElementById('audio-player').play()" title="Озвучить">
                    🔊
                </button>
                <h1>{current_word}</h1>
                <audio id="audio-player" src="data:audio/wav;base64,{audio_b64}"></audio>
            </div>
        </body>
    </html>
    """
    
    components.html(html_code, height=110)
    
    options = [
        (word_data["correct"], True),
        (word_data["wrong"], False)
    ]
    random.shuffle(options)
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button(options[0][0], use_container_width=True):
            check_answer(options[0][1], word_data)
            st.rerun()
    with col_btn2:
        if st.button(options[1][0], use_container_width=True):
            check_answer(options[1][1], word_data)
            st.rerun()
            
    if st.session_state.feedback:
        st.markdown(f"<h3 style='text-align: center;'>{st.session_state.feedback}</h3>", unsafe_allow_html=True)

# 3. ЭКРАН РЕЗУЛЬТАТОВ
elif st.session_state.app_state == 'results':
    st.markdown("<h1 style='text-align: center;'>🏆 Время вышло!</h1>", unsafe_allow_html=True)
    st.divider()
    
    st.success(f"🎯 Правильных ответов: **{st.session_state.score}**")
    st.error(f"⚠️ Ошибок: **{st.session_state.errors}**")
    
    total = st.session_state.score + st.session_state.errors
    if total > 0:
        accuracy = int((st.session_state.score / total) * 100)
        st.info(f"📊 Твоя точность: **{accuracy}%**")
    
    st.divider()
    if st.button("🔄 Сыграть еще раз", use_container_width=True):
        st.session_state.app_state = 'menu'
        st.rerun()
