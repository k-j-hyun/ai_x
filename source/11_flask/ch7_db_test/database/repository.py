import cx_Oracle
conn = cx_Oracle.connect("scott", 
                        "tiger", 
                        "210.121.189.12:1521/xe")

def get_emp_list():
    cursor = conn.cursor() # SQL 전송&결과 받아주는 객체
    sql = "SELECT * FROM EMP ORDER BY EMPNO"
    cursor.execute(sql) # SQL 전송 + 전송결과 받기
    emps = cursor.fetchall() # 전송결과 list 모두 받기(튜플 list)
    # print(emps)
    keys = [desc[0] for desc in cursor.description]
    emp_list = [dict(zip(keys, emp)) for emp in emps] # 딕셔너리 list 만들기
    return emp_list