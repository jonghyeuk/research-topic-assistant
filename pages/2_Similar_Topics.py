import streamlit as st
import pandas as pd
import re
from utils.data_utils import load_isef_data, search_similar_topics
from utils.api_utils import search_arxiv, search_crossref, merge_search_results
from utils.gpt_utils import get_completion
import time

# 관련성 평가 및 필터링 함수들
def extract_core_keywords(topic):
    """
    주제에서 핵심 키워드를 추출합니다.
    """
    prompt = f"""
    다음 연구 주제에서 가장 핵심적인 키워드 5개를 추출하고 중요도 순으로 나열해주세요:
    "{topic}"
    
    결과는 쉼표로 구분된 단일 라인으로 제공해주세요. 예: 키워드1, 키워드2, 키워드3, 키워드4, 키워드5
    """
    
    response = get_completion(prompt)
    keywords = [kw.strip() for kw in response.split(',')]
    return keywords

def identify_academic_domain(topic):
    """
    주제의 학문 분야를 식별합니다.
    """
    prompt = f"""
    다음 연구 주제가 속하는 학문 분야를 가장 구체적으로 식별해주세요:
    "{topic}"
    
    다음 중 하나를 선택하고, 가능하면 더 구체적인 하위 분야를 명시해주세요:
    - 물리학 (예: 플라즈마 물리학, 양자역학, 열역학)
    - 화학 (예: 유기화학, 생화학, 재료화학)
    - 생물학 (예: 분자생물학, 생태학, 유전학)
    - 의학 (예: 면역학, 신경과학, 종양학)
    - 공학 (예: 전기공학, 기계공학, 화학공학)
    - 컴퓨터 과학 (예: 인공지능, 데이터베이스, 사이버보안)
    - 수학 (예: 대수학, 통계학, 확률론)
    - 사회과학 (예: 경제학, 심리학, 사회학)
    - 인문학 (예: 철학, 역사학, 언어학)
    - 환경 과학 (예: 기후학, 생태학, 환경화학)
    
    응답은 간결하게 분야와 하위분야만 제공해주세요. 예: "물리학: 플라즈마 물리학"
    """
    
    response = get_completion(prompt)
    return response.strip()

def assess_relevance_with_gpt(topic, paper):
    """
    GPT를 사용하여 논문과 주제 간의 관련성을 평가합니다.
    """
    # 논문 정보 구성
    paper_info = f"제목: {paper['title']}\n"
    if paper.get('summary') and paper['summary'] != "요약 정보 없음":
        paper_info += f"요약: {paper['summary']}\n"
    
    prompt = f"""
    다음 연구 주제와 논문 간의 관련성을 0.0에서 1.0 사이의 숫자로 평가해주세요:
    
    연구 주제: "{topic}"
    
    논문 정보:
    {paper_info}
    
    관련성 점수 (0.0 ~ 1.0)만 숫자로 응답해주세요. 다른 설명은 필요하지 않습니다.
    """
    
    try:
        response = get_completion(prompt)
        # 숫자만 추출
        score_match = re.search(r'(\d+\.\d+|\d+)', response)
        if score_match:
            score = float(score_match.group(1))
            # 범위 제한
            score = max(0.0, min(1.0, score))
            return score
        return 0.5  # 기본값
    except:
        return 0.5  # 오류 시 기본값

def filter_results_by_relevance(topic, keywords, results, threshold=0.5):
    """
    검색 결과에서 주제와 관련성이 높은 항목만 필터링합니다.
    """
    filtered_results = []
    
    for result in results:
        # 1. 제목에 키워드 포함 여부 확인
        title = result['title'].lower()
        keyword_match = sum(1 for kw in keywords if kw.lower() in title) / len(keywords)
        
        # 2. GPT를 통한 관련성 평가 (키워드 매칭만으로 충분히 관련성이 높으면 건너뜀)
        if keyword_match >= 0.4:  # 40% 이상의 키워드가 제목에 포함되면 관련성 높음
            relevance_score = 0.7 + (keyword_match * 0.3)  # 최소 0.7, 최대 1.0
        else:
            relevance_score = assess_relevance_with_gpt(topic, result)
        
        # 관련성 점수 저장
        result['relevance_score'] = relevance_score
        
        # 임계값 이상인 경우만 포함
        if relevance_score >= threshold:
            filtered_results.append(result)
    
    # 관련성 점수 기준으로 정렬
    filtered_results.sort(key=lambda x: x['relevance_score'], reverse=True)
    
    # 최대 8개까지만 반환
    return filtered_results[:8]

