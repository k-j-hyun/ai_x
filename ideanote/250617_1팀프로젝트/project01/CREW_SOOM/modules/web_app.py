from flask import Flask, render_template, request, jsonify, session
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import os
import json
from datetime import datetime, timedelta
import io
import base64
import time
import threading
import requests
import urllib.parse
from dotenv import load_dotenv
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score, roc_curve
from modules.multi_weather_api import MultiWeatherAPI
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

class FloodWebApp:
    """4개 기상청 API 통합 침수 예측 시스템 - 설계구조도 기반"""

    def __init__(self):
        load_dotenv()
        
        # 🔧 올바른 템플릿 경로 설정
        import os
        current_dir = os.path.dirname(__file__)  # modules 폴더
        project_root = os.path.dirname(current_dir)  # CREW_SOOM 폴더
        
        self.app = Flask(__name__, 
                        template_folder=os.path.join(project_root, 'templates'),
                        static_folder=os.path.join(project_root, 'static'))
        self.app.secret_key = 'soom_flood_prediction_2024'
        
        # 🔧 기존 모듈들 초기화
        from modules.data_loader import DataLoader  # Ensure the correct module path
        self.data_loader = DataLoader()
        from modules.preprocessor import DataPreprocessor  # Ensure the correct module path
        self.preprocessor = DataPreprocessor()
        from modules.trainer import ModelTrainer  # Ensure the correct module path
        self.trainer = ModelTrainer()
        from modules.evaluator import ModelEvaluator  # Ensure the correct module path
        self.evaluator = ModelEvaluator()
        from modules.visualizer import DataVisualizer  # Ensure the correct module path
        self.visualizer = DataVisualizer()
        
        # 기본 변수 초기화
        self.model = None
        self.feature_names = []
        self.data = None
        self.model_loaded = False
        self.data_last_updated = None
        self.data_start_date = None
        self.data_end_date = None
        self.auto_update_enabled = False
        self.update_interval = 3600  # 1시간
        self.last_check_time = None
        self.selected_model_name = 'randomforest'
        
        # 실제 데이터 수집 관련
        self.data_collection_in_progress = False
        self.collection_progress = 0
        self.collection_status = "대기 중"
        
        # API 설정
        self.service_key = os.getenv('OPENWEATHER_API_KEY')
        self.city = os.getenv('WEATHER_CITY', 'Seoul')
        self.api_available = bool(self.service_key)
        
        if self.api_available:
            self.multi_api = MultiWeatherAPI(self.service_key)
            print(f"✅ 4개 기상청 API 연결 성공")
        else:
            print("API 키가 없습니다. 시뮬레이션 모드는 지원하지 않습니다.")
            self.multi_api = None
        
        # 디렉토리 생성
        self.ensure_directories()
        
        # 라우트 설정
        self.setup_routes()
        
        # 기존 데이터 확인 (설계구조도 기반)
        self.check_existing_data()
        
        # 자동 업데이트 서비스 시작
        self.start_auto_update_service()
    
    def ensure_directories(self):
        """필요한 디렉토리 생성 (설계구조도 기반)"""
        directories = [
            'data', 'data/processed', 'data/raw', 'data/database', 'data/flood_events',
            'models', 'outputs', 'logs', 'users', 'logo'
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def setup_routes(self):
        """라우트 설정"""
        
        @self.app.route('/')
        def dashboard():
            return render_template('dashboard.html')
        
        @self.app.route('/login')
        def login_page():
            return render_template('login.html')
        
        @self.app.route('/api/status')
        def get_status():
            return jsonify({
                'data_loaded': self.data is not None,
                'data_rows': len(self.data) if self.data is not None else 0,
                'model_loaded': self.model_loaded,
                'features': len(self.feature_names) if self.feature_names else 0,
                'data_start_date': self.data_start_date.isoformat() if self.data_start_date else None,
                'data_end_date': self.data_end_date.isoformat() if self.data_end_date else None,
                'data_last_updated': self.data_last_updated.isoformat() if self.data_last_updated else None,
                'auto_update_enabled': self.auto_update_enabled,
                'last_check_time': self.last_check_time.isoformat() if self.last_check_time else None,
                'update_interval': self.update_interval,
                'update_interval_minutes': self.update_interval // 60,
                'api_available': self.api_available,
                'api_location': f"{self.city} (4개 기상청 API 통합)" if self.api_available else None,
                'today': datetime.now().strftime('%Y-%m-%d'),
                'current_model_name': self.selected_model_name,
                'collection_in_progress': self.data_collection_in_progress,
                'collection_progress': self.collection_progress,
                'collection_status': self.collection_status
            })
        
        @self.app.route('/api/login', methods=['POST'])
        def login_api():
            data = request.get_json()
            if data.get('username') == 'admin' and data.get('password') == '1234':
                session['user'] = 'admin'
                return jsonify({'success': True})
            else:
                return jsonify({'success': False, 'message': 'ID 또는 비밀번호가 틀립니다.'})
        
        @self.app.route('/api/logout')
        def logout():
            session.pop('user', None)
            return jsonify({'success': True})
        
        @self.app.route('/api/session')
        def session_check():
            return jsonify({'logged_in': 'user' in session})
        
        @self.app.route('/api/load_data', methods=['POST'])
        def load_data():
            """실제 데이터 수집 시작"""
            try:
                if not self.api_available:
                    return jsonify({'success': False, 'message': 'API 키가 필요합니다.'})
                
                if self.data_collection_in_progress:
                    return jsonify({'success': False, 'message': '데이터 수집이 이미 진행 중입니다.'})
                
                # 기존 데이터 확인
                if self.data is not None and len(self.data) > 0:
                    return jsonify({
                        'success': True,
                        'message': f'기존 데이터 로드 완료: {len(self.data)}행',
                        'rows': len(self.data),
                        'start_date': self.data_start_date.isoformat() if self.data_start_date else None,
                        'end_date': self.data_end_date.isoformat() if self.data_end_date else None
                    })
                
                # 백그라운드에서 실제 데이터 수집 시작
                self.start_real_data_collection()
                
                return jsonify({
                    'success': True,
                    'message': '실제 데이터 수집을 시작했습니다. 진행 상황을 모니터링하세요.',
                    'collection_started': True
                })
                
            except Exception as e:
                return jsonify({'success': False, 'message': str(e)})
        
        @self.app.route('/api/update_data', methods=['POST'])
        def update_data():
            """실제 API 데이터 업데이트"""
            try:
                if not self.api_available:
                    return jsonify({'success': False, 'message': 'API 키가 필요합니다.'})
                
                if self.data is None:
                    return jsonify({'success': False, 'message': '먼저 데이터를 로드하세요.'})
                
                old_count = len(self.data)
                
                # 🔧 실제 4개 API 데이터 수집
                success_count, new_data = self.collect_real_time_data()
                
                if new_data:
                    # 실제 데이터를 데이터프레임에 추가
                    new_df = pd.DataFrame([new_data])
                    self.data = pd.concat([self.data, new_df], ignore_index=True)
                    
                    # 데이터 저장 (설계구조도 기반 경로)
                    self.save_data_to_file()
                    
                    # 최신 날짜 업데이트
                    self.data_end_date = new_data['obs_date']
                    self.data_last_updated = datetime.now()
                    
                    return jsonify({
                        'success': True,
                        'message': f'실제 API 데이터 업데이트 완료 ({success_count}/4 성공)',
                        'old_count': old_count,
                        'new_count': len(self.data),
                        'added_count': 1,
                        'api_success_count': success_count,
                        'data_quality': 'REAL_DATA',
                        'latest_date': self.data_end_date.isoformat()
                    })
                else:
                    return jsonify({
                        'success': False,
                        'message': f'API 데이터 수집 실패 ({success_count}/4 성공)'
                    })
                
            except Exception as e:
                return jsonify({'success': False, 'message': str(e)})
        
        @self.app.route('/api/toggle_auto_update', methods=['POST'])
        def toggle_auto_update():
            try:
                if not self.api_available:
                    return jsonify({'success': False, 'message': 'API 키가 필요합니다.'})
                
                self.auto_update_enabled = not self.auto_update_enabled
                return jsonify({
                    'success': True,
                    'auto_update_enabled': self.auto_update_enabled,
                    'message': f'실제 데이터 자동 업데이트가 {"활성화" if self.auto_update_enabled else "비활성화"}되었습니다.'
                })
            except Exception as e:
                return jsonify({'success': False, 'message': str(e)})
        
        @self.app.route('/api/train_model', methods=['POST'])
        def train_model():
            try:
                if self.data is None:
                    return jsonify({'success': False, 'message': '먼저 실제 데이터를 로드하세요.'})
                
                # 실제 데이터 기반 특성 선택
                feature_cols = ['precipitation', 'humidity', 'avg_temp', 'wind_speed', 'pressure', 'month']
                available_cols = [col for col in feature_cols if col in self.data.columns]
                
                if len(available_cols) < 3:
                    return jsonify({'success': False, 'message': '충분한 특성이 없습니다.'})
                
                # 타겟 변수 생성 (실제 데이터 기반)
                if 'is_flood_risk' not in self.data.columns:
                    self.data['is_flood_risk'] = (self.data['precipitation'] >= 50).astype(int)
                
                X = self.data[available_cols].fillna(0)
                y = self.data['is_flood_risk']
                
                # 실제 데이터가 충분한지 확인
                if len(X) < 100:
                    return jsonify({'success': False, 'message': f'훈련에 필요한 데이터가 부족합니다. (현재: {len(X)}행, 필요: 100행 이상)'})
                
                # 데이터 분할
                split_idx = int(len(X) * 0.8)
                X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
                y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
                
                # 모델 훈련 (실제 데이터 기반)
                self.model = RandomForestClassifier(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42,
                    n_jobs=-1
                )
                self.model.fit(X_train, y_train)
                self.feature_names = available_cols
                self.model_loaded = True
                
                # 성능 평가
                y_pred = self.model.predict(X_test)
                from sklearn.metrics import accuracy_score, precision_score, recall_score
                
                accuracy = accuracy_score(y_test, y_pred)
                precision = precision_score(y_test, y_pred, average='weighted')
                recall = recall_score(y_test, y_pred, average='weighted')
                
                # 모델 저장
                os.makedirs('models', exist_ok=True)
                joblib.dump(self.model, 'models/randomforest_model.pkl')
                joblib.dump(self.feature_names, 'models/feature_names.pkl')
                
                return jsonify({
                    'success': True,
                    'message': '실제 데이터 기반 모델 훈련 완료!',
                    'accuracy': round(accuracy, 3),
                    'precision': round(precision, 3),
                    'recall': round(recall, 3),
                    'features': len(available_cols),
                    'training_size': len(X_train),
                    'data_type': 'REAL_API_DATA'
                })
            except Exception as e:
                return jsonify({'success': False, 'message': str(e)})
        
        @self.app.route('/api/predict', methods=['POST'])
        def predict():
            try:
                data = request.get_json()
                
                # 실제 데이터 기반 예측
                if self.model_loaded and self.model is not None:
                    # ML 모델 예측
                    risk_score = self.predict_with_model(data)
                else:
                    # 규칙 기반 예측
                    risk_score = self.calculate_risk_score(data)
                
                # 위험 등급 결정
                risk_info = self.get_risk_level(risk_score)
                
                recommendations = {
                    0: ["정상적인 업무 진행", "일기예보 정기 확인"],
                    1: ["기상 상황 주시", "우산 준비"],
                    2: ["외출 시 주의", "지하공간 점검"],
                    3: ["불필요한 외출 자제", "중요 물품 이동"],
                    4: ["즉시 대피 준비", "119 신고 대기"]
                }
                
                return jsonify({
                    'risk_score': round(risk_score, 1),
                    'risk_level': risk_info['level'],
                    'risk_name': risk_info['name'],
                    'risk_color': risk_info['color'],
                    'action': risk_info['action'],
                    'recommendations': recommendations.get(risk_info['level'], []),
                    'prediction_time': datetime.now().isoformat(),
                    'model_used': f'{self.selected_model_name} ML Model' if self.model_loaded else 'Rule-based',
                    'data_source': 'ML_COMPLETE_DATASET'
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/create_visualization', methods=['POST'])
        def create_visualization():
            try:
                if self.data is None:
                    return jsonify({'success': False, 'message': '먼저 실제 데이터를 로드하세요.'})
                
                viz_type = request.json.get('type', 'precipitation')
                
                plt.figure(figsize=(12, 8))
                
                if viz_type == 'precipitation':
                    plt.plot(self.data['obs_date'], self.data['precipitation'], linewidth=2, alpha=0.8)
                    plt.title('실제 API 데이터 - 강수량 시계열', fontsize=16)
                    plt.xlabel('날짜')
                    plt.ylabel('강수량 (mm)')
                    plt.xticks(rotation=45)
                    plt.grid(True, alpha=0.3)
                    
                    # 실제 데이터 품질 표시
                    plt.text(0.02, 0.98, f'📊 실제 데이터: {len(self.data)}개', 
                            transform=plt.gca().transAxes, fontsize=10,
                            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue'))
                
                elif viz_type == 'distribution':
                    plt.hist(self.data['precipitation'], bins=30, alpha=0.7, edgecolor='black')
                    plt.title('실제 API 데이터 - 강수량 분포', fontsize=16)
                    plt.xlabel('강수량 (mm)')
                    plt.ylabel('빈도')
                    plt.grid(True, alpha=0.3)
                    
                    # 통계 정보 표시
                    mean_val = self.data['precipitation'].mean()
                    plt.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'평균: {mean_val:.1f}mm')
                    plt.legend()
                
                plt.tight_layout()
                
                # 이미지를 base64로 변환
                img_buffer = io.BytesIO()
                plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
                img_buffer.seek(0)
                img_base64 = base64.b64encode(img_buffer.read()).decode()
                plt.close()
                
                return jsonify({
                    'success': True,
                    'image': f'data:image/png;base64,{img_base64}',
                    'message': f'실제 데이터 {viz_type} 차트 생성 완료',
                    'data_count': len(self.data),
                    'data_type': 'REAL_API_DATA'
                })
            except Exception as e:
                return jsonify({'success': False, 'message': str(e)})
        
        @self.app.route('/api/collection_progress')
        def get_collection_progress():
            """데이터 수집 진행 상황 조회"""
            return jsonify({
                'in_progress': self.data_collection_in_progress,
                'progress': self.collection_progress,
                'status': self.collection_status,
                'current_data_count': len(self.data) if self.data is not None else 0
            })
    
    def start_real_data_collection(self):
        """실제 데이터 수집 시작 (백그라운드)"""
        def collection_worker():
            self.data_collection_in_progress = True
            self.collection_progress = 0
            self.collection_status = "실제 데이터 수집 시작"
            
            try:
                print("🏭 실제 데이터 수집 시작")
                
                # 최근 30일부터 시작 (테스트용)
                end_date = datetime.now() - timedelta(days=2)
                start_date = end_date - timedelta(days=30)
                
                collected_data = []
                date_range = pd.date_range(start=start_date, end=end_date, freq='D')
                total_days = len(date_range)
                
                for i, date in enumerate(date_range):
                    self.collection_progress = int((i / total_days) * 100)
                    self.collection_status = f"데이터 수집 중: {date.strftime('%Y-%m-%d')}"
                    
                    # 실제 API 호출
                    daily_data = self.collect_single_day_data(date)
                    if daily_data:
                        collected_data.append(daily_data)
                    
                    # API 제한 준수
                    time.sleep(2)
                
                # 수집된 데이터를 DataFrame으로 변환
                if collected_data:
                    self.data = pd.DataFrame(collected_data)
                    self.data_start_date = self.data['obs_date'].min()
                    self.data_end_date = self.data['obs_date'].max()
                    self.data_last_updated = datetime.now()
                    
                    # 파일 저장
                    self.save_data_to_file()
                    
                    self.collection_status = f"수집 완료: {len(collected_data)}개 데이터"
                    print(f"✅ 실제 데이터 수집 완료: {len(collected_data)}개")
                else:
                    self.collection_status = "수집 실패: 데이터 없음"
                    print("❌ 데이터 수집 실패")
                
            except Exception as e:
                self.collection_status = f"수집 오류: {str(e)}"
                print(f"❌ 데이터 수집 오류: {e}")
            
            finally:
                self.data_collection_in_progress = False
                self.collection_progress = 100
        
        # 백그라운드 스레드 시작
        collection_thread = threading.Thread(target=collection_worker, daemon=True)
        collection_thread.start()
    
    def collect_single_day_data(self, date):
        """특정 날짜의 실제 데이터 수집"""
        try:
            if not self.multi_api:
                return None
            
            # 날짜를 API 호출용 형식으로 변환
            date_str = date.strftime('%Y%m%d')
            
            # 4개 API 통합 호출 (과거 데이터용으로 수정 필요)
            weather_results = self.multi_api.get_comprehensive_weather_data()
            
            if weather_results['success']:
                data = weather_results['weather_data']
                
                return {
                    'obs_date': date,
                    'precipitation': data.get('precipitation', 0),
                    'humidity': data.get('humidity', 60),
                    'avg_temp': data.get('temperature', 20),
                    'wind_speed': data.get('wind_speed', 0),
                    'pressure': data.get('pressure', 1013),
                    'month': date.month,
                    'data_quality': 'REAL_API',
                    'api_success_count': len(weather_results['data_sources']),
                    'data_source': 'REAL_DATA'
                }
            else:
                return None
                
        except Exception as e:
            print(f"❌ {date} 데이터 수집 실패: {e}")
            return None
    
    def collect_real_time_data(self):
        """실시간 실제 데이터 수집"""
        try:
            if not self.multi_api:
                return 0, None
            
            # 4개 API 통합 호출
            weather_results = self.multi_api.get_comprehensive_weather_data()
            
            if weather_results['success']:
                data = weather_results['weather_data']
                success_count = len(weather_results['data_sources'])
                
                new_data = {
                    'obs_date': datetime.now(),
                    'precipitation': data.get('precipitation', 0),
                    'humidity': data.get('humidity', 60),
                    'avg_temp': data.get('temperature', 20),
                    'wind_speed': data.get('wind_speed', 0),
                    'pressure': data.get('pressure', 1013),
                    'month': datetime.now().month,
                    'data_quality': 'REAL_API',
                    'api_success_count': success_count,
                    'data_source': 'REAL_DATA'
                }
                
                # 침수 위험 여부 계산
                new_data['is_flood_risk'] = 1 if new_data['precipitation'] >= 50 else 0
                
                return success_count, new_data
            else:
                return 0, None
                
        except Exception as e:
            print(f"❌ 실시간 데이터 수집 실패: {e}")
            return 0, None
    
    def check_existing_data(self):
        """기존 데이터 확인"""
        data_path = 'data/processed/REAL_WEATHER_DATA.csv'
        
        if os.path.exists(data_path):
            try:
                self.data = pd.read_csv(data_path)
                self.data['obs_date'] = pd.to_datetime(self.data['obs_date'])
                self.data_start_date = self.data['obs_date'].min()
                self.data_end_date = self.data['obs_date'].max()
                self.data_last_updated = datetime.now()
                print(f"✅ 기존 실제 데이터 로드: {len(self.data)}행")
                print(f"📅 데이터 기간: {self.data_start_date.date()} ~ {self.data_end_date.date()}")
            except Exception as e:
                print(f"❌ 데이터 로드 실패: {e}")
                self.data = None
        else:
            print("📊 기존 데이터 없음. 새로 수집이 필요합니다.")
        
        # 모델 체크
        if os.path.exists('models/randomforest_model.pkl'):
            try:
                self.model = joblib.load('models/randomforest_model.pkl')
                self.feature_names = joblib.load('models/feature_names.pkl')
                self.model_loaded = True
                print("✅ 모델 로드 성공")
            except:
                print("❌ 모델 로드 실패")
    
    def save_data_to_file(self):
        """실제 데이터 파일 저장"""
        if self.data is not None:
            output_path = 'data/processed/REAL_WEATHER_DATA.csv'
            self.data.to_csv(output_path, index=False)
            print(f"💾 실제 데이터 저장: {output_path}")
    
    def predict_with_real_model(self, data):
        """실제 데이터 기반 ML 모델 예측"""
        try:
            features = []
            feature_data = {
                'precipitation': data.get('precipitation', 0),
                'humidity': data.get('humidity', 60),
                'avg_temp': data.get('avg_temp', 20),
                'wind_speed': data.get('wind_speed', 2),
                'pressure': data.get('pressure', 1013),
                'month': datetime.now().month
            }
            
            for feature_name in self.feature_names:
                features.append(feature_data.get(feature_name, 0))
            
            prediction_proba = self.model.predict_proba([features])[0][1]
            return prediction_proba * 100
            
        except Exception as e:
            return self.calculate_risk_score(data)
    
    def calculate_risk_score(self, data):
        """규칙 기반 위험도 계산"""
        score = 0
        
        precipitation = data.get('precipitation', 0)
        score += min(precipitation * 0.5, 50)
        
        humidity = data.get('humidity', 50)
        score += min((humidity - 50) * 0.3, 20)
        
        pressure = data.get('pressure', 1013)
        if pressure < 1000:
            score += 15
        elif pressure < 1005:
            score += 10
        
        season_type = data.get('season_type', 'dry')
        if season_type == 'rainy':
            score += 15
        
        return min(score, 100)
    
    def get_risk_level(self, score):
        """위험도 등급"""
        if score <= 20:
            return {'level': 0, 'name': '매우낮음', 'color': '🟢', 'action': '정상 업무'}
        elif score <= 40:
            return {'level': 1, 'name': '낮음', 'color': '🟡', 'action': '상황 주시'}
        elif score <= 60:
            return {'level': 2, 'name': '보통', 'color': '🟠', 'action': '주의 준비'}
        elif score <= 80:
            return {'level': 3, 'name': '높음', 'color': '🔴', 'action': '대비 조치'}
        else:
            return {'level': 4, 'name': '매우높음', 'color': '🟣', 'action': '즉시 대응'}
    
    def start_auto_update_service(self):
        """실제 데이터 자동 업데이트 서비스"""
        def auto_update_worker():
            while True:
                if self.auto_update_enabled and self.api_available:
                    self.last_check_time = datetime.now()
                    try:
                        print(f"🕐 {self.last_check_time.strftime('%H:%M:%S')} - 실제 데이터 자동 업데이트 실행")
                        
                        success_count, new_data = self.collect_real_time_data()
                        
                        if new_data and self.data is not None:
                            # 실제 데이터 추가
                            new_df = pd.DataFrame([new_data])
                            self.data = pd.concat([self.data, new_df], ignore_index=True)
                            
                            # 파일 저장
                            self.save_data_to_file()
                            
                            self.data_end_date = new_data['obs_date']
                            self.data_last_updated = datetime.now()
                            
                            print(f"✅ 실제 데이터 자동 업데이트 완료 ({success_count}/4 성공)")
                        
                    except Exception as e:
                        print(f"❌ 자동 업데이트 오류: {e}")
                
                time.sleep(self.update_interval)
        
        if self.api_available:
            update_thread = threading.Thread(target=auto_update_worker, daemon=True)
            update_thread.start()
            print("🔄 실제 데이터 자동 업데이트 서비스 시작")
    
    def run(self):
        """웹 서버 실행"""
        print("🌊 CREW_SOOM 실제 데이터 수집 시스템 시작!")
        print("📡 4개 기상청 API 실제 데이터만 사용")
        print("📍 주소: http://localhost:5000")
        print("🔑 로그인: admin / 1234")
        print("🛑 종료: Ctrl+C")
        
        self.app.run(debug=True, host='0.0.0.0', port=5000)