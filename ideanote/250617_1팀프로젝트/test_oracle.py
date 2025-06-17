try:
    import cx_Oracle
    print("✅ cx_Oracle 모듈 로드 성공")
    
    # Oracle 11g XE 연결 테스트
    dsn = cx_Oracle.makedsn('localhost', 1521, service_name='XE')
    print(f"연결 문자열: {dsn}")
    
    # SYSTEM 계정으로 연결 테스트
    connection = cx_Oracle.connect('SYSTEM', 'oracle', dsn)
    print("✅ Oracle 데이터베이스 연결 성공! (SYSTEM 계정)")
    
    # 간단한 쿼리 테스트
    cursor = connection.cursor()
    cursor.execute("SELECT 'Hello Oracle' FROM DUAL")
    result = cursor.fetchone()
    print(f"쿼리 결과: {result[0]}")
    
    connection.close()
    
except ImportError:
    print("❌ cx_Oracle 모듈이 설치되지 않았습니다")
except Exception as e:
    print(f"⚠️ Oracle 연결 오류: {e}")