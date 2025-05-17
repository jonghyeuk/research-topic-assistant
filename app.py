import streamlit as st
import os
from PIL import Image
import config

# 상단 빈 박스 제거 (파일 상단에 추가)
st.markdown("""
<style>
    [data-testid="stHeader"] {display: none;}
    .main > div:first-child {visibility: hidden; height: 0; margin: 0; padding: 0;}
</style>
""", unsafe_allow_html=True)

# 페이지 기본 설정
st.set_page_config(
    page_title="연구 주제 선정 도우미",
    page_icon=config.APP_ICON if os.path.exists(config.APP_ICON) else "📚",
    layout="centered",
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

# 사이드바 - 진행 단계 표시 (시각적으로 개선)
st.sidebar.title("연구 주제 선정 도우미")
if os.path.exists(config.APP_ICON):
    st.sidebar.image(config.APP_ICON, width=80)
st.sidebar.markdown("---")

# 진행 단계 표시 (사이드바에 항상 표시) - 시각적으로 개선
st.sidebar.markdown('<div class="step-progress-sidebar">', unsafe_allow_html=True)
for i, (name, _) in enumerate(config.PAGES.items(), 1):
    if i == st.session_state.step:
        st.sidebar.markdown(f'<div class="step-item-sidebar active"><span class="step-number">{i}</span><span class="step-label">{name}</span></div>', unsafe_allow_html=True)
    else:
        st.sidebar.markdown(f'<div class="step-item-sidebar"><span class="step-number">{i}</span><span class="step-label">{name}</span></div>', unsafe_allow_html=True)
st.sidebar.markdown('</div>', unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.info("이 앱은 고등학생과 연구자들의 논문 주제 선정을 돕기 위해 개발되었습니다.")

# 메인 콘텐츠 - 제한된 너비의 컨테이너에 표시
st.markdown('<div class="content-container">', unsafe_allow_html=True)

# 메인 페이지 - 소개 및 시작하기 (헤더 개선)
st.markdown('<h1 class="main-title">논문 연구를 위한<br>AI 파트너</h1>', unsafe_allow_html=True)
st.markdown('<p class="main-subtitle">최신 AI 기술로 연구 주제 선정부터 논문 구조화까지</p>', unsafe_allow_html=True)

# 설명 텍스트를 중앙 정렬된 섹션에 배치
st.markdown('<div class="intro-text">', unsafe_allow_html=True)
st.markdown("""
이 도구는 학생들과 연구자들이 연구 주제를 선정하고 발전시키는 과정을 AI를 통해 도와줍니다.
인공지능이 학술 데이터베이스를 검색하고 분석하여 체계적인 연구를 지원합니다.
""")
st.markdown('</div>', unsafe_allow_html=True)

# 기능 목록을 카드 형태로 표시
st.markdown('<div class="features-container">', unsafe_allow_html=True)

features = [
    {"icon": "🔍", "title": "주제 분석", "desc": "관심 주제에 대한 상세 분석을 제공합니다"},
    {"icon": "🔄", "title": "유사 주제 추천", "desc": "관련된 연구 방향을 제안합니다"},
    {"icon": "📝", "title": "논문 구조 생성", "desc": "AI 기반 논문 구조를 자동으로 생성합니다"},
    {"icon": "📄", "title": "PDF 미리보기", "desc": "완성된 논문을 PDF 형식으로 확인합니다"},
    {"icon": "💡", "title": "틈새 주제 제안", "desc": "미개척 연구 영역을 발견합니다"}
]

for feature in features:
    st.markdown(f"""
    <div class="feature-card">
        <div class="feature-icon">{feature['icon']}</div>
        <div class="feature-content">
            <div class="feature-title">{feature['title']}</div>
            <div class="feature-desc">{feature['desc']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# 시작하기 버튼 - 중앙 정렬 및 크게 표시
st.markdown('<div class="start-button-container">', unsafe_allow_html=True)
if st.button("연구 시작하기", key="start_button", use_container_width=True):
    st.session_state.step = 1
    st.switch_page("pages/1_Topic_Input.py")
st.markdown('</div>', unsafe_allow_html=True)

# 하단 정보
st.markdown('<div class="footer-text">© 2023 연구 주제 선정 도우미 AI | GPT 기반 연구 지원 도구</div>', unsafe_allow_html=True)

# 컨테이너 닫기
st.markdown('</div>', unsafe_allow_html=True)
