import pandas as pd
import os
import config

def load_isef_data():
    """
    ISEF 데이터셋을 로드합니다.
    """
    try:
        if os.path.exists(config.ISEF_DATA_PATH):
            df = pd.read_excel(config.ISEF_DATA_PATH)
            return df
        else:
            print(f"ISEF 데이터 파일을 찾을 수 없습니다: {config.ISEF_DATA_PATH}")
            return pd.DataFrame()  # 빈 데이터프레임 반환
    except Exception as e:
        print(f"ISEF 데이터 로드 오류: {str(e)}")
        return pd.DataFrame()

def search_similar_topics(df, query, max_results=10):
    """
    ISEF 데이터셋에서 유사한 주제를 검색합니다.
    """
    if df.empty:
        return []
    
    # 검색 쿼리 키워드 분리
    keywords = query.lower().split()
    
    # 제목 컬럼 이름 (실제 데이터셋에 맞게 조정 필요)
    title_column = "Title"  # 또는 실제 컬럼명으로 변경
    
    if title_column not in df.columns:
        # 첫 번째 컬럼을 제목으로 가정
        title_column = df.columns[0]
    
    # 점수 계산을 위한 컬럼 추가
    df['search_score'] = 0
    
    # 각 키워드에 대해 제목에 포함되어 있으면 점수 증가
    for keyword in keywords:
        df.loc[df[title_column].str.lower().str.contains(keyword, na=False), 'search_score'] += 1
    
    # 점수 기준으로 정렬하여 상위 결과 반환
    results = df.sort_values('search_score', ascending=False).head(max_results)
    
    # 필요한 정보만 추출하여 리스트로 변환
    similar_topics = []
    for _, row in results.iterrows():
        if row['search_score'] > 0:  # 최소 1개 이상의 키워드가 일치하는 경우만
            topic_info = {
                'title': row[title_column],
                'score': row['search_score'],
                'source': 'ISEF',
            }
            
            # 다른 컬럼도 있다면 추가
            for col in df.columns:
                if col != title_column and col != 'search_score':
                    topic_info[col.lower()] = row[col]
            
            similar_topics.append(topic_info)
    
    return similar_topics
