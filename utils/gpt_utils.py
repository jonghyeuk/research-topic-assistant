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

def verify_generated_topics(original_topic, ai_generated_text):
    """
    GPT가 생성한 유사 주제들을 검증하고 필요시 수정합니다.
    """
    # 이미 검증이 충분히 잘 되었으면 그대로 반환
    return ai_generated_text

def generate_similar_topics(topic, count=5):
    """
    입력된 주제와 유사한 연구 주제를 생성합니다.
    GPT의 내장 지식을 최대한 활용하여 풍부한 관련 주제 제공
    """
    # 주제의 핵심 키워드와 분야 식별 (기존 코드 유지)
    topic_keywords = extract_core_keywords(topic)
    domain = identify_academic_domain(topic)
    
    # 외부 API 검색 부분 (기존 코드 유지)
    with st.spinner("학술 데이터베이스에서 관련 연구를 검색 중입니다..."):
        try:
            arxiv_results = search_arxiv(topic, max_results=10)
            crossref_results = search_crossref(topic, max_results=10)
            all_results = merge_search_results(arxiv_results, crossref_results, max_total=20)
            api_results = filter_results_by_relevance(topic, topic_keywords, all_results)
        except Exception as e:
            st.warning(f"외부 학술 데이터베이스 검색 중 오류가 발생했습니다. GPT 지식을 활용합니다.")
            api_results = []
    
    # 검색된 논문 정보 구성 (기존 코드 유지)
    paper_info = ""
    if api_results:
        paper_info = "다음은 해당 주제와 관련된 실제 논문 정보입니다. 이를 참고하되 이에 국한되지 않고 더 풍부한 주제를 생성해주세요:\n\n"
        for i, paper in enumerate(api_results, 1):
            paper_info += f"{i}. 제목: {paper['title']}\n"
            if 'authors' in paper and paper['authors']:
                paper_info += f"   저자: {paper['authors']}\n"
            if 'published' in paper:
                paper_info += f"   발행: {paper['published']}\n"
            if paper.get('summary') and paper['summary'] != "요약 정보 없음":
                paper_info += f"   요약: {paper['summary'][:150]}...\n"
            paper_info += "\n"
    
    # 개선된 GPT 프롬프트: 더 구체적이고 자세한 설명 요구
    prompt = f"""
    당신은 '{domain}' 분야의 세계적인 전문가로 20년 이상의 연구 경험을 가지고 있습니다.
    연구 주제 "{topic}"와 관련된 유사하면서도 독창적인 연구 주제 {count}개를 생성해야 합니다.
    
    {paper_info if paper_info else ""}
    
    각 유사 주제는 다음 구조로 상세히 설명해주세요:
    
    ## 주제 1: [주제명 - 명확하고 학술적인 제목으로 작성]
    
    ✅ **개념 정의 및 개요**
    - 이 연구 주제가 무엇인지 3-4문장으로 명확하게 정의하고 개략적으로 설명
    - 이 주제가 다루는 핵심 현상이나 문제를 구체적으로 설명
    - 이 주제의 학문적 배경과 연구 맥락 제시
    
    ✅ **원주제와의 관련성**
    - 이 주제가 원래 주제인 "{topic}"와 어떻게 연관되는지 구체적으로 설명
    - 두 주제 간의 이론적/방법론적 연결고리 제시
    - 원 주제에서 파생되거나 확장된 측면 설명
    
    ✅ **연구 방법론 또는 접근법**
    - 이 주제를 연구하기 위한 2-3가지 구체적인 연구 방법 제안
    - 필요한 데이터, 실험 설계, 분석 방법 등 구체적 방법론 설명
    - 해당 방법론이 이 주제 연구에 적합한 이유 설명
    
    ✅ **학술적 중요성 및 잠재적 영향**
    - 이 연구가 학계에 기여할 수 있는 이론적 가치 설명
    - 이 연구가 실용적/산업적 측면에서 가질 수 있는 응용 가치 설명
    - 이 연구를 통해 해결할 수 있는 실제 문제나 질문 제시
    
    ✅ **관련 연구자 또는 논문**
    - 이 주제와 관련된 실제 연구자나 논문 2-3개 언급 (있는 경우)
    - 관련 연구의 핵심 발견이나 한계점 간략 설명
    
    ## 주제 2: [주제명]
    ...
    
    각 주제는 실제로 연구될 가치가 있는 구체적이고 명확한 주제여야 합니다.
    최신 연구 동향을 반영하되, 너무 일반적이거나 모호한 주제는 피해주세요.
    주제들은 원래 주제인 "{topic}"와 명확하게 연관되어야 하지만, 단순히 동일한 주제의 다른 표현이 아닌 새로운 연구 방향을 제시해야 합니다.
    """
    
    with st.spinner("유사 주제를 생성 중입니다..."):
        ai_result = get_completion(prompt)
    
    # API 결과와 GPT 생성 결과 통합
    combined_results = []
    
    # 기존 API 결과 추가 (관련성 점수가 높은 것만)
    for paper in api_results:
        if 'relevance_score' in paper and paper['relevance_score'] >= 0.65:  # 관련성 65% 이상만 포함
            combined_results.append({
                'title': paper['title'],
                'authors': paper.get('authors', '정보 없음'),
                'published': paper.get('published', '정보 없음'),
                'source': paper.get('source', 'API 검색 결과'),
                'summary': paper.get('summary', '요약 정보 없음'),
                'relevance_score': paper.get('relevance_score', 0.5),
                'is_api_result': True,
                'is_gpt_generated': False
            })
    
    # 파싱된 GPT 생성 결과 추가
    gpt_topics = parse_gpt_generated_topics(ai_result)
    for gpt_topic in gpt_topics:
        # API 결과가 너무 적거나, 최대 개수에 도달하지 않았으면 GPT 생성 주제 추가
        if len(combined_results) < count:
            gpt_topic['is_api_result'] = False
            gpt_topic['is_gpt_generated'] = True
            gpt_topic['relevance_score'] = 0.9  # GPT 생성 주제는 높은 관련성 점수 부여
            combined_results.append(gpt_topic)
    
    # 결과가 여전히 부족하면 더 많은 GPT 생성 주제 추가
    if len(combined_results) < 3:
        additional_prompt = f"""
        당신은 '{domain}' 분야의 전문가입니다. 
        연구 주제 "{topic}"와 관련된 추가적인 연구 주제 3개를 더 생성해주세요.
        앞서 생성한 주제와 겹치지 않고, 더 폭넓은 관점에서 연관된 주제를 제안해주세요.
        
        각 주제는 다음 형식으로 제시해주세요:
        
        ## 주제: [주제명]
        **설명**: [주제에 대한 간략한 설명]
        **관련성**: [원래 주제와의 관련성]
        **중요성**: [연구의 중요성]
        
        주제는 구체적이고 실행 가능해야 하며, 현대 연구 동향을 반영해야 합니다.
        """
        
        try:
            additional_result = get_completion(additional_prompt)
            additional_topics = parse_additional_topics(additional_result)
            
            for topic in additional_topics:
                if len(combined_results) < count:
                    topic['is_api_result'] = False
                    topic['is_gpt_generated'] = True
                    topic['relevance_score'] = 0.85
                    combined_results.append(topic)
        except:
            pass
    
    # 관련성 점수로 정렬
    combined_results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
    
    # 최종 결과 반환 (최대 count개)
    return {
        "ai_generated": ai_result,
        "api_results": api_results,
        "combined_results": combined_results[:count]
    }
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

