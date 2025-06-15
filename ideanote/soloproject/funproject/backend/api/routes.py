from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
import asyncio
from datetime import datetime

# 내부 모듈
from crawler.lotto_crawler import LottoCrawler
from models.lotto_model import LottoPredictionModel

logger = logging.getLogger(__name__)

# API 라우터 생성
router = APIRouter()

# 전역 변수 (실제로는 dependency injection 사용 권장)
crawler = None
model = None

# Pydantic 모델들 (API 요청/응답 스키마)
class PredictionResponse(BaseModel):
    success: bool
    message: str
    predictions: List[Dict[str, Any]] = []
    model_info: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class UpdateResponse(BaseModel):
    success: bool
    message: str
    total_draws: Optional[int] = None
    latest_draw: Optional[int] = None
    new_draws: Optional[int] = None
    failed_draws: Optional[int] = None
    error: Optional[str] = None

class StatusResponse(BaseModel):
    data_exists: bool
    total_draws: int
    latest_draw: int
    model_ready: bool
    last_updated: Optional[str] = None

# 진행률 추적을 위한 전역 변수
update_progress = {"status": "idle", "progress": 0, "message": ""}
prediction_progress = {"status": "idle", "progress": 0, "message": ""}

@router.on_event("startup")
async def startup():
    """라우터 시작시 초기화"""
    global crawler, model
    try:
        crawler = LottoCrawler()
        model = LottoPredictionModel()
        logger.info("✅ API 라우터 초기화 완료")
    except Exception as e:
        logger.error(f"❌ API 라우터 초기화 실패: {e}")

@router.get("/data/status", response_model=StatusResponse)
async def get_data_status():
    """데이터 및 모델 상태 확인"""
    try:
        # 크롤러 상태 확인
        data_info = crawler.get_data_info() if crawler else {"exists": False}
        
        # 모델 상태 확인
        model_ready = False
        if model:
            model_ready = hasattr(model, 'is_trained') and model.is_trained
        
        return StatusResponse(
            data_exists=data_info.get("exists", False),
            total_draws=data_info.get("total_draws", 0),
            latest_draw=data_info.get("latest_draw", 0),
            model_ready=model_ready,
            last_updated=data_info.get("last_modified")
        )
        
    except Exception as e:
        logger.error(f"상태 확인 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/data/update", response_model=UpdateResponse)
async def update_data(background_tasks: BackgroundTasks):
    """로또 데이터 업데이트"""
    global update_progress
    
    if update_progress["status"] == "running":
        raise HTTPException(status_code=400, detail="이미 업데이트가 진행 중입니다.")
    
    # 백그라운드에서 업데이트 실행
    background_tasks.add_task(run_data_update)
    
    return UpdateResponse(
        success=True,
        message="데이터 업데이트가 시작되었습니다. 진행 상황은 /api/data/update/progress에서 확인하세요."
    )

@router.get("/data/update/progress")
async def get_update_progress():
    """데이터 업데이트 진행 상황"""
    return update_progress

async def run_data_update():
    """백그라운드에서 실행되는 데이터 업데이트"""
    global update_progress, crawler
    
    try:
        update_progress = {"status": "running", "progress": 0, "message": "데이터 업데이트 시작"}
        
        def progress_callback(progress, current, total):
            update_progress["progress"] = progress
            update_progress["message"] = f"크롤링 중: {current}/{total} ({progress:.1f}%)"
        
        # 크롤링 실행
        result = crawler.update_data(progress_callback)
        
        if result["success"]:
            update_progress = {
                "status": "completed",
                "progress": 100,
                "message": result["message"],
                "result": result
            }
        else:
            update_progress = {
                "status": "failed",
                "progress": 0,
                "message": result["message"],
                "error": result.get("error")
            }
            
    except Exception as e:
        logger.error(f"백그라운드 업데이트 실패: {e}")
        update_progress = {
            "status": "failed",
            "progress": 0,
            "message": f"업데이트 실패: {str(e)}",
            "error": str(e)
        }

@router.post("/model/train")
async def train_model(background_tasks: BackgroundTasks):
    """모델 학습 (백그라운드)"""
    global model
    
    if not model:
        raise HTTPException(status_code=500, detail="모델이 초기화되지 않았습니다.")
    
    # 데이터 존재 확인
    data_info = crawler.get_data_info() if crawler else {"exists": False}
    if not data_info["exists"]:
        raise HTTPException(status_code=400, detail="학습할 데이터가 없습니다. 먼저 데이터를 업데이트하세요.")
    
    # 백그라운드에서 학습 실행
    background_tasks.add_task(run_model_training)
    
    return {"success": True, "message": "모델 학습이 시작되었습니다."}

