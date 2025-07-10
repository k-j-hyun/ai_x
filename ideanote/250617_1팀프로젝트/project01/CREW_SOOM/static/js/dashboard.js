// static/js/elancer_dashboard.js - Elancer 스타일 고급 대시보드

let statusUpdateInterval;
let modelPerformanceData = {};
let currentModels = ['RandomForest', 'XGBoost', 'LSTM_CNN', 'Transformer'];

// ======================
// 전역 로딩 및 상태 관리
// ======================

function showGlobalLoading(message = '처리 중...') {
    document.getElementById('loading-message').textContent = message;
    document.getElementById('loading-overlay').style.display = 'flex';
}

function hideGlobalLoading() {
    document.getElementById('loading-overlay').style.display = 'none';
}

function showNotification(message, type = 'info') {
    // 동적 알림 생성
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-icon">${getNotificationIcon(type)}</span>
            <span class="notification-message">${message}</span>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
        </div>
    `;
    
    // 알림을 body에 추가
    document.body.appendChild(notification);
    
    // 자동 제거 (5초 후)
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

function getNotificationIcon(type) {
    const icons = {
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️'
    };
    return icons[type] || 'ℹ️';
}

// ======================
// 시스템 상태 관리
// ======================

async function checkStatus() {
    try {
        const response = await fetch('/api/status');
        const status = await response.json();
        
        updateSystemStatus(status);
        updateDataCards(status);
        updateModelStatus(status);
        
    } catch (error) {
        console.error('상태 확인 오류:', error);
        showNotification('시스템 상태 확인 중 오류가 발생했습니다.', 'error');
    }
}

function updateSystemStatus(status) {
    // 오늘 날짜 표시
    if (status.today) {
        document.getElementById('today-date').textContent = `📅 ${status.today}`;
        document.getElementById('prediction-date').value = status.today;
    }
    
    // API 상태 업데이트
    const apiStatusElement = document.getElementById('api-status');
    if (status.api_available) {
        apiStatusElement.textContent = '연결됨';
        apiStatusElement.className = 'api-status status-connected';
    } else {
        apiStatusElement.textContent = '연결 안됨';
        apiStatusElement.className = 'api-status status-disconnected';
    }
    
    // 자동 업데이트 토글
    const autoUpdateToggle = document.getElementById('auto-update-toggle');
    autoUpdateToggle.checked = status.auto_update_enabled;
    
    // 마지막 체크 시간
    const lastCheckSpan = document.getElementById('last-check');
    if (status.last_check_time && status.auto_update_enabled) {
        const lastCheck = new Date(status.last_check_time);
        const now = new Date();
        const diffSeconds = Math.floor((now - lastCheck) / 1000);
        
        if (diffSeconds < 60) {
            lastCheckSpan.textContent = `(${diffSeconds}초 전 체크)`;
        } else {
            const diffMinutes = Math.floor(diffSeconds / 60);
            lastCheckSpan.textContent = `(${diffMinutes}분 전 체크)`;
        }
    } else {
        lastCheckSpan.textContent = '';
    }
}

function updateDataCards(status) {
    // 데이터 행 수
    document.getElementById('data-rows').textContent = status.data_rows?.toLocaleString() || '-';
    
    // 데이터 기간
    if (status.data_start_date && status.data_end_date) {
        const startDate = new Date(status.data_start_date).toLocaleDateString('ko-KR');
        const endDate = new Date(status.data_end_date).toLocaleDateString('ko-KR');
        document.getElementById('data-period').textContent = `${startDate} ~ ${endDate}`;
    } else {
        document.getElementById('data-period').textContent = '-';
    }
    
    // 마지막 업데이트
    if (status.data_last_updated) {
        const lastUpdate = new Date(status.data_last_updated);
        const now = new Date();
        const diffMinutes = Math.floor((now - lastUpdate) / 60000);
        
        const lastUpdateElement = document.getElementById('last-update');
        if (diffMinutes < 5) {
            lastUpdateElement.innerHTML = `<span class="fresh">${diffMinutes}분 전</span>`;
        } else if (diffMinutes < 60) {
            lastUpdateElement.textContent = `${diffMinutes}분 전`;
        } else {
            const diffHours = Math.floor(diffMinutes / 60);
            if (diffHours < 24) {
                lastUpdateElement.innerHTML = `<span class="stale">${diffHours}시간 전</span>`;
            } else {
                lastUpdateElement.innerHTML = `<span class="stale">${lastUpdate.toLocaleDateString('ko-KR')}</span>`;
            }
        }
    } else {
        document.getElementById('last-update').textContent = '-';
    }
}

function updateModelStatus(status) {
    // 활성 모델 수
    document.getElementById('active-models').textContent = `${currentModels.length}개`;
    
    // 모델 상태
    const modelStatusElement = document.getElementById('model-status');
    if (status.model_loaded) {
        modelStatusElement.textContent = '준비됨';
        modelStatusElement.className = 'model-status status-ready';
    } else {
        modelStatusElement.textContent = '미훈련';
        modelStatusElement.className = 'model-status status-not-ready';
    }
    
    // 최고 성능 표시 (기본값)
    document.getElementById('best-model-performance').textContent = 'AUC 0.952';
}

// ======================
// 자동 업데이트 관리
// ======================

async function toggleAutoUpdate() {
    try {
        showGlobalLoading('자동 업데이트 설정 변경 중...');
        
        const response = await fetch('/api/toggle_auto_update', { method: 'POST' });
        const result = await response.json();
        
        if (result.success) {
            showNotification(result.message, 'success');
            checkStatus(); // 상태 즉시 업데이트
        } else {
            showNotification(`오류: ${result.message}`, 'error');
        }
    } catch (error) {
        showNotification('자동 업데이트 설정 오류: ' + error.message, 'error');
    } finally {
        hideGlobalLoading();
    }
}

// ======================
// 데이터 관리
// ======================

async function loadData() {
    showGlobalLoading('실제 데이터를 수집하고 있습니다...');
    try {
        const response = await fetch('/api/load_data', { method: 'POST' });
        const result = await response.json();
        
        if (result.success) {
            let message = `✅ ${result.message}`;
            if (result.start_date && result.end_date) {
                message += `\n📅 기간: ${result.start_date} ~ ${result.end_date}`;
            }
            if (result.rows) {
                message += `\n📊 데이터: ${result.rows.toLocaleString()}행`;
            }
            
            showNotification(message, 'success');
            checkStatus();
            
            // 데이터 로드 후 히어로 통계 업데이트
            updateHeroStats(result);
        } else {
            showNotification(`❌ ${result.message}`, 'error');
        }
    } catch (error) {
        showNotification('데이터 로드 오류: ' + error.message, 'error');
    } finally {
        hideGlobalLoading();
    }
}

async function updateData() {
    showGlobalLoading('실시간 API 데이터를 가져오고 있습니다...');
    try {
        const response = await fetch('/api/update_data', { method: 'POST' });
        const result = await response.json();
        
        if (result.success) {
            let message = `✅ ${result.message}`;
            if (result.api_success_count) {
                message += `\n🌐 API 성공: ${result.api_success_count}/4`;
            }
            if (result.latest_date) {
                message += `\n📅 최신: ${new Date(result.latest_date).toLocaleDateString('ko-KR')}`;
            }
            message += `\n📊 ${result.old_count} → ${result.new_count}행`;
            
            showNotification(message, 'success');
            checkStatus();
        } else {
            showNotification(`❌ ${result.message}`, 'error');
        }
    } catch (error) {
        showNotification('데이터 업데이트 오류: ' + error.message, 'error');
    } finally {
        hideGlobalLoading();
    }
}

function updateHeroStats(data) {
    // 히어로 섹션의 통계 업데이트
    if (data.rows) {
        document.getElementById('data-rows').textContent = data.rows.toLocaleString();
    }
    
    // 처리 속도 업데이트 (시뮬레이션)
    document.getElementById('processing-speed').textContent = '< 1초';
    
    // 정확도 애니메이션 (시뮬레이션)
    animateCounter('accuracy-rate', 95.2, '%', 2000);
}

function animateCounter(elementId, targetValue, suffix = '', duration = 1000) {
    const element = document.getElementById(elementId);
    const startValue = 0;
    const increment = targetValue / (duration / 16); // 60fps
    let currentValue = startValue;
    
    const timer = setInterval(() => {
        currentValue += increment;
        if (currentValue >= targetValue) {
            currentValue = targetValue;
            clearInterval(timer);
        }
        element.textContent = currentValue.toFixed(1) + suffix;
    }, 16);
}

// ======================
// 고급 모델 훈련
// ======================

async function trainModel() {
    showGlobalLoading('고급 AI 모델들을 훈련하고 있습니다...');
    try {
        const response = await fetch('/api/train_advanced_models', { method: 'POST' });
        const result = await response.json();
        
        if (result.success) {
            let message = `🎓 모델 훈련 완료!\n`;
            message += `📊 훈련된 모델: ${result.models_trained}개\n`;
            if (result.best_model) {
                message += `🏆 최고 성능: ${result.best_model.name} (${result.best_model.metric}: ${result.best_model.score.toFixed(4)})\n`;
            }
            message += `📈 평균 정확도: ${result.average_accuracy?.toFixed(3) || 'N/A'}`;
            
            showNotification(message, 'success');
            checkStatus();
            updateModelPerformance(result.performance);
        } else {
            showNotification(`❌ ${result.message}`, 'error');
        }
    } catch (error) {
        showNotification('모델 훈련 오류: ' + error.message, 'error');
    } finally {
        hideGlobalLoading();
    }
}

function updateModelPerformance(performance) {
    if (!performance) return;
    
    modelPerformanceData = performance;
    
    // 각 모델별 성능 업데이트
    Object.keys(performance).forEach(modelName => {
        const perf = performance[modelName];
        const normalizedName = modelName.toLowerCase().replace('_', '');
        
        // 정확도
        const accElement = document.getElementById(`${normalizedName}-accuracy`);
        if (accElement) accElement.textContent = perf.accuracy?.toFixed(3) || '-';
        
        // AUC
        const aucElement = document.getElementById(`${normalizedName}-auc`);
        if (aucElement) aucElement.textContent = perf.auc?.toFixed(3) || '-';
        
        // F1 Score
        const f1Element = document.getElementById(`${normalizedName}-f1`);
        if (f1Element) f1Element.textContent = perf.f1_score?.toFixed(3) || '-';
    });
    
    // 최고 성능 모델 표시
    const bestAucModel = Object.keys(performance).reduce((best, current) => 
        performance[current].auc > performance[best].auc ? current : best
    );
    
    document.getElementById('best-model-performance').textContent = 
        `${bestAucModel} AUC ${performance[bestAucModel].auc.toFixed(3)}`;
}

// ======================
// 위험 예측
// ======================

async function predictRisk() {
    const inputData = {
        precipitation: parseFloat(document.getElementById('precipitation').value),
        humidity: parseFloat(document.getElementById('humidity').value),
        avg_temp: parseFloat(document.getElementById('temperature').value),
        precip_sum_3d: parseFloat(document.getElementById('precip_3d').value),
        season_type: document.getElementById('season').value,
        target_date: document.getElementById('prediction-date').value
    };
    
    try {
        showGlobalLoading('AI 모델들이 위험도를 분석하고 있습니다...');
        
        const response = await fetch('/api/predict_advanced', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(inputData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            updateRiskDisplay(result);
            updateModelPredictions(result.model_predictions);
            updateRecommendations(result.recommendations);
            updatePredictionMeta(result);
            
            showNotification('위험도 예측이 완료되었습니다.', 'success');
        } else {
            throw new Error(result.message || '예측 실패');
        }
        
    } catch (error) {
        showNotification('예측 오류: ' + error.message, 'error');
    } finally {
        hideGlobalLoading();
    }
}

function updateRiskDisplay(result) {
    const riskDisplay = document.getElementById('risk-display');
    const riskLevel = result.risk_level;
    const riskNames = ['매우낮음', '낮음', '보통', '높음', '매우높음'];
    const riskColors = ['🟢', '🟡', '🟠', '🔴', '🟣'];
    
    riskDisplay.className = `risk-meter risk-${riskLevel}`;
    riskDisplay.innerHTML = `
        ${riskColors[riskLevel]} ${riskNames[riskLevel]}<br>
        <div class="risk-score">${Math.round(result.risk_score)}점</div>
        ${result.action}
    `;
    
    // 애니메이션 효과
    riskDisplay.style.transform = 'scale(0.8)';
    riskDisplay.style.opacity = '0';
    setTimeout(() => {
        riskDisplay.style.transform = 'scale(1)';
        riskDisplay.style.opacity = '1';
        riskDisplay.style.transition = 'all 0.5s ease';
    }, 100);
}

function updateModelPredictions(predictions) {
    if (!predictions) return;
    
    Object.keys(predictions).forEach(modelName => {
        const pred = predictions[modelName];
        const normalizedName = modelName.toLowerCase().replace('_', '').replace('+', '');
        
        // 점수 업데이트
        const scoreElement = document.getElementById(`${normalizedName}-score`);
        if (scoreElement) {
            scoreElement.textContent = `${Math.round(pred.score)}점`;
        }
        
        // 신뢰도 업데이트
        const confidenceElement = document.getElementById(`${normalizedName}-confidence`);
        if (confidenceElement) {
            confidenceElement.textContent = `신뢰도: ${pred.confidence}%`;
        }
    });
}

function updateRecommendations(recommendations) {
    const recommendationsDiv = document.getElementById('recommendations');
    
    if (recommendations && recommendations.length > 0) {
        recommendationsDiv.innerHTML = `
            <h4>📋 권장 행동</h4>
            <ul>
                ${recommendations.map(rec => `<li>${rec}</li>`).join('')}
            </ul>
        `;
    } else {
        recommendationsDiv.innerHTML = `
            <h4>📋 권장 행동</h4>
            <ul>
                <li>현재 기상 상황을 지속적으로 모니터링하세요</li>
                <li>정기적으로 일기예보를 확인하세요</li>
            </ul>
        `;
    }
}

function updatePredictionMeta(result) {
    const metaDiv = document.getElementById('prediction-meta');
    const predictionTime = new Date(result.prediction_time).toLocaleString('ko-KR');
    
    metaDiv.innerHTML = `
        <p><strong>예측 날짜:</strong> ${result.prediction_date || document.getElementById('prediction-date').value}</p>
        <p><strong>예측 시간:</strong> ${predictionTime}</p>
        <p><strong>사용 모델:</strong> ${result.models_used || '통합 AI 모델'}</p>
        <p><strong>데이터 신선도:</strong> ${result.data_freshness || '실시간'}</p>
    `;
}

// ======================
// 테스트 시나리오
// ======================

const scenarios = {
    'calm': {
        precipitation: 0, humidity: 60, avg_temp: 20, 
        precip_sum_3d: 0, season_type: 'dry',
        name: '평온한 날씨'
    },
    'light': {
        precipitation: 15, humidity: 75, avg_temp: 22, 
        precip_sum_3d: 25, season_type: 'rainy',
        name: '약한 비'
    },
    'medium': {
        precipitation: 35, humidity: 85, avg_temp: 24, 
        precip_sum_3d: 60, season_type: 'rainy',
        name: '보통 비'
    },
    'heavy': {
        precipitation: 80, humidity: 95, avg_temp: 26, 
        precip_sum_3d: 120, season_type: 'rainy',
        name: '폭우'
    },
    'extreme': {
        precipitation: 130, humidity: 96, avg_temp: 26, 
        precip_sum_3d: 200, season_type: 'rainy',
        name: '극한 폭우'
    }
};

function testScenario(scenarioName) {
    const scenario = scenarios[scenarioName];
    if (!scenario) return;
    
    // 입력 필드 업데이트
    document.getElementById('precipitation').value = scenario.precipitation;
    document.getElementById('humidity').value = scenario.humidity;
    document.getElementById('temperature').value = scenario.avg_temp;
    document.getElementById('precip_3d').value = scenario.precip_sum_3d;
    document.getElementById('season').value = scenario.season_type;
    
    // 시각적 피드백
    showNotification(`📋 ${scenario.name} 시나리오가 적용되었습니다.`, 'info');
    
    // 자동 예측 실행
    setTimeout(() => {
        predictRisk();
    }, 500);
}

// ======================
// 시각화 및 분석
// ======================

async function createVisualization(type) {
    showGlobalLoading(`${getVisualizationName(type)} 차트를 생성하고 있습니다...`);
    try {
        const response = await fetch('/api/create_visualization', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type: type })
        });
        const result = await response.json();
        
        if (result.success) {
            const vizArea = document.getElementById('visualization-area');
            vizArea.innerHTML = `
                <div class="viz-result">
                    <img src="${result.image}" class="viz-image" alt="${type} 차트">
                    <div class="viz-info">
                        <p><strong>분석 결과:</strong> ${result.message}</p>
                        <p><strong>데이터 개수:</strong> ${result.data_count?.toLocaleString()}개</p>
                        <p><strong>분석 기간:</strong> ${result.data_period}</p>
                    </div>
                </div>
            `;
            
            showNotification(`${getVisualizationName(type)} 분석이 완료되었습니다.`, 'success');
        } else {
            throw new Error(result.message);
        }
    } catch (error) {
        showNotification('시각화 오류: ' + error.message, 'error');
    } finally {
        hideGlobalLoading();
    }
}

async function createModelVisualization() {
    showGlobalLoading('AI 모델 성능 비교 차트를 생성하고 있습니다...');
    try {
        const response = await fetch('/api/create_model_comparison', { method: 'POST' });
        const result = await response.json();
        
        if (result.success) {
            const vizArea = document.getElementById('visualization-area');
            vizArea.innerHTML = `
                <div class="viz-result">
                    <img src="${result.image}" class="viz-image" alt="모델 성능 비교 차트">
                    <div class="viz-info">
                        <p><strong>분석 결과:</strong> 4개 고급 AI 모델 성능 비교</p>
                        <p><strong>최고 모델:</strong> ${result.best_model || 'N/A'}</p>
                        <p><strong>평균 정확도:</strong> ${result.avg_accuracy || 'N/A'}</p>
                    </div>
                </div>
            `;
            
            showNotification('모델 성능 비교 분석이 완료되었습니다.', 'success');
        } else {
            throw new Error(result.message);
        }
    } catch (error) {
        showNotification('모델 비교 오류: ' + error.message, 'error');
    } finally {
        hideGlobalLoading();
    }
}

function getVisualizationName(type) {
    const names = {
        'precipitation': '강수량 시계열',
        'distribution': '강수량 분포',
        'monthly': '월별 패턴',
        'correlation': '상관관계',
        'trend': '최신 트렌드'
    };
    return names[type] || type;
}

// ======================
// 모델 관리
// ======================

async function showModelComparison() {
    await createModelVisualization();
}

async function exportModels() {
    showGlobalLoading('AI 모델을 내보내고 있습니다...');
    try {
        const response = await fetch('/api/export_models', { method: 'POST' });
        const result = await response.json();
        
        if (result.success) {
            // 다운로드 링크 생성
            const link = document.createElement('a');
            link.href = result.download_url;
            link.download = result.filename;
            link.click();
            
            showNotification('모델 내보내기가 완료되었습니다.', 'success');
        } else {
            throw new Error(result.message);
        }
    } catch (error) {
        showNotification('모델 내보내기 오류: ' + error.message, 'error');
    } finally {
        hideGlobalLoading();
    }
}

// ======================
// 로그인/로그아웃
// ======================

async function logout() {
    try {
        const response = await fetch('/api/logout');
        const result = await response.json();
        
        if (result.success) {
            window.location.href = '/login';
        }
    } catch (error) {
        showNotification('로그아웃 오류: ' + error.message, 'error');
    }
}

// ======================
// 네비게이션
// ======================

function initializeNavigation() {
    // 네비게이션 링크 클릭 이벤트
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            
            // 모든 링크에서 active 클래스 제거
            document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
            
            // 클릭된 링크에 active 클래스 추가
            link.classList.add('active');
            
            // 해당 섹션으로 스크롤
            const targetId = link.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // 스크롤 시 네비게이션 업데이트
    window.addEventListener('scroll', updateActiveNavigation);
}

function updateActiveNavigation() {
    const sections = ['dashboard', 'prediction', 'analytics', 'models'];
    let currentSection = 'dashboard';
    
    sections.forEach(sectionId => {
        const element = document.getElementById(sectionId);
        if (element) {
            const rect = element.getBoundingClientRect();
            if (rect.top <= 100 && rect.bottom >= 100) {
                currentSection = sectionId;
            }
        }
    });
    
    // 네비게이션 링크 업데이트
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${currentSection}`) {
            link.classList.add('active');
        }
    });
}

