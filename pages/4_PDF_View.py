import streamlit as st
import base64
from utils.pdf_utils import create_research_paper_pdf
import os

# 페이지 제목
st.title("4. PDF 보기")

# 생성된 논문이 없으면 이전 페이지로 리다이렉트
if "generated_paper" not in st.session_state or not st.session_state.generated_paper:
    st.warning("먼저 논문을 생성해주세요.")
    st.button("논문 생성으로 돌아가기", on_click=lambda: st.switch_page("pages/3_Paper_Generation.py"))
else:
    # 경고 메시지 표시
    st.warning("이 PDF는 참고용으로만 사용해주세요. 학술적 인용 시 원본 출처를 확인하세요.")
    
    # PDF 파일 생성
    with st.spinner("PDF를 생성하고 있습니다..."):
        # 논문 데이터 구조화 (실제 구현 시 파싱 필요)
        # 간단화를 위해 임의 구조화
        paper_data = {
            'title': st.session_state.generated_paper['title'],
            'authors': st.session_state.generated_paper['authors'],
            'abstract': "이 연구는...",  # 실제 구현 시 파싱 필요
            'introduction': "서론...",   # 실제 구현 시 파싱 필요
            'methods': "연구 방법...",    # 실제 구현 시 파싱 필요
            'results': "예상 결과...",    # 실제 구현 시 파싱 필요
            'conclusion': "결론...",     # 실제 구현 시 파싱 필요
            'references': ["참고문헌1", "참고문헌2"]  # 실제 구현 시 파싱 필요
        }
        
        pdf_path = create_research_paper_pdf(paper_data)
    
    if pdf_path and os.path.exists(pdf_path):
        # PDF 파일 표시
        with open(pdf_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        
        # PDF 표시
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
        
        # 다운로드 버튼
        st.download_button(
            label="PDF 다운로드",
            data=open(pdf_path, "rb"),
            file_name=f"{st.session_state.selected_topic.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
        
        # 임시 파일 삭제 (선택 사항)
        # os.remove(pdf_path)
    else:
        st.error("PDF 생성 중 오류가 발생했습니다.")
    
    # 다음 단계로 이동 버튼
    st.session_state.step = 5
    if st.button("틈새 주제 제안 →"):
        st.switch_page("pages/5_Niche_Topics.py")
    
    # 되돌아가기 버튼
    if st.button("논문 생성으로 돌아가기"):
        st.session_state.step = 3
        st.switch_page("pages/3_Paper_Generation.py")
