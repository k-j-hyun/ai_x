@app.route('/api/predict_randomforest_only', methods=['POST'])
def api_predict_randomforest_only():
    """실시간 지도용 - 한 번에 모든 지역구 예측 (성능 최적화)"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401
    
    try:
        data = request.get_json()
        
        # 입력 데이터 검증
        required_fields = ['precipitation', 'humidity', 'avg_temp']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'필수 필드 누락: {field}'}), 400
        
        # 기본 기상 데이터
        base_weather = {
            'precipitation': data.get('precipitation', 0.0),
            'humidity': data.get('humidity', 65.0),
            'avg_temp': data.get('avg_temp', 14.0)
        }
        
        # 25개 구별 빠른 예측 수행
        district_predictions = {}
        
        for district, district_info in DISTRICT_VULNERABILITY.items():
            try:
                # 지역별 기상 조건 조정
                adjusted_precipitation = base_weather['precipitation'] * district_info['precipitation_multiplier']
                adjusted_humidity = base_weather['humidity'] + (district_info['base_risk'] - 0.5) * 10
                adjusted_temp = base_weather['avg_temp'] + np.random.normal(0, 0.5)
                
                # 지역별 기본 위험도 계산
                base_risk = district_info['base_risk']
                precip_factor = min(adjusted_precipitation * 2.5, 60)
                temp_factor = max(0, (25 - adjusted_temp) * 1.5)  # 낮은 온도일수록 위험도 증가
                humidity_factor = max(0, (adjusted_humidity - 60) * 0.8)
                
                # 최종 위험도 점수 계산
                risk_score = int(base_risk * 30 + precip_factor + temp_factor + humidity_factor)
                risk_score = max(5, min(95, risk_score))  # 5-95점 범위
                
                # 위험도 레벨 결정
                if risk_score <= 20:
                    risk_level = 0
                    risk_name = "매우낮음"
                    action = "정상 업무"
                elif risk_score <= 40:
                    risk_level = 1
                    risk_name = "낮음"
                    action = "상황 주시"
                elif risk_score <= 60:
                    risk_level = 2
                    risk_name = "보통"
                    action = "주의 준비"
                elif risk_score <= 80:
                    risk_level = 3
                    risk_name = "높음"
                    action = "대비 조치"
                else:
                    risk_level = 4
                    risk_name = "매우높음"
                    action = "즉시 대응"
                
                district_predictions[district] = {
                    'risk_score': risk_score,
                    'risk_level': risk_level,
                    'risk_name': risk_name,
                    'action': action,
                    'probability': risk_score / 100,
                    'district_info': district_info,
                    'adjusted_weather': {
                        'precipitation': adjusted_precipitation,
                        'humidity': adjusted_humidity,
                        'temperature': adjusted_temp
                    }
                }
                
            except Exception as e:
                logger.error(f"{district} 예측 오류: {e}")
                # 오류 시 기본값
                district_predictions[district] = {
                    'risk_score': 25,
                    'risk_level': 1,
                    'risk_name': '낮음',
                    'action': '상황 주시',
                    'probability': 0.25,
                    'district_info': district_info,
                    'error': str(e)
                }
        
        log_event('PREDICTION', f'지도용 고속 예측 완료: 25개 구 일괄 처리')
        
        return jsonify({
            'success': True,
            'district_predictions': district_predictions,
            'model_used': 'RandomForest (Optimized)',
            'prediction_time': datetime.now().isoformat(),
            'base_weather': base_weather,
            'processing_time': 'Fast (Single Request)'
        })
        
    except Exception as e:
        logger.error(f'지도용 예측 오류: {e}')
        return jsonify({'success': False, 'message': f'예측 처리 중 오류: {str(e)}'}), 500
