#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CREW_SOOM 빠른 설치 스크립트
자동으로 필요한 패키지 설치 및 환경 설정
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_header():
    """헤더 출력"""
    print("🌊" * 20)
    print("  CREW_SOOM 침수 예측 AI 시스템")
    print("      빠른 설치 스크립트")
    print("🌊" * 20)
    print()

def check_python():
    """Python 버전 확인"""
    print("🐍 Python 환경 확인...")
    version = sys.version_info
    print(f"   Python 버전: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 8:
        print("   ✅ Python 버전 적합")
        return True
    else:
        print("   ❌ Python 3.8 이상이 필요합니다")
        print("   💡 https://python.org에서 최신 Python 다운로드")
        return False

def upgrade_pip():
    """pip 업그레이드"""
    print("📦 pip 업그레이드...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
        print("   ✅ pip 업그레이드 완료")
        return True
    except subprocess.CalledProcessError:
        print("   ⚠️ pip 업그레이드 실패 (계속 진행)")
        return True

def install_packages():
    """필수 패키지 설치"""
    print("📥 필수 패키지 설치...")
    
    # 기본 패키지 목록
    basic_packages = [
        'Flask==2.3.3',
        'Werkzeug==2.3.7',
        'pandas==2.1.1',
        'numpy==1.24.3',
        'matplotlib==3.7.2',
        'seaborn==0.12.2',
        'scikit-learn==1.3.0',
        'requests==2.31.0',
        'python-dotenv==1.0.0',
        'joblib==1.3.2'
    ]
    
    # 선택적 패키지
    optional_packages = [
        'xgboost==1.7.6',
        'psutil==5.9.5'
    ]
    
    # 기본 패키지 설치
    for package in basic_packages:
        try:
            print(f"   📦 설치 중: {package}")
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', package
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"   ✅ 완료: {package}")
        except subprocess.CalledProcessError:
            print(f"   ❌ 실패: {package}")
            return False
    
    # 선택적 패키지 설치
    print("\n🔧 선택적 패키지 설치...")
    for package in optional_packages:
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', package
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"   ✅ 완료: {package}")
        except subprocess.CalledProcessError:
            print(f"   ⚠️ 스킵: {package}")
    
    return True

def create_directories():
    """필요한 디렉토리 생성"""
    print("📁 디렉토리 구조 생성...")
    
    directories = [
        'data', 'data/processed', 'data/raw', 'data/database', 'data/flood_events',
        'models', 'outputs', 'logs', 'users', 'logo',
        'modules', 'templates', 'static', 'static/css', 'static/js'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   📂 {directory}/")
    
    print("   ✅ 디렉토리 생성 완료")

def create_env_file():
    """환경 변수 파일 생성"""
    print("🔧 환경 변수 파일 생성...")
    
    if os.path.exists('.env'):
        print("   ⚠️ .env 파일이 이미 존재합니다")
        return
    
    env_content = """# CREW_SOOM 환경 변수 설정
# 기상청 API 키 (공공데이터포털에서 발급)
OPENWEATHER_API_KEY=your_api_key_here

# 기상 데이터 위치 설정
WEATHER_CITY=Seoul
WEATHER_NX=60
WEATHER_NY=127

# Flask 애플리케이션 설정
FLASK_ENV=development
FLASK_DEBUG=True
"""
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("   ✅ .env 파일 생성 완료")
    print("   💡 API 키를 설정하려면 .env 파일을 편집하세요")

def create_batch_files():
    """Windows용 배치 파일 생성"""
    if platform.system() != 'Windows':
        return
    
    print("🔧 Windows 배치 파일 생성...")
    
    # 시스템 체크 배치 파일
    check_bat = """@echo off
echo 🔍 시스템 체크 실행...
python check_system.py
pause
"""
    
    with open('check_system.bat', 'w', encoding='utf-8') as f:
        f.write(check_bat)
    
    # 실행 배치 파일
    run_bat = """@echo off
echo 🚀 CREW_SOOM 시스템 실행...
python run.py
pause
"""
    
    with open('run_system.bat', 'w', encoding='utf-8') as f:
        f.write(run_bat)
    
    print("   ✅ Windows 배치 파일 생성 완료")

def create_shell_scripts():
    """Unix/Linux용 쉘 스크립트 생성"""
    if platform.system() == 'Windows':
        return
    
    print("🔧 쉘 스크립트 생성...")
    
    # 시스템 체크 스크립트
    check_sh = """#!/bin/bash
echo "🔍 시스템 체크 실행..."
python3 check_system.py
"""
    
    with open('check_system.sh', 'w') as f:
        f.write(check_sh)
    os.chmod('check_system.sh', 0o755)
    
    # 실행 스크립트
    run_sh = """#!/bin/bash
echo "🚀 CREW_SOOM 시스템 실행..."
python3 run.py
"""
    
    with open('run_system.sh', 'w') as f:
        f.write(run_sh)
    os.chmod('run_system.sh', 0o755)
    
    print("   ✅ 쉘 스크립트 생성 완료")

def test_imports():
    """기본 import 테스트"""
    print("🧪 패키지 import 테스트...")
    
    test_packages = [
        'flask', 'pandas', 'numpy', 'matplotlib', 
        'seaborn', 'sklearn', 'requests', 'dotenv'
    ]
    
    failed = []
    for package in test_packages:
        try:
            if package == 'sklearn':
                import sklearn
            elif package == 'dotenv':
                import dotenv
            else:
                __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package}")
            failed.append(package)
    
    if failed:
        print(f"\n❌ 다음 패키지 import 실패: {', '.join(failed)}")
        return False
    
    print("   ✅ 모든 패키지 import 성공")
    return True

