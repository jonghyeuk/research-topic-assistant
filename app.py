import streamlit as st
import os
from PIL import Image
import config

# 페이지 기본 설정 - 한글 타이틀
st.set_page_config(
    page_title="연구 주제 선정 도우미",  # 한글로 변경
    page_icon=config.APP_ICON if os.path.exists(config.APP_ICON) else "📚",
    layout="centered",  # "wide"에서 "centered"로 변경
    initial_sidebar_state="expanded"
)

# 커스텀 CSS 로드
def load_css():
    with open("assets/styles.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

if os.path.exists("assets/styles.css"):
    load_css()

# 세션 상태 초기화
if "step" not in st.session_state:
    st.session_state.step = 1
if "topic" not in st.session_state:
    st.session_state.topic = ""
if "topic_analysis" not in st.session_state:
    st.session_state.topic_analysis = {}
if "similar_topics" not in st.session_state:
    st.session_state.similar_topics = []
if "selected_topic" not in st.session_state:
    st.session_state.selected_topic = ""
if "generated_paper" not in st.session_state:
    st.session_state.generated_paper = {}
if "niche_topics" not in st.session_state:
    st.session_state.niche_topics = []

# 사이드바 - 진행 단계 표시
st.sidebar.title("연구 주제 선정 도우미 AI")
if os.path.exists(config.APP_ICON):
    st.sidebar.image(config.APP_ICON, width=100)
st.sidebar.markdown("---")
st.sidebar.markdown("## 진행 단계")

# 진행 단계 표시 (사이드바에 항상 표시)
for i, (name, _) in enumerate(config.PAGES.items(), 1):
    if i == st.session_state.step:
        st.sidebar.markdown(f"**→ {i}. {name}**")
    else:
        st.sidebar.markdown(f"{i}. {name}")

st.sidebar.markdown("---")
st.sidebar.info("이 앱은 고등학생과 연구자들의 논문 주제 선정을 돕기 위해 개발되었습니다.")

# 메인 콘텐츠 - 제한된 너비의 컨테이너에 표시
st.markdown('<div class="content-container">', unsafe_allow_html=True)

# 메인 페이지 - 소개 및 시작하기
st.markdown('<h1 class="centered-header">연구 주제 선정 도우미 AI</h1>', unsafe_allow_html=True)
st.markdown('<h3 class="centered-header">당신의 연구 주제 선정을 도와드립니다</h3>', unsafe_allow_html=True)

# 설명 텍스트를 중앙 정렬된 섹션에 배치
st.markdown('<div class="text-content">', unsafe_allow_html=True)
st.markdown("""
이 도구는 학생들과 연구자들이 연구 주제를 선정하고 발전시키는 과정을 AI를 통해 도와줍니다.
""")
st.markdown('</div>', unsafe_allow_html=True)

# 기능 목록을 중앙 정렬된 형태로 표시
st.markdown('<div class="centered-section">', unsafe_allow_html=True)
st.markdown('<h4>주요 기능:</h4>', unsafe_allow_html=True)
st.markdown('<ul class="feature-list">', unsafe_allow_html=True)
st.markdown('<li>관심 주제에 대한 상세 분석</li>', unsafe_allow_html=True)
st.markdown('<li>유사 연구 주제 추천</li>', unsafe_allow_html=True)
st.markdown('<li>AI 기반 논문 구조 생성</li>', unsafe_allow_html=True)
st.markdown('<li>PDF 형식의 논문 미리보기</li>', unsafe_allow_html=True)
st.markdown('<li>틈새 연구 주제 제안</li>', unsafe_allow_html=True)
st.markdown('</ul>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# 시작하기 버튼 - 기존 코드 유지하되 스타일은 CSS로 적용됨
if st.button("시작하기", key="start_button", use_container_width=True):
    st.session_state.step = 1
    st.switch_page("pages/1_Topic_Input.py")

# 하단 정보
st.markdown('<div style="margin-top: 40px;"></div>', unsafe_allow_html=True)
st.markdown('<div class="footer-text">© 2023 연구 주제 선정 도우미 AI | GPT 기반 연구 지원 도구</div>', unsafe_allow_html=True)

# 컨테이너 닫기
st.markdown('</div>', unsafe_allow_html=True)