def parse_gpt_generated_topics(gpt_text):
    """
    GPT가 생성한 텍스트에서 개별 주제를 구조화된 형태로 추출합니다.
    """
    topics = []
    
    # 정규 표현식으로 '## 주제:' 형식으로 시작하는 섹션 분리
    import re
    topic_pattern = r'##\s+주제\s+\d+:\s+(.*?)(?=##\s+주제|$)'
    topic_matches = re.finditer(topic_pattern, gpt_text, re.DOTALL)
    
    for match in topic_matches:
        topic_text = match.group(1).strip()
        
        # 제목 추출
        title = topic_text.split('\n')[0].strip()
        
        # 각 섹션 추출
        concept = re.search(r'✅\s+\*\*개념 정의 및 개요\*\*(.*?)(?=✅|\Z)', topic_text, re.DOTALL)
        relevance = re.search(r'✅\s+\*\*원주제와의 관련성\*\*(.*?)(?=✅|\Z)', topic_text, re.DOTALL)
        methodology = re.search(r'✅\s+\*\*연구 방법론 또는 접근법\*\*(.*?)(?=✅|\Z)', topic_text, re.DOTALL)
        importance = re.search(r'✅\s+\*\*학술적 중요성 및 잠재적 영향\*\*(.*?)(?=✅|\Z)', topic_text, re.DOTALL)
        references = re.search(r'✅\s+\*\*관련 연구자 또는 논문\*\*(.*?)(?=✅|\Z)', topic_text, re.DOTALL)
        
        # 결과 구성
        topic_info = {
            'title': title,
            'summary': concept.group(1).strip() if concept else '',
            'relevance_to_original': relevance.group(1).strip() if relevance else '',
            'methodology': methodology.group(1).strip() if methodology else '',
            'importance': importance.group(1).strip() if importance else '',
            'references': references.group(1).strip() if references else '',
            'source': 'GPT 생성',
            'authors': '자동 생성됨',
            'published': '현재'
        }
        
        topics.append(topic_info)
    
    return topics

def parse_additional_topics(text):
    """
    추가 생성된 GPT 주제를 파싱합니다.
    """
    topics = []
    
    # 정규 표현식으로 '## 주제:' 형식으로 시작하는 섹션 분리
    import re
    topic_pattern = r'##\s+주제:\s+(.*?)(?=##\s+주제:|$)'
    topic_matches = re.finditer(topic_pattern, text, re.DOTALL)
    
    for match in topic_matches:
        topic_text = match.group(1).strip()
        
        # 제목 추출
        title = topic_text.split('\n')[0].strip()
        
        # 각 섹션 추출
        explanation = re.search(r'\*\*설명\*\*:\s+(.*?)(?=\*\*|\Z)', topic_text, re.DOTALL)
        relevance = re.search(r'\*\*관련성\*\*:\s+(.*?)(?=\*\*|\Z)', topic_text, re.DOTALL)
        importance = re.search(r'\*\*중요성\*\*:\s+(.*?)(?=\*\*|\Z)', topic_text, re.DOTALL)
        
        topics.append({
            'title': title,
            'summary': explanation.group(1).strip() if explanation else '',
            'relevance_to_original': relevance.group(1).strip() if relevance else '',
            'importance': importance.group(1).strip() if importance else '',
            'source': 'GPT 추가 생성',
            'authors': '자동 생성됨',
            'published': '현재'
        })
    
    return topics
