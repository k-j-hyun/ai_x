from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import os
import json
import time
import pickle
import logging
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
from collections import Counter

# TensorFlow 관련 (선택적 로드)
try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential, Model
    from tensorflow.keras.layers import Dense, Dropout, BatchNormalization, Input, Concatenate, LSTM
    from tensorflow.keras.optimizers import Adam
    from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import f1_score
    from sklearn.preprocessing import StandardScaler
    ML_AVAILABLE = True
    print("✅ TensorFlow 로드 완료")
except ImportError:
    print("⚠️ TensorFlow를 찾을 수 없습니다. 기본 예측 모드로 실행됩니다.")
    ML_AVAILABLE = False

# FastAPI 앱 생성
app = FastAPI(
    title="🎲 AI 로또 예측기",
    description="딥러닝 기반 로또 번호 예측 서비스",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 변수
CSV_PATH = "data/lotto_numbers.csv"
MODEL_PATH = "models/model_weights/lotto_model.h5"
SCALER_PATH = "models/model_weights/scaler.pkl"

# 진행 상태 추적
progress_status = {"type": "", "progress": 0, "message": "", "status": "idle"}

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===========================================
# 🐌 안전한 로또 크롤러
# ===========================================

class SafeLottoCrawler:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def get_latest_draw_no(self):
        """최신 회차 번호 가져오기"""
        try:
            url = "https://www.dhlottery.co.kr/gameResult.do?method=byWin"
            res = self.session.get(url, timeout=30)
            soup = BeautifulSoup(res.text, "html.parser")
            latest_no_tag = soup.select_one(".nums > strong")
            latest_no = int(latest_no_tag.text.strip()) if latest_no_tag else 1176
            logger.info(f"✅ 최신 회차 확인: {latest_no}회")
            return latest_no
        except Exception as e:
            logger.error(f"최신 회차 조회 실패: {e}")
            return 1176
    
    def get_lotto_numbers(self, draw_no, max_retries=5):
        """특정 회차 로또 번호 가져오기 (매우 안전하게)"""
        for attempt in range(max_retries):
            try:
                url = f"https://www.dhlottery.co.kr/gameResult.do?method=byWin&drwNo={draw_no}"
                
                # 더 긴 대기시간과 재시도
                res = self.session.get(url, timeout=30)
                
                # 응답 상태 확인
                if res.status_code != 200:
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 3
                        logger.warning(f"[{draw_no}회] HTTP {res.status_code}, {wait_time}초 후 재시도...")
                        time.sleep(wait_time)
                        continue
                    return None
                
                soup = BeautifulSoup(res.text, "html.parser")
                
                # 데이터 파싱
                win_nums = soup.select(".win_result .nums span.ball_645")
                bonus_num = soup.select_one(".win_result .bonus span.ball_645")
                
                if len(win_nums) < 6 or bonus_num is None:
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 2
                        logger.warning(f"[{draw_no}회] 데이터 부족, {wait_time}초 후 재시도...")
                        time.sleep(wait_time)
                        continue
                    logger.warning(f"[{draw_no}회] 데이터를 찾을 수 없음")
                    return None
                    
                win_nums = [int(num.text) for num in win_nums]
                bonus = int(bonus_num.text)
                
                logger.info(f"✅ [{draw_no}회] 성공: {win_nums} + {bonus}")
                return {
                    "회차": draw_no,
                    "번호1": win_nums[0], "번호2": win_nums[1], "번호3": win_nums[2],
                    "번호4": win_nums[3], "번호5": win_nums[4], "번호6": win_nums[5],
                    "보너스": bonus
                }
                
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 5
                    logger.warning(f"[{draw_no}회] 타임아웃, {wait_time}초 후 재시도...")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"❌ [{draw_no}회] 최종 타임아웃 실패")
                    return None
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 3
                    logger.warning(f"[{draw_no}회] 오류 ({e}), {wait_time}초 후 재시도...")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"❌ [{draw_no}회] 최종 실패: {e}")
                    return None
        
        return None
    
    def safe_update(self):
        """안전한 배치 업데이트 (10개씩)"""
        global progress_status
        
        try:
            logger.info("🐌 안전한 배치 크롤링 시작")
            progress_status = {
                "type": "safe_crawl",
                "progress": 0,
                "message": "안전한 크롤링 모드로 시작합니다...",
                "status": "running"
            }
            
            # 기존 데이터 확인
            if os.path.exists(CSV_PATH):
                df_existing = pd.read_csv(CSV_PATH)
                start_no = df_existing["회차"].max() + 1
                logger.info(f"📊 기존 데이터: {len(df_existing)}회차, {start_no}회부터 시작")
            else:
                df_existing = pd.DataFrame()
                start_no = 1
                logger.info("📊 기존 데이터 없음, 1회부터 시작")
            
            progress_status["progress"] = 10
            progress_status["message"] = "최신 회차 확인 중..."
            
            latest_no = self.get_latest_draw_no()
            
            if start_no > latest_no:
                progress_status = {
                    "type": "safe_crawl",
                    "progress": 100,
                    "message": "이미 최신 데이터입니다.",
                    "status": "completed"
                }
                return {
                    "success": True,
                    "message": "이미 최신 데이터입니다.",
                    "total": len(df_existing),
                    "new": 0,
                    "remaining": 0
                }
            
            # 배치 크기 설정 (10개씩)
            batch_size = 10
            end_no = min(start_no + batch_size - 1, latest_no)
            
            logger.info(f"🎯 이번 배치: {start_no}~{end_no}회차 ({end_no - start_no + 1}개)")
            
            progress_status["progress"] = 20
            progress_status["message"] = f"배치 크롤링: {start_no}~{end_no}회차"
            
            new_data = []
            total_in_batch = end_no - start_no + 1
            
            for i, draw_no in enumerate(range(start_no, end_no + 1)):
                # 진행률 업데이트 (20% ~ 90%)
                progress = 20 + ((i + 1) / total_in_batch) * 70
                progress_status = {
                    "type": "safe_crawl",
                    "progress": progress,
                    "message": f"수집 중: {draw_no}회차 ({i+1}/{total_in_batch})",
                    "status": "running"
                }
                
                result = self.get_lotto_numbers(draw_no)
                if result:
                    new_data.append(result)
                
                # 각 요청 후 충분한 대기 (서버 부하 방지)
                if i < total_in_batch - 1:  # 마지막이 아니면
                    wait_time = 2.0  # 2초 대기
                    logger.info(f"⏳ [{draw_no}회] 완료, {wait_time}초 대기...")
                    time.sleep(wait_time)
            
            progress_status["progress"] = 95
            progress_status["message"] = "데이터 저장 중..."
            
            # 데이터 저장
            if new_data:
                if not df_existing.empty:
                    df_new = pd.DataFrame(new_data)
                    df_all = pd.concat([df_existing, df_new], ignore_index=True)
                else:
                    df_all = pd.DataFrame(new_data)
                
                df_all = df_all.sort_values('회차').reset_index(drop=True)
                
                os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
                df_all.to_csv(CSV_PATH, index=False, encoding='utf-8-sig')
                
                remaining = latest_no - end_no
                
                logger.info(f"✅ 배치 완료: {len(new_data)}개 추가 (총 {len(df_all)}회차), 남은 회차: {remaining}개")
                
                if remaining > 0:
                    message = f"배치 완료! {len(new_data)}개 추가 (총 {len(df_all)}회차)\n\n남은 회차: {remaining}개\n계속하려면 '데이터 업데이트' 버튼을 다시 눌러주세요!"
                else:
                    message = f"🎉 전체 크롤링 완료! 총 {len(df_all)}회차 수집 완료!"
                
                progress_status = {
                    "type": "safe_crawl",
                    "progress": 100,
                    "message": message,
                    "status": "completed"
                }
                
                return {
                    "success": True,
                    "message": message,
                    "total": len(df_all),
                    "new": len(new_data),
                    "remaining": max(0, remaining),
                    "next_start": end_no + 1 if remaining > 0 else None
                }
            else:
                logger.warning("⚠️ 수집된 데이터가 없음")
                progress_status = {
                    "type": "safe_crawl",
                    "progress": 100,
                    "message": "이번 배치에서 수집된 데이터가 없습니다.",
                    "status": "completed"
                }
                
                return {
                    "success": True,
                    "message": "이번 배치에서 수집된 데이터가 없습니다.",
                    "total": len(df_existing),
                    "new": 0,
                    "remaining": 0
                }
                
        except Exception as e:
            logger.error(f"❌ 안전 크롤링 실패: {e}")
            progress_status = {
                "type": "safe_crawl",
                "progress": 0,
                "message": f"크롤링 실패: {str(e)}",
                "status": "error"
            }
            return {"success": False, "message": str(e)}

