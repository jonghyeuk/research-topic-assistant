import requests
import json
import time
import config
import streamlit as st
import re
import xml.etree.ElementTree as ET

def get_completion(prompt, model=config.GPT_MODEL, temperature=config.TEMPERATURE, max_tokens=config.MAX_TOKENS):
    """
    GPT 모델로부터 응답을 받아옵니다. OpenAI 라이브러리 대신 직접 API 호출을 사용합니다.
    """
    system_prompt = """당신은 학생과 연구자를 위한 연구 주제 선정 전문가입니다.  
주어진 연구 주제에 대해 학술적 분석을 제공하고, 신뢰할 수 있는 출처 및 참고문헌을 포함하여 연구자가 가치 있는 연구를 수행하도록 돕습니다.  
### 🧪 역할  
- 연구 주제 분석 전문가  
- 복잡한 연구 내용을 쉽게 설명  
- 최신 연구 동향 반영  
- 명확하고 구체적인 연구 주제 및 논문 구조 제안  
### 📚 주요 기능  
✅ 논문 검색 API를 활용해 **실제 논문만 인용** (가짜 논문 생성 금지)  
✅ 과학적 깊이 + 명확한 구조 + 최신 연구 동향 반영  
✅ 답변은 **구조화된 마크다운 형식**으로 제공  
🔹 **답변 구성**  
- 🧠 개요  
- 🔬 기전 또는 작동 원리  
- 🧩 핵심 변수 또는 치료/요인  
- 📊 논문 비교 및 근거 요약  
- 🧾 결론  
- 🔗 출처 테이블  
### 🎯 연구 주제 커버 분야  
🔹 생명과학  
🔹 물리학, 천문학  
🔹 화학, 재료과학  
🔹 환경과학, 기후과학  
🔹 컴퓨터과학, 데이터과학  
🔹 심리학, 사회과학  
🔹 공학 및 응용기술  
### ⚡ 행동 기준  
1️⃣ 복잡한 연구 주제를 쉽게 설명  
2️⃣ 실용적이고 실현 가능한 연구 주제 제안  
3️⃣ 최신 연구 동향과 학계의 관심사 반영  
4️⃣ 명확하고 구체적인 조언 제공 (모호한 표현 금지)  
5️⃣ 학술적 표준과 관행을 따르는 논문 구조 제안  
6️⃣ 정확한 인용 형식 사용  
### 🚫 금지사항  
❌ 논문 제목, 저자, 연도 등을 임의로 생성 금지  
❌ 인용은 반드시 **API를 통해 가져온 실제 논문만 사용**"""
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config.OPENAI_API_KEY}"
    }
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            data=json.dumps(payload)
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            st.error(f"GPT API 오류: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        st.error(f"GPT API 오류: {str(e)}")
        time.sleep(1)
        return None

def analyze_topic(topic):
    """
    입력된 주제를 분석하여 정의, 의미, 문제점, 해결 사례 등을 제공합니다.
    """
    # 먼저 실제 논문 검색
    arxiv_papers = search_arxiv(topic, max_results=5)
    crossref_papers = search_crossref(topic, max_results=5)
    all_papers = merge_search_results(arxiv_papers, crossref_papers, max_total=7)
    
    # 검색된 논문 정보를 포함한 프롬프트 생성
    paper_info = ""
    if all_papers:
        paper_info = "다음은 해당 주제와 관련된 실제 논문 정보입니다:\n\n"
        for i, paper in enumerate(all_papers, 1):
            paper_info += f"{i}. 제목: {paper['title']}\n"
            paper_info += f"   저자: {paper['authors']}\n"
            paper_info += f"   발행: {paper['published']}\n"
            paper_info += f"   출처: {paper['source']}\n"
            if paper['summary'] and paper['summary'] != "요약 정보 없음":
                paper_info += f"   요약: {paper['summary']}\n"
            paper_info += "\n"
    
    prompt = f"""
    다음 연구 주제에 대해 상세히 분석해주세요: "{topic}"
    
    분석은 다음 구조로 작성해주세요:
    
    ## 🧠 개요
    [주제 정의 및 현재 연구 동향 개요]
    
    ## 🔬 기전 또는 작동 원리
    [주제와 관련된 핵심 과학적 원리 설명]
    
    ## 🧩 핵심 변수 또는 요인
    [주제를 이해하는 데 중요한 핵심 요소들]
    
    ## 📊 논문 비교 및 근거 요약
    [주요 연구 논문들의 결과 비교 및 주요 발견]
    
    ## 🧾 결론
    [현재 연구 상황 요약 및 향후 연구 방향 제안]
    
    ## 🔗 출처 테이블
    [정확한 인용 형식으로 출처 나열]
    
    {paper_info}
    
    실제 존재하는 논문만 인용하고, 가짜 논문이나 정보를 생성하지 마세요.
    제공된 논문 정보를 활용하여 분석해주세요.
    """
    
    # 로딩 표시
    with st.spinner("주제를 분석 중입니다..."):
        result = get_completion(prompt)
    
    # 반환 값을 정형화된 데이터로 변환
    if result:
        return {
            "full_text": result,
            "topic": topic,
            "papers": all_papers
        }
    else:
        return None

def extract_keywords(query, min_length=3, max_keywords=7):
    """
    검색어에서 핵심 키워드를 추출합니다.
    """
    # 특수문자 제거 및 소문자 변환
    cleaned_query = re.sub(r'[^\w\s]', ' ', query.lower())
    
    # 불용어 목록 (필요시 확장)
    stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    
    # 단어 분리 및 불용어/짧은 단어 제거
    words = [word for word in cleaned_query.split() if word not in stopwords and len(word) >= min_length]
    
    # 최대 키워드 수 제한
    return words[:max_keywords]

def search_arxiv(query, max_results=5):
    """
    arXiv API를 사용하여 학술 논문을 검색합니다.
    유사성을 높이기 위해 다양한 검색 방식을 시도합니다.
    """
    try:
        # 키워드 추출
        keywords = extract_keywords(query)
        
        # 키워드가 충분하지 않은 경우 원본 쿼리 사용
        if len(keywords) < 2:
            search_query = query
        else:
            # 다양한 검색 방식 시도
            search_queries = [
                # 원본 쿼리
                query,
                # AND 검색 (모든 키워드 포함)
                " AND ".join(keywords[:3]),
                # OR 검색 (넓은 범위)
                " OR ".join(keywords[:3])
            ]
            
            # 무작위로 하나 선택 (다양성 확보)
            import random
            search_query = random.choice(search_queries)
        
        # arXiv API 요청 URL
        url = f"http://export.arxiv.org/api/query?search_query=all:{search_query}&start=0&max_results={max_results}"
        
        # API 요청
        response = requests.get(url)
        
        if response.status_code == 200:
            # XML 파싱
            # 네임스페이스 정의
            namespaces = {
                'atom': 'http://www.w3.org/2005/Atom',
                'arxiv': 'http://arxiv.org/schemas/atom'
            }
            
            # XML 파싱
            root = ET.fromstring(response.content)
            
            # 결과 추출
            results = []
            for entry in root.findall('.//atom:entry', namespaces):
                title_elem = entry.find('atom:title', namespaces)
                title = title_elem.text.strip() if title_elem is not None else "제목 없음"
                
                summary_elem = entry.find('atom:summary', namespaces)
                summary = summary_elem.text.strip() if summary_elem is not None else "요약 없음"
                
                published_elem = entry.find('atom:published', namespaces)
                published = published_elem.text[:10] if published_elem is not None else "날짜 없음"
                
                # 저자 추출
                authors = []
                for author in entry.findall('.//atom:author/atom:name', namespaces):
                    authors.append(author.text)
                
                # PDF 링크 추출
                pdf_url = None
                for link in entry.findall('atom:link', namespaces):
                    if link.get('title') == 'pdf':
                        pdf_url = link.get('href')
                        break
                
                if pdf_url is None:
                    # 대체 링크 검색
                    for link in entry.findall('atom:link', namespaces):
                        if link.get('rel') == 'alternate':
                            pdf_url = link.get('href')
                            break
                
                # 결과 추가
                results.append({
                    'title': title,
                    'authors': ', '.join(authors),
                    'summary': summary[:300] + "..." if len(summary) > 300 else summary,
                    'published': published,
                    'url': pdf_url,
                    'source': 'arXiv'
                })
            
            return results
        else:
            st.error(f"arXiv API 오류: {response.status_code}")
            return []
    
    except Exception as e:
        st.error(f"arXiv 검색 오류: {str(e)}")
        return []

def search_crossref(query, max_results=5):
    """
    Crossref API를 사용하여 학술 논문을 검색합니다.
    """
    try:
        # 키워드 추출
        keywords = extract_keywords(query)
        
        # 검색 쿼리 준비
        if len(keywords) < 2:
            search_query = query
        else:
            search_query = " ".join(keywords[:3])
        
        # API 요청 URL
        email = getattr(config, 'CROSSREF_EMAIL', 'example@example.com')
        url = f"https://api.crossref.org/works?query={search_query}&rows={max_results}&mailto={email}"
        
        # API 요청
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            
            results = []
            if 'message' in data and 'items' in data['message']:
                for item in data['message']['items']:
                    # 제목 추출
                    title = "제목 없음"
                    if 'title' in item and item['title']:
                        title = item['title'][0]
                    
                    # 저자 추출
                    authors = []
                    if 'author' in item:
                        for author in item['author']:
                            name_parts = []
                            if 'given' in author:
                                name_parts.append(author['given'])
                            if 'family' in author:
                                name_parts.append(author['family'])
                            if name_parts:
                                authors.append(' '.join(name_parts))
                    
                    # 발행일 추출
                    published = "날짜 없음"
                    if 'published-print' in item and 'date-parts' in item['published-print']:
                        date_parts = item['published-print']['date-parts'][0]
                        if len(date_parts) >= 1:
                            published = str(date_parts[0])
                    
                    # URL 추출
                    url = None
                    if 'URL' in item:
                        url = item['URL']
                    
                    # 요약 (없는 경우가 많음)
                    summary = "요약 정보 없음"
                    if 'abstract' in item:
                        summary = item['abstract']
                    
                    # 결과 추가
                    results.append({
                        'title': title,
                        'authors': ', '.join(authors),
                        'summary': summary[:300] + "..." if len(summary) > 300 else summary,
                        'published': published,
                        'url': url,
                        'source': 'Crossref'
                    })
            
            return results
        else:
            st.error(f"Crossref API 오류: {response.status_code}")
            return []
    
    except Exception as e:
        st.error(f"Crossref 검색 오류: {str(e)}")
        return []

def merge_search_results(arxiv_results, crossref_results, max_total=10):
    """
    여러 API에서 가져온 검색 결과를 병합합니다.
    """
    # 결과 병합
    all_results = arxiv_results + crossref_results
    
    # 중복 제거 (제목 기준)
    unique_results = []
    seen_titles = set()
    
    for result in all_results:
        title_lower = result['title'].lower()
        # 짧은 제목 제외 (너무 일반적인 제목일 가능성)
        if len(title_lower) < 10:
            continue
            
        if title_lower not in seen_titles:
            seen_titles.add(title_lower)
            
            # 관련성 점수 계산
            score = 0
            
            # 특별히 원본 쿼리에서 중요 키워드 추출
            keywords = extract_keywords(result['title'])
            
            # 제목에 키워드가 많을수록 점수 증가
            for keyword in keywords:
                if keyword in title_lower:
                    score += 2
            
            # 요약이 있으면 점수 증가
            if result['summary'] and result['summary'] != "요약 정보 없음":
                score += 1
            
            # 저자 정보가 있으면 점수 증가
            if result['authors'] and result['authors'] != "":
                score += 1
            
            # URL이 있으면 점수 증가
            if result['url'] and result['url'] != "":
                score += 1
            
            # 점수 저장
            result['relevance_score'] = score
            
            unique_results.append(result)
    
    # 관련성 점수로 정렬
    sorted_results = sorted(unique_results, key=lambda x: x.get('relevance_score', 0), reverse=True)
    
    # 최대 개수만큼 반환
    return sorted_results[:max_total]

def generate_similar_topics(topic, count=5):
    """
    입력된 주제와 유사한 연구 주제를 생성합니다.
    추가로 실제 학술 검색 결과도 함께 제공합니다.
    """
    # 외부 API를 통한 실제 연구 검색
    with st.spinner("학술 데이터베이스에서 관련 연구를 검색 중입니다..."):
        try:
            # arXiv 검색
            arxiv_results = search_arxiv(topic, max_results=5)
            
            # Crossref 검색
            crossref_results = search_crossref(topic, max_results=5)
            
            # 결과 병합
            api_results = merge_search_results(arxiv_results, crossref_results, max_total=8)
        except Exception as e:
            st.error(f"학술 API 검색 오류: {str(e)}")
            api_results = []
    
    # 검색된 논문 정보를 프롬프트에 추가
    paper_info = ""
    if api_results:
        paper_info = "다음은 해당 주제와 관련된 실제 논문 정보입니다. 이를 참고하여 유사 주제를 생성해주세요:\n\n"
        for i, paper in enumerate(api_results, 1):
            paper_info += f"{i}. 제목: {paper['title']}\n"
            paper_info += f"   저자: {paper['authors']}\n"
            paper_info += f"   발행: {paper['published']}\n"
            paper_info += f"   출처: {paper['source']}\n"
            if paper['summary'] and paper['summary'] != "요약 정보 없음":
                paper_info += f"   요약: {paper['summary'][:150]}...\n"
            paper_info += "\n"
    
    # GPT를 통한 유사 주제 생성
    prompt = f"""
    다음 연구 주제와 관련된 유사하지만 독창적인 연구 주제 {count}개를 생성해주세요: "{topic}"
    
    {paper_info}
    
    각 주제는 다음 형식으로 제시해주세요:
    
    ## 주제 1: [주제명]
    **설명**: [주제에 대한 간략한 설명 및 연구 가치]
    **관련 논문**: [위 목록에서 관련 있는 논문 참조]
    
    ## 주제 2: [주제명]
    ...
    
    실제 논문을 기반으로 하되, 새롭고 독창적인 연구 주제를 제안해주세요.
    각 주제는 실행 가능하고, 명확하며, 구체적이어야 합니다.
    """
    
    with st.spinner("유사 주제를 생성 중입니다..."):
        ai_result = get_completion(prompt)
    
    # 최종 결과 반환
    return {
        "ai_generated": ai_result,
        "api_results": api_results
    }

def generate_paper_structure(topic):
    """
    선택된 주제에 대한 논문 구조를 생성합니다.
    """
    # 먼저 실제 논문 검색
    arxiv_papers = search_arxiv(topic, max_results=3)
    crossref_papers = search_crossref(topic, max_results=3)
    all_papers = merge_search_results(arxiv_papers, crossref_papers, max_total=5)
    
    # 검색된 논문 정보를 포함한 프롬프트 생성
    paper_info = ""
    if all_papers:
        paper_info = "다음은 해당 주제와 관련된 실제 논문 정보입니다. 이를 참고하여 논문 구조를 생성해주세요:\n\n"
        for i, paper in enumerate(all_papers, 1):
            paper_info += f"{i}. 제목: {paper['title']}\n"
            paper_info += f"   저자: {paper['authors']}\n"
            paper_info += f"   발행: {paper['published']}\n"
            paper_info += f"   출처: {paper['source']}\n"
            if paper['summary'] and paper['summary'] != "요약 정보 없음":
                paper_info += f"   요약: {paper['summary']}\n"
            paper_info += "\n"
    
    prompt = f"""
    다음 연구 주제에 대한 학술 논문 구조를 생성해주세요: "{topic}"
    
    {paper_info}
    
    논문은 다음 섹션을 포함해야 합니다:
    
    # [논문 제목]
    
    ## 초록
    [연구의 목적, 방법, 결과, 의의를 요약 (200-250단어)]
    
    ## 1. 서론
    ### 1.1 연구 배경
    ### 1.2 연구 목적 및 질문
    ### 1.3 연구의 중요성
    
    ## 2. 선행 연구 검토
    ### 2.1 이론적 배경
    ### 2.2 관련 연구 동향
    ### 2.3 연구 공백 및 본 연구의 위치
    
    ## 3. 연구 방법
    ### 3.1 연구 설계
    ### 3.2 데이터 수집 방법
    ### 3.3 분석 방법
    
    ## 4. 예상 결과
    ### 4.1 주요 발견
    ### 4.2 결과 해석
    
    ## 5. 결론 및 논의
    ### 5.1 연구 요약
    ### 5.2 연구의 의의
    ### 5.3 한계점 및 향후 연구 방향
    
    ## 참고문헌
    [실제 논문을 정확한 인용 형식으로 나열]
    
    각 섹션에 구체적인 내용을 작성해주세요. 실제 논문처럼 학술적이고 체계적이어야 합니다.
    참고문헌은 제공된 실제 논문을 포함하여 정확한 인용 형식으로 작성해주세요.
    """
    
    with st.spinner("논문 구조를 생성 중입니다... (약 1분 소요)"):
        result = get_completion(prompt, max_tokens=2500)
    
    if result:
        return {
            "content": result,
            "papers": all_papers
        }
    else:
        return None

def generate_niche_topics(topic, count=4):
    """
    선택된 주제와 관련된 틈새 연구 주제를 제안합니다.
    """
    # 먼저 실제 논문 검색
    arxiv_papers = search_arxiv(topic, max_results=3)
    crossref_papers = search_crossref(topic, max_results=3)
    all_papers = merge_search_results(arxiv_papers, crossref_papers, max_total=5)
    
    # 검색된 논문 정보를 포함한 프롬프트 생성
    paper_info = ""
    if all_papers:
        paper_info = "다음은 해당 주제와 관련된 실제 논문 정보입니다. 이를 참고하여 틈새 주제를 제안해주세요:\n\n"
        for i, paper in enumerate(all_papers, 1):
            paper_info += f"{i}. 제목: {paper['title']}\n"
            paper_info += f"   저자: {paper['authors']}\n"
            paper_info += f"   발행: {paper['published']}\n"
            paper_info += f"   출처: {paper['source']}\n"
            if paper['summary'] and paper['summary'] != "요약 정보 없음":
                paper_info += f"   요약: {paper['summary'][:150]}...\n"
            paper_info += "\n"
    
    prompt = f"""
    다음 연구 주제와 관련된 틈새 연구 주제 {count}개를 제안해주세요: "{topic}"
    
    {paper_info}
    
    틈새 주제란 아직 충분히 연구되지 않았지만 잠재적으로 가치 있는 연구 영역입니다.
    
    각 틈새 주제는 다음 형식으로 제시해주세요:
    
    ## 틈새 주제 1: [주제명]
    
    **배경**: [이 분야에서 현재까지의 연구 상황]
    
    **틈새 영역으로 고려되는 이유**: 
    [왜 이 주제가 충분히 연구되지 않았는지, 어떤 측면이 간과되고 있는지]
    
    **연구 가치와 영향력**: 
    [이 주제 연구가 학문적/실용적으로 어떤 가치가 있는지]
    
    **제안 연구 방법**: 
    [어떤 방법론과 접근 방식으로 연구할 수 있는지]
    
    **관련 논문**: 
    [위 목록에서 관련 있는 논문 참조]
    
    실제 논문을 기반으로 하되, 새롭고 혁신적인 연구 틈새를 찾아내주세요.
    각 틈새 주제는 실행 가능하고, 구체적이며, 학술적 가치가 있어야 합니다.
    """
    
    with st.spinner("틈새 주제를 생성 중입니다..."):
        result = get_completion(prompt)
    
    if result:
        return {
            "content": result,
            "papers": all_papers
        }
    else:
        return None