async def run_model_training():
    """백그라운드에서 실행되는 모델 학습"""
    global model, prediction_progress
    
    try:
        prediction_progress = {"status": "training", "progress": 0, "message": "모델 학습 시작"}
        
        # 모델 초기화 및 학습
        result = model.initialize_model()
        
        if result["success"]:
            prediction_progress = {
                "status": "completed",
                "progress": 100,
                "message": "모델 학습 완료",
                "result": result
            }
        else:
            prediction_progress = {
                "status": "failed",
                "progress": 0,
                "message": result["message"],
                "error": result.get("error")
            }
            
    except Exception as e:
        logger.error(f"모델 학습 실패: {e}")
        prediction_progress = {
            "status": "failed",
            "progress": 0,
            "message": f"학습 실패: {str(e)}",
            "error": str(e)
        }

@router.get("/model/status")
async def get_model_status():
    """모델 상태 확인"""
    global model
    
    if not model:
        return {"ready": False, "trained": False, "message": "모델이 초기화되지 않았습니다."}
    
    return {
        "ready": hasattr(model, 'model') and model.model is not None,
        "trained": hasattr(model, 'is_trained') and model.is_trained,
        "data_loaded": hasattr(model, 'df') and model.df is not None,
        "model_path_exists": model.load_model() if hasattr(model, 'load_model') else False
    }

@router.post("/predict", response_model=PredictionResponse)
async def predict_numbers(num_predictions: int = 10):
    """로또 번호 예측"""
    global model
    
    try:
        if not model:
            raise HTTPException(status_code=500, detail="모델이 초기화되지 않았습니다.")
        
        # 모델이 학습되지 않았으면 자동으로 초기화 시도
        if not (hasattr(model, 'is_trained') and model.is_trained):
            logger.info("모델이 학습되지 않아 자동 초기화 시도")
            init_result = model.initialize_model()
            if not init_result["success"]:
                raise HTTPException(status_code=400, detail=f"모델 초기화 실패: {init_result['message']}")
        
        # 예측 실행
        result = model.predict_next_numbers(num_predictions)
        
        if result["success"]:
            return PredictionResponse(
                success=True,
                message=result["message"],
                predictions=result["predictions"],
                model_info=result.get("model_info")
            )
        else:
            return PredictionResponse(
                success=False,
                message=result["message"],
                error=result.get("error")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"예측 실패: {e}")
        return PredictionResponse(
            success=False,
            message=f"예측 실패: {str(e)}",
            error=str(e)
        )

@router.get("/predict/progress")
async def get_prediction_progress():
    """예측/학습 진행 상황"""
    return prediction_progress

@router.get("/stats")
async def get_statistics():
    """로또 통계 정보"""
    try:
        if not model or not hasattr(model, 'df') or model.df is None:
            # 데이터만으로 기본 통계 제공
            data_info = crawler.get_data_info() if crawler else {"exists": False}
            return {
                "data_exists": data_info["exists"],
                "total_draws": data_info.get("total_draws", 0),
                "latest_draw": data_info.get("latest_draw", 0)
            }
        
        df = model.df
        
        # 기본 통계
        total_draws = len(df)
        latest_draw = df['회차'].max() if '회차' in df.columns else 0
        
        # 번호별 출현 빈도 (최근 100회)
        recent_df = df.tail(100)
        all_numbers = []
        for _, row in recent_df.iterrows():
            nums = row[['번호1','번호2','번호3','번호4','번호5','번호6']].values
            all_numbers.extend(nums)
        
        from collections import Counter
        freq_counter = Counter(all_numbers)
        
        # 가장 자주/적게 나온 번호들
        most_common = freq_counter.most_common(10)
        least_common = freq_counter.most_common()[:-11:-1]  # 하위 10개
        
        # 홀짝 분포
        odd_count = sum(1 for n in all_numbers if n % 2 == 1)
        even_count = len(all_numbers) - odd_count
        
        # 구간별 분포
        zone1 = sum(1 for n in all_numbers if 1 <= n <= 15)
        zone2 = sum(1 for n in all_numbers if 16 <= n <= 30)
        zone3 = sum(1 for n in all_numbers if 31 <= n <= 45)
        
        return {
            "data_exists": True,
            "total_draws": total_draws,
            "latest_draw": latest_draw,
            "recent_analysis": {
                "period": "최근 100회",
                "most_common": most_common,
                "least_common": least_common,
                "odd_even": {
                    "odd": odd_count,
                    "even": even_count,
                    "odd_ratio": odd_count / len(all_numbers) if all_numbers else 0
                },
                "zone_distribution": {
                    "zone1_1to15": zone1,
                    "zone2_16to30": zone2, 
                    "zone3_31to45": zone3
                }
            }
        }
        
    except Exception as e:
        logger.error(f"통계 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test")
async def test_api():
    """API 테스트용 엔드포인트"""
    return {
        "message": "API가 정상 작동 중입니다!",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "crawler": crawler is not None,
            "model": model is not None
        }
    }