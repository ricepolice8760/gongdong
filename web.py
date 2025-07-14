import streamlit as st
import sqlite3
import matplotlib.pyplot as plt
import pandas as pd

# 📌 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'  # Windows 전용
plt.rcParams['axes.unicode_minus'] = False

# 📦 데이터베이스 연결
conn = sqlite3.connect('movies.db')
c = conn.cursor()

# 🎯 테이블 생성 (후기 포함)
c.execute('''
CREATE TABLE IF NOT EXISTS movie_prefs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    genre TEXT,
    preference INTEGER,
    review TEXT
)
''')
conn.commit()

# 🧾 앱 제목
st.title("🎬 영화 선호도 및 후기 기록 웹앱")

# 📥 영화 등록 폼
with st.form("movie_form"):
    title = st.text_input("영화 제목")
    genre = st.selectbox("장르", ["액션", "로맨스", "코미디", "스릴러", "SF", "드라마"])
    preference = st.slider("선호도 (1~5)", 1, 5, 3)
    review = st.text_area("한 줄 후기")
    submitted = st.form_submit_button("등록")

    if submitted and title:
        c.execute("INSERT INTO movie_prefs (title, genre, preference, review) VALUES (?, ?, ?, ?)",
                  (title, genre, preference, review))
        conn.commit()
        st.success(f"✅ '{title}' 등록 완료!")

# 🔍 검색 및 필터
st.subheader("🔎 영화 검색 및 정렬")
search_term = st.text_input("영화 제목으로 검색")
sort_order = st.radio("정렬 방식", ["입력 순", "선호도 높은 순", "선호도 낮은 순"], horizontal=True)

# 장르 필터
c.execute("SELECT DISTINCT genre FROM movie_prefs")
genre_list = [g[0] for g in c.fetchall()]
selected_genre = st.selectbox("장르 필터", ["전체 보기"] + genre_list)

# 📋 전체 데이터 불러오기
c.execute("SELECT id, title, genre, preference, review FROM movie_prefs")
rows = c.fetchall()

# 🔎 검색 및 필터링 처리
filtered_rows = []
for row in rows:
    if search_term.lower() in row[1].lower():
        if selected_genre == "전체 보기" or row[2] == selected_genre:
            filtered_rows.append(row)

# 🔃 정렬
if sort_order == "선호도 높은 순":
    filtered_rows.sort(key=lambda x: x[3], reverse=True)
elif sort_order == "선호도 낮은 순":
    filtered_rows.sort(key=lambda x: x[3])

# 📋 영화 출력 및 삭제
st.subheader("🎞️ 영화 목록")
if filtered_rows:
    for row in filtered_rows:
        st.markdown(f"**제목:** {row[1]} | **장르:** {row[2]} | **선호도:** {row[3]}점")
        st.markdown(f"📝 후기: {row[4]}")
        if st.button(f"❌ 삭제: {row[1]}", key=row[0]):
            c.execute("DELETE FROM movie_prefs WHERE id = ?", (row[0],))
            conn.commit()
            st.success(f"'{row[1]}' 삭제 완료!")
            st.rerun() # 변경된 부분
else:
    st.info("조건에 맞는 영화가 없습니다.")

# 📊 통계 요약
st.subheader("📈 선호도 통계 요약")
if rows:
    scores = [r[3] for r in rows]
    st.write(f"🔹 평균 선호도: {sum(scores)/len(scores):.2f}")
    st.write(f"🔹 최고 선호도: {max(scores)}")
    st.write(f"🔹 최저 선호도: {min(scores)}")

# 📊 시각화
st.subheader("📊 장르별 평균 선호도 시각화")
c.execute("SELECT genre, AVG(preference) FROM movie_prefs GROUP BY genre")
genre_data = c.fetchall()

if genre_data:
    genres = [g[0] for g in genre_data]
    values = [g[1] for g in genre_data]

    fig, ax = plt.subplots()
    ax.bar(genres, values, color='salmon')
    ax.set_ylabel("평균 선호도")
    ax.set_title("장르별 평균 선호도")
    st.pyplot(fig)

# 종료
conn.close()