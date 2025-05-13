import requests
import json
import time
import config
import streamlit as st

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

def generate_similar_topics(topic, count=5):
    """
    입력된 주제와 유사한 연구 주제를 생성합니다.
    """
    prompt = f"""
    다음 연구 주제와 관련된 유사하지만 독창적인 연구 주제 {count}개를 생성해주세요: "{topic}"
    
    각 주제에 대해 간략한 설명(1-2문장)을 함께 제공해주세요.
    주제는 번호를 매겨서 리스트 형태로 제시해주세요.
    """
    
    with st.spinner("유사 주제를 생성 중입니다..."):
        result = get_completion(prompt)
    
    if result:
        # 여기서는 전체 텍스트를 반환하지만,
        # 필요시 파싱하여 리스트 형태로 반환 가능
        return result
    else:
        return None

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
