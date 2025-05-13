import requests
import time
import arxiv
import config
from habanero import Crossref

def search_arxiv(query, max_results=config.MAX_ARXIV_RESULTS):
    """
    arXiv API를 사용하여 학술 논문을 검색합니다.
    """
    try:
        # arXiv 클라이언트 생성
        client = arxiv.Client()
        
        # 검색 쿼리 생성
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        # 결과 가져오기
        results = []
        for paper in client.results(search):
            results.append({
                'title': paper.title,
                'authors': ', '.join(author.name for author in paper.authors),
                'summary': paper.summary,
                'published': paper.published.strftime('%Y-%m-%d'),
                'url': paper.pdf_url,
                'source': 'arXiv'
            })
        
        return results
    
    except Exception as e:
        print(f"arXiv API 오류: {str(e)}")
        return []

def search_crossref(query, max_results=config.MAX_CROSSREF_RESULTS):
    """
    Crossref API를 사용하여 학술 논문을 검색합니다.
    """
    try:
        # Crossref 클라이언트 생성
        cr = Crossref(mailto=config.CROSSREF_EMAIL)
        
        # 검색 실행
        results = cr.works(query=query, limit=max_results)
        
        # 결과 파싱
        papers = []
        if 'message' in results and 'items' in results['message']:
            for item in results['message']['items']:
                # 기본 정보 추출
                title = item.get('title', ['제목 없음'])[0] if item.get('title') else '제목 없음'
                
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
                url = None
                if 'URL' in item:
                    url = item['URL']
                
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
                
                papers.append({
                    'title': title,
                    'authors': ', '.join(authors),
                    'summary': summary,
                    'published': published,
                    'url': url,
                    'source': 'Crossref'
                })
        
        return papers
    
    except Exception as e:
        print(f"Crossref API 오류: {str(e)}")
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
        if title_lower not in seen_titles:
            seen_titles.add(title_lower)
            unique_results.append(result)
    
    # 최대 개수만큼 반환
    return unique_results[:max_total]