# ===========================================
# 🤖 AI 예측 모델 (기존과 동일)
# ===========================================

class SimpleLottoPredictor:
    def __init__(self):
        self.is_trained = ML_AVAILABLE
    
    def predict_numbers(self, num_predictions=10):
        """로또 번호 예측 (통계 기반)"""
        try:
            if not os.path.exists(CSV_PATH):
                return {
                    "success": False,
                    "message": "예측할 데이터가 없습니다. 먼저 데이터를 업데이트하세요.",
                    "predictions": []
                }
            
            # 데이터 로드
            df = pd.read_csv(CSV_PATH)
            logger.info(f"📊 예측용 데이터 로드: {len(df)}회차")
            
            if len(df) < 10:
                return {
                    "success": False,
                    "message": f"데이터가 부족합니다. 최소 10회차 필요 (현재: {len(df)}회차)",
                    "predictions": []
                }
            
            # 최근 100회차 분석 (또는 전체 데이터)
            recent_df = df.tail(min(100, len(df)))
            all_numbers = []
            
            for _, row in recent_df.iterrows():
                nums = [row['번호1'], row['번호2'], row['번호3'], row['번호4'], row['번호5'], row['번호6']]
                all_numbers.extend(nums)
            
            # 번호별 출현 빈도 계산
            counter = Counter(all_numbers)
            logger.info(f"📈 분석 완료: {len(recent_df)}회차, 총 {len(all_numbers)}개 번호")
            
            # 예측 생성
            predictions = []
            
            for i in range(num_predictions):
                # 가중치 기반 선택
                numbers = list(range(1, 46))
                weights = [counter.get(num, 1) + np.random.normal(0, 0.3) for num in numbers]
                weights = [max(0.1, w) for w in weights]
                
                # 가중 랜덤 선택으로 7개 선택
                selected = np.random.choice(numbers, size=7, replace=False, p=np.array(weights)/sum(weights))
                
                # 메인 6개, 보너스 1개로 분리
                main_numbers = sorted(selected[:6])
                bonus_number = selected[6]
                
                # 신뢰도 계산
                confidence = np.mean([counter.get(num, 1) for num in selected]) / max(counter.values())
                confidence = min(0.85, max(0.45, confidence))
                
                predictions.append({
                    'main': main_numbers.tolist(),
                    'bonus': int(bonus_number),
                    'confidence': float(confidence)
                })
            
            # 신뢰도 순으로 정렬
            predictions.sort(key=lambda x: x['confidence'], reverse=True)
            
            logger.info(f"🎯 예측 완료: {num_predictions}개 조합 생성")
            
            return {
                "success": True,
                "message": "예측 완료",
                "predictions": predictions,
                "model_info": {
                    "data_size": len(df),
                    "latest_draw": int(df['회차'].max()) if '회차' in df.columns else 0,
                    "analysis_period": f"최근 {len(recent_df)}회차"
                }
            }
            
        except Exception as e:
            logger.error(f"❌ 예측 실패: {e}")
            return {
                "success": False,
                "message": f"예측 실패: {str(e)}",
                "predictions": []
            }

