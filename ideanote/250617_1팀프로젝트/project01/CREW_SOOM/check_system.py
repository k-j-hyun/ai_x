# check_system.py - 시스템 환경 체크 스크립트
import sys
import os
import platform
import subprocess
import importlib.util

def check_python_version():
    """Python 버전 확인"""
    print("🐍 Python 버전 확인...")
    version = sys.version_info
    print(f"   현재 Python 버전: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 8:
        print("   ✅ Python 버전 OK")
        return True
    else:
        print("   ❌ Python 3.8 이상이 필요합니다")
        return False

def check_directories():
    """필요한 디렉토리 확인 및 생성"""
    print("📁 디렉토리 구조 확인...")
    
    required_dirs = [
        'data', 'data/processed', 'data/raw', 
        'models', 'outputs', 'logs', 'users',
        'modules', 'templates', 'static'
    ]
    
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path, exist_ok=True)
                print(f"   📂 생성: {dir_path}")
            except Exception as e:
                print(f"   ❌ 디렉토리 생성 실패: {dir_path} - {e}")
                return False
        else:
            print(f"   ✅ 존재: {dir_path}")
    
    return True

def check_required_packages():
    """필수 패키지 확인"""
    print("📦 필수 패키지 확인...")
    
    required_packages = [
        'flask', 'pandas', 'numpy', 'matplotlib', 
        'seaborn', 'scikit-learn', 'requests', 'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            # 패키지 import 시도
            if package == 'python-dotenv':
                package_name = 'dotenv'
            elif package == 'scikit-learn':
                package_name = 'sklearn'
            else:
                package_name = package
            
            spec = importlib.util.find_spec(package_name)
            if spec is None:
                missing_packages.append(package)
                print(f"   ❌ 누락: {package}")
            else:
                print(f"   ✅ 설치됨: {package}")
        except Exception as e:
            missing_packages.append(package)
            print(f"   ❌ 오류: {package} - {e}")
    
    if missing_packages:
        print(f"\n📋 누락된 패키지: {', '.join(missing_packages)}")
        print("💡 설치 명령어: pip install " + " ".join(missing_packages))
        return False
    
    return True

def check_env_file():
    """환경 변수 파일 확인"""
    print("🔧 환경 설정 파일 확인...")
    
    if os.path.exists('.env'):
        print("   ✅ .env 파일 존재")
        
        # .env 파일 내용 확인
        try:
            with open('.env', 'r') as f:
                content = f.read()
                if 'OPENWEATHER_API_KEY' in content:
                    print("   ✅ API 키 설정 확인됨")
                else:
                    print("   ⚠️ API 키가 설정되지 않음 (시뮬레이션 모드로 동작)")
        except Exception as e:
            print(f"   ❌ .env 파일 읽기 오류: {e}")
            return False
    else:
        print("   ⚠️ .env 파일이 없습니다")
        print("   💡 .env.example을 복사하여 .env 파일을 만드세요")
        return False
    
    return True

def check_port_availability():
    """포트 사용 가능 여부 확인"""
    print("🌐 포트 사용 가능 여부 확인...")
    
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', 5000))
        sock.close()
        
        if result == 0:
            print("   ⚠️ 포트 5000이 이미 사용 중입니다")
            print("   💡 다른 Flask 앱이 실행 중이거나 다른 서비스가 포트를 사용 중입니다")
            return False
        else:
            print("   ✅ 포트 5000 사용 가능")
            return True
    except Exception as e:
        print(f"   ❌ 포트 확인 오류: {e}")
        return False

def check_system_resources():
    """시스템 리소스 확인"""
    print("💻 시스템 리소스 확인...")
    
    try:
        import psutil
        
        # 메모리 확인
        memory = psutil.virtual_memory()
        memory_gb = memory.total / (1024**3)
        print(f"   🧠 총 메모리: {memory_gb:.1f} GB")
        
        if memory_gb < 4:
            print("   ⚠️ 메모리가 부족할 수 있습니다 (권장: 4GB 이상)")
        else:
            print("   ✅ 메모리 충분")
        
        # 디스크 공간 확인
        disk = psutil.disk_usage('.')
        disk_gb = disk.free / (1024**3)
        print(f"   💾 여유 디스크 공간: {disk_gb:.1f} GB")
        
        if disk_gb < 2:
            print("   ⚠️ 디스크 공간이 부족할 수 있습니다 (권장: 2GB 이상)")
        else:
            print("   ✅ 디스크 공간 충분")
        
        return True
        
    except ImportError:
        print("   ⚠️ psutil 패키지가 없어 시스템 리소스를 확인할 수 없습니다")
        print("   💡 설치: pip install psutil")
        return True  # 필수는 아니므로 True 반환

def check_font_availability():
    """한글 폰트 사용 가능 여부 확인"""
    print("🔤 한글 폰트 확인...")
    
    try:
        import matplotlib.pyplot as plt
        import matplotlib.font_manager as fm
        
        # 시스템 폰트 목록 가져오기
        font_list = [f.name for f in fm.fontManager.ttflist]
        
        korean_fonts = ['Malgun Gothic', 'NanumGothic', 'AppleGothic', 'DejaVu Sans']
        available_korean_fonts = [font for font in korean_fonts if font in font_list]
        
        if available_korean_fonts:
            print(f"   ✅ 사용 가능한 한글 폰트: {', '.join(available_korean_fonts)}")
            return True
        else:
            print("   ⚠️ 한글 폰트가 없습니다. 그래프에서 한글이 깨질 수 있습니다")
            if platform.system() == 'Windows':
                print("   💡 Windows: 제어판 → 글꼴에서 '맑은 고딕' 설치 확인")
            elif platform.system() == 'Darwin':
                print("   💡 macOS: 기본 한글 폰트 사용")
            else:
                print("   💡 Linux: sudo apt-get install fonts-nanum")
            return False
            
    except ImportError:
        print("   ⚠️ matplotlib가 없어 폰트를 확인할 수 없습니다")
        return True

def run_basic_imports():
    """기본 import 테스트"""
    print("🔄 기본 모듈 import 테스트...")
    
    try:
        import flask
        import pandas as pd
        import numpy as np
        import matplotlib.pyplot as plt
        import seaborn as sns
        import sklearn
        import requests
        import dotenv
        
        print("   ✅ 모든 필수 모듈 import 성공")
        return True
        
    except Exception as e:
        print(f"   ❌ 모듈 import 실패: {e}")
        return False

def main():
    """메인 체크 함수"""
    print("🚀 CREW_SOOM 시스템 환경 체크 시작\n")
    print("=" * 50)
    
    checks = [
        ("Python 버전", check_python_version),
        ("디렉토리 구조", check_directories),
        ("필수 패키지", check_required_packages),
        ("환경 설정", check_env_file),
        ("포트 사용 가능", check_port_availability),
        ("시스템 리소스", check_system_resources),
        ("한글 폰트", check_font_availability),
        ("모듈 import", run_basic_imports)
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, check_func in checks:
        print(f"\n{check_name}:")
        if check_func():
            passed += 1
        print("-" * 30)
    
    print(f"\n📊 체크 결과: {passed}/{total} 통과")
    
    if passed == total:
        print("🎉 모든 체크 통과! 시스템 실행 준비 완료")
        print("▶️ 실행 명령어: python run.py")
        return True
    else:
        print("⚠️ 일부 체크에서 문제가 발견되었습니다")
        print("💡 위의 권장사항을 참고하여 문제를 해결하세요")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)