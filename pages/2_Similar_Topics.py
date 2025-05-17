import streamlit as st
import pandas as pd
import re
import time
from utils.data_utils import load_isef_data, search_similar_topics
from utils.gpt_utils import generate_similar_topics, get_completion

# 관련성 배지 HTML 생성 함수
def get_relevance_badge(score):
    """
    관련성 점수에 따른 배지 HTML을 반환합니다.
    """
    if score >= 0.8:
        return f'<span class="relevance-badge high-relevance">관련성 높음 ({score:.2f})</span>'
    elif score >= 0.6:
        return f'<span class="relevance-badge medium-relevance">관련성 중간 ({score:.2f})</span>'
    else:
        return f'<span class="relevance-badge low-relevance">관련성 낮음 ({score:.2f})</span>'

# 단계별 분석 상태 메시지 표시 함수
def show_analysis_step(container, step_message, delay=0.5):
    container.markdown(f'<div class="analysis-step-message">{step_message}</div>', unsafe_allow_html=True)
    time.sleep(delay)

# 타이핑 효과 함수 수정
def typing_effect(container, text, speed=0.05, chunk_size=10):
    full_text = text
    displayed_text = ""
    
    # 더 큰 청크와 더 느린 속도로 설정
    for i in range(0, len(full_text), chunk_size):
        displayed_text = full_text[:i + chunk_size]
        container.markdown(displayed_text, unsafe_allow_html=True)
        
        # 짧은 텍스트는 건너뛰기 (불필요한 업데이트 줄이기)
        if i < 50:  # 초반 부분은 빠르게 표시
            time.sleep(speed * 0.5)
        else:
            time.sleep(speed)

# 메인 코드 시작
st.title("2. 유사 연구 주제")

# 주제가 없으면 첫 페이지로 리다이렉트
if "topic" not in st.session_state or not st.session_state.topic:
    st.warning("먼저 연구 주제를 입력해주세요.")
    st.button("주제 입력으로 돌아가기", on_click=lambda: st.switch_page("pages/1_Topic_Input.py"))