def get_relevance_badge(score):
    """
    관련성 점수에 따른 배지 HTML을 반환합니다.
    """
    if score >= 0.8:
        return f'<span style="background-color: #28a745; color: white; padding: 2px 6px; border-radius: 10px; font-size: 12px;">관련성 높음 ({score:.2f})</span>'
    elif score >= 0.6:
        return f'<span style="background-color: #ffc107; color: #333; padding: 2px 6px; border-radius: 10px; font-size: 12px;">관련성 중간 ({score:.2f})</span>'
    else:
        return f'<span style="background-color: #dc3545; color: white; padding: 2px 6px; border-radius: 10px; font-size: 12px;">관련성 낮음 ({score:.2f})</span>'

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
        # 검색 중 메시지
        search_message = st.empty()
        search_message.info("유사한 연구 주제를 검색 중입니다...")
        
        # 주제의 핵심 키워드 추출
        keywords = extract_core_keywords(st.session_state.topic)
        domain = identify_academic_domain(st.session_state.topic)
        
        with st.expander("주제 분석 정보", expanded=False):
            st.write(f"**학문 분야:** {domain}")
            st.write("**핵심 키워드:**")
            for kw in keywords:
                st.write(f"- {kw}")
        
        # 내부 DB(ISEF) 검색
        isef_data = load_isef_data()
        isef_results = search_similar_topics(isef_data, st.session_state.topic)
        
        # 외부 API 검색 - 더 많은 결과 가져오기
        arxiv_results = search_arxiv(st.session_state.topic, max_results=10)
        crossref_results = search_crossref(st.session_state.topic, max_results=10)
        
        # 결과 병합
        all_api_results = merge_search_results(arxiv_results, crossref_results, max_total=20)
        
        # 관련성 기반 필터링
        filtered_api_results = filter_results_by_relevance(st.session_state.topic, keywords, all_api_results)
        
        # 내부 데이터도 관련성 평가
        if isef_results:
            for result in isef_results:
                relevance_score = assess_relevance_with_gpt(st.session_state.topic, result)
                result['relevance_score'] = relevance_score
            
            # 관련성 점수로 정렬 및 필터링
            isef_results = [r for r in isef_results if r['relevance_score'] >= 0.5]
            isef_results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # 모든 결과 저장
        st.session_state.similar_topics = {
            "isef": isef_results,
            "api": filtered_api_results,
            "domain": domain,
            "keywords": keywords
        }
        
        # 검색 완료 메시지 업데이트
        search_message.success("유사 주제 검색이 완료되었습니다!")
    
    # 유사 주제 표시
    st.markdown('<div class="section-title">내부 데이터베이스에서 발견된 유사 주제</div>', unsafe_allow_html=True)
    
    if st.session_state.similar_topics["isef"]:
        # ISEF 결과 표시 (최대 5개)
        for i, topic in enumerate(st.session_state.similar_topics["isef"][:5], 1):
            with st.container():
                st.markdown('<div class="similar-topic-card">', unsafe_allow_html=True)
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**{i}. {topic['title']}**")
                    if 'relevance_score' in topic:
                        st.markdown(get_relevance_badge(topic['relevance_score']), unsafe_allow_html=True)
                with col2:
                    if st.button("선택", key=f"isef_{i}"):
                        st.session_state.selected_topic = topic['title']
                        st.session_state.selected_source = "isef"
                        st.session_state.step = 3
                        st.switch_page("pages/3_Paper_Generation.py")
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="section-content">내부 데이터베이스에서 유사한 주제를 찾지 못했습니다.</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="section-title">학술 데이터베이스에서 발견된 유사 주제</div>', unsafe_allow_html=True)
    
    if st.session_state.similar_topics["api"]:
        # API 결과 표시 (최대 5개)
        for i, paper in enumerate(st.session_state.similar_topics["api"][:5], 1):
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
    
    # 새로 검색하기 버튼
    if st.button("유사 주제 다시 검색", key="refresh_search"):
        # 유사 주제 결과 초기화
        if "similar_topics" in st.session_state:
            del st.session_state.similar_topics
        st.experimental_rerun()
    
    # 되돌아가기 버튼
    if st.button("주제 입력으로 돌아가기"):
        st.session_state.step = 1
        st.switch_page("pages/1_Topic_Input.py")