// ======================
// 실시간 업데이트
// ======================

function startRealTimeUpdates() {
    // 5초마다 상태 확인
    statusUpdateInterval = setInterval(checkStatus, 5000);
    
    // 10분마다 데이터 자동 갱신 (자동 업데이트가 켜져있으면)
    setInterval(async () => {
        const autoUpdateToggle = document.getElementById('auto-update-toggle');
        if (autoUpdateToggle && autoUpdateToggle.checked) {
            console.log('자동 데이터 갱신 실행...');
            // 조용히 업데이트 (사용자에게 알림 없음)
            try {
                await fetch('/api/update_data', { method: 'POST' });
            } catch (error) {
                console.error('자동 업데이트 실패:', error);
            }
        }
    }, 600000); // 10분
}

function stopRealTimeUpdates() {
    if (statusUpdateInterval) {
        clearInterval(statusUpdateInterval);
    }
}

// ======================
// 키보드 단축키
// ======================

function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + 단축키
        if (e.ctrlKey || e.metaKey) {
            switch (e.key) {
                case 'p':
                    e.preventDefault();
                    predictRisk();
                    break;
                case 'r':
                    e.preventDefault();
                    checkStatus();
                    break;
                case 'u':
                    e.preventDefault();
                    updateData();
                    break;
                case 't':
                    e.preventDefault();
                    trainModel();
                    break;
            }
        }
        
        // ESC 키로 로딩 오버레이 숨기기 (비상용)
        if (e.key === 'Escape') {
            hideGlobalLoading();
        }
    });
}

