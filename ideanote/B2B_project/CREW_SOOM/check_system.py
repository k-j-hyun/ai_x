#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
check_system.py - CREW_SOOM 시스템 상태 진단 스크립트
"""

import sys
import os
import importlib.util
from pathlib import Path

def print_banner():
    """진단 시작 배너"""
    banner = """
══════════════════════════════════════════════════════════════════════
                         CREW_SOOM 시스템 진단                                       
                   ..문제 해결을 위한 상태 점검 도구.                                 
══════════════════════════════════════════════════════════════════════
    """
    print(banner)

def check_python_version():
    """Python 버전 확인"""
    print("Python 환경 확인...")
    version = sys.version_info
    print(f"   Python 버전: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 8:
        print("   Python 버전 요구사항 충족")
        return True
    else:
        print("   Python 3.8 이상이 필요합니다.")
        return False

def check_required_modules():
    """필수 모듈 확인"""
    print("\n필수 모듈 확인...")
    
    required_modules = {
        'pandas': 'pandas',
        'numpy': 'numpy', 
        'matplotlib': 'matplotlib',
        'sklearn': 'scikit-learn',
        'requests': 'requests',
        'flask': 'Flask',
        'joblib': 'joblib',
        'lxml': 'lxml'
    }
    
    missing_modules = []
    
    for module_name, package_name in required_modules.items():
        try:
            importlib.import_module(module_name)
            print(f"   {package_name}")
        except ImportError:
            print(f"   {package_name} - 설치 필요")
            missing_modules.append(package_name)
    
    if missing_modules:
        print(f"\n설치 명령: pip install {' '.join(missing_modules)}")
        return False
    
    return True

def check_optional_modules():
    """선택적 모듈 확인"""
    print("\n선택적 모듈 확인...")
    
    optional_modules = {
        'tensorflow': 'TensorFlow (LSTM+CNN, Transformer 모델용)',
        'xgboost': 'XGBoost (XGBoost 모델용)',
        'seaborn': 'Seaborn (시각화 향상)',
        'imblearn': 'imbalanced-learn (불균형 데이터 처리)'
    }
    
    for module_name, description in optional_modules.items():
        try:
            importlib.import_module(module_name)
            print(f"   {description}")
        except ImportError:
            print(f"   {description} - 선택사항")

def check_project_structure():
    """프로젝트 구조 확인"""
    print("\n프로젝트 구조 확인...")
    
    required_files = [
        'modules/preprocessor.py',
        'modules/trainer.py',
        'modules/trainer_rf.py',
        'modules/trainer_xgb.py',
        'modules/trainer_lstm_cnn.py',
        'modules/trainer_transformer.py',
        'modules/visualizer.py',
        'modules/web_app.py',
        'templates/dashboard.html',
        'templates/login.html',
        'templates/map.html',
        'templates/news.html',
        'static/css/style.css',
        'static/js/dashboard.js',
        'run.py'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   {file_path}")
        else:
            print(f"   {file_path} - 파일 없음")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n누락된 파일 {len(missing_files)}개를 확인하세요.")
        return False
    
    return True

def check_data_directories():
    """데이터 디렉토리 확인"""
    print("\n데이터 디렉토리 확인...")
    
    required_dirs = [
        'data',
        'models',
        'outputs',
        'logs',
        'users'
    ]
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"   {dir_path}/")
        else:
            print(f"   {dir_path}/ - 자동 생성됨")
            os.makedirs(dir_path, exist_ok=True)

def check_env_file():
    """환경 설정 파일 확인"""
    print("\n환경 설정 확인...")
    
    if os.path.exists('.env'):
        print("   .env 파일 존재")
        
        # .env 파일 내용 확인
        try:
            with open('.env', 'r', encoding='utf-8') as f:
                content = f.read()
                if 'OPENWEATHER_API_KEY' in content:
                    if 'your_api_key_here' not in content:
                        print("   API 키 설정 완료")
                    else:
                        print("   API 키가 기본값으로 설정됨 - 수정 필요")
                else:
                    print("   OPENWEATHER_API_KEY가 설정되지 않음")
        except Exception as e:
            print(f"   .env 파일 읽기 오류: {e}")
    else:
        print("   .env 파일 없음")
        print("   python setup.py 실행 또는 수동으로 .env 파일 생성 필요")

def test_module_imports():
    """모듈 import 테스트"""
    print("\n모듈 import 테스트...")
    
    test_modules = [
        ('modules.preprocessor', 'preprocess_data'),
        ('modules.trainer', 'preprocess_hourly_data'),
        ('modules.trainer_rf', 'train_random_forest'),
        ('modules.trainer_xgb', 'train_xgboost'),
        ('modules.trainer_lstm_cnn', 'train_lstm_cnn'),
        ('modules.trainer_transformer', 'train_transformer'),
        ('modules.visualizer', 'plot_model_comparison'),
        ('modules.web_app', 'app')
    ]
    
    failed_imports = []
    
    for module_path, function_name in test_modules:
        try:
            module = importlib.import_module(module_path)
            if hasattr(module, function_name):
                print(f"   {module_path}.{function_name}")
            else:
                print(f"   {module_path}.{function_name} - 함수 없음")
                failed_imports.append(module_path)
        except ImportError as e:
            print(f"   {module_path} - Import 오류: {str(e)[:50]}...")
            failed_imports.append(module_path)
        except Exception as e:
            print(f"   {module_path} - 기타 오류: {str(e)[:50]}...")
    
    return len(failed_imports) == 0

def check_data_files():
    """데이터 파일 확인"""
    print("\n데이터 파일 확인...")
    
    data_files = [
        ('data/asos_seoul_daily.csv', '일자료 (원본)'),
        ('data/asos_seoul_hourly.csv', '시간자료 (원본)'),
        ('data/asos_seoul_daily_enriched.csv', '일자료 (전처리됨)'),
        ('data/asos_seoul_hourly_with_flood_risk.csv', '시간자료 (전처리됨)')
    ]
    
    data_exists = False
    
    for file_path, description in data_files:
        if os.path.exists(file_path):
            try:
                import pandas as pd
                df = pd.read_csv(file_path)
                print(f"   {description}: {len(df)}행")
                data_exists = True
            except Exception as e:
                print(f"   {description}: 파일 손상됨 ({e})")
        else:
            print(f"   {description}: 파일 없음")
    
    if not data_exists:
        print("   데이터 수집 필요: python run.py → 1,2,3 순서로 실행")
    
    return data_exists

def check_model_files():
    """모델 파일 확인"""
    print("\n모델 파일 확인...")
    
    model_files = [
        ('models/randomforest_model.pkl', 'RandomForest 모델'),
        ('models/xgb_model_daily.pkl', 'XGBoost 모델'),
        ('models/xgb_scaler_daily.pkl', 'XGBoost 스케일러'),
        ('models/lstm_cnn_model.h5', 'LSTM+CNN 모델'),
        ('models/lstm_cnn_scaler.pkl', 'LSTM+CNN 스케일러'),
        ('models/transformer_flood_model.h5', 'Transformer 모델')
    ]
    
    model_exists = False
    
    for file_path, description in model_files:
        if os.path.exists(file_path):
            print(f"   {description}: 존재")
            model_exists = True
        else:
            print(f"   {description}: 파일 없음")
    
    if not model_exists:
        print("   모델 훈련 필요: python run.py → 8 (전체 모델 학습)")
    
    return model_exists

def check_web_app():
    """웹 애플리케이션 확인"""
    print("\n웹 애플리케이션 확인...")
    
    try:
        from modules.web_app import app
        print("   Flask 앱 로드 성공")
        
        # 라우트 확인
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        essential_routes = ['/', '/login', '/api/status', '/api/predict_advanced']
        
        missing_routes = []
        for route in essential_routes:
            if route in routes:
                print(f"   라우트: {route}")
            else:
                print(f"   라우트: {route} - 없음")
                missing_routes.append(route)
        
        return len(missing_routes) == 0
        
    except Exception as e:
        print(f"   웹 앱 로드 실패: {e}")
        return False

def suggest_fixes():
    """문제 해결 제안"""
    print("\n문제 해결 가이드:")
    print("   1. 의존성 설치: python setup.py 또는 pip install -r requirements.txt")
    print("   2. 환경 설정: .env 파일에서 API 키 설정")
    print("   3. 데이터 수집: python run.py → 1,2,3 순서로 실행")
    print("   4. 모델 훈련: python run.py → 8 (전체 모델 학습)")
    print("   5. 웹 앱 실행: python run.py → 10")
    print("\n추가 도움이 필요하면:")
    print("   - 로그 파일 확인: logs/ 디렉토리")
    print("   - 모듈별 개별 실행으로 오류 확인")
    print("   - TensorFlow 설치 문제: pip install tensorflow")

def main():
    """메인 진단 함수"""
    print_banner()
    
    checks = [
        ("Python 버전", check_python_version),
        ("필수 모듈", check_required_modules), 
        ("프로젝트 구조", check_project_structure),
        ("데이터 디렉토리", check_data_directories),
        ("환경 설정", check_env_file),
        ("모듈 Import", test_module_imports),
        ("데이터 파일", check_data_files),
        ("모델 파일", check_model_files),
        ("웹 애플리케이션", check_web_app)
    ]
    
    results = []
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"   {check_name} 확인 중 오류: {e}")
            results.append((check_name, False))
    
    # 선택적 모듈 확인 (오류 무시)
    try:
        check_optional_modules()
    except:
        pass
    
    # 결과 요약
    print("\n" + "="*80)
    print("진단 결과 요약:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "통과" if result else "실패"
        print(f"   {check_name}: {status}")
    
    print(f"\n전체 상태: {passed}/{total} 통과")
    
    if passed == total:
        print("모든 확인 완료! 시스템이 정상 상태입니다.")
        print("이제 python run.py로 시스템을 실행하세요.")
    elif passed >= total - 2:
        print("일부 문제가 있지만 기본 실행은 가능합니다.")
        print("💡 python run.py로 시스템을 실행한 후 필요한 부분을 설정하세요.")
    else:
        print("여러 문제가 발견되었습니다.")
        suggest_fixes()
    
    return passed >= total - 2

if __name__ == "__main__":
    try:
        success = main()
        input(f"\n{'진단 완료!' if success else '❌ 문제 발견!'} Enter 키로 종료...")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n🛑 사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n진단 중 예상치 못한 오류: {e}")
        sys.exit(1)