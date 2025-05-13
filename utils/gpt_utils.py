import requests
import time
import arxiv
import config
from habanero import Crossref
import re

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

def generate_query_variations(query):
    """
    검색어로부터 여러 변형을 생성합니다.
    """
    variations = []
    
    # 원본 쿼리 추가
    variations.append(query)
    
    # 키워드 추출
    keywords = extract_keywords(query)
    
    # 키워드 조합 (AND 연결)
    if len(keywords) >= 2:
        variations.append(" AND ".join(keywords))
    
    # 주요 키워드만 사용 (처음 3개)
    if len(keywords) >= 3:
        variations.append(" ".join(keywords[:3]))
    
    # 모든 키워드 OR 연결 (넓은 검색)
    if len(keywords) >= 2:
        variations.append(" OR ".join(keywords))
    
    return variations

def search_arxiv(query, max_results=config.MAX_ARXIV_RESULTS):
    """
    arXiv API를 사용하여 학술 논문을 검색합니다.
    유사성을 높이기 위해 다양한 쿼리 변형을 시도합니다.
    """
    all_results = []
    seen_titles = set()  # 중복 제거용
    
    try:
        # 쿼리 변형 생성
        query_variations = generate_query_variations(query)
        
        # arXiv 클라이언트 생성
        client = arxiv.Client()
        
        # 각 쿼리 변형으로 검색
        for variation in query_variations:
            try:
                # 검색 쿼리 생성
                search = arxiv.Search(
                    query=variation,
                    max_results=max_results // len(query_variations) + 1,  # 각 변형당 결과 수 분배
                    sort_by=arxiv.SortCriterion.Relevance
                )
                
                # 결과 가져오기
                for paper in client.results(search):
                    title = paper.title.lower()
                    
                    # 중복 확인
                    if title not in seen_titles:
                        seen_titles.add(title)
                        all_results.append({
                            'title': paper.title,
                            'authors': ', '.join(author.name for author in paper.authors),
                            'summary': paper.summary[:300] + "..." if len(paper.summary) > 300 else paper.summary,
                            'published': paper.published.strftime('%Y-%m-%d'),
                            'url': paper.pdf_url,
                            'source': 'arXiv'
                        })
            except Exception as e:
                print(f"arXiv 검색 변형 '{variation}' 오류: {str(e)}")
                continue
        
        return all_results
    
    except Exception as e:
        print(f"arXiv API 오류: {str(e)}")
        return []

