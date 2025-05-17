import streamlit as st
from utils.gpt_utils import analyze_topic
import time
import re

# 섹션 제목과 내용을 포맷팅하는 함수
def format_text_with_section_titles(text):
    # 이미 HTML 태그가 있는지 확인
    if '<div class="section-title">' in text:
        return text  # 이미 포맷팅된 경우 그대로 반환
        
    # 제목 패턴 찾기 (## 이모지 제목 형식)
    # 이모지 문자와 함께 사용되는 마크다운 제목을 찾는 패턴
    pattern = r'(##\s+(?:🧬|🧩|📚|📊|🔍|✨|📝|🔬|💡|🌐|📑|🧪)?\s*.*?)(?=\n|$)'
    
    # 섹션별로 텍스트 분할
    sections = re.split(pattern, text)
    
    # 빈 문자열 제거
    sections = [s for s in sections if s.strip()]
    
    formatted_parts = []
    
    for i in range(0, len(sections)):
        section = sections[i].strip()
        
        if section.startswith('##'):
            # 제목 처리
            title_text = section.replace('##', '').strip()
            formatted_parts.append(f'<div class="section-title">{title_text}</div>')
        else:
            # 내용 처리
            # 여러 단락으로 나누기
            paragraphs = section.split('\n\n')
            for p in paragraphs:
                if p.strip():
                    formatted_parts.append(f'<div class="section-content">{p.strip()}</div>')
            
            # 섹션 구분선 추가 (마지막 섹션이 아닌 경우)
            if i < len(sections) - 1:
                formatted_parts.append('<div class="section-divider"></div>')
    
    return '\n'.join(formatted_parts)

# 타이핑 효과 함수
def typing_effect(container, text, speed=0.01, chunk_size=3):
    full_text = text
    displayed_text = ""
    
    # 한번에 표시할 문자 수와 지연 시간 설정
    for i in range(0, len(full_text), chunk_size):
        displayed_text = full_text[:i + chunk_size]
        container.markdown(displayed_text, unsafe_allow_html=True)
        time.sleep(speed)

# 단계별 분석 상태 메시지 표시 함수
def show_analysis_step(container, step_message, delay=0.6):
    container.markdown(f'<div class="analysis-step-message">{step_message}</div>', unsafe_allow_html=True)
    time.sleep(delay)

# 콘텐츠 컨테이너로 감싸기
st.markdown('<div class="content-container">', unsafe_allow_html=True)

# 페이지 제목
st.markdown('<h1 class="page-title">주제 입력</h1>', unsafe_allow_html=True)

# 설명
st.markdown("""
연구하고 싶은 주제나 관심 있는 연구 테마를 입력해주세요.
AI가 해당 주제에 대한 상세 정보와 관련 이슈를 분석해 드립니다.
""")

# 주제 입력 폼 - 스타일 개선
st.markdown('<div class="input-form-container">', unsafe_allow_html=True)
with st.form("topic_input_form"):
    topic = st.text_input("연구 주제 또는 관심 테마", 
                          placeholder="예: 미세 플라스틱이 해양 생태계에 미치는 영향",
                          value=st.session_state.topic if "topic" in st.session_state else "")
    
    submit_col1, submit_col2, submit_col3 = st.columns([1, 2, 1])
    with submit_col2:
        submit_button = st.form_submit_button("분석 시작하기", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

if submit_button and topic:
    # 입력 값 세션 상태에 저장
    st.session_state.topic = topic
    
    # 분석 상태 컨테이너
    analysis_status = st.empty()
    
    # 결과 컨테이너
    result_title = st.empty()
    result_content = st.empty()
    
    # 단계별 분석 상태 표시
    show_analysis_step(analysis_status, "🔍 주제 키워드를 추출하고 있습니다...")
    show_analysis_step(analysis_status, "📚 관련 학문 분야를 식별하고 있습니다...")
    show_analysis_step(analysis_status, "🧠 주제의 핵심 개념을 정의하고 있습니다...")
    show_analysis_step(analysis_status, "🔄 학술 데이터베이스에서 관련 자료를 검색하고 있습니다...")
    show_analysis_step(analysis_status, "⚙️ 수집된 정보를 종합적으로 분석하고 있습니다...")
    show_analysis_step(analysis_status, "📝 최종 분석 결과를 생성하고 있습니다...")
    
    # GPT API를 통한 주제 분석
    analysis_result = analyze_topic(topic)
    
    if analysis_result:
        # 분석 결과 저장
        st.session_state.topic_analysis = analysis_result
        
        # 완료 메시지 표시
        analysis_status.markdown('<div class="analysis-complete">✅ 분석이 완료되었습니다!</div>', unsafe_allow_html=True)
        
        # 원본 텍스트를 스타일이 적용된 HTML로 변환
        original_text = analysis_result["full_text"]
        formatted_text = format_text_with_section_titles(original_text)
        
        # 결과 제목 표시
        result_title.markdown('<div class="analysis-result-title">주제 분석 결과</div>', unsafe_allow_html=True)
        
        # 타이핑 효과로 결과 표시
        typing_effect(result_content, formatted_text, speed=0.005, chunk_size=5)
        
        # 다음 단계로 이동 버튼 - 중앙 정렬 및 스타일 개선
        st.session_state.step = 2
        
        st.markdown('<div class="button-container">', unsafe_allow_html=True)
        btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])
        with btn_col2:
            if st.button("유사 주제 찾기 →", use_container_width=True):
                st.switch_page("pages/2_Similar_Topics.py")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.error("주제 분석 중 오류가 발생했습니다. 다시 시도해 주세요.")

# 세션에 분석 결과가 있으면 표시
elif "topic_analysis" in st.session_state and st.session_state.topic_analysis:
    original_text = st.session_state.topic_analysis["full_text"]
    formatted_text = format_text_with_section_titles(original_text)
    
    st.markdown('<div class="analysis-result-title">주제 분석 결과</div>', unsafe_allow_html=True)
    st.markdown(formatted_text, unsafe_allow_html=True)
    
    # 다음 단계로 이동 버튼 - 중앙 정렬 및 스타일 개선
    st.session_state.step = 2
    
    st.markdown('<div class="button-container">', unsafe_allow_html=True)
    btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])
    with btn_col2:
        if st.button("유사 주제 찾기 →", use_container_width=True):
            st.switch_page("pages/2_Similar_Topics.py")
    st.markdown('</div>', unsafe_allow_html=True)

# 컨테이너 닫기
st.markdown('</div>', unsafe_allow_html=True)
