# pip install cx_oracle # 파이썬과 오라클을 연동하는 모듈
# pip install jupyter ipykernel # jupyter notebook 설치
# pip install pandas # pandas 모듈 설치
# pip install flask
from flask import Flask, render_template
# import cx_Oracle
# import pandas as pd
from database.repository import get_emp_list

app = Flask(__name__)

# conn = cx_Oracle.connect("scott", 
#                         "tiger", 
#                         "210.121.189.12:1521/xe")

@app.route('/')
def index():
    # cursor = conn.cursor() # SQL 전송&결과 받아주는 객체
    # sql = "SELECT * FROM EMP ORDER BY EMPNO"
    # cursor.execute(sql) # SQL 전송 + 전송결과 받기
    # emps = cursor.fetchall() # 전송결과 list 모두 받기(튜플 list)
    # # print(emps)
    # keys = [desc[0] for desc in cursor.description]
    # emp_list = [dict(zip(keys, emp)) for emp in emps] # 딕셔너리 list 만들기
    emp_list = get_emp_list();
    return render_template('index.html', emp_list=emp_list)

if __name__ == '__main__':
    app.run(debug=True)