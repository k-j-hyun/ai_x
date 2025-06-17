import tensorflow as tf
print(f"TensorFlow 버전: {tf.__version__}")
print(f"GPU 사용 가능: {tf.config.list_physical_devices('GPU')}")

# GPU 장치 상세 정보
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    print(f"🎉 GPU 발견: {len(gpus)}개")
    for i, gpu in enumerate(gpus):
        print(f"  GPU {i}: {gpu}")
    
    # GPU 메모리 증가 설정 (권장)
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        print("✅ GPU 메모리 증가 설정 완료")
    except RuntimeError as e:
        print(f"⚠️ GPU 설정 주의: {e}")
else:
    print("❌ GPU가 발견되지 않았습니다. CPU 모드로 실행됩니다.")


CUDA_PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.2
PATH에 추가: %CUDA_PATH%\bin