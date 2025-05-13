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
        paper_result = generate_paper_structure(st.session_state.selected_topic)
        
        if paper_result and "content" in paper_result:
            # 논문 콘텐츠 저장
            st.session_state.generated_paper = {
                "topic": st.session_state.selected_topic,
                "content": paper_result["content"],
                "papers": paper_result.get("papers", [])
            }
            
            # A4 형식 논문 표시 컨테이너
            paper_container.empty()
            
            # 타이핑 효과를 위한 컨테이너
            typing_container = st.empty()
            
            # 타이핑 효과 구현 (간단한 버전)
            full_text = paper_result["content"]
            if isinstance(full_text, str):  # 문자열 타입 확인
                displayed_text = ""
                
                # 애니메이션 효과 (선택적)
                with st.spinner("논문 내용을 표시하는 중..."):
                    for i in range(min(len(full_text) + 1, 1000)):  # 최대 1000자까지만 애니메이션 (성능 고려)
                        displayed_text = full_text[:i]
                        
                        # A4 형식으로 표시
                        typing_container.markdown(
                            f"""
                            <div class="paper-container">
                                <div class="paper-content">{displayed_text}</div>
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
                        
                        time.sleep(0.001)  # 매우 빠른 속도로 표시
                    
                    # 나머지 텍스트 한 번에 표시
                    typing_container.markdown(
                        f"""
                        <div class="paper-container">
                            <div class="paper-content">{full_text}</div>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
            else:
                # 문자열이 아닌 경우 그냥 전체 내용 표시
                typing_container.markdown(
                    f"""
                    <div class="paper-container">
                        <div class="paper-content">{full_text}</div>
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
        else:
            paper_container.error("논문 생성 중 오류가 발생했습니다. 다시 시도해 주세요.")
    
    # 이미 생성된 논문이 있으면 표시
    else:
        # A4 형식으로 논문 콘텐츠 표시
        st.markdown(
            f"""
            <div class="paper-container">
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
