import pickle
import pandas as pd

# 단순 예제: 실제 모델에 맞게 수정 필요
def predict_demand(product_id, date):
    # 모델 불러오기
    with open('model/demand_model.pkl', 'rb') as f:
        model = pickle.load(f)

    # 입력 데이터 구성 (예: product_id, date → 특성으로 변환)
    input_data = pd.DataFrame([{
        "product_id": int(product_id),
        "day_of_week": pd.to_datetime(date).dayofweek,
        "month": pd.to_datetime(date).month
    }])
    
    # 예측 수행
    prediction = model.predict(input_data)[0]
    return int(prediction)