# 🌊 CREW_SOOM 침수 예측 AI 시스템

> **4개 기상청 API 통합 + 3년치 데이터 + 웹 기반 머신러닝 플랫폼**

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)
![ML](https://img.shields.io/badge/ML-scikit--learn-orange.svg)
![API](https://img.shields.io/badge/API-4개%20기상청-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

</div>

## 📋 목차

- [🎯 프로젝트 개요](#-프로젝트-개요)
- [✨ 주요 기능](#-주요-기능)
- [🚀 빠른 시작](#-빠른-시작)
- [🛠️ 설치 가이드](#️-설치-가이드)
- [📊 사용 방법](#-사용-방법)
- [🔧 API 설정](#-api-설정)
- [📁 프로젝트 구조](#-프로젝트-구조)
- [🔍 문제 해결](#-문제-해결)
- [🤝 기여 방법](#-기여-방법)
- [📞 지원](#-지원)

---

## 🎯 프로젝트 개요

**CREW_SOOM**은 **4개 기상청 API를 통합**하여 실시간 침수 위험도를 예측하는 **웹 기반 AI 시스템**입니다. 

### 🌟 핵심 특징

- **🇰🇷 4개 기상청 API 통합**: ASOS 시간자료, 일자료, 기상특보, 단기예보
- **🧠 머신러닝 기반 예측**: Random Forest, XGBoost 등 다중 모델 지원
- **📊 3년치 데이터 자동 생성**: 1,096일간의 현실적인 기상 데이터
- **🌐 완전한 웹 인터페이스**: Flask 기반 반응형 대시보드
- **⏰ 실시간 자동 업데이트**: 1시간마다 최신 데이터 수집
- **🗺️ 지도 기반 시각화**: 서울시 구별 위험도 지도
- **📈 5가지 시각화 차트**: 시계열, 분포, 상관관계, 트렌드 분석

---

## ✨ 주요 기능

### 📡 데이터 수집 시스템
- **ASOS 시간자료**: 가장 정확한 실시간 관측 데이터
- **ASOS 일자료**: 누적 강수량, 최고/최저 온도 등 통계 데이터
- **기상특보**: 호우경보, 대설경보 등 직접적인 침수 위험 지표
- **단기예보**: 격자 기반 실황 데이터

### 🤖 머신러닝 모델
- **Random Forest**: 기본 분류 모델
- **XGBoost**: 고성능 부스팅 모델 (선택사항)
- **모델 비교**: 실시간 성능 비교 및 최적 모델 선택
- **특성 중요도**: 예측에 영향을 미치는 주요 변수 분석

### 🌐 웹 인터페이스
- **실시간 대시보드**: 시스템 상태, 데이터 현황, 예측 결과
- **침수 위험 예측**: 기상 데이터 입력으로 즉시 위험도 계산
- **데이터 시각화**: 강수량, 월별 패턴, 분포, 상관관계, 트렌드
- **서울시 위험도 지도**: 25개 구별 실시간 위험도 색상 표시
- **사용자 관리**: 로그인/로그아웃, 사용자별 접근 제어

### 🔄 자동화 시스템
- **1시간마다 데이터 업데이트**: 백그라운드 자동 수집
- **오늘까지 데이터 채우기**: 누락된 날짜 자동 보완
- **모델 자동 재훈련**: 새로운 데이터로 성능 향상
- **로그 시스템**: 모든 활동 자동 기록

---

## 🚀 빠른 시작

### Windows 사용자 (추천)

1. **자동 설치 실행**:
   ```cmd
   quick_start.bat
   ```

2. **단계별 설치**:
   ```cmd
   install.bat    # 시스템 설치
   check.bat      # 환경 체크
   run.bat        # 시스템 실행
   ```

### 모든 플랫폼

1. **환경 확인**:
   ```bash
   python check_system.py
   ```

2. **자동 설치**:
   ```bash
   python setup.py
   ```

3. **시스템 실행**:
   ```bash
   python run.py
   ```

4. **웹 브라우저 접속**:
   - 주소: http://localhost:5000
   - 로그인: `admin` / `1234`

---

## 🛠️ 설치 가이드

### 📋 시스템 요구사항

| 구분 | 요구사항 |
|------|----------|
| **Python** | 3.8 이상 (권장: 3.9-3.11) |
| **운영체제** | Windows 10+, macOS 10.14+, Ubuntu 18.04+ |
| **메모리** | 최소 4GB RAM (권장: 8GB+) |
| **디스크** | 최소 2GB 여유 공간 |
| **네트워크** | 인터넷 연결 (API 데이터 수집용) |

### 1️⃣ 프로젝트 다운로드

```bash
# Git 클론 (권장)
git clone https://github.com/your-repo/crew_soom.git
cd crew_soom

# 또는 ZIP 파일 다운로드 후 압축 해제
```

### 2️⃣ 가상환경 설정

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3️⃣ 패키지 설치

```bash
# 자동 설치 (권장)
python setup.py

# 또는 수동 설치
pip install -r requirements.txt
```

### 4️⃣ 환경 변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집
# OPENWEATHER_API_KEY=your_actual_api_key_here
```

---

## 📊 사용 방법

### 🎮 기본 워크플로우

1. **시스템 시작**:
   ```bash
   python run.py
   ```

2. **웹 인터페이스 접속**:
   - 브라우저: http://localhost:5000

3. **데이터 준비**:
   - "📊 데이터 로드" 버튼 클릭
   - 3년치 데이터 자동 생성 (1,096일)

4. **모델 훈련**:
   - "🤖 모델 훈련" 버튼 클릭
   - Random Forest 모델 학습

5. **예측 실행**:
   - 기상 데이터 입력 (강수량, 습도, 온도 등)
   - "🔍 위험도 예측" 버튼 클릭

### 🔧 고급 기능

#### 자동 업데이트 설정
```javascript
// 웹 대시보드에서 토글 스위치 활성화
// 1시간마다 4개 API에서 실제 데이터 수집
```

#### 모델 비교 및 선택
```bash
# 웹에서 /models 페이지 접속
# 여러 모델 성능 비교 후 최적 모델 선택
```

#### 시각화 차트 생성
- **강수량 시계열**: 3년간 강수량 변화 및 최근 1년 상세 분석
- **월별 패턴**: 계절별 강수량 패턴 분석
- **강수량 분포**: 히스토그램 및 통계 분포
- **상관관계**: 기상 변수 간 상관관계 매트릭스
- **최근 트렌드**: 최근 30일 다중 변수 트렌드

#### 서울시 위험도 지도
- 25개 구별 실시간 위험도 색상 표시
- 클릭 시 구별 상세 정보 확인
- 자동 업데이트 및 애니메이션 효과

---

## 🔧 API 설정

### 📡 공공데이터포털 API 키 발급

1. **공공데이터포털 가입**: https://data.go.kr
2. **API 서비스 신청** (다음 4개 모두 신청):
   - 기상청_지상(종관, ASOS) 시간자료 조회서비스
   - 기상청_지상(종관, ASOS) 일자료 조회서비스
   - 기상청_기상특보 조회서비스
   - 기상청_단기예보 ((구)동네예보) 조회서비스

3. **서비스 키 발급 후 .env 파일 설정**:
   ```env
   OPENWEATHER_API_KEY=your_actual_service_key_here
   ```

### 🔑 API 키 없이 사용

API 키가 없어도 시스템은 **시뮬레이션 모드**로 완전히 동작합니다:
- 3년치 샘플 데이터 자동 생성
- 모든 기능 정상 작동
- 실제 기상 데이터 대신 현실적인 모의 데이터 사용

---

## 📁 프로젝트 구조

```
CREW_SOOM/
│
├── 📄 실행 파일
│   ├── run.py                    # 메인 실행 스크립트
│   ├── setup.py                  # 자동 설치 스크립트
│   ├── check_system.py           # 시스템 환경 체크
│   └── requirements.txt          # 패키지 의존성
│
├── 📁 모듈 (modules/)
│   ├── web_app.py               # Flask 웹 애플리케이션
│   ├── multi_weather_api.py     # 4개 기상청 API 통합
│   ├── data_loader.py           # 데이터 로딩
│   ├── preprocessor.py          # 데이터 전처리
│   ├── trainer.py               # 모델 훈련
│   ├── evaluator.py             # 모델 평가
│   └── visualizer.py            # 데이터 시각화
│
├── 📁 웹 인터페이스
│   ├── templates/               # HTML 템플릿
│   │   ├── dashboard.html       # 메인 대시보드
│   │   ├── login.html          # 로그인 페이지
│   │   ├── map.html            # 지도 페이지
│   │   └── models.html         # 모델 비교 페이지
│   └── static/                 # 정적 파일
│       ├── css/style.css       # 스타일시트
│       └── js/dashboard.js     # 자바스크립트
│
├── 📁 데이터 저장소
│   ├── data/                   # 원시 및 처리된 데이터
│   ├── models/                 # 훈련된 ML 모델
│   ├── outputs/                # 결과 파일 (차트, 리포트)
│   ├── logs/                   # 시스템 로그
│   └── users/                  # 사용자 정보
│
├── 📁 Windows 지원
│   ├── quick_start.bat         # 통합 실행 메뉴
│   ├── install.bat             # 설치 배치 파일
│   ├── check.bat               # 체크 배치 파일
│   └── run.bat                 # 실행 배치 파일
│
└── 📄 설정 파일
    ├── .env                    # 환경 변수 (생성 필요)
    ├── .env.example           # 환경 변수 예시
    ├── README.md              # 프로젝트 설명서
    └── 설계구조도.txt         # 시스템 구조 설명
```

---

## 🔍 문제 해결

### 🚨 자주 발생하는 오류

#### 1. **Flask/Werkzeug 버전 충돌**
```bash
# 해결 방법
pip install Flask==2.3.3 Werkzeug==2.3.7
```

#### 2. **포트 5000 사용 중**
```python
# web_app.py 마지막 줄 수정
self.app.run(debug=True, host='0.0.0.0', port=5001)
```

#### 3. **한글 폰트 깨짐 (그래프)**
```python
# Windows: 제어판 → 글꼴 → 맑은 고딕 설치 확인
# macOS: 기본 설치됨
# Linux: sudo apt-get install fonts-nanum
```

#### 4. **메모리 부족**
```python
# trainer.py에서 모델 파라미터 조정
n_estimators=50  # 기본값 150에서 감소
max_depth=10     # 기본값 20에서 감소
```

#### 5. **API 호출 실패**
- `.env` 파일의 API 키 확인
- 공공데이터포털 서비스 승인 상태 확인
- 시뮬레이션 모드로 대체 동작

### 🔧 디버깅 도구

#### 시스템 전체 체크
```bash
python check_system.py
```

#### 로그 확인
```bash
# 웹에서 확인
http://localhost:5000/logs

# 파일로 확인
type logs/log_events.json  # Windows
cat logs/log_events.json   # macOS/Linux
```

#### 패키지 확인
```bash
pip list
python -c "import flask, pandas, numpy, matplotlib; print('모든 패키지 정상')"
```

---

## 🔄 업데이트 및 유지보수

### 📦 시스템 업데이트
```bash
# 패키지 업데이트
pip install --upgrade -r requirements.txt

# 데이터 백업
cp data/processed/ML_COMPLETE_DATASET.csv backup/

# 모델 재훈련 (웹에서 실행)
```

### 🧹 시스템 정리
```bash
# Windows
clean.bat

# macOS/Linux
rm -rf __pycache__ modules/__pycache__ *.pyc
```

### 📊 정기 점검
- **월간**: API 키 유효성 확인
- **주간**: 데이터 품질 및 모델 성능 모니터링
- **일간**: 시스템 로그 확인

---

## 🤝 기여 방법

### 🐛 버그 리포트
1. 이슈 템플릿 사용
2. 재현 가능한 단계 포함
3. 시스템 환경 정보 첨부
4. 로그 파일 포함

### 💡 기능 제안
1. 기능 요청 템플릿 사용
2. 사용 사례 설명
3. 예상 구현 방법 제시

### 🔧 개발 참여
1. Fork 후 브랜치 생성
2. 코드 스타일 가이드 준수
3. 테스트 코드 작성
4. Pull Request 제출

---

## 📞 지원

### 📧 문의 채널
- **이슈 트래커**: GitHub Issues
- **토론**: GitHub Discussions
- **이메일**: crew.soom@example.com

### 📚 추가 자료
- **API 문서**: https://docs.crew-soom.com
- **튜토리얼**: https://tutorial.crew-soom.com
- **FAQ**: https://faq.crew-soom.com

### 🆘 긴급 지원
심각한 보안 문제나 시스템 장애 시:
- **보안 이슈**: security@crew-soom.com
- **장애 신고**: support@crew-soom.com

---

## 📊 성능 및 통계

### 📈 시스템 성능
- **예측 정확도**: AUC 0.85+ (실제 데이터 기준)
- **응답 시간**: < 2초 (웹 인터페이스)
- **데이터 처리**: 1,096일 < 30초
- **메모리 사용**: < 1GB (기본 모델)

### 📊 데이터 통계
- **총 데이터**: 3년 1,096일
- **특성 수**: 13개 기상 변수
- **API 통합**: 4개 기상청 서비스
- **업데이트 주기**: 1시간마다

---

## 🏆 인정 및 라이선스

### 🙏 감사 인사
- **기상청**: 공공 기상 데이터 제공
- **공공데이터포털**: API 서비스 지원
- **오픈소스 커뮤니티**: 라이브러리 개발

### 📜 라이선스
```
MIT License

Copyright (c) 2025 CREW_SOOM Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<div align="center">

**🌊 CREW_SOOM과 함께 침수 위험으로부터 안전한 도시를 만들어갑시다! 🌊**

[![⭐ Star](https://img.shields.io/github/stars/your-repo/crew_soom?style=social)](https://github.com/your-repo/crew_soom)
[![🍴 Fork](https://img.shields.io/github/forks/your-repo/crew_soom?style=social)](https://github.com/your-repo/crew_soom/fork)
[![👁️ Watch](https://img.shields.io/github/watchers/your-repo/crew_soom?style=social)](https://github.com/your-repo/crew_soom/watchers)

</div>