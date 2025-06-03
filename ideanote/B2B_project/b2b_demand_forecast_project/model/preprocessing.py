import pandas as pd

def load_and_preprocess(path):
    """CSV 파일을 읽고 전처리합니다."""
    df = pd.read_csv(path)

    # 🧼 결측치 제거 또는 처리
    df = df.dropna()

    # 🧩 날짜 처리
    df['date'] = pd.to_datetime(df['date'])
    df['day_of_week'] = df['date'].dt.dayofweek  # 0=월 ~ 6=일
    df['month'] = df['date'].dt.month

    # 🎯 예측할 대상 컬럼: 수요량
    df = df[['product_id', 'day_of_week', 'month', 'demand']]

    return df