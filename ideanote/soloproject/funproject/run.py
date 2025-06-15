#!/usr/bin/env python3
"""
로또 예측 앱 실행 스크립트

사용법:
    python run.py                    # 개발 서버 실행
    python run.py --production       # 프로덕션 서버 실행
    python run.py --setup            # 초기 설정만 실행
    python run.py --crawl            # 데이터 크롤링만 실행
    python run.py --train            # 모델 학습만 실행
"""

import argparse
import asyncio
import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "backend"))

import uvicorn
import logging
from datetime import datetime

# 내부 모듈
from config import create_directories, API_HOST, API_PORT, DEBUG, LOG_LEVEL
from crawler.lotto_crawler import LottoCrawler
from models.lotto_model import LottoPredictionModel

# 로깅 설정
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backend/data/logs/app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def print_banner():
    """시작 배너 출력"""
    banner = """
🎲 ========================================== 🎲
    AI 로또 번호 예측 시스템
    
    딥러닝과 웹크롤링을 활용한
    차세대 로또 번호 추천 서비스
    
    Made with ❤️ by AI & Human
🎲 ========================================== 🎲
    """
    print(banner)

def setup_project():
    """프로젝트 초기 설정"""
    print("🔧 프로젝트 초기 설정 중...")
    
    try:
        # 디렉토리 생성
        create_directories()
        
        # __init__.py 파일들 생성
        init_files = [
            "backend/__init__.py",
            "backend/models/__init__.py", 
            "backend/crawler/__init__.py",
            "backend/api/__init__.py",
            "backend/utils/__init__.py"
        ]
        
        for init_file in init_files:
            Path(init_file).touch(exist_ok=True)
        
        print("✅ 프로젝트 초기 설정 완료!")
        return True
        
    except Exception as e:
        logger.error(f"프로젝트 설정 실패: {e}")
        return False

def crawl_data():
    """데이터 크롤링 실행"""
    print("🕷️ 로또 데이터 크롤링 시작...")
    
    try:
        crawler = LottoCrawler()
        
        def progress_callback(progress, current, total):
            print(f"\r진행률: {progress:.1f}% ({current}/{total})", end="", flush=True)
        
        result = crawler.update_data(progress_callback)
        print()  # 새 줄
        
        if result["success"]:
            print(f"✅ {result['message']}")
            print(f"   총 회차: {result['total_draws']}")
            print(f"   최신 회차: {result['latest_draw']}")
            if result.get('new_draws', 0) > 0:
                print(f"   새로 추가된 회차: {result['new_draws']}개")
            return True
        else:
            print(f"❌ 크롤링 실패: {result['message']}")
            return False
            
    except Exception as e:
        logger.error(f"크롤링 중 오류: {e}")
        print(f"❌ 크롤링 실패: {e}")
        return False

def train_model():
    """AI 모델 학습"""
    print("🤖 AI 모델 학습 시작...")
    
    try:
        model = LottoPredictionModel()
        result = model.initialize_model()
        
        if result["success"]:
            print(f"✅ {result['message']}")
            
            # 간단한 예측 테스트
            test_result = model.predict_next_numbers(3)
            if test_result["success"]:
                print("\n🎯 테스트 예측 결과:")
                for i, pred in enumerate(test_result["predictions"], 1):
                    main_str = ', '.join(map(str, pred['main']))
                    print(f"  {i}. [{main_str}] + {pred['bonus']} (신뢰도: {pred['confidence']:.3f})")
            
            return True
        else:
            print(f"❌ 모델 학습 실패: {result['message']}")
            return False
            
    except Exception as e:
        logger.error(f"모델 학습 중 오류: {e}")
        print(f"❌ 모델 학습 실패: {e}")
        return False

def run_server(production=False):
    """웹 서버 실행"""
    print("🚀 웹 서버 시작...")
    
    try:
        if production:
            # 프로덕션 설정
            uvicorn.run(
                "backend.app:app",
                host="0.0.0.0",
                port=API_PORT,
                workers=4,
                log_level="info"
            )
        else:
            # 개발 설정
            uvicorn.run(
                "backend.app:app",
                host=API_HOST,
                port=API_PORT,
                reload=True,
                log_level="debug" if DEBUG else "info"
            )
            
    except KeyboardInterrupt:
        print("\n👋 서버를 종료합니다.")
    except Exception as e:
        logger.error(f"서버 실행 실패: {e}")
        print(f"❌ 서버 실행 실패: {e}")

def check_dependencies():
    """의존성 패키지 확인"""
    required_packages = [
        'fastapi', 'uvicorn', 'tensorflow', 'pandas', 
        'numpy', 'scikit-learn', 'requests', 'beautifulsoup4'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ 다음 패키지들이 설치되지 않았습니다:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n설치 명령어:")
        print("pip install -r requirements.txt")
        return False
    
    print("✅ 모든 필수 패키지가 설치되어 있습니다.")
    return True

def main():
    parser = argparse.ArgumentParser(
        description="AI 로또 예측 시스템",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python run.py                    # 개발 서버 실행
  python run.py --production       # 프로덕션 서버 실행  
  python run.py --setup            # 초기 설정
  python run.py --crawl            # 데이터 크롤링
  python run.py --train            # 모델 학습
  python run.py --all              # 전체 파이프라인 실행
        """
    )
    
    parser.add_argument('--production', action='store_true', 
                       help='프로덕션 모드로 서버 실행')
    parser.add_argument('--setup', action='store_true',
                       help='프로젝트 초기 설정만 실행')
    parser.add_argument('--crawl', action='store_true',
                       help='데이터 크롤링만 실행')
    parser.add_argument('--train', action='store_true', 
                       help='모델 학습만 실행')
    parser.add_argument('--all', action='store_true',
                       help='전체 파이프라인 실행 (설정 → 크롤링 → 학습 → 서버)')
    
    args = parser.parse_args()
    
    print_banner()
    
    # 의존성 확인
    if not check_dependencies():
        sys.exit(1)
    
    # 인자별 실행
    if args.setup:
        setup_project()
    elif args.crawl:
        if not setup_project():
            sys.exit(1)
        crawl_data()
    elif args.train:
        if not setup_project():
            sys.exit(1)
        train_model()
    elif args.all:
        print("🔄 전체 파이프라인 실행...")
        
        # 1. 프로젝트 설정
        if not setup_project():
            print("❌ 프로젝트 설정 실패")
            sys.exit(1)
        
        # 2. 데이터 크롤링
        print("\n" + "="*50)
        if not crawl_data():
            print("❌ 데이터 크롤링 실패")
            sys.exit(1)
        
        # 3. 모델 학습
        print("\n" + "="*50)
        if not train_model():
            print("❌ 모델 학습 실패")
            sys.exit(1)
        
        # 4. 서버 실행
        print("\n" + "="*50)
        print("🎉 전체 파이프라인 완료! 서버를 시작합니다...")
        print(f"🌐 웹 브라우저에서 http://localhost:{API_PORT} 에 접속하세요!")
        run_server(args.production)
    else:
        # 기본: 서버만 실행
        setup_project()  # 기본 설정은 항상 실행
        print(f"🌐 웹 브라우저에서 http://localhost:{API_PORT} 에 접속하세요!")
        print("💡 데이터가 없다면 웹에서 '데이터 업데이트' 버튼을 눌러주세요!")
        run_server(args.production)

if __name__ == "__main__":
    main()