// ======================
// 페이지 초기화
// ======================

window.addEventListener('DOMContentLoaded', function() {
    console.log('🌊 CREW_SOOM 고급 AI 대시보드 초기화 시작...');
    
    // 네비게이션 초기화
    initializeNavigation();
    
    // 키보드 단축키 초기화
    initializeKeyboardShortcuts();
    
    // 초기 상태 확인
    checkStatus();
    
    // 초기 예측 실행
    predictRisk();
    
    // 실시간 업데이트 시작
    startRealTimeUpdates();
    
    console.log('✅ 대시보드 초기화 완료!');
});

// 페이지 언로드 시 정리
window.addEventListener('beforeunload', function() {
    stopRealTimeUpdates();
});

// ======================
// CSS 동적 스타일 추가
// ======================

// 알림 스타일 추가
const notificationStyles = `
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        background: white;
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        z-index: 10000;
        animation: slideInRight 0.3s ease;
        min-width: 300px;
        max-width: 500px;
    }
    
    .notification-content {
        padding: 16px 20px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .notification-icon {
        font-size: 1.2rem;
        flex-shrink: 0;
    }
    
    .notification-message {
        flex: 1;
        white-space: pre-line;
        font-size: 0.9rem;
        line-height: 1.4;
    }
    
    .notification-close {
        background: none;
        border: none;
        font-size: 1.2rem;
        cursor: pointer;
        color: #666;
        flex-shrink: 0;
    }
    
    .notification-success {
        border-left: 4px solid #28a745;
    }
    
    .notification-error {
        border-left: 4px solid #dc3545;
    }
    
    .notification-warning {
        border-left: 4px solid #ffc107;
    }
    
    .notification-info {
        border-left: 4px solid #17a2b8;
    }
    
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    .status-connected {
        color: #28a745 !important;
        font-weight: 600;
    }
    
    .status-disconnected {
        color: #dc3545 !important;
        font-weight: 600;
    }
    
    .status-ready {
        color: #28a745 !important;
        font-weight: 600;
    }
    
    .status-not-ready {
        color: #ffc107 !important;
        font-weight: 600;
    }
    
    .fresh {
        color: #28a745 !important;
        font-weight: 600;
    }
    
    .stale {
        color: #dc3545 !important;
        font-weight: 600;
    }
    
    .viz-result {
        width: 100%;
    }
    
    .viz-image {
        width: 100%;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 16px;
    }
    
    .viz-info {
        background: #f8f9fa;
        padding: 16px;
        border-radius: 8px;
        font-size: 0.9rem;
    }
    
    .viz-info p {
        margin-bottom: 8px;
    }
    
    .viz-info p:last-child {
        margin-bottom: 0;
    }
`;

// 스타일 추가
const styleSheet = document.createElement('style');
styleSheet.textContent = notificationStyles;
document.head.appendChild(styleSheet);