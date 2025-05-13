import requests
import json
import time
import config
import streamlit as st
import re

def get_completion(prompt, model=config.GPT_MODEL, temperature=config.TEMPERATURE, max_tokens=config.MAX_TOKENS):
    """
    GPT 모델로부터 응답을 받아옵니다. OpenAI 라이브러리 대신 직접 API 호출을 사용합니다.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config.OPENAI_API_KEY}"
    }
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "당신은 연구 주제 선정을 돕는 AI 보조입니다."},
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
    prompt = f"""
    다음 연구 주제에 대해 상세히 분석해주세요: "{topic}"
    
    다음 형식으로 구조화된 분석을 제공해주세요:
    
    1. 주제 정의: 이 주제가 무엇인지 명확하게 정의
    2. 현재 의미: 이 주제가 현재 학계/산업에서 갖는 의미와 중요성
    3. 과학적/사회적 문제: 이 주제와 관련된 주요 문제 및 이슈
    4. 해결 사례/현재 상황: 주요 연구 사례나 현재까지의 발전 상황
    5. 출처 및 참고자료: 관련 연구나 문헌 (저자, 제목, 연도 포함)
    
    깊이 있는 분석을 제공해주세요.
    """
    
    # 로딩 표시
    with st.spinner("주제를 분석 중입니다..."):
        result = get_completion(prompt)
    
    # 반환 값을 정형화된 데이터로 변환 (예시)
    if result:
        # 여기서는 간단하게 전체 텍스트를 반환하지만,
        # 필요시 섹션별로 파싱하여 구조화된 데이터로 반환 가능
        return {
            "full_text": result,
            "topic": topic
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
            # XML 파싱 (간단한 방식)
            import xml.etree.ElementTree as ET
            
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
    # GPT를 통한 유사 주제 생성
    prompt = f"""
    다음 연구 주제와 관련된 유사하지만 독창적인 연구 주제 {count}개를 생성해주세요: "{topic}"
    
    각 주제에 대해 간략한 설명(1-2문장)을 함께 제공해주세요.
    주제는 번호를 매겨서 리스트 형태로 제시해주세요.
    """
    
    with st.spinner("유사 주제를 생성 중입니다..."):
        ai_result = get_completion(prompt)
    
    # 외부 API를 통한 실제 연구 검색
    with st.spinner("학술 데이터베이스에서 관련 연구를 검색 중입니다..."):
        try:
            # arXiv 검색
            arxiv_results = search_arxiv(topic, max_results=3)
            
            # Crossref 검색
            crossref_results = search_crossref(topic, max_results=3)
            
            # 결과 병합
            api_results = merge_search_results(arxiv_results, crossref_results, max_total=6)
        except Exception as e:
            st.error(f"학술 API 검색 오류: {str(e)}")
            api_results = []
    
    # 각 학술 데이터베이스에서 검색 결과가 없는 경우
    if not api_results:
        # GPT API로 대체 결과 생성
        with st.spinner("추가 유사 주제를 생성 중입니다..."):
            prompt_extra = f"""
            다음 연구 주제와 관련된 실제 존재하는 학술 논문 제목과 저자, 발행년도를 {count}개 생성해주세요: "{topic}"
            
            다음 형식으로 작성해주세요:
            1. "논문 제목" - 저자명 (발행년도)
            2. "논문 제목" - 저자명 (발행년도)
            ...
            
            최신 연구 동향을 반영하고, 다양한 학술지나 컨퍼런스에서 발표된 논문을 포함해주세요.
            """
            extra_results = get_completion(prompt_extra)
            
            # 형식화된 대체 결과 생성
            api_results = []
            lines = extra_results.strip().split('\n')
            for line in lines:
                if not line.strip():
                    continue
                    
                # 기본 형식: 번호. "제목" - 저자 (연도)
                try:
                    parts = line.split('"')
                    if len(parts) >= 2:
                        title = parts[1].strip()
                        rest = parts[2].strip()
                        
                        author_year = rest.split('(')
                        author = author_year[0].replace('-', '').strip()
                        year = author_year[1].replace(')', '').strip() if len(author_year) > 1 else "N/A"
                        
                        api_results.append({
                            'title': title,
                            'authors': author,
                            'published': year,
                            'summary': "GPT 생성 추천 논문 (실제 논문과 일치하지 않을 수 있습니다)",
                            'url': "",
                            'source': 'GPT 추천'
                        })
                except:
                    # 파싱 오류시 그냥 넘어감
                    continue
    
    # 최종 결과 반환
    return {
        "ai_generated": ai_result,
        "api_results": api_results
    }

def generate_paper_structure(topic):
    """
    선택된 주제에 대한 논문 구조를 생성합니다.
    """
    prompt = f"""
    다음 연구 주제에 대한 학술 논문 구조를 생성해주세요: "{topic}"
    
    다음 섹션을 포함하는 상세한 논문 구조를 작성해주세요:
    
    1. 제목: 명확하고 구체적인 논문 제목
    2. 초록: 연구의 목적, 방법, 결과, 의의를 요약 (200-250단어)
    3. 서론: 연구 배경, 중요성, 연구 질문, 가설 등을 설명
    4. 실험 방법: 제안된 연구 방법 및 실험 설계 상세 설명
    5. 예상 결과: 실험을 통해 얻을 수 있는 예상 결과 설명
    6. 결론: 연구의 의의와 향후 연구 방향 제시
    7. 참고문헌: 관련 연구 5-7개 (형식: 저자, 제목, 저널명, 연도)
    
    각 섹션은 실제 논문처럼 구체적이고 학술적인 내용으로 작성해주세요.
    """
    
    with st.spinner("논문 구조를 생성 중입니다... (약 1분 소요)"):
        result = get_completion(prompt, max_tokens=2500)
    
    if result:
        return result
    else:
        return None

def generate_niche_topics(topic, count=4):
    """
    선택된 주제와 관련된 틈새 연구 주제를 제안합니다.
    """
    prompt = f"""
    다음 연구 주제와 관련된 틈새 연구 주제 {count}개를 제안해주세요: "{topic}"
    
    틈새 주제란 아직 충분히 연구되지 않았지만 잠재적으로 가치 있는 연구 영역입니다.
    각 틈새 주제에 대해:
    1. 주제명 (간결하게)
    2. 틈새 영역으로 고려되는 이유
    3. 이 주제 연구의 잠재적 영향력
    4. 연구 방법 제안
    
    각 틈새 주제는 독창적이고 실행 가능해야 합니다.
    """
    
    with st.spinner("틈새 주제를 생성 중입니다..."):
        result = get_completion(prompt)
    
    if result:
        return result
    else:
        return None