def create_readme():
    """README 파일 생성"""
    print("📝 README 파일 생성...")
    
    readme_content = """# 🌊 CREW_SOOM 침수 예측 AI 시스템

## 🚀 빠른 시작

1. **시스템 체크**:
   ```bash
   python check_system.py
   ```

2. **시스템 실행**:
   ```bash
   python run.py
   ```

3. **웹 브라우저 접속**:
   - 주소: http://localhost:5000
   - 로그인: admin / 1234

## 📋 주요 기능

- 🌊 실시간 침수 위험도 예측
- 📊 4개 기상청 API 통합 데이터 수집
- 🤖 머신러닝 모델 훈련 및 비교
- 📈 실시간 데이터 시각화
- 🗺️ 서울시 구별 위험도 지도
- ⏰ 1시간마다 자동 업데이트

## 🔧 설정

### API 키 설정
1. https://data.go.kr 에서 기상청 API 키 발급
2. `.env` 파일에 API 키 입력:
   ```
   OPENWEATHER_API_KEY=your_api_key_here
   ```

### 문제 해결
- 시스템 체크: `python check_system.py`
- 로그 확인: `logs/log_events.json`
- 포트 변경: `web_app.py`의 마지막 줄 수정

## 📞 지원

문제 발생 시 다음을 확인하세요:
1. Python 3.8 이상 설치
2. 필수 패키지 설치 완료
3. 포트 5000 사용 가능
4. 메모리 4GB 이상 권장
"""
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("   ✅ README.md 생성 완료")

def main():
    """메인 설치 함수"""
    print_header()
    
    # 1. Python 버전 확인
    if not check_python():
        input("\n❌ Python 버전을 확인하고 다시 실행하세요. (Enter 키로 종료)")
        return False
    
    # 2. pip 업그레이드
    upgrade_pip()
    
    # 3. 필수 패키지 설치
    if not install_packages():
        input("\n❌ 패키지 설치에 실패했습니다. (Enter 키로 종료)")
        return False
    
    # 4. 디렉토리 생성
    create_directories()
    
    # 5. 환경 변수 파일 생성
    create_env_file()
    
    # 6. 플랫폼별 스크립트 생성
    create_batch_files()
    create_shell_scripts()
    
    # 7. README 파일 생성
    create_readme()
    
    # 8. import 테스트
    if not test_imports():
        input("\n❌ 패키지 import 테스트에 실패했습니다. (Enter 키로 종료)")
        return False
    
    # 9. 설치 완료 메시지
    print("\n" + "🎉" * 20)
    print("  설치가 완료되었습니다!")
    print("🎉" * 20)
    print()
    print("📋 다음 단계:")
    print("1. 📝 .env 파일에 API 키 설정 (선택사항)")
    print("2. 🔍 시스템 체크: python check_system.py")
    print("3. 🚀 시스템 실행: python run.py")
    print("4. 🌐 브라우저 접속: http://localhost:5000")
    print()
    print("💡 문제가 있다면 check_system.py를 먼저 실행하세요!")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            input("\n✅ 설치 완료! Enter 키를 눌러 종료하세요.")
        else:
            input("\n❌ 설치 실패! Enter 키를 눌러 종료하세요.")
    except KeyboardInterrupt:
        print("\n\n🛑 설치가 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 설치 중 오류 발생: {e}")
        input("Enter 키를 눌러 종료하세요.")