import streamlit as st
import time
from utils.gpt_utils import generate_niche_topics

# 페이지 제목
st.title("5. 틈새 연구 주제 제안")

# 생성된 논문이 없으면 이전 페이지로 리다이렉트
if "generated_paper" not in st.session_state or not st.session_state.generated_paper:
    st.warning("먼저 논문을 생성해주세요.")
    st.button("논문 생성으로 돌아가기", on_click=lambda: st.switch_page("pages/3_Paper_Generation.py"))
else:
    # 선택된 주제 표시
    st.markdown(f"### 기반 주제: {st.session_state.selected_topic}")
    
    # 틈새 주제 생성 시작
    if "niche_topics" not in st.session_state or not st.session_state.niche_topics:
        # 생성 중 메시지
        niche_container = st.empty()
        niche_container.info("AI가 관련 틈새 연구 주제를 생성하고 있습니다...")
        
        # 틈새 주제 생성
        niche_topics_content = generate_niche_topics(st.session_state.selected_topic)
        
        if niche_topics_content:
            # 틈새 주제 저장
            st.session_state.niche_topics = niche_topics_content
            
            # 타이핑 효과 구현 (간단한 버전)
            niche_container.empty()
            typing_container = st.empty()
            
            full_text = niche_topics_content
            displayed_text = ""
            
            # 실제 서비스에서는 WebSocket으로 스트리밍 구현
            # 여기서는 간단한 타이핑 효과 시뮬레이션
            for i in range(len(full_text) + 1):
                displayed_text = full_text[:i]
                typing_container.markdown(displayed_text)
                time.sleep(0.01)  # 프로덕션에서는 더 자연스러운 속도로 조정
        else:
            niche_container.error("틈새 주제 생성 중 오류가 발생했습니다. 다시 시도해 주세요.")
    
    # 이미 생성된 틈새 주제가 있으면 표시
    else:
        st.markdown(st.session_state.niche_topics)
    
    # 새로운 틈새 주제 연구 시작 버튼 (실제 구현 시 파싱 및 처리 필요)
    st.markdown("### 새로운 틈새 주제로 연구 시작하기")
    
    # 임의의 틈새 주제 리스트 (실제 구현 시 파싱 필요)
    # 간단화를 위해 임의의 주제 사용
    niche_topics_list = [
        "틈새 주제 1: 환경 변화에 따른 적응 메커니즘",
        "틈새 주제 2: 지속 가능한 에너지 저장 기술",
        "틈새 주제 3: 인공지능 기반 생태계 모니터링",
        "틈새 주제 4: 미세플라스틱 분해 미생물 연구"
    ]
    
    # 각 틈새 주제에 대한 버튼
    for i, topic in enumerate(niche_topics_list, 1):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"**{topic}**")
        with col2:
            if st.button("선택", key=f"niche_{i}"):
                # 새 주제로 처음부터 시작 (세션 초기화)
                st.session_state.topic = topic.split(": ")[1]
                st.session_state.pop("topic_analysis", None)
                st.session_state.pop("similar_topics", None)
                st.session_state.pop("selected_topic", None)
                st.session_state.pop("generated_paper", None)
                st.session_state.pop("niche_topics", None)
                st.session_state.step = 1
                st.switch_page("pages/1_Topic_Input.py")
    
    # 처음으로 돌아가기 버튼
    if st.button("처음으로 돌아가기"):
        # 세션 초기화
        for key in list(st.session_state.keys()):
            if key != "step":
                st.session_state.pop(key, None)
        st.session_state.step = 1
        st.switch_page("pages/1_Topic_Input.py")
    
    # 이전 단계로 돌아가기
    if st.button("PDF 보기로 돌아가기"):
        st.session_state.step = 4
        st.switch_page("pages/4_PDF_View.py")

/* 전체 앱 스타일 */
.stApp {
    font-family: 'Roboto', 'Noto Sans KR', sans-serif;
}

/* 사이드바 스타일 */
.sidebar .sidebar-content {
    background-color: #f8f9fa;
}

/* 타이핑 효과 애니메이션 */
@keyframes typing {
    from { width: 0 }
    to { width: 100% }
}

.typing-effect {
    overflow: hidden;
    border-right: .15em solid #4CAF50;
    white-space: nowrap;
    margin: 0 auto;
    animation: 
        typing 3.5s steps(40, end),
        blink-caret .75s step-end infinite;
}

/* 논문 스타일 - A4 형식 */
.paper-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 40px;
    background-color: white;
    box-shadow: 0 0 10px rgba(0,0,0,0.1);
}

.paper-title {
    font-size: 24px;
    font-weight: bold;
    text-align: center;
    margin-bottom: 20px;
}

.paper-authors {
    font-size: 16px;
    font-style: italic;
    text-align: center;
    margin-bottom: 30px;
}

.paper-section-title {
    font-size: 18px;
    font-weight: bold;
    margin-top: 25px;
    margin-bottom: 10px;
}

.paper-content {
    font-size: 14px;
    line-height: 1.6;
    text-align: justify;
}

/* 버튼 스타일 */
.stButton > button {
    border-radius: 20px;
    padding: 10px 24px;
    background-color: #4CAF50;
    color: white;
}

.stButton > button:hover {
    background-color: #45a049;
}

/* 진행 단계 표시 */
.step-progress {
    margin-bottom: 20px;
}

.step-item {
    padding: 8px;
    border-radius: 5px;
}

.step-active {
    background-color: #e6f7e6;
    border-left: 3px solid #4CAF50;
    font-weight: bold;
}
