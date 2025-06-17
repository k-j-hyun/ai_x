import sys
print(f"Python 버전: {sys.version}")

try:
    import numpy as np
    print(f"NumPy 버전: {np.__version__}")
except ImportError:
    print("❌ NumPy 설치 실패")

try:
    import pandas as pd
    print(f"Pandas 버전: {pd.__version__}")
except ImportError:
    print("❌ Pandas 설치 실패")

try:
    import tensorflow as tf
    print(f"TensorFlow 버전: {tf.__version__}")
    print(f"GPU 사용 가능: {tf.config.list_physical_devices('GPU')}")
except ImportError:
    print("❌ TensorFlow 설치 실패")

try:
    import matplotlib.pyplot as plt
    print("✅ Matplotlib 설치 성공")
except ImportError:
    print("❌ Matplotlib 설치 실패")

try:
    import flask
    print(f"Flask 버전: {flask.__version__}")
except ImportError:
    print("❌ Flask 설치 실패")

try:
    import cx_Oracle
    print("✅ cx_Oracle 설치 성공")
except ImportError:
    print("❌ cx_Oracle 설치 실패")

print("\n🎉 모든 라이브러리 확인 완료!")
