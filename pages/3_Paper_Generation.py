import streamlit as st
import time
from utils.gpt_utils import generate_paper_structure

# 페이지 제목
st.title("3. 논문 생성")

# 선택된 주제가 없으면 이전 페이지로 리다이렉트
if "selected_topic" not in st.session_state or not st.session_state.selected_topic:
    st.warning("먼저 연구 주제를 선택해주세요.")
    st.button("유사 주제 선택으로 돌아가기", on_click=lambda: st.switch_page("pages/2_Similar_Topics.py"))
else:
    # 선택된 주제 표시
    st.markdown(f"### 선택한 주제: {st.session_state.selected_topic}")
    
    # 논문 생성 시작
    if "generated_paper" not in st.session_state or not st.session_state.generated_paper:
        # 생성 중 메시지
        paper_container = st.empty()
        paper_container.info("AI가 논문 구조를 생성하고 있습니다...")
        
        # 논문 생성 시작
        paper_content = generate_paper_structure(st.session_state.selected_topic)
        
        if paper_content:
            # 논문 콘텐츠 저장
            st.session_state.generated_paper = {
                "topic": st.session_state.selected_topic,
                "content": paper_content,
                "title": st.session_state.selected_topic,  # 간단화를 위해 같은 값 사용
                "authors": "AI 연구 도우미",
                # 추가 정보는 파싱 필요 (실제 구현 시)
            }
            
            # A4 형식 논문 표시 컨테이너
            paper_container.empty()
            
            # 타이핑 효과를 위한 컨테이너
            typing_container = st.empty()
            
            # 타이핑 효과 구현 (간단한 버전)
            full_text = paper_content
            displayed_text = ""
            
            # 실제 서비스에서는 WebSocket으로 스트리밍 구현
            # 여기서는 간단한 타이핑 효과 시뮬레이션
            for i in range(len(full_text) + 1):
                displayed_text = full_text[:i]
                
                # A4 형식으로 표시
                typing_container.markdown(
                    f"""
                    <div class="paper-container">
                        <div class="paper-title">{st.session_state.selected_topic}</div>
                        <div class="paper-authors">AI 연구 도우미</div>
                        <div class="paper-content">{displayed_text}</div>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                
                time.sleep(0.01)  # 프로덕션에서는 더 자연스러운 속도로 조정
            
            # 다음 단계로 이동 버튼
            st.session_state.step = 4
            col1, col2 = st.columns(2)
            with col1:
                if st.button("PDF로 보기 →"):
                    st.switch_page("pages/4_PDF_View.py")
            with col2:
                if st.button("틈새 주제 제안 →"):
                    st.switch_page("pages/5_Niche_Topics.py")
        else:
            paper_container.error("논문 생성 중 오류가 발생했습니다. 다시 시도해 주세요.")
    
    # 이미 생성된 논문이 있으면 표시
    else:
        # A4 형식으로 논문 콘텐츠 표시
        st.markdown(
            f"""
            <div class="paper-container">
                <div class="paper-title">{st.session_state.selected_topic}</div>
                <div class="paper-authors">AI 연구 도우미</div>
                <div class="paper-content">{st.session_state.generated_paper['content']}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        # 다음 단계로 이동 버튼
        st.session_state.step = 4
        col1, col2 = st.columns(2)
        with col1:
            if st.button("PDF로 보기 →"):
                st.switch_page("pages/4_PDF_View.py")
        with col2:
            if st.button("틈새 주제 제안 →"):
                st.switch_page("pages/5_Niche_Topics.py")
    
    # 되돌아가기 버튼
    if st.button("유사 주제 선택으로 돌아가기"):
        st.session_state.step = 2
        st.switch_page("pages/2_Similar_Topics.py")
