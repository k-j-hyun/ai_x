import cx_Oracle

# Oracle 연결 정보
def get_connection():
    dsn = cx_Oracle.makedsn("localhost", 1521, service_name="orcl")  # 환경에 맞게 수정
    conn = cx_Oracle.connect(user="YOUR_ID", password="YOUR_PW", dsn=dsn)
    return conn

# 제품 리스트 불러오기
def get_product_data():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT PRODUCT_ID, PRODUCT_NAME FROM PRODUCTS")  # 테이블명은 너의 환경에 맞게
    results = cur.fetchall()
    cur.close()
    conn.close()
    
    # 결과를 리스트로 변환
    return [{"id": row[0], "name": row[1]} for row in results]