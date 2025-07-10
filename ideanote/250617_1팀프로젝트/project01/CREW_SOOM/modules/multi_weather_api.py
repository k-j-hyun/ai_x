# modules/multi_weather_api.py - 서울시 25개 지역구 전용 전략적 침수 예측 데이터 수집 시스템
import requests
import urllib.parse
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import os
import time
import calendar
import sqlite3
import os
import time
import calendar


class MultiWeatherAPI:
    """서울시 25개 지역구 전용 전략적 침수 예측 데이터 수집 시스템
    
    주요 개선사항:
    1. 전략적 수집: 장마철(5-9월) 중심 + 대조군(1,2,11,12월)
    2. 안정적 API만 사용: ASOS 일자료 + 단기예보 (2개만)
    3. CSV 직접 저장: web_app.py와 완벽 호환
    4. 증분 업데이트: 이미 수집된 데이터는 스킵
    5. ML 준비 완료: 바로 훈련 가능한 데이터셋 제공
    """
    
    def __init__(self, service_key):
        # URL 디코딩
        self.service_key = urllib.parse.unquote(service_key)
        
        # 안정적인 2개 API만 사용 (ASOS 시간자료, 기상특보 제외)
        self.apis = {
            'asos_daily': {
                'url': 'http://apis.data.go.kr/1360000/AsosDalyInfoService/getWthrDataList',
                'name': '지상(ASOS) 일자료',
                'description': '일별 종합 기상 데이터 (안정적)'
            },
            'short_forecast': {
                'url': 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst',
                'name': '단기예보(초단기실황)',
                'description': '격자 기반 실시간 데이터 (안정적)'
            }
        }
        
        # 서울시 25개 지역구 전용 관측소 정보
        self.seoul_stations = {
            'main': {'stnId': '108', 'name': '서울', 'nx': 60, 'ny': 127},              # 서울시 중구 (본청)
            'gangnam': {'stnId': '401', 'name': '서울강남', 'nx': 61, 'ny': 125},      # 강남구
            'songpa': {'stnId': '402', 'name': '서울송파', 'nx': 62, 'ny': 126}        # 송파구
        }
        
        # 전략적 수집 계획 (StrategicFloodDataCollector 참조)
        self.collection_strategy = {
            # 장마철 집중 수집 (침수 위험 높음)
            "rainy_season": [5, 6, 7, 8, 9],  # 5-9월 (장마+태풍)
            
            # 대조군 수집 (침수 위험 낮음)  
            "dry_season": [1, 2, 11, 12],  # 겨울철 (건조)
            
            # 연도별 수집 (2022-2025년)
            "years": [2022, 2023, 2024, 2025]
        }
        
        # CSV 파일 경로 설정
        self.csv_path = 'data/processed/REAL_WEATHER_DATA.csv'
        os.makedirs('data/processed', exist_ok=True)
        print("✅ CSV 기반 데이터 저장 시스템 초기화 완료")
        
        # 실제 침수 사건 데이터 (기존 코드 참조)
        self.actual_flood_events = [
            {"district": "강남구", "date": "2022-08-08", "severity": 4, "precip_24h": 381.5, "desc": "강남역 일대 대침수"},
            {"district": "서초구", "date": "2022-08-08", "severity": 4, "precip_24h": 381.5, "desc": "반포동 침수"},
            {"district": "관악구", "date": "2022-08-08", "severity": 3, "precip_24h": 381.5, "desc": "신림동 침수"},
            {"district": "송파구", "date": "2025-05-23", "severity": 2, "precip_24h": 78.4, "desc": "잠실동 침수"},
            {"district": "광진구", "date": "2025-06-15", "severity": 3, "precip_24h": 112.7, "desc": "구의동 침수"}
        ]
    
    def init_strategic_database(self):
        """전략적 수집용 SQLite DB 초기화"""
        self.db_path = 'data/processed/seoul_flood_prediction.db'
        os.makedirs('data/processed', exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 전략적 일자료 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS strategic_daily (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year INTEGER, month INTEGER, day INTEGER,
                obs_date DATE, season_type TEXT,
                avg_temp REAL, min_temp REAL, max_temp REAL,
                humidity REAL, precipitation REAL, wind_speed REAL,
                is_flood_risk INTEGER,
                actual_flood INTEGER DEFAULT 0,
                data_quality TEXT DEFAULT 'API',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(obs_date)
            )
        ''')
        
        # 실시간 기상 데이터 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS realtime_weather (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                temperature REAL, precipitation REAL, humidity REAL,
                wind_speed REAL, pressure REAL,
                data_source TEXT,
                collected_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 실제 침수 사건 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS actual_flood_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                district TEXT, flood_date DATE,
                severity INTEGER, precipitation_24h REAL,
                description TEXT, source TEXT DEFAULT 'NEWS',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ 전략적 침수 예측 DB 초기화 완료")
    
    def get_comprehensive_weather_data(self):
        """안정적인 2개 API로 종합 기상 데이터 수집"""
        print("🌤️ 안정적인 2개 API 데이터 수집 시작...")
        
        results = {
            'timestamp': datetime.now(),
            'data_sources': [],
            'weather_data': {},
            'success': False,
            'errors': []
        }
        
        # 1. ASOS 일자료 (가장 안정적)
        asos_daily = self.fetch_asos_daily_data()
        if asos_daily['success']:
            results['weather_data'].update(asos_daily['data'])
            results['data_sources'].append('ASOS 일자료')
            print("✅ ASOS 일자료 수집 성공")
        else:
            results['errors'].append(f"ASOS 일자료: {asos_daily['error']}")
            print(f"❌ ASOS 일자료 실패: {asos_daily['error']}")
        
        # 2. 단기예보 (격자 데이터)
        short_forecast = self.fetch_short_forecast_data()
        if short_forecast['success']:
            results['weather_data'].update(short_forecast['data'])
            results['data_sources'].append('단기예보')
            print("✅ 단기예보 수집 성공")
        else:
            results['errors'].append(f"단기예보: {short_forecast['error']}")
            print(f"❌ 단기예보 실패: {short_forecast['error']}")
        
        # 성공 여부 판단 (1개 이상 성공)
        results['success'] = len(results['data_sources']) > 0
        
        if results['success']:
            # 데이터 통합 및 실시간 저장
            results['weather_data'] = self.integrate_weather_data(results)
            self.save_realtime_data(results['weather_data'])
            print(f"🎯 안정적인 데이터 수집 완료! (성공: {len(results['data_sources'])}/2)")
        else:
            print("❌ 모든 API 호출 실패")
        
        return results
    
    def fetch_asos_daily_data(self, max_years=5):
        """ASOS 일자료 API 호출 - 증분 업데이트 (마지막 수집일 다음부터만)"""
        try:
            station = self.seoul_stations['main']
            
            # 1. 이미 수집된 마지막 날짜 확인 (CSV 파일에서)
            if os.path.exists(self.csv_path):
                try:
                    existing_df = pd.read_csv(self.csv_path)
                    if not existing_df.empty and 'obs_date' in existing_df.columns:
                        existing_df['obs_date'] = pd.to_datetime(existing_df['obs_date'])
                        last_date = existing_df['obs_date'].max()
                        
                        # 🔧 수정: 날짜 타입 통일 (datetime.date로 변환)
                        if hasattr(last_date, 'date'):
                            last_date = last_date.date()
                        
                        start_date = last_date + timedelta(days=1)
                        update_type = "증분 업데이트"
                        print(f"📅 {update_type}: {last_date} 다음부터 수집")
                    else:
                        # CSV 파일이 비어있음
                        end_date = datetime.now() - timedelta(days=1)
                        start_date = end_date - timedelta(days=max_years * 365)
                        update_type = "초기 수집"
                        print(f"📅 {update_type}: {max_years}년치 전체 수집")
                except Exception as e:
                    print(f"⚠️ 기존 CSV 읽기 오류: {e}")
                    end_date = datetime.now() - timedelta(days=1)
                    start_date = end_date - timedelta(days=max_years * 365)
                    update_type = "초기 수집"
                    print(f"📅 {update_type}: {max_years}년치 전체 수집")
            else:
                # CSV 파일이 없음
                end_date = datetime.now() - timedelta(days=1)
                start_date = end_date - timedelta(days=max_years * 365)
                update_type = "초기 수집"
                print(f"📅 {update_type}: {max_years}년치 전체 수집")
            
            # 2. 수집 종료일 설정
            end_date = datetime.now() - timedelta(days=1)  # 어제까지
            
            # 수집할 날짜가 없으면 종료
            if start_date > end_date:
                print("✅ 이미 최신 데이터입니다. 수집할 새로운 데이터가 없습니다.")
                
                # 최신 데이터 반환 (CSV에서 읽기)
                try:
                    latest_df = pd.read_csv(self.csv_path)
                    if not latest_df.empty:
                        latest_df['obs_date'] = pd.to_datetime(latest_df['obs_date'])
                        latest_row = latest_df.iloc[-1]  # 마지막 행
                        
                        return {
                            'success': True,
                            'data': {
                                'daily_precipitation': latest_row.get('precipitation', 0),
                                'max_temperature': latest_row.get('max_temp', 0),
                                'min_temperature': latest_row.get('min_temp', 0),
                                'avg_temperature': latest_row.get('avg_temp', 0),
                                'avg_humidity': latest_row.get('humidity', 60),
                                'max_wind_speed': latest_row.get('wind_speed', 0),
                                'sunshine_duration': 0,
                                'observation_date': latest_row.get('obs_date'),
                                'data_count': 0,
                                'update_type': '최신 상태'
                            }
                        }
                except Exception as e:
                    print(f"⚠️ CSV 읽기 오류: {e}")
                
                return {
                    'success': True,
                    'data': {
                        'update_type': '최신 상태',
                        'message': '새로운 데이터 없음',
                        'data_count': 0
                    }
                }
            
            # 3. 수집할 일수 계산
            days_to_collect = (end_date - start_date).days + 1
            print(f"📊 수집 예정: {days_to_collect}일 ({start_date} ~ {end_date})")
            
            all_data = []
            current_start = start_date
            batch_size = 500  # 🔧 수정: 999 → 500으로 안전하게
            
            while current_start <= end_date:
                # 배치별 종료일 계산 (1일 빼서 정확히 500일)
                current_end = min(current_start + timedelta(days=batch_size - 1), end_date)
                
                start_dt = current_start.strftime('%Y%m%d')
                end_dt = current_end.strftime('%Y%m%d')
                
                batch_days = (current_end - current_start).days + 1
                print(f"📅 배치 수집: {start_dt} ~ {end_dt} ({batch_days}일)")
                
                params = {
                    'serviceKey': self.service_key,
                    'pageNo': '1',
                    'numOfRows': str(batch_days + 50),  # 🔧 수정: 여유있게 설정
                    'dataType': 'JSON',
                    'dataCd': 'ASOS',
                    'dateCd': 'DAY',
                    'startDt': start_dt,
                    'endDt': end_dt,
                    'stnIds': station['stnId']
                }
                
                try:
                    response = requests.get(self.apis['asos_daily']['url'], params=params, timeout=30)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        if 'response' in data and data['response']['header']['resultCode'] == '00':
                            items = data['response']['body'].get('items', {}).get('item', [])
                            
                            if items:
                                # 리스트가 아닌 경우 리스트로 변환
                                if not isinstance(items, list):
                                    items = [items]
                                
                                all_data.extend(items)
                                print(f"    ✅ {len(items)}일 수집 완료 (총 {len(all_data)}일)")
                                
                                # CSV에 배치 저장
                                self.save_daily_data_to_csv(items)
                            else:
                                print(f"    ⚠️ {start_dt}~{end_dt}: 데이터 없음")
                        else:
                            error_code = data.get('response', {}).get('header', {}).get('resultCode', 'UNKNOWN')
                            error_msg = data.get('response', {}).get('header', {}).get('resultMsg', '알 수 없는 오류')
                            print(f"    ❌ API 오류 ({error_code}): {error_msg}")
                            
                            # 99번 오류(날짜 범위 초과)면 해당 배치 스킵하고 계속 진행
                            if error_code == '99':
                                print(f"    ⏭️ 날짜 범위 초과로 배치 스킵 - 계속 진행")
                                # break 제거 - 다음 배치 계속 진행
                            else:
                                print(f"    ❌ 다른 API 오류로 배치 스킵")
                                # 다른 오류는 스킵하고 계속
                    else:
                        print(f"    ❌ HTTP 오류: {response.status_code}")
                    
                    # API 제한 준수를 위한 대기
                    if update_type == "증분 업데이트" and days_to_collect < 30:
                        time.sleep(0.5)  # 짧은 업데이트는 빠르게
                    else:
                        time.sleep(1.0)  # 대량 수집은 안전하게
                    
                except Exception as e:
                    print(f"    ❌ 배치 수집 실패 ({start_dt}~{end_dt}): {e}")
                
                # 다음 배치로 이동 (batch_size만큼 이동)
                current_start = current_end + timedelta(days=1)
            
            print(f"🎯 {update_type} 완료: 총 {len(all_data)}일 수집")
            
            if all_data:
                # 최신 데이터 반환
                latest_item = all_data[-1]
                
                return {
                    'success': True,
                    'data': {
                        'daily_precipitation': float(latest_item.get('sumRn', 0) or 0),
                        'max_temperature': float(latest_item.get('maxTa', 0) or 0),
                        'min_temperature': float(latest_item.get('minTa', 0) or 0),
                        'avg_temperature': (float(latest_item.get('maxTa', 0) or 0) + float(latest_item.get('minTa', 0) or 0)) / 2,
                        'avg_humidity': float(latest_item.get('avgRhm', 60) or 60),
                        'max_wind_speed': float(latest_item.get('maxWs', 0) or 0),
                        'sunshine_duration': float(latest_item.get('sumSsHr', 0) or 0),
                        'observation_date': latest_item.get('tm', end_date.strftime('%Y%m%d')),
                        'data_count': len(all_data),
                        'update_type': update_type,
                        'collection_period': f"{start_date} ~ {end_date}",
                        'total_days_collected': days_to_collect
                    }
                }
            else:
                return {
                    'success': True, 
                    'data': {
                        'update_type': update_type,
                        'message': '새로운 데이터 없음 또는 수집 완료',
                        'data_count': 0
                    }
                }
                
        except Exception as e:
            return {'success': False, 'error': f'예외 발생: {str(e)}'}
    
    def fetch_short_forecast_data(self):
        """단기예보 (격자) API 호출"""
        try:
            station = self.seoul_stations['main']
            now = datetime.now()
            base_time = now.replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)
            
            params = {
                'serviceKey': self.service_key,
                'pageNo': '1',
                'numOfRows': '1000',
                'dataType': 'JSON',
                'base_date': base_time.strftime('%Y%m%d'),
                'base_time': base_time.strftime('%H%M'),
                'nx': str(station['nx']),
                'ny': str(station['ny'])
            }
            
            response = requests.get(self.apis['short_forecast']['url'], params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'response' in data and data['response']['header']['resultCode'] == '00':
                    items = data['response']['body'].get('items', {}).get('item', [])
                    
                    forecast_data = {}
                    for item in items:
                        category = item.get('category')
                        value = item.get('obsrValue', 0)
                        
                        if category == 'T1H':  # 기온
                            forecast_data['grid_temperature'] = float(value)
                        elif category == 'RN1':  # 1시간 강수량
                            forecast_data['grid_precipitation'] = float(value)
                        elif category == 'REH':  # 습도
                            forecast_data['grid_humidity'] = float(value)
                        elif category == 'WSD':  # 풍속
                            forecast_data['grid_wind_speed'] = float(value)
                    
                    return {
                        'success': True,
                        'data': forecast_data
                    }
                else:
                    return {'success': False, 'error': data['response']['header'].get('resultMsg', '예보 없음')}
            else:
                return {'success': False, 'error': f'HTTP {response.status_code}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def save_daily_data_to_csv(self, items):
        """일자료를 CSV 파일에 저장 (web_app.py와 호환)"""
        
        # web_app.py가 읽는 파일 경로
        csv_path = 'data/processed/REAL_WEATHER_DATA.csv'
        
        # 기존 CSV 파일이 있으면 로드, 없으면 새로 생성
        if os.path.exists(csv_path):
            try:
                existing_df = pd.read_csv(csv_path)
                existing_df['obs_date'] = pd.to_datetime(existing_df['obs_date'])
            except:
                existing_df = pd.DataFrame()
        else:
            existing_df = pd.DataFrame()
        
        # 새로운 데이터 변환
        new_data = []
        for item in items:
            obs_date = item.get('tm', '')
            if not obs_date:
                continue
                
            # 날짜 파싱
            try:
                date_obj = datetime.strptime(obs_date, '%Y-%m-%d')
            except:
                continue
            
            # 계절 타입 결정
            season_type = 'rainy' if date_obj.month in [5, 6, 7, 8, 9] else 'dry'
            
            # 침수 위험 여부 (50mm 이상)
            precipitation = float(item.get('sumRn', 0) or 0)
            is_flood_risk = 1 if precipitation >= 50 else 0
            
            # 실제 침수 발생 여부 확인
            actual_flood = self.check_actual_flood(date_obj.date(), precipitation)
            
            # web_app.py 호환 형식으로 데이터 생성
            row_data = {
                'obs_date': date_obj,
                'year': date_obj.year,
                'month': date_obj.month, 
                'day': date_obj.day,
                'season_type': season_type,
                'avg_temp': float(item.get('avgTa', 0) or 0),
                'min_temp': float(item.get('minTa', 0) or 0),
                'max_temp': float(item.get('maxTa', 0) or 0),
                'humidity': float(item.get('avgRhm', 60) or 60),
                'precipitation': precipitation,
                'wind_speed': float(item.get('avgWs', 0) or 0),
                'is_flood_risk': is_flood_risk,
                'actual_flood': actual_flood,
                'data_quality': 'ASOS_DAILY',
                'temperature': float(item.get('avgTa', 0) or 0),  # web_app.py 호환용
                'data_source': 'REAL_DATA'
            }
            
            new_data.append(row_data)
        
        if new_data:
            # 새 데이터를 DataFrame으로 변환
            new_df = pd.DataFrame(new_data)
            
            # 기존 데이터와 합치기 (중복 제거)
            if not existing_df.empty:
                # 날짜 기준으로 중복 제거
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                combined_df = combined_df.drop_duplicates(subset=['obs_date'], keep='last')
            else:
                combined_df = new_df
            
            # 날짜순 정렬
            combined_df = combined_df.sort_values('obs_date').reset_index(drop=True)
            
            # CSV 파일로 저장
            os.makedirs('data/processed', exist_ok=True)
            combined_df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            
            print(f"💾 CSV 저장 완료: {len(combined_df)}행 → {csv_path}")
            return len(new_data)
        
        return 0
    
    def check_actual_flood(self, check_date, precipitation):
        """실제 침수 발생 여부 확인"""
        date_str = check_date.strftime('%Y-%m-%d')
        
        for event in self.actual_flood_events:
            if event['date'] == date_str:
                return 1
        
        # 강수량이 매우 높으면 침수 가능성 추정
        if precipitation >= 200:
            return 1
        
        return 0
    
    def save_realtime_data(self, weather_data):
        """실시간 기상 데이터를 CSV에 추가 저장"""
        try:
            # 간단한 실시간 데이터 로그 (선택사항)
            realtime_data = {
                'timestamp': datetime.now(),
                'temperature': weather_data.get('temperature', 0),
                'precipitation': weather_data.get('precipitation', 0),
                'humidity': weather_data.get('humidity', 60),
                'wind_speed': weather_data.get('wind_speed', 0),
                'pressure': weather_data.get('pressure', 1013),
                'data_source': ', '.join(weather_data.get('data_sources_used', []))
            }
            
            # 실시간 로그 파일에 저장 (선택사항)
            realtime_path = 'data/processed/realtime_log.csv'
            if os.path.exists(realtime_path):
                log_df = pd.read_csv(realtime_path)
                new_log = pd.DataFrame([realtime_data])
                combined_log = pd.concat([log_df, new_log], ignore_index=True)
                # 최근 100개만 유지
                if len(combined_log) > 100:
                    combined_log = combined_log.tail(100)
            else:
                combined_log = pd.DataFrame([realtime_data])
            
            combined_log.to_csv(realtime_path, index=False)
            
        except Exception as e:
            print(f"⚠️ 실시간 데이터 로그 저장 오류: {e}")
    
    def integrate_weather_data(self, results):
        """2개 API 데이터 통합 및 보완"""
        integrated = results['weather_data'].copy()
        
        # 강수량 데이터 우선순위: 격자 데이터 > 일자료
        precipitation = (
            integrated.get('grid_precipitation') or 
            integrated.get('daily_precipitation', 0) / 24 or
            0
        )
        
        # 온도 데이터 우선순위: 격자 > 일자료
        temperature = (
            integrated.get('grid_temperature') or 
            integrated.get('avg_temperature') or
            (integrated.get('max_temperature', 20) + integrated.get('min_temperature', 10)) / 2 or
            20
        )
        
        # 습도 데이터
        humidity = (
            integrated.get('grid_humidity') or 
            integrated.get('avg_humidity') or 
            60
        )
        
        # 풍속 데이터
        wind_speed = (
            integrated.get('grid_wind_speed') or 
            integrated.get('max_wind_speed', 0) / 2 or
            0
        )
        
        # 통합된 최종 데이터
        final_data = {
            'precipitation': precipitation,
            'temperature': temperature,
            'humidity': humidity,
            'wind_speed': wind_speed,
            'pressure': 1013,  # 기본값
            'data_quality_score': len(results['data_sources']) / 2 * 100,
            'data_sources_used': results['data_sources'],
            'collection_time': datetime.now().isoformat()
        }
        
        return final_data
    
    def collect_strategic_historical_data(self, max_days=30):
        """전략적 과거 데이터 수집 (장마철 중심)"""
        print(f"📊 전략적 과거 데이터 수집 시작 (최대 {max_days}일)...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 이미 수집된 날짜 확인
        cursor.execute("SELECT DISTINCT obs_date FROM strategic_daily ORDER BY obs_date DESC LIMIT 1")
        last_date_row = cursor.fetchone()
        
        if last_date_row:
            last_date = datetime.strptime(last_date_row[0], '%Y-%m-%d').date()
            start_date = last_date + timedelta(days=1)
            print(f"📅 증분 업데이트: {last_date} 다음부터 수집")
        else:
            start_date = datetime.now().date() - timedelta(days=max_days)
            print(f"📅 새로운 수집: {max_days}일 전부터 수집")
        
        end_date = datetime.now().date() - timedelta(days=1)  # 어제까지
        
        current_date = start_date
        collected_count = 0
        
        while current_date <= end_date and collected_count < max_days:
            # 전략적 수집: 장마철 우선
            if current_date.month in [5, 6, 7, 8, 9]:  # 장마철
                success = self.collect_single_historical_day(current_date)
                if success:
                    collected_count += 1
                    if collected_count % 10 == 0:
                        print(f"  🌧️ 장마철 데이터: {collected_count}일 완료")
            elif current_date.month in [1, 2, 11, 12]:  # 대조군
                success = self.collect_single_historical_day(current_date)
                if success:
                    collected_count += 1
                    if collected_count % 10 == 0:
                        print(f"  ☀️ 대조군 데이터: {collected_count}일 완료")
            
            current_date += timedelta(days=1)
            time.sleep(0.5)  # API 제한 준수
        
        conn.close()
        print(f"✅ 전략적 과거 데이터 수집 완료: {collected_count}일")
        return collected_count
    
    def collect_single_historical_day(self, target_date):
        """단일 날짜 과거 데이터 수집"""
        date_str = target_date.strftime('%Y%m%d')
        
        params = {
            'serviceKey': self.service_key,
            'pageNo': '1',
            'numOfRows': '5',
            'dataType': 'JSON',
            'dataCd': 'ASOS',
            'dateCd': 'DAY',
            'startDt': date_str,
            'endDt': date_str,
            'stnIds': '108'
        }
        
        try:
            response = requests.get(self.apis['asos_daily']['url'], params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("response", {}).get("header", {}).get("resultCode") == "00":
                    items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
                    
                    if items:
                        self.save_daily_data_to_db(items)
                        return True
        
        except Exception as e:
            print(f"    ❌ {date_str} 수집 실패: {e}")
        
        return False
    
    def export_ml_ready_dataset(self):
        """ML 준비 완료 데이터셋 내보내기"""
        print("🤖 ML 준비 완료 데이터셋 생성 중...")
        
        conn = sqlite3.connect(self.db_path)
        
        # 전체 데이터 로드
        df = pd.read_sql_query("""
            SELECT * FROM strategic_daily 
            ORDER BY obs_date
        """, conn)
        
        if df.empty:
            print("❌ 수집된 데이터가 없습니다.")
            return None
        
        # ML 특성 추가
        df = self.add_ml_features(df)
        
        # 파일 저장
        output_path = 'data/processed/ML_COMPLETE_DATASET.csv'
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        
        # 통계 출력
        print(f"✅ ML 데이터셋 생성 완료:")
        print(f"   📊 총 데이터: {len(df):,}일")
        print(f"   🌧️ 장마철: {len(df[df['season_type']=='rainy']):,}일")
        print(f"   ☀️ 대조군: {len(df[df['season_type']=='dry']):,}일")
        print(f"   ⚠️ 침수 위험: {len(df[df['is_flood_risk']==1]):,}일")
        print(f"   🌊 실제 침수: {len(df[df['actual_flood']==1]):,}일")
        print(f"   💾 저장 위치: {output_path}")
        
        conn.close()
        return output_path
    
    def add_ml_features(self, df):
        """ML용 추가 특성 생성"""
        # 날짜 기반 특성
        df['obs_date'] = pd.to_datetime(df['obs_date'])
        df['month'] = df['obs_date'].dt.month
        df['day_of_year'] = df['obs_date'].dt.dayofyear
        df['is_peak_rainy'] = ((df['month'] >= 6) & (df['month'] <= 8)).astype(int)
        df['is_typhoon_season'] = ((df['month'] >= 7) & (df['month'] <= 9)).astype(int)
        
        # 이동평균 특성
        df = df.sort_values('obs_date')
        df['precip_ma3'] = df['precipitation'].rolling(window=3, min_periods=1).mean()
        df['precip_ma7'] = df['precipitation'].rolling(window=7, min_periods=1).mean()
        df['temp_ma3'] = df['avg_temp'].rolling(window=3, min_periods=1).mean()
        
        # 누적 특성
        df['rain_days_cumsum'] = (df['precipitation'] > 0).cumsum()
        df['precip_cumsum_3d'] = df['precipitation'].rolling(window=3, min_periods=1).sum()
        df['precip_cumsum_7d'] = df['precipitation'].rolling(window=7, min_periods=1).sum()
        
        # 위험도 레벨
        df['precip_risk_level'] = pd.cut(
            df['precipitation'], 
            bins=[-np.inf, 0, 10, 30, 50, np.inf], 
            labels=[0, 1, 2, 3, 4]
        ).astype(int)
        
        # 온도-습도 상호작용
        df['temp_humidity_interaction'] = df['avg_temp'] * df['humidity'] / 100
        
        return df
    
    def get_csv_stats(self):
        """CSV 파일 통계 조회"""
        if not os.path.exists(self.csv_path):
            return {'daily': {}, 'message': 'CSV 파일이 없습니다.'}
        
        try:
            df = pd.read_csv(self.csv_path)
            if df.empty:
                return {'daily': {}, 'message': 'CSV 파일이 비어있습니다.'}
            
            df['obs_date'] = pd.to_datetime(df['obs_date'])
            
            stats = {
                'total_days': len(df),
                'rainy_days': len(df[df.get('season_type', '') == 'rainy']) if 'season_type' in df.columns else 0,
                'dry_days': len(df[df.get('season_type', '') == 'dry']) if 'season_type' in df.columns else 0,
                'flood_risk_days': len(df[df.get('is_flood_risk', 0) == 1]) if 'is_flood_risk' in df.columns else 0,
                'actual_flood_days': len(df[df.get('actual_flood', 0) == 1]) if 'actual_flood' in df.columns else 0,
                'start_date': df['obs_date'].min().strftime('%Y-%m-%d'),
                'end_date': df['obs_date'].max().strftime('%Y-%m-%d'),
                'avg_precipitation': df['precipitation'].mean() if 'precipitation' in df.columns else 0,
                'max_precipitation': df['precipitation'].max() if 'precipitation' in df.columns else 0
            }
            
            return {
                'daily': stats,
                'message': 'CSV 통계 조회 성공'
            }
        
        except Exception as e:
            return {
                'daily': {},
                'message': f'CSV 통계 조회 오류: {e}'
            }


def test_strategic_weather_api():
    """전략적 기상 API 테스트"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    service_key = os.getenv('OPENWEATHER_API_KEY')
    
    if not service_key:
        print("❌ 서비스 키가 없습니다!")
        return False
    
    api = MultiWeatherAPI(service_key)
    
    print("🇰🇷 서울시 25개 지역구 전용 - 전략적 침수 예측 시스템 테스트")
    print("📅 안정적인 2개 API + SQLite + ML 준비 완료")
    print("=" * 60)
    
    # 1. 실시간 데이터 수집
    print("\n1️⃣ 실시간 데이터 수집 테스트...")
    results = api.get_comprehensive_weather_data()
    
    if results['success']:
        data = results['weather_data']
        print(f"✅ 실시간 수집 성공!")
        print(f"📊 사용된 API: {', '.join(results['data_sources'])}")
        print(f"📈 데이터 품질: {data['data_quality_score']:.1f}%")
        print(f"🌧️ 강수량: {data['precipitation']:.1f}mm")
        print(f"🌡️ 온도: {data['temperature']:.1f}°C")
        print(f"💧 습도: {data['humidity']:.1f}%")
    
    # 2. 전략적 과거 데이터 수집
    print("\n2️⃣ 전략적 과거 데이터 수집 테스트...")
    collected = api.collect_strategic_historical_data(max_days=10)
    print(f"✅ 과거 데이터 {collected}일 수집 완료")
    
    # 3. ML 데이터셋 생성
    print("\n3️⃣ ML 준비 완료 데이터셋 생성...")
    ml_path = api.export_ml_ready_dataset()
    if ml_path:
        print(f"✅ ML 데이터셋 준비 완료: {ml_path}")
    
    # 4. CSV 파일 통계
    print("\n4️⃣ CSV 파일 통계...")
    stats = api.get_csv_stats()
    if stats['daily']:
        daily = stats['daily']
        print(f"📊 수집 현황:")
        print(f"   📅 총 일수: {daily.get('total_days', 0):,}일")
        print(f"   🌧️ 장마철: {daily.get('rainy_days', 0):,}일")
        print(f"   ☀️ 대조군: {daily.get('dry_days', 0):,}일")
        print(f"   ⚠️ 침수 위험: {daily.get('flood_risk_days', 0):,}일")
        print(f"   📈 평균 강수량: {daily.get('avg_precipitation', 0):.1f}mm")
        print(f"   📍 수집 기간: {daily.get('start_date')} ~ {daily.get('end_date')}")
    else:
        print(f"⚠️ {stats['message']}")
    
    print(f"\n🎯 전략적 침수 예측 시스템 준비 완료!")
    print(f"💡 이제 안정적인 2개 API + CSV 직접 저장으로 web_app.py와 완벽 호환됩니다.")
    
    return True


if __name__ == "__main__":
    test_strategic_weather_api()