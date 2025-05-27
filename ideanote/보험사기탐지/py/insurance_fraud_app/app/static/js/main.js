// main.js
document.addEventListener('DOMContentLoaded', function () {
    console.log('보험 사기 탐지 앱이 정상적으로 로딩되었습니다.');

    // 버튼 예시 추가용 (나중에 실제 버튼이 생기면 연결 가능)
    const testBtn = document.getElementById('test-button');
    if (testBtn) {
        testBtn.addEventListener('click', function () {
            alert('테스트 버튼이 클릭되었습니다!');
        });
    }
});