#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CREW_SOOM 침수 예측 AI 시스템 실행 스크립트
4개 기상청 API 통합 + 3년치 데이터 + 웹 기반 머신러닝 플랫폼
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def check_python_version():
    """Python 버전 체크"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        return True
    else:
        print("❌ Python 3.8 이상이 필요합니다.")
        print(f"   현재 버전: {version.major}.{version.minor}.{version.micro}")
        return False

def create_directories():
    """필요한 디렉토리 생성"""
    directories = [
        'data', 'data/processed', 'data/raw', 'data/database', 'data/flood_events',
        'models', 'outputs', 'logs', 'users', 'logo'
    ]
    
    print("📁 필요한 디렉토리 생성 중...")
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {directory}/")

def check_required_files():
    """필요한 파일들 확인"""
    required_files = [
        'modules/web_app.py',
        'modules/multi_weather_api.py',
        'modules/data_loader.py',
        'modules/preprocessor.py',
        'modules/trainer.py',
        'modules/evaluator.py',
        'modules/visualizer.py',
        'templates/dashboard.html',
        'static/css/style.css',
        'static/js/dashboard.js'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ 누락된 파일들:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    
    return True

def check_env_file():
    """환경 변수 파일 체크"""
    if not os.path.exists('.env'):
        print("⚠️ .env 파일이 없습니다.")
        if os.path.exists('.env.example'):
            print("💡 .env.example을 복사하여 .env 파일을 만드세요:")
            print("   cp .env.example .env")
        else:
            print("💡 .env 파일을 생성하세요:")
            print("   OPENWEATHER_API_KEY=your_api_key_here")
        return False
    
    return True

def install_requirements():
    """필요한 패키지 설치"""
    if os.path.exists('requirements.txt'):
        print("📦 패키지 의존성 확인 중...")
        try:
            # 주요 패키지 import 테스트
            import flask
            import pandas
            import numpy
            import matplotlib
            import sklearn
            print("   ✅ 필수 패키지 이미 설치됨")
            return True
        except ImportError as e:
            print(f"   ❌ 패키지 누락: {e}")
            print("   📥 패키지 설치 중...")
            
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
                print("   ✅ 패키지 설치 완료")
                return True
            except subprocess.CalledProcessError:
                print("   ❌ 패키지 설치 실패")
                print("   💡 수동 설치: pip install -r requirements.txt")
                return False
    else:
        print("⚠️ requirements.txt 파일이 없습니다.")
        return False

def set_matplotlib_font():
    """matplotlib 한글 폰트 설정"""
    try:
        import matplotlib.pyplot as plt
        import matplotlib.font_manager as fm
        
        # 운영체제별 한글 폰트 설정
        if platform.system() == 'Windows':
            font_name = 'Malgun Gothic'
        elif platform.system() == 'Darwin':  # macOS
            font_name = 'AppleGothic'
        else:  # Linux
            font_name = 'DejaVu Sans'
        
        # 폰트 설정
        plt.rcParams['font.family'] = font_name
        plt.rcParams['axes.unicode_minus'] = False
        
        print(f"   📝 한글 폰트 설정: {font_name}")
        return True
        
    except ImportError:
        print("   ⚠️ matplotlib가 설치되지 않았습니다.")
        return False

def main():
    """메인 실행 함수"""
    print("🌊 CREW_SOOM 침수 예측 AI 시스템 시작!")
    print("=" * 60)
    
    # 1. Python 버전 체크
    if not check_python_version():
        sys.exit(1)
    
    # 2. 디렉토리 생성
    create_directories()
    
    # 3. 필요한 파일 체크
    if not check_required_files():
        print("\n❌ 필요한 파일이 누락되었습니다.")
        print("💡 프로젝트 파일을 모두 복사했는지 확인하세요.")
        sys.exit(1)
    
    # 4. 환경 변수 파일 체크
    if not check_env_file():
        print("⚠️ .env 파일 없이 시뮬레이션 모드로 실행됩니다.")
    
    # 5. 패키지 설치 체크
    if not install_requirements():
        print("❌ 패키지 설치에 실패했습니다.")
        sys.exit(1)
    
    # 6. 한글 폰트 설정
    set_matplotlib_font()
    
    print("\n🚀 시스템 초기화 완료!")
    print("🌐 웹 서버 시작 중...")
    print("-" * 40)
    
    # 7. 웹 애플리케이션 실행
    try:
        from modules.web_app import FloodWebApp
        
        print("✅ 웹 애플리케이션 모듈 로드 성공")
        app = FloodWebApp()
        
        print("\n🎯 시스템 준비 완료!")
        print("📍 접속 주소: http://localhost:5000")
        print("🔑 기본 로그인: admin / 1234")
        print("🛑 종료: Ctrl+C\n")
        
        app.run()
        
    except ImportError as e:
        print(f"❌ 모듈 import 오류: {e}")
        print("💡 modules/ 폴더와 필요한 파일들이 있는지 확인하세요.")
        sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n🛑 사용자에 의해 종료되었습니다.")
        sys.exit(0)
    
    except Exception as e:
        print(f"❌ 예상치 못한 오류가 발생했습니다: {e}")
        print("💡 check_system.py를 실행하여 시스템 상태를 확인하세요.")
        sys.exit(1)

if __name__ == "__main__":
    main()