import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import pickle

from preprocessing import load_and_preprocess

def train_model():
    # 1. 데이터 불러오기
    df = load_and_preprocess("data/demand_data.csv")

    # 2. 특성과 라벨 분리
    X = df[['product_id', 'day_of_week', 'month']]
    y = df['demand']

    # 3. 학습용/검증용 나누기
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 4. 모델 정의 및 학습
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # 5. 평가
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    print(f"✅ 모델 학습 완료! MSE: {mse:.2f}")

    # 6. 모델 저장
    with open("model/demand_model.pkl", "wb") as f:
        pickle.dump(model, f)
        print("✅ 모델 저장됨: model/demand_model.pkl")

if __name__ == "__main__":
    train_model()