import streamlit as st  
import pandas as pd  
import matplotlib.pyplot as plt  
import sqlite3  
from datetime import datetime  
  
# 1. 데이터베이스 설정 (영구 저장)  
def init_db():  
    conn = sqlite3.connect('church_feedback.db')  
    c = conn.cursor()  
    c.execute('''CREATE TABLE IF NOT EXISTS feedback   
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,   
                  date TEXT,   
                  category TEXT,   
                  content TEXT)''')  
    conn.commit()  
    conn.close()  
  
def save_feedback(category, content):  
    conn = sqlite3.connect('church_feedback.db')  
    c = conn.cursor()  
    now = datetime.now().strftime('%Y-%m-%d')  
    c.execute("INSERT INTO feedback (date, category, content) VALUES (?, ?, ?)", (now, category, content))  
    conn.commit()  
    conn.close()  
  
def get_data():  
    conn = sqlite3.connect('church_feedback.db')  
    df = pd.read_sql_query("SELECT * FROM feedback", conn)  
    conn.close()  
    return df  
  
# 데이터베이스 초기화  
init_db()  
  
# 2. 화면 디자인 (베이지 톤) - 에러 방지를 위해 수정한 버전  
st.set_page_config(page_title="청소년부 소통창구", layout="centered")  
st.write(  
    """  
    <style>  
    .stApp {  
        background-color: #F5F5DC;  
    }  
    div.stButton > button {  
        background-color: #D2B48C !important;  
        color: white !important;  
    }  
    </style>  
    """,  
    unsafe_allow_html=True  
)  
  
# 카테고리 설정  
categories = ["신앙 상담", "친목/활동 아이디어", "간식/식사 건의", "기타 의견"]  
  
st.title("⛪ 청소년부 마음 나눔터")  
st.write("여러분의 이야기를 들려주세요. 작성된 내용은 익명으로 소중히 전달됩니다.")  
  
tab1, tab2 = st.tabs(["📝 의견 보내기", "📊 월별 통계 보기"])  
  
with tab1:  
    st.subheader("익명 메시지 작성")  
    selected_cat = st.selectbox("카테고리를 선택해 주세요", categories)  
    user_opinion = st.text_area("무엇이든 자유롭게 적어주세요.", placeholder="여기에 작성하세요...")  
      
    if st.button("전송하기"):  
        if user_opinion.strip():  
            save_feedback(selected_cat, user_opinion)  
            st.success("소중한 의견이 저장되었습니다!")  
        else:  
            st.warning("내용을 입력해 주세요.")  
  
with tab2:  
    st.subheader("월별 의견 수집 현황")  
    df = get_data()  
      
    if not df.empty:  
        df['date'] = pd.to_datetime(df['date'])  
        df['year_month'] = df['date'].dt.to_period('M').astype(str)  
        available_months = sorted(df['year_month'].unique(), reverse=True)  
        selected_month = st.selectbox("조회할 달을 선택하세요", available_months)  
        filtered_df = df[df['year_month'] == selected_month]  
        counts = filtered_df["category"].value_counts()  
          
        col1, col2 = st.columns([1, 1])  
        with col1:  
            st.write(f"### {selected_month} 통계")  
            fig, ax = plt.subplots(facecolor='#F5F5DC')  
            ax.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=90,   
                   colors=['#D2B48C', '#E6CCBE', '#C19A6B', '#A67B5B'])  
            ax.axis('equal')  
            st.pyplot(fig)  
              
        with col2:  
            st.write("### 질문 개수")  
            for cat, count in counts.items():  
                st.write(f"- **{cat}**: {count}개")  
          
        st.write("---")  
        st.write(f"🔍 **{selected_month} 상세 의견 목록**")  
        st.dataframe(filtered_df[['date', 'category', 'content']], use_container_width=True)  
    else:  
        st.info("아직 수집된 데이터가 없습니다.")  
