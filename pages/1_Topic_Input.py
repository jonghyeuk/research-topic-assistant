import streamlit as st
from utils.gpt_utils import analyze_topic
import time

# 콘텐츠 컨테이너로 감싸기
st.markdown('<div class="content-container">', unsafe_allow_html=True)

# 페이지 제목
st.title("주제 입력")

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
    
    submit_col1, submit_col2, submit_col3 = st.columns([1, 2, 1])
    with submit_col2:
        submit_button = st.form_submit_button("분석 시작하기", use_container_width=True)

if submit_button and topic:
    # 입력 값 세션 상태에 저장
    st.session_state.topic = topic
    
    # 타이핑 효과를 위한 컨테이너
    analysis_container = st.empty()
    
    # 분석 시작 메시지
    analysis_container.markdown('<div class="analysis-loading">AI가 주제를 분석하고 있습니다...</div>', unsafe_allow_html=True)
    
    # GPT API를 통한 주제 분석
    analysis_result = analyze_topic(topic)
    
    if analysis_result:
        # 분석 결과 저장
        st.session_state.topic_analysis = analysis_result
        
        # 타이핑 효과 구현 (개선된 버전)
        full_text = analysis_result["full_text"]
        displayed_text = ""
        
        # 컨테이너 준비
        analysis_container.markdown('<div class="analysis-result-title">주제 분석 결과</div>', unsafe_allow_html=True)
        text_container = analysis_container.empty()
        
        # 최대 2000자까지만 애니메이션 적용 (성능 최적화)
        max_length = min(len(full_text), 2000)
        
        for i in range(max_length + 1):
            displayed_text = full_text[:i]
            text_container.markdown(
                f'<div class="analysis-result-content">{displayed_text}</div>', 
                unsafe_allow_html=True
            )
            time.sleep(0.005)  # 더 빠른 속도로 조정
        
        # 나머지 텍스트 표시
        if len(full_text) > max_length:
            text_container.markdown(
                f'<div class="analysis-result-content">{full_text}</div>', 
                unsafe_allow_html=True
            )
        
        # 다음 단계로 이동 버튼
        st.session_state.step = 2
        
        # 버튼 가운데 정렬
        btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])
        with btn_col2:
            if st.button("유사 주제 찾기 →", use_container_width=True):
                st.switch_page("pages/2_Similar_Topics.py")
    else:
        st.error("주제 분석 중 오류가 발생했습니다. 다시 시도해 주세요.")

# 세션에 분석 결과가 있으면 표시
elif "topic_analysis" in st.session_state and st.session_state.topic_analysis:
    st.markdown('<div class="analysis-result-title">주제 분석 결과</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="analysis-result-content">{st.session_state.topic_analysis["full_text"]}</div>',
        unsafe_allow_html=True
    )
    
    # 다음 단계로 이동 버튼
    st.session_state.step = 2
    
    # 버튼 가운데 정렬
    btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])
    with btn_col2:
        if st.button("유사 주제 찾기 →", use_container_width=True):
            st.switch_page("pages/2_Similar_Topics.py")

# 컨테이너 닫기
st.markdown('</div>', unsafe_allow_html=True)