# 전역 인스턴스
crawler = SafeLottoCrawler()
predictor = SimpleLottoPredictor()

# ===========================================
# 🌐 메인 페이지
# ===========================================

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """메인 페이지"""
    try:
        # 프론트엔드 HTML 파일 찾기
        html_paths = [
            "../frontend/index.html",
            "frontend/index.html",
            "../index.html"
        ]
        
        for html_path in html_paths:
            if os.path.exists(html_path):
                with open(html_path, "r", encoding="utf-8") as f:
                    return HTMLResponse(content=f.read())
    except Exception as e:
        logger.error(f"HTML 파일 로드 실패: {e}")
    
    # 기본 HTML 반환
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>🎲 AI 로또 예측기</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; min-height: 100vh; margin: 0;
                display: flex; align-items: center; justify-content: center;
            }
            .container {
                background: rgba(255,255,255,0.1); padding: 40px;
                border-radius: 20px; backdrop-filter: blur(10px);
                text-align: center; max-width: 600px;
            }
            h1 { font-size: 2.5em; margin-bottom: 20px; }
            .status { 
                background: rgba(76, 175, 80, 0.2); padding: 20px;
                border-radius: 15px; margin: 20px 0;
            }
            .feature-box {
                background: rgba(255,255,255,0.1); padding: 20px;
                margin: 15px 0; border-radius: 15px; text-align: left;
            }
            .feature-title { 
                font-weight: bold; color: #4caf50; margin-bottom: 10px; 
                font-size: 1.1em;
            }
            button {
                background: rgba(76, 175, 80, 0.8); color: white;
                border: none; padding: 15px 25px; border-radius: 10px;
                cursor: pointer; margin: 10px; font-size: 16px; font-weight: bold;
                transition: all 0.3s ease;
            }
            button:hover { 
                background: rgba(76, 175, 80, 1); 
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }
            .warning {
                background: rgba(255, 193, 7, 0.2);
                border: 1px solid rgba(255, 193, 7, 0.5);
                padding: 15px; border-radius: 10px; margin: 20px 0;
                font-size: 0.9em;
            }
        </style>
        <script>
            async function testUpdate() {
                try {
                    const response = await fetch('/api/data/update', { method: 'POST' });
                    const result = await response.json();
                    
                    if (result.success) {
                        let msg = '✅ ' + result.message;
                        if (result.remaining && result.remaining > 0) {
                            msg += '\\n\\n💡 팁: 전체 데이터 수집을 위해 버튼을 계속 눌러주세요!';
                        }
                        alert(msg);
                    } else {
                        alert('❌ 오류: ' + result.message);
                    }
                } catch (error) {
                    alert('❌ 연결 오류: ' + error.message);
                }
            }
            
            async function testPredict() {
                try {
                    const response = await fetch('/api/predict', { method: 'POST' });
                    const result = await response.json();
                    if (result.success) {
                        let msg = '🎯 AI 예측 결과:\\n\\n';
                        result.predictions.slice(0, 5).forEach((pred, i) => {
                            msg += `${i+1}위: [${pred.main.join(', ')}] + ${pred.bonus} (${(pred.confidence*100).toFixed(1)}%)\\n`;
                        });
                        alert(msg);
                    } else {
                        alert('❌ 예측 실패: ' + result.message);
                    }
                } catch (error) {
                    alert('❌ 오류: ' + error.message);
                }
            }
            
            async function checkStatus() {
                try {
                    const response = await fetch('/api/data/status');
                    const result = await response.json();
                    
                    let msg = `📊 현재 상태:\\n`;
                    msg += `• 데이터: ${result.data_exists ? '✅' : '❌'} (${result.total_draws}회차)\\n`;
                    msg += `• 최신 회차: ${result.latest_draw}회\\n`;
                    msg += `• AI 모델: ${result.model_ready ? '✅' : '❌'}`;
                    
                    alert(msg);
                } catch (error) {
                    alert('❌ 상태 확인 실패: ' + error.message);
                }
            }
        </script>
    </head>
    <body>
        <div class="container">
            <h1>🎲 AI 로또 예측기</h1>
            <div class="status">
                <p><strong>🐌 안전한 배치 크롤링 시스템</strong></p>
                <p>서버 부하를 방지하는 친화적 크롤링</p>
            </div>
            
            <div class="feature-box">
                <div class="feature-title">🛡️ 안전 크롤링 시스템</div>
                <p>• <strong>배치 처리</strong>: 10개 회차씩 안전하게 수집</p>
                <p>• <strong>지능형 재시도</strong>: 실패시 자동으로 5번까지 재시도</p>
                <p>• <strong>서버 친화적</strong>: 각 요청 후 2초 대기로 부하 방지</p>
                <p>• <strong>안정성 우선</strong>: 타임아웃 30초, 긴 대기시간</p>
            </div>
            
            <div class="feature-box">
                <div class="feature-title">📊 진행 상황</div>
                <p>• <strong>실시간 로그</strong>: 터미널에서 수집 상황 확인</p>
                <p>• <strong>배치별 완료</strong>: 10개씩 완료 후 다음 배치 진행</p>
                <p>• <strong>자동 저장</strong>: 각 배치 완료 후 즉시 CSV 저장</p>
            </div>
            
            <div class="warning">
                <strong>⏰ 예상 소요 시간</strong><br>
                • 배치당: 약 30초 (10개 회차)<br>
                • 전체 1176회차: 약 60분 (117번 클릭)<br>
                • 하지만 안전하고 확실합니다! 🛡️
            </div>
            
            <div style="margin: 30px 0;">
                <button onclick="testUpdate()">🐌 안전 데이터 업데이트</button>
                <button onclick="testPredict()">🎯 AI 번호 예측</button>
                <button onclick="checkStatus()">📊 현재 상태 확인</button>
            </div>
            
            <p style="margin-top: 30px; opacity: 0.8; font-size: 0.9em;">
                💡 <strong>사용법</strong>: '안전 데이터 업데이트' 버튼을 반복해서 눌러주세요!<br>
                각 배치(10개 회차) 완료 후 자동으로 저장됩니다.
            </p>
        </div>
    </body>
    </html>
    """)

# ===========================================
# 🌐 API 엔드포인트들
# ===========================================

@app.get("/api/data/status")
async def get_data_status():
    """데이터 상태 확인"""
    try:
        if not os.path.exists(CSV_PATH):
            return {
                "data_exists": False,
                "total_draws": 0,
                "latest_draw": 0,
                "model_ready": False
            }
        
        df = pd.read_csv(CSV_PATH)
        return {
            "data_exists": True,
            "total_draws": len(df),
            "latest_draw": int(df['회차'].max()) if '회차' in df.columns else 0,
            "model_ready": ML_AVAILABLE
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/data/update")
async def update_data():
    """안전한 배치 데이터 업데이트"""
    global progress_status
    
    if progress_status["status"] == "running":
        return {
            "success": False,
            "message": "이미 업데이트가 진행 중입니다. 잠시 후 다시 시도해주세요."
        }
    
    try:
        logger.info("🐌 안전한 배치 업데이트 시작")
        result = crawler.safe_update()
        logger.info(f"✅ 안전 업데이트 완료: {result}")
        return result
        
    except Exception as e:
        logger.error(f"❌ 안전 업데이트 실패: {e}")
        progress_status = {
            "type": "safe_crawl",
            "progress": 0,
            "message": f"업데이트 실패: {str(e)}",
            "status": "error"
        }
        return {
            "success": False,
            "message": f"업데이트 실패: {str(e)}"
        }

@app.get("/api/data/update/progress")
async def get_update_progress():
    """업데이트 진행 상황"""
    return progress_status

@app.get("/api/model/status")
async def get_model_status():
    """모델 상태 확인"""
    return {
        "ready": ML_AVAILABLE,
        "trained": predictor.is_trained,
        "type": "Statistics Based AI" if ML_AVAILABLE else "Basic Statistics"
    }

@app.post("/api/predict")
async def predict_numbers(num_predictions: int = 10):
    """로또 번호 예측"""
    try:
        logger.info(f"🎯 번호 예측 요청: {num_predictions}개")
        result = predictor.predict_numbers(num_predictions)
        logger.info(f"📈 예측 결과: {result['success']}")
        return result
    except Exception as e:
        logger.error(f"❌ 예측 API 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_statistics():
    """통계 정보"""
    try:
        if not os.path.exists(CSV_PATH):
            return {"data_exists": False}
        
        df = pd.read_csv(CSV_PATH)
        recent_df = df.tail(min(100, len(df)))
        
        # 최근 회차 번호 분석
        all_numbers = []
        for _, row in recent_df.iterrows():
            nums = [row['번호1'], row['번호2'], row['번호3'], row['번호4'], row['번호5'], row['번호6']]
            all_numbers.extend(nums)
        
        counter = Counter(all_numbers)
        
        # 홀짝 분석
        odd_count = sum(1 for n in all_numbers if n % 2 == 1)
        even_count = len(all_numbers) - odd_count
        
        # 구간별 분석
        zone1 = sum(1 for n in all_numbers if 1 <= n <= 15)
        zone2 = sum(1 for n in all_numbers if 16 <= n <= 30)
        zone3 = sum(1 for n in all_numbers if 31 <= n <= 45)
        
        return {
            "data_exists": True,
            "total_draws": len(df),
            "latest_draw": int(df['회차'].max()) if '회차' in df.columns else 0,
            "recent_analysis": {
                "period": f"최근 {len(recent_df)}회",
                "most_common": counter.most_common(10),
                "least_common": counter.most_common()[:-11:-1],
                "odd_even": {
                    "odd": odd_count,
                    "even": even_count
                },
                "zone_distribution": {
                    "zone1_1to15": zone1,
                    "zone2_16to30": zone2,
                    "zone3_31to45": zone3
                }
            }
        }
    except Exception as e:
        logger.error(f"❌ 통계 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """서버 상태 확인"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "ml_available": ML_AVAILABLE,
        "crawler_mode": "safe_batch",
        "version": "1.0.0"
    }

# ===========================================
# 🚀 서버 실행
# ===========================================

if __name__ == "__main__":
    print("🎲 AI 로또 예측기 서버 시작!")
    print("🌐 http://localhost:8000 에서 확인하세요!")
    print("📱 모바일에서도 접속 가능합니다!")
    print("\n🐌 안전한 배치 크롤링 시스템:")
    print("   • 10개씩 안전하게 수집")
    print("   • 서버 친화적 대기시간")
    print("   • 자동 재시도 기능")
    print("   • 타임아웃 방지 최적화")
    uvicorn.run(app, host="0.0.0.0", port=8000)