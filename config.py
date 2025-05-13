import os
from dotenv import load_dotenv
import streamlit as st

# 환경 변수 로드 (로컬 개발용)
load_dotenv()

# API 키 (Streamlit Cloud 또는 환경 변수에서 가져오기)
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", ""))
CROSSREF_EMAIL = st.secrets.get("CROSSREF_EMAIL", os.getenv("CROSSREF_EMAIL", ""))
HUGGINGFACE_API_KEY = st.secrets.get("HUGGINGFACE_API_KEY", os.getenv("HUGGINGFACE_API_KEY", ""))
EXTRACTURL_API_KEY = st.secrets.get("EXTRACTURL_API_KEY", os.getenv("EXTRACTURL_API_KEY", ""))
WEBSEARCHRANKED_API_KEY = st.secrets.get("WEBSEARCHRANKED_API_KEY", os.getenv("WEBSEARCHRANKED_API_KEY", ""))

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
