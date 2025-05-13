import streamlit as st
import pandas as pd
from utils.data_utils import load_isef_data, search_similar_topics
from utils.api_utils import search_arxiv, search_crossref, merge_search_results
import time

# 페이지 제목
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
        
        # 내부 DB(ISEF) 검색
        isef_data = load_isef_data()
        isef_results = search_similar_topics(isef_data, st.session_state.topic)
        
        # 외부 API 검색
        arxiv_results = search_arxiv(st.session_state.topic)
        crossref_results = search_crossref(st.session_state.topic)
        
        # 결과 병합
        api_results = merge_search_results(arxiv_results, crossref_results)
        
        # 모든 결과 저장
        st.session_state.similar_topics = {
            "isef": isef_results,
            "api": api_results
        }
        
        # 검색 완료 메시지 업데이트
        search_message.success("유사 주제 검색이 완료되었습니다!")
    
    # 유사 주제 표시
    st.markdown("## 내부 데이터베이스에서 발견된 유사 주제")
    
    if st.session_state.similar_topics["isef"]:
        # ISEF 결과 표시 (최대 5개)
        for i, topic in enumerate(st.session_state.similar_topics["isef"][:5], 1):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{i}. {topic['title']}**")
            with col2:
                if st.button("선택", key=f"isef_{i}"):
                    st.session_state.selected_topic = topic['title']
                    st.session_state.selected_source = "isef"
                    st.session_state.step = 3
                    st.switch_page("pages/3_Paper_Generation.py")
    else:
        st.markdown("내부 데이터베이스에서 유사한 주제를 찾지 못했습니다.")
    
    st.markdown("## 학술 데이터베이스에서 발견된 유사 주제")
    
    if st.session_state.similar_topics["api"]:
        # API 결과 표시 (최대 5개)
        for i, paper in enumerate(st.session_state.similar_topics["api"][:5], 1):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{i}. {paper['title']}**")
                st.markdown(f"*출처: {paper['source']} | 발행: {paper['published']}*")
            with col2:
                if st.button("선택", key=f"api_{i}"):
                    st.session_state.selected_topic = paper['title']
                    st.session_state.selected_source = "api"
                    st.session_state.selected_paper = paper
                    st.session_state.step = 3
                    st.switch_page("pages/3_Paper_Generation.py")
    else:
        st.markdown("학술 데이터베이스에서 유사한 주제를 찾지 못했습니다.")
    
    # 되돌아가기 버튼
    if st.button("주제 입력으로 돌아가기"):
        st.session_state.step = 1
        st.switch_page("pages/1_Topic_Input.py")
