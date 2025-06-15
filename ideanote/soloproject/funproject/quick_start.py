#!/usr/bin/env python3
"""
🎲 로또 예측 앱 즉시 실행기

이 파일로 바로 실행됩니다!
python quick_start.py
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_directories():
    """필요한 디렉토리 생성"""
    dirs = [
        "backend/data",
        "backend/data/logs", 
        "backend/models",
        "backend/models/model_weights"
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    print("✅ 디렉토리 설정 완료")

def check_backend():
    """백엔드 파일 확인"""
    backend_app = Path("backend/app.py")
    if not backend_app.exists():
        print("❌ backend/app.py 파일이 없습니다!")
        return False
    
    print("✅ 백엔드 파일 확인 완료")
    return True

def run_server():
    """서버 실행"""
    print("🚀 AI 로또 예측 서버 시작!")
    print("🌐 브라우저에서 http://localhost:8000 접속하세요!")
    print("⏹️  종료하려면 Ctrl+C를 누르세요")
    print("=" * 50)
    
    try:
        # backend 디렉토리로 이동해서 실행
        os.chdir("backend")
        
        # uvicorn으로 서버 실행
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "app:app",
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ])
        
    except KeyboardInterrupt:
        print("\n\n👋 서버를 종료했습니다!")
    except FileNotFoundError:
        print("❌ uvicorn을 찾을 수 없습니다!")
        print("💡 설치: pip install uvicorn")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        print("\n🔧 수동 실행 방법:")
        print("1. cd backend")
        print("2. python -m uvicorn app:app --host 0.0.0.0 --port 8000")

def main():
    print("🎲 AI 로또 예측기")
    print("딥러닝 기반 로또 번호 예측 서비스")
    print("=" * 40)
    
    # 디렉토리 설정
    setup_directories()
    
    # 백엔드 확인
    if not check_backend():
        print("❌ 필수 파일이 없어 실행할 수 없습니다.")
        input("Enter 키를 눌러 종료...")
        return
    
    # 서버 실행
    run_server()

if __name__ == "__main__":
    main()