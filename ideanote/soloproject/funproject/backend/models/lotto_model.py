import pandas as pd
import numpy as np
import os
import pickle
import logging
from datetime import datetime
from collections import Counter

# TensorFlow 관련
import tensorflow as tf
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization, Input, Concatenate, LSTM, Reshape
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, classification_report
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

class LottoPredictionModel:
    def __init__(self, csv_path='data/lotto_numbers.csv'):
        self.csv_path = csv_path
        self.model = None
        self.scaler = StandardScaler()
        self.window_size = 10
        self.is_trained = False
        self.model_save_path = 'models/model_weights/lotto_model.h5'
        self.scaler_save_path = 'models/model_weights/scaler.pkl'
        
        # 재현 가능한 결과를 위한 시드 설정
        np.random.seed(42)
        tf.random.set_seed(42)
        
    def load_and_preprocess_data(self):
        """데이터 로드 및 전처리"""
        try:
            logger.info("📊 데이터 로딩 중...")
            
            if not os.path.exists(self.csv_path):
                raise FileNotFoundError(f"데이터 파일을 찾을 수 없습니다: {self.csv_path}")
            
            self.df = pd.read_csv(self.csv_path)
            
            # 회차 기준으로 정렬 (최신 데이터가 마지막에 오도록)
            if '회차' in self.df.columns:
                self.df = self.df.sort_values('회차').reset_index(drop=True)
            
            logger.info(f"✅ 총 {len(self.df)}회차 데이터 로드 완료")
            return True
            
        except Exception as e:
            logger.error(f"데이터 로딩 실패: {e}")
            return False
        
    def numbers_to_onehot(self, numbers, size=45):
        """번호를 원-핫 인코딩"""
        onehot = np.zeros(size)
        for n in numbers:
            if 1 <= n <= 45:
                onehot[n-1] = 1
        return onehot
    
    def create_statistical_features(self, window_data):
        """통계적 특성 추출"""
        features = []
        
        # 각 회차별 번호들
        all_numbers = []
        for _, row in window_data.iterrows():
            nums = row[['번호1','번호2','번호3','번호4','번호5','번호6']].values
            all_numbers.extend(nums)
        
        # 번호별 출현 빈도
        counter = Counter(all_numbers)
        freq_features = [counter.get(i, 0) for i in range(1, 46)]
        
        # 연속번호 패턴
        consecutive_count = 0
        for _, row in window_data.iterrows():
            nums = sorted(row[['번호1','번호2','번호3','번호4','번호5','번호6']].values)
            for i in range(len(nums)-1):
                if nums[i+1] - nums[i] == 1:
                    consecutive_count += 1
        
        # 홀짝 비율
        odd_count = sum(1 for n in all_numbers if n % 2 == 1)
        odd_ratio = odd_count / len(all_numbers) if all_numbers else 0
        
        # 구간별 분포 (1-15, 16-30, 31-45)
        zone1 = sum(1 for n in all_numbers if 1 <= n <= 15)
        zone2 = sum(1 for n in all_numbers if 16 <= n <= 30) 
        zone3 = sum(1 for n in all_numbers if 31 <= n <= 45)
        total = len(all_numbers)
        zone_ratios = [zone1/total, zone2/total, zone3/total] if total > 0 else [0, 0, 0]
        
        # 평균, 분산
        avg_num = np.mean(all_numbers) if all_numbers else 0
        var_num = np.var(all_numbers) if all_numbers else 0
        
        features.extend(freq_features)  # 45개
        features.extend([consecutive_count, odd_ratio, avg_num, var_num])  # 4개
        features.extend(zone_ratios)  # 3개
        
        return np.array(features)
    
    def create_dataset(self):
        """학습용 데이터셋 생성"""
        logger.info("🔄 데이터셋 생성 중...")
        
        if len(self.df) < self.window_size + 1:
            raise ValueError(f"데이터가 부족합니다. 최소 {self.window_size + 1}회차 필요")
        
        X_onehot_list = []
        X_stat_list = []
        Y_list = []
        
        for i in range(len(self.df) - self.window_size):
            # 원-핫 인코딩 특성
            onehot_vector = []
            window_data = self.df.iloc[i:i+self.window_size]
            
            for j in range(len(window_data)):
                nums = window_data.iloc[j][['번호1','번호2','번호3','번호4','번호5','번호6','보너스']].values
                onehot_vector.append(self.numbers_to_onehot(nums))
            
            X_onehot_list.append(np.array(onehot_vector))  # (window_size, 45)
            
            # 통계적 특성
            stat_features = self.create_statistical_features(window_data)
            X_stat_list.append(stat_features)
            
            # 타겟 (다음 회차)
            next_nums = self.df.iloc[i + self.window_size][['번호1','번호2','번호3','번호4','번호5','번호6','보너스']].values
            Y_list.append(self.numbers_to_onehot(next_nums))
        
        self.X_onehot = np.array(X_onehot_list)
        self.X_stat = np.array(X_stat_list)
        self.Y = np.array(Y_list)
        
        # 통계 특성 정규화
        self.X_stat = self.scaler.fit_transform(self.X_stat)
        
        logger.info(f"✅ 데이터셋 생성 완료: {len(self.X_onehot)}개 샘플")
        logger.info(f"   - 원핫 특성: {self.X_onehot.shape}")
        logger.info(f"   - 통계 특성: {self.X_stat.shape}")
        logger.info(f"   - 타겟: {self.Y.shape}")
        
        return True
    
    def build_model(self):
        """하이브리드 딥러닝 모델 구축"""
        logger.info("🏗️ 모델 구축 중...")
        
        # 원-핫 인코딩 입력 (시퀀스 데이터)
        onehot_input = Input(shape=(self.window_size, 45), name='onehot_input')
        
        # LSTM으로 시퀀스 패턴 학습
        lstm_out = LSTM(128, return_sequences=True, dropout=0.3)(onehot_input)
        lstm_out = LSTM(64, dropout=0.3)(lstm_out)
        lstm_out = Dense(32, activation='relu')(lstm_out)
        
        # 통계적 특성 입력
        stat_input = Input(shape=(self.X_stat.shape[1],), name='stat_input')
        stat_dense = Dense(64, activation='relu')(stat_input)
        stat_dense = Dropout(0.3)(stat_dense)
        stat_dense = Dense(32, activation='relu')(stat_dense)
        
        # 두 경로 결합
        combined = Concatenate()([lstm_out, stat_dense])
        combined = BatchNormalization()(combined)
        combined = Dropout(0.4)(combined)
        
        # 최종 예측 레이어
        x = Dense(256, activation='relu')(combined)
        x = BatchNormalization()(x)
        x = Dropout(0.4)(x)
        
        x = Dense(128, activation='relu')(x)
        x = BatchNormalization()(x)
        x = Dropout(0.3)(x)
        
        x = Dense(64, activation='relu')(x)
        x = Dropout(0.2)(x)
        
        # 출력층 - 각 번호별 확률
        output = Dense(45, activation='sigmoid', name='output')(x)
        
        self.model = Model(inputs=[onehot_input, stat_input], outputs=output)
        
        # 컴파일
        self.model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        logger.info("✅ 모델 구축 완료")
        return True
    
    def train_model(self, epochs=50, batch_size=16):
        """모델 학습"""
        logger.info("🎯 모델 학습 시작...")
        
        try:
            # 데이터 분할
            indices = np.arange(len(self.X_onehot))
            train_idx, val_idx = train_test_split(indices, test_size=0.2, random_state=42)
            
            X_onehot_train, X_onehot_val = self.X_onehot[train_idx], self.X_onehot[val_idx]
            X_stat_train, X_stat_val = self.X_stat[train_idx], self.X_stat[val_idx]
            Y_train, Y_val = self.Y[train_idx], self.Y[val_idx]
            
            # 콜백 설정
            callbacks = [
                EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True),
                ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=8, min_lr=1e-6)
            ]
            
            # 학습
            history = self.model.fit(
                [X_onehot_train, X_stat_train], Y_train,
                epochs=epochs,
                batch_size=batch_size,
                validation_data=([X_onehot_val, X_stat_val], Y_val),
                callbacks=callbacks,
                verbose=1
            )
            
            # 모델 저장
            self.save_model()
            
            # 검증 데이터로 평가
            self.evaluate_model(X_onehot_val, X_stat_val, Y_val)
            
            self.is_trained = True
            logger.info("✅ 모델 학습 완료")
            
            return {
                "success": True,
                "message": "모델 학습 완료",
                "history": {
                    "loss": history.history['loss'][-1],
                    "val_loss": history.history['val_loss'][-1],
                    "epochs": len(history.history['loss'])
                }
            }
            
        except Exception as e:
            logger.error(f"모델 학습 실패: {e}")
            return {
                "success": False,
                "message": f"모델 학습 실패: {str(e)}",
                "error": str(e)
            }
    
    def evaluate_model(self, X_onehot_val, X_stat_val, Y_val):
        """모델 평가"""
        logger.info("📈 모델 평가 중...")
        
        y_pred_prob = self.model.predict([X_onehot_val, X_stat_val], verbose=0)
        
        # 임계값 최적화
        best_f1 = 0
        best_threshold = 0.5
        
        for threshold in np.arange(0.3, 0.8, 0.05):
            y_pred_bin = (y_pred_prob > threshold).astype(int)
            f1 = f1_score(Y_val, y_pred_bin, average='macro', zero_division=0)
            if f1 > best_f1:
                best_f1 = f1
                best_threshold = threshold
        
        logger.info(f"✅ 최적 임계값: {best_threshold:.2f}")
        logger.info(f"✅ 최고 F1 Score: {best_f1:.4f}")
        
        self.best_threshold = best_threshold
        return best_f1, best_threshold
    
    def predict_next_numbers(self, num_predictions=10):
        """다음 회차 번호 예측"""
        if not self.is_trained or self.model is None:
            return {
                "success": False,
                "message": "모델이 학습되지 않았습니다.",
                "predictions": []
            }
        
        try:
            logger.info(f"🎯 다음 회차 로또 번호 {num_predictions}개 조합 예측...")
            
            # 최근 window_size개 회차 데이터 준비
            recent_data = self.df.tail(self.window_size)
            
            # 원-핫 인코딩
            onehot_vector = []
            for i in range(len(recent_data)):
                nums = recent_data.iloc[i][['번호1','번호2','번호3','번호4','번호5','번호6','보너스']].values
                onehot_vector.append(self.numbers_to_onehot(nums))
            
            X_onehot_pred = np.array([onehot_vector])
            
            # 통계적 특성
            stat_features = self.create_statistical_features(recent_data)
            X_stat_pred = self.scaler.transform([stat_features])
            
            # 예측
            predictions = []
            for i in range(num_predictions):
                # 약간의 노이즈 추가로 다양성 확보
                noise_factor = 0.01
                X_onehot_noisy = X_onehot_pred + np.random.normal(0, noise_factor, X_onehot_pred.shape)
                X_stat_noisy = X_stat_pred + np.random.normal(0, noise_factor, X_stat_pred.shape)
                
                y_pred_prob = self.model.predict([X_onehot_noisy, X_stat_noisy], verbose=0)[0]
                
                # 상위 확률 번호들 선택 (약간의 랜덤성 추가)
                top_indices = np.argsort(y_pred_prob)[-15:]  # 상위 15개 후보
                
                # 가중 랜덤 선택으로 7개 선택
                probs = y_pred_prob[top_indices]
                probs = probs / np.sum(probs)  # 정규화
                
                selected_indices = np.random.choice(top_indices, size=7, replace=False, p=probs)
                selected_numbers = selected_indices + 1
                
                # 메인 6개, 보너스 1개로 분리
                np.random.shuffle(selected_numbers)
                main_numbers = sorted(selected_numbers[:6])
                bonus_number = selected_numbers[6]
                
                predictions.append({
                    'main': main_numbers,
                    'bonus': bonus_number,
                    'confidence': float(np.mean(y_pred_prob[selected_indices]))
                })
            
            # 신뢰도 순으로 정렬
            predictions.sort(key=lambda x: x['confidence'], reverse=True)
            
            logger.info("✅ 예측 완료")
            
            return {
                "success": True,
                "message": "예측 완료",
                "predictions": predictions,
                "model_info": {
                    "data_size": len(self.df),
                    "latest_draw": int(self.df['회차'].max()) if '회차' in self.df.columns else 0
                }
            }
            
        except Exception as e:
            logger.error(f"예측 실패: {e}")
            return {
                "success": False,
                "message": f"예측 실패: {str(e)}",
                "error": str(e),
                "predictions": []
            }
    
    def save_model(self):
        """모델 저장"""
        try:
            os.makedirs(os.path.dirname(self.model_save_path), exist_ok=True)
            self.model.save(self.model_save_path)
            
            # 스케일러도 저장
            with open(self.scaler_save_path, 'wb') as f:
                pickle.dump(self.scaler, f)
                
            logger.info("✅ 모델 저장 완료")
            return True
            
        except Exception as e:
            logger.error(f"모델 저장 실패: {e}")
            return False
    
    def load_model(self):
        """저장된 모델 로드"""
        try:
            if os.path.exists(self.model_save_path) and os.path.exists(self.scaler_save_path):
                self.model = tf.keras.models.load_model(self.model_save_path)
                
                with open(self.scaler_save_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                
                self.is_trained = True
                logger.info("✅ 저장된 모델 로드 완료")
                return True
            else:
                logger.info("저장된 모델이 없습니다.")
                return False
                
        except Exception as e:
            logger.error(f"모델 로드 실패: {e}")
            return False
    
    def initialize_model(self):
        """모델 초기화 (데이터 로드 → 모델 구축 → 학습)"""
        try:
            # 1. 데이터 로드
            if not self.load_and_preprocess_data():
                return {"success": False, "message": "데이터 로드 실패"}
            
            # 2. 저장된 모델이 있으면 로드 시도
            if self.load_model():
                    return {"success": True, "message": "저장된 모델 로드 완료"}
            
            # 3. 새로 학습
            if not self.create_dataset():
                return {"success": False, "message": "데이터셋 생성 실패"}
            
            if not self.build_model():
                return {"success": False, "message": "모델 구축 실패"}
            
            result = self.train_model()
            return result
            
        except Exception as e:
            logger.error(f"모델 초기화 실패: {e}")
            return {"success": False, "message": f"모델 초기화 실패: {str(e)}"}

# 테스트용 메인 함수
if __name__ == "__main__":
    model = LottoPredictionModel()
    
    # 모델 초기화
    result = model.initialize_model()
    print(f"초기화 결과: {result}")
    
    if result["success"]:
        # 예측 실행
        predictions = model.predict_next_numbers(10)
        print(f"예측 결과: {predictions}")
        
        if predictions["success"]:
            print("\n🎯 추천 번호 조합:")
            for i, pred in enumerate(predictions["predictions"], 1):
                main_str = ', '.join(map(str, pred['main']))
                print(f"{i:2d}. [{main_str}] + {pred['bonus']} (신뢰도: {pred['confidence']:.3f})")