def search_crossref(query, max_results=config.MAX_CROSSREF_RESULTS):
    """
    Crossref API를 사용하여 학술 논문을 검색합니다.
    유사성을 높이기 위해 다양한 쿼리 변형을 시도합니다.
    """
    all_results = []
    seen_titles = set()  # 중복 제거용
    
    try:
        # 쿼리 변형 생성
        query_variations = generate_query_variations(query)
        
        # Crossref 클라이언트 생성
        cr = Crossref(mailto=config.CROSSREF_EMAIL)
        
        # 각 쿼리 변형으로 검색
        for variation in query_variations:
            try:
                # 검색 실행
                results = cr.works(query=variation, limit=max_results // len(query_variations) + 1)
                
                # 결과 파싱
                if 'message' in results and 'items' in results['message']:
                    for item in results['message']['items']:
                        # 기본 정보 추출
                        title = item.get('title', ['제목 없음'])[0] if item.get('title') else '제목 없음'
                        title_lower = title.lower()
                        
                        # 중복 확인
                        if title_lower not in seen_titles:
                            seen_titles.add(title_lower)
                            
                            # 저자 정보 추출
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
                            
                            # URL 추출
                            url = item.get('URL', None)
                            
                            # 발행 정보
                            published = None
                            if 'created' in item and 'date-parts' in item['created']:
                                date_parts = item['created']['date-parts'][0]
                                if len(date_parts) >= 1:
                                    published = str(date_parts[0])
                                    if len(date_parts) >= 3:
                                        published = f"{date_parts[0]}-{date_parts[1]:02d}-{date_parts[2]:02d}"
                            
                            # 요약 정보 (abstract)
                            summary = item.get('abstract', '요약 정보 없음')
                            if isinstance(summary, list) and summary:
                                summary = summary[0]
                            
                            # 결과 추가
                            all_results.append({
                                'title': title,
                                'authors': ', '.join(authors),
                                'summary': summary[:300] + "..." if len(summary) > 300 else summary,
                                'published': published,
                                'url': url,
                                'source': 'Crossref'
                            })
            except Exception as e:
                print(f"Crossref 검색 변형 '{variation}' 오류: {str(e)}")
                continue
        
        return all_results
    
    except Exception as e:
        print(f"Crossref API 오류: {str(e)}")
        return []

def search_semantic_scholar(query, max_results=5):
    """
    Semantic Scholar API를 사용하여 학술 논문을 검색합니다.
    유사성을 높이기 위해 키워드 기반 검색을 수행합니다.
    이 함수는 선택적으로 추가할 수 있습니다.
    """
    all_results = []
    seen_titles = set()
    
    try:
        # API 키가 있는 경우 헤더에 추가
        headers = {}
        if hasattr(config, 'SEMANTIC_SCHOLAR_API_KEY') and config.SEMANTIC_SCHOLAR_API_KEY:
            headers["x-api-key"] = config.SEMANTIC_SCHOLAR_API_KEY
        
        # 키워드 추출
        keywords = extract_keywords(query)
        
        # 키워드를 사용하여 검색
        search_query = " ".join(keywords)
        
        # API 요청
        url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={search_query}&limit={max_results}&fields=title,authors,abstract,url,year"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'data' in data:
                for item in data['data']:
                    title = item.get('title', '제목 없음')
                    title_lower = title.lower()
                    
                    # 중복 확인
                    if title_lower not in seen_titles:
                        seen_titles.add(title_lower)
                        
                        # 저자 정보
                        authors = []
                        if 'authors' in item:
                            for author in item['authors']:
                                authors.append(author.get('name', ''))
                        
                        # 요약 및 기타 정보
                        summary = item.get('abstract', '요약 정보 없음')
                        year = item.get('year', None)
                        paper_url = item.get('url', None)
                        
                        # 결과 추가
                        all_results.append({
                            'title': title,
                            'authors': ', '.join(authors),
                            'summary': summary[:300] + "..." if len(summary) > 300 else summary,
                            'published': str(year) if year else None,
                            'url': paper_url,
                            'source': 'Semantic Scholar'
                        })
        
        return all_results
    
    except Exception as e:
        print(f"Semantic Scholar API 오류: {str(e)}")
        return []

def calculate_relevance_score(item, query):
    """
    검색 결과와 원래 쿼리의 관련성 점수를 계산합니다.
    """
    score = 0
    keywords = extract_keywords(query)
    
    # 제목에서 키워드 검색
    title = item['title'].lower()
    for keyword in keywords:
        if keyword in title:
            score += 3  # 제목에 있으면 높은 점수
    
    # 요약에서 키워드 검색
    summary = item.get('summary', '').lower()
    for keyword in keywords:
        if keyword in summary:
            score += 1  # 요약에 있으면 낮은 점수
    
    # 저자 정보에서 키워드 검색 (연구 주제와 직접 관련된 저자 가중치)
    authors = item.get('authors', '').lower()
    for keyword in keywords:
        if keyword in authors:
            score += 0.5
    
    return score

def merge_search_results(arxiv_results, crossref_results, semantic_scholar_results=None, max_total=10):
    """
    여러 API에서 가져온 검색 결과를 병합하고 관련성에 따라 정렬합니다.
    """
    # 모든 결과 병합
    all_results = arxiv_results + crossref_results
    if semantic_scholar_results:
        all_results += semantic_scholar_results
    
    # 중복 제거
    unique_results = []
    seen_titles = set()
    
    for result in all_results:
        title_lower = result['title'].lower()
        if title_lower not in seen_titles:
            seen_titles.add(title_lower)
            unique_results.append(result)
    
    # 결과가 없으면 빈 리스트 반환
    if not unique_results:
        return []
    
    # 관련성 점수 계산 및 정렬
    for item in unique_results:
        # 여기서는 원본 쿼리를 사용할 수 없으므로 단순히 출처에 따른 가중치 적용
        if item['source'] == 'arXiv':
            item['relevance'] = 3  # arXiv 결과 우선
        elif item['source'] == 'Semantic Scholar':
            item['relevance'] = 2  # 다음은 Semantic Scholar
        else:
            item['relevance'] = 1  # Crossref는 마지막
        
        # 제목 길이 가중치 (너무 짧거나 긴 제목 페널티)
        title_length = len(item['title'])
        if 10 <= title_length <= 100:
            item['relevance'] += 1
        
        # 발행일이 있는 경우 가중치
        if item.get('published'):
            item['relevance'] += 0.5
    
    # 관련성 점수로 정렬
    sorted_results = sorted(unique_results, key=lambda x: x.get('relevance', 0), reverse=True)
    
    # 최대 개수만큼 반환
    return sorted_results[:max_total]