else:
    # 현재 주제 표시
    st.markdown(f"### 선택한 주제: {st.session_state.topic}")
    
    # 유사 주제 검색 시작
    if "similar_topics" not in st.session_state or not st.session_state.similar_topics:
        # 검색 상태 컨테이너
        search_status = st.empty()
        
        # 단계별 분석 상태 표시
        show_analysis_step(search_status, "🔍 주제 키워드를 추출하고 있습니다...")
        show_analysis_step(search_status, "📚 학문 분야를 분석하고 있습니다...")
        show_analysis_step(search_status, "🔄 내부 데이터베이스를 검색하고 있습니다...")
        show_analysis_step(search_status, "🌐 학술 데이터베이스에서 관련 논문을 검색하고 있습니다...")
        show_analysis_step(search_status, "⚖️ 검색 결과의 관련성을 평가하고 있습니다...")
        show_analysis_step(search_status, "🧠 인공지능으로 추가 유사 주제를 생성하고 있습니다...")
        
        # generate_similar_topics 함수 사용 (gpt_utils.py에서 제공)
        similar_topics_result = generate_similar_topics(st.session_state.topic, count=5)
        
        # 모든 결과 저장
        st.session_state.similar_topics = similar_topics_result
        
        # 완료 메시지 표시
        search_status.markdown('<div class="analysis-complete">✅ 유사 주제 검색이 완료되었습니다!</div>', unsafe_allow_html=True)
    
    # 주제 분석 정보 표시
    if "domain" in st.session_state.similar_topics and "keywords" in st.session_state.similar_topics:
        with st.expander("주제 분석 정보", expanded=False):
            st.markdown(f"**학문 분야:** {st.session_state.similar_topics['domain']}")
            st.markdown("**핵심 키워드:**")
            keyword_html = ""
            for kw in st.session_state.similar_topics['keywords']:
                keyword_html += f'<span class="keyword-tag">{kw}</span> '
            st.markdown(f'<div class="keyword-container">{keyword_html}</div>', unsafe_allow_html=True)
    
    # GPT 생성 유사 주제 먼저 표시 (순서 변경)
    st.markdown('<div class="section-title">AI가 생성한 관련 연구 주제 제안</div>', unsafe_allow_html=True)
    
    if "ai_generated" in st.session_state.similar_topics and st.session_state.similar_topics["ai_generated"]:
        # GPT 응답을 직접 표시
        ai_content = st.session_state.similar_topics["ai_generated"]
        
        # 제목은 HTML로 변환하여 스타일 적용
        ai_content = re.sub(r'## 주제 (\d+): (.*?)(?=\n|$)', 
                         r'<div class="topic-title-container"><span class="topic-number">\1.</span> <span class="topic-title">\2</span> <span class="gpt-generated-badge">AI 생성</span></div>', 
                         ai_content)
        
        # 강조 표시 (볼드 텍스트)
        ai_content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', ai_content)
        
        # HTML 컨테이너에 배치
        st.markdown(f'<div class="similar-topic-card gpt-generated-card">{ai_content}</div>', unsafe_allow_html=True)
        
        # 주제 선택 버튼
        if st.button("이 주제들로 계속하기", key="gpt_continue"):
            st.session_state.selected_topic = st.session_state.topic + " (AI 생성 주제 기반)"
            st.session_state.selected_source = "gpt"
            st.session_state.step = 3
            st.switch_page("pages/3_Paper_Generation.py")
    
    # "combined_results"도 확인 (기존 코드와 호환성 유지)
    elif "combined_results" in st.session_state.similar_topics and st.session_state.similar_topics["combined_results"]:
        # GPT 생성 결과만 필터링
        gpt_topics = [t for t in st.session_state.similar_topics["combined_results"] if t.get('is_gpt_generated', False)]
        
        if gpt_topics:
            for i, topic in enumerate(gpt_topics, 1):
                with st.container():
                    st.markdown('<div class="similar-topic-card gpt-generated-card">', unsafe_allow_html=True)
                    
                    # GPT 생성 배지와 함께 제목 표시
                    st.markdown(f'<div class="topic-title-container"><span class="topic-number">{i}.</span> <span class="topic-title">{topic["title"]}</span> <span class="gpt-generated-badge">AI 생성</span></div>', unsafe_allow_html=True)
                    
                    # 요약 정보
                    if 'summary' in topic and topic['summary']:
                        with st.expander("개요"):
                            st.write(topic['summary'])
                    
                    # 원래 주제와의 관련성
                    if 'relevance_to_original' in topic and topic['relevance_to_original']:
                        with st.expander("원주제와의 관련성"):
                            st.write(topic['relevance_to_original'])
                    
                    # 연구 방법론
                    if 'methodology' in topic and topic['methodology']:
                        with st.expander("연구 방법론"):
                            st.write(topic['methodology'])
                    
                    # 학술적 중요성
                    if 'importance' in topic and topic['importance']:
                        with st.expander("학술적 중요성"):
                            st.write(topic['importance'])
                    
                    # 선택 버튼
                    if st.button("선택", key=f"gpt_{i}"):
                        st.session_state.selected_topic = topic['title']
                        st.session_state.selected_source = "gpt"
                        st.session_state.selected_gpt_topic = topic
                        st.session_state.step = 3
                        st.switch_page("pages/3_Paper_Generation.py")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="section-content">AI가 생성한 관련 주제가 없습니다.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="section-content">AI가 생성한 관련 주제가 없습니다.</div>', unsafe_allow_html=True)
    
    # API 검색 결과 표시 (GPT 생성 주제 다음에 표시)
    st.markdown('<div class="section-title">학술 데이터베이스에서 발견된 유사 주제</div>', unsafe_allow_html=True)
    
    if "api_results" in st.session_state.similar_topics and st.session_state.similar_topics["api_results"]:
        # API 결과 표시
        for i, paper in enumerate(st.session_state.similar_topics["api_results"][:5], 1):
            with st.container():
                st.markdown('<div class="similar-topic-card">', unsafe_allow_html=True)
                
                # 제목과 관련성 점수
                st.markdown(f"**{i}. {paper['title']}**")
                if 'relevance_score' in paper:
                    st.markdown(get_relevance_badge(paper['relevance_score']), unsafe_allow_html=True)
                
                # 메타 정보
                st.markdown(f"*출처: {paper['source']} | 발행: {paper['published']}*")
                
                # 요약 정보가 있으면 표시
                if paper.get('summary') and paper['summary'] != "요약 정보 없음":
                    with st.expander("요약 보기"):
                        st.write(paper['summary'])
                
                # 선택 버튼
                if st.button("선택", key=f"api_{i}"):
                    st.session_state.selected_topic = paper['title']
                    st.session_state.selected_source = "api"
                    st.session_state.selected_paper = paper
                    st.session_state.step = 3
                    st.switch_page("pages/3_Paper_Generation.py")
                
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="section-content">학술 데이터베이스에서 유사한 주제를 찾지 못했습니다.</div>', unsafe_allow_html=True)
    
    # 내부 DB(ISEF) 결과 표시
    st.markdown('<div class="section-title">내부 데이터베이스에서 발견된 유사 주제</div>', unsafe_allow_html=True)
    
    isef_data = load_isef_data()
    isef_results = search_similar_topics(isef_data, st.session_state.topic)
    
    if isef_results:
        # 관련성 평가
        for result in isef_results:
            if 'relevance_score' not in result:
                result['relevance_score'] = 0.5  # 기본값
        
        # 관련성 점수로 정렬 및 필터링
        isef_results = [r for r in isef_results if r['relevance_score'] >= 0.5]
        isef_results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        # ISEF 결과 표시 (최대 5개)
        for i, topic in enumerate(isef_results[:5], 1):
            with st.container():
                st.markdown('<div class="similar-topic-card">', unsafe_allow_html=True)
                
                # 제목과 관련성 점수
                st.markdown(f"**{i}. {topic['title']}**")
                if 'relevance_score' in topic:
                    st.markdown(get_relevance_badge(topic['relevance_score']), unsafe_allow_html=True)
                
                # 선택 버튼
                if st.button("선택", key=f"isef_{i}"):
                    st.session_state.selected_topic = topic['title']
                    st.session_state.selected_source = "isef"
                    st.session_state.step = 3
                    st.switch_page("pages/3_Paper_Generation.py")
                
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="section-content">내부 데이터베이스에서 유사한 주제를 찾지 못했습니다.</div>', unsafe_allow_html=True)
    
    # 새로 검색하기 버튼
    if st.button("유사 주제 다시 검색", key="refresh_search", use_container_width=False):
        # 유사 주제 결과 초기화
        if "similar_topics" in st.session_state:
            del st.session_state.similar_topics
        st.experimental_rerun()
    
    # 되돌아가기 버튼
    if st.button("주제 입력으로 돌아가기", use_container_width=False):
        st.session_state.step = 1
        st.switch_page("pages/1_Topic_Input.py")
        st.session_state.step = 1
        st.switch_page("pages/1_Topic_Input.py")
