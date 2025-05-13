import streamlit as st
from utils.gpt_utils import analyze_topic
import time

# 페이지 제목
st.title("1. 연구 주제 입력")

# 설명
st.markdown("""
연구하고 싶은 주제나 관심 있는 연구 테마를 입력해주세요.
AI가 해당 주제에 대한 상세 정보와 관련 이슈를 분석해 드립니다.
""")

# 주제 입력 폼
with st.form("topic_input_form"):
    topic = st.text_input("연구 주제 또는 관심 테마", 
                          placeholder="예: 미세 플라스틱이 해양 생태계에 미치는 영향",
                          value=st.session_state.topic if "topic" in st.session_state else "")
    
    submit_button = st.form_submit_button("분석 시작하기")

if submit_button and topic:
    # 입력 값 세션 상태에 저장
    st.session_state.topic = topic
    
    # 타이핑 효과를 위한 컨테이너
    analysis_container = st.empty()
    
    # 분석 시작 메시지
    analysis_container.markdown("AI가 주제를 분석하고 있습니다...")
    
    # GPT API를 통한 주제 분석
    analysis_result = analyze_topic(topic)
    
    if analysis_result:
        # 분석 결과 저장
        st.session_state.topic_analysis = analysis_result
        
        # 타이핑 효과 구현 (간단한 버전)
        full_text = analysis_result["full_text"]
        displayed_text = ""
        
        # 실제 서비스에서는 WebSocket으로 스트리밍 구현
        # 여기서는 간단한 타이핑 효과 시뮬레이션
        analysis_container.markdown("## 주제 분석 결과")
        text_container = analysis_container.empty()
        
        for i in range(len(full_text) + 1):
            displayed_text = full_text[:i]
            text_container.markdown(displayed_text)
            time.sleep(0.01)  # 프로덕션에서는 더 자연스러운 속도로 조정
        
        # 다음 단계로 이동 버튼
        st.session_state.step = 2
        if st.button("유사 주제 찾기 →"):
            st.switch_page("pages/2_Similar_Topics.py")
    else:
        st.error("주제 분석 중 오류가 발생했습니다. 다시 시도해 주세요.")

# 세션에 분석 결과가 있으면 표시
elif "topic_analysis" in st.session_state and st.session_state.topic_analysis:
    st.markdown("## 주제 분석 결과")
    st.markdown(st.session_state.topic_analysis["full_text"])
    
    # 다음 단계로 이동 버튼
    st.session_state.step = 2
    if st.button("유사 주제 찾기 →"):
        st.switch_page("pages/2_Similar_Topics.py")
