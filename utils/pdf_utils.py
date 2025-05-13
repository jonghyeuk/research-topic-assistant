import os
from fpdf import FPDF
import tempfile
import textwrap
import streamlit as st

class ResearchPaperPDF(FPDF):
    """
    연구 논문 형식의 PDF를 생성하는 클래스
    """
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()
        self.set_margins(20, 20, 20)
        
        # 폰트 설정
        self.add_font('DejaVu', '', 'assets/DejaVuSansCondensed.ttf', uni=True)
        self.add_font('DejaVu', 'B', 'assets/DejaVuSansCondensed-Bold.ttf', uni=True)
        self.add_font('DejaVu', 'I', 'assets/DejaVuSansCondensed-Oblique.ttf', uni=True)
        
        self.set_font('DejaVu', '', 11)
    
    def header(self):
        # 페이지 번호 (첫 페이지 제외)
        if self.page_no() > 1:
            self.set_font('DejaVu', '', 9)
            self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'R')
            self.ln(10)
    
    def footer(self):
        # 저작권 고지 추가
        self.set_y(-15)
        self.set_font('DejaVu', 'I', 8)
        self.cell(0, 10, '이 문서는 AI 생성 참조용 자료입니다. 실제 연구에 인용 시 원본 출처를 확인하세요.', 0, 0, 'C')
    
    def add_title(self, title):
        self.set_font('DejaVu', 'B', 16)
        self.multi_cell(0, 10, title, 0, 'C')
        self.ln(5)
    
    def add_authors(self, authors):
        self.set_font('DejaVu', 'I', 12)
        self.multi_cell(0, 8, authors, 0, 'C')
        self.ln(10)
    
    def add_abstract(self, abstract):
        self.set_font('DejaVu', 'B', 12)
        self.cell(0, 8, '초록 (Abstract)', 0, 1, 'L')
        self.ln(2)
        
        self.set_font('DejaVu', '', 10)
        
        # 여러 줄 텍스트 처리
        abstract_wrapped = textwrap.fill(abstract, width=100)
        self.multi_cell(0, 5, abstract_wrapped)
        self.ln(10)
    
    def add_section(self, section_title, content):
        self.set_font('DejaVu', 'B', 12)
        self.cell(0, 8, section_title, 0, 1, 'L')
        self.ln(2)
        
        self.set_font('DejaVu', '', 10)
        
        # 여러 줄 텍스트 처리
        content_wrapped = textwrap.fill(content, width=100)
        self.multi_cell(0, 5, content_wrapped)
        self.ln(5)
    
    def add_references(self, references):
        self.set_font('DejaVu', 'B', 12)
        self.cell(0, 8, '참고문헌 (References)', 0, 1, 'L')
        self.ln(2)
        
        self.set_font('DejaVu', '', 10)
        
        # 각 참고문헌 항목 추가
        for ref in references:
            ref_wrapped = textwrap.fill(ref, width=100)
            self.multi_cell(0, 5, ref_wrapped)
            self.ln(3)
        
        self.ln(5)

def create_research_paper_pdf(paper_data):
    """
    연구 논문 데이터를 PDF로 변환합니다.
    
    paper_data 형식:
    {
        'title': '논문 제목',
        'authors': '저자 이름들',
        'abstract': '초록 내용',
        'introduction': '서론 내용',
        'methods': '연구 방법 내용',
        'results': '예상 결과 내용',
        'conclusion': '결론 내용',
        'references': ['참고문헌1', '참고문헌2', ...]
    }
    """
    # DejaVu 폰트가 없으면 다운로드 필요
    try:
        # 폰트 파일 경로 확인
        font_dir = "assets"
        if not os.path.exists(font_dir):
            os.makedirs(font_dir)
        
        font_normal = os.path.join(font_dir, "DejaVuSansCondensed.ttf")
        font_bold = os.path.join(font_dir, "DejaVuSansCondensed-Bold.ttf")
        font_italic = os.path.join(font_dir, "DejaVuSansCondensed-Oblique.ttf")
        
        # 폰트 파일이 없으면 기본 폰트 사용
        if not (os.path.exists(font_normal) and os.path.exists(font_bold) and os.path.exists(font_italic)):
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            pdf.set_margins(20, 20, 20)
            font_available = False
        else:
            pdf = ResearchPaperPDF()
            font_available = True
        
        # 제목 추가
        if font_available:
            pdf.add_title(paper_data['title'])
        else:
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, paper_data['title'], 0, 1, "C")
            pdf.ln(5)
        
        # 저자 추가
        if font_available:
            pdf.add_authors(paper_data['authors'])
        else:
            pdf.set_font("Arial", "I", 12)
            pdf.cell(0, 8, paper_data['authors'], 0, 1, "C")
            pdf.ln(10)
        
        # 초록 추가
        if font_available:
            pdf.add_abstract(paper_data['abstract'])
        else:
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 8, "초록 (Abstract)", 0, 1, "L")
            pdf.ln(2)
            pdf.set_font("Arial", "", 10)
            pdf.multi_cell(0, 5, paper_data['abstract'])
            pdf.ln(10)
        
        # 섹션 추가
        sections = [
            ("서론 (Introduction)", paper_data['introduction']),
            ("연구 방법 (Methods)", paper_data['methods']),
            ("예상 결과 (Expected Results)", paper_data['results']),
            ("결론 (Conclusion)", paper_data['conclusion'])
        ]
        
        for title, content in sections:
            if font_available:
                pdf.add_section(title, content)
            else:
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 8, title, 0, 1, "L")
                pdf.ln(2)
                pdf.set_font("Arial", "", 10)
                pdf.multi_cell(0, 5, content)
                pdf.ln(5)
        
        # 참고문헌 추가
        if font_available:
            pdf.add_references(paper_data['references'])
        else:
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 8, "참고문헌 (References)", 0, 1, "L")
            pdf.ln(2)
            pdf.set_font("Arial", "", 10)
            for ref in paper_data['references']:
                pdf.multi_cell(0, 5, ref)
                pdf.ln(3)
        
        # 임시 파일 생성
        pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        pdf_file.close()
        
        # PDF 저장
        pdf.output(pdf_file.name)
        
        return pdf_file.name
    
    except Exception as e:
        st.error(f"PDF 생성 오류: {str(e)}")
        return None
