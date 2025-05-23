import os
from dotenv import load_dotenv
import streamlit as st

# 환경 변수 로드 (로컬 개발용)
load_dotenv()

# 필수 API 키
try:
    # Streamlit Cloud에서 실행 중인 경우
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
    CROSSREF_EMAIL = st.secrets["CROSSREF_EMAIL"]
except (KeyError, TypeError):
    # 로컬에서 실행 중인 경우
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    CROSSREF_EMAIL = os.getenv("CROSSREF_EMAIL", "")
    
    if not OPENAI_API_KEY:
        print("Warning: OPENAI_API_KEY not found")

# GPT 설정
GPT_MODEL = "gpt-4-turbo" # 또는 "gpt-3.5-turbo" (비용 절감)
MAX_TOKENS = 4000
TEMPERATURE = 0.7

# 앱 설정
APP_TITLE = "연구 주제 선정 도우미 AI"
APP_ICON = "assets/logo.png"
ISEF_DATA_PATH = "data/isef_data.xlsx"

# 검색 설정
MAX_SIMILAR_TOPICS = 10
MAX_ARXIV_RESULTS = 5
MAX_CROSSREF_RESULTS = 5

# 페이지 경로
PAGES = {
    "주제 입력": "1_Topic_Input",
    "유사 주제": "2_Similar_Topics",
    "논문 생성": "3_Paper_Generation",
    "PDF 보기": "4_PDF_View",
    "틈새 주제": "5_Niche_Topics",
}
