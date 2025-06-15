# config.py (backend/config.py)
import os
from pathlib import Path
# 디렉토리 생성 함수 (누락된 부분)
def create_directories():
    """필요한 디렉토리들을 생성합니다."""
    directories = [
        DATA_DIR,
        LOGS_DIR, 
        MODELS_DIR,
        MODEL_WEIGHTS_DIR
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    
    print("✅ 필요한 디렉토리들이 생성되었습니다.")

if __name__ == "__main__":
    create_directories()