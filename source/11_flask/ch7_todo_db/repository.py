import cx_Oracle
conn = cx_Oracle.connect('scott',
                        'tiger',
                        '210.121.189.12:1521/xe')

from models import TodoRequest # pydantic 사용
from typing import List # 타입체크

def get_todos(order) -> List[dict]:
    cursor = conn.cursor()
    if order == 'asc':
        sql = 'SELECT * FROM TODO ORDER BY ID'
    else:
        sql = 'SELECT * FROM TODO ORDER BY ID DESC'
    cursor.execute(sql)
    # keys = [desc[0] for desc in cursor.description] # 데이터 컬럼 이름 얻기 ['id', 'content', 'is_done']
    # ret = cursor.fetchall() # 데이터 조회
    result = cursor.fetchall() # 데이터 조회 튜플리스트
    # todos = [dict(zip(keys, row)) for row in result] # 데이터 조회
    cursor.close()
    todos = []
    for row in result:
        todos.append({'id': row[0], 'content': row[1], 'is_done': row[2]})
    return todos
    # return [TodoRequest(**todo).model_dump() for todo in ret] 


def get_next_id() -> int:
    cursor = conn.cursor()
    sql = 'SELECT NVL(MAX(ID), 0)+1 FROM TODO'
    cursor.execute(sql)
    result = cursor.fetchone() # 데이터 조회 튜플리스트 (4,)
    cursor.close()
    return result[0]

def get_todo(id:int) -> dict:
    cursor = conn.cursor()
    sql = 'SELECT * FROM TODO WHERE ID = :id'
    cursor.execute(sql, {'id': id})
    result = cursor.fetchone() # 데이터 조회 튜플리스트 (1, '바꿀내용', 0)
    cursor.close()
    return {'id': result[0], 'content': result[1], 'is_done': result[2]}

def create_todo(todo:TodoRequest) -> int:
    cursor = conn.cursor()
    sql = "INSERT INTO TODO (ID, CONTENTS, IS_DONE) VALUES (:id, :content, :is_done)"
    cursor.execute(sql, 
                    todo.model_dump()) # todo를 dict형태로 변환 {'id': 1, 'content': '바꿀내용', 'is_done': 0}
    # conn.commit()
    cursor.close()
    return cursor.rowcount # 추가 성공시 1, 실패시 0 반환

def update_todo(todo:TodoRequest) -> int:
    cursor = conn.cursor()
    sql = "UPDATE TODO SET CONTENTS=:content, IS_DONE=:is_done WHERE ID=:id"
    cursor.execute(sql, 
                    todo.model_dump()) # todo를 dict형태로 변환 {'id': 1, 'content': '바꿀내용', 'is_done': 0}
    conn.commit()
    cursor.close()
    if cursor.rowcount:
        return f"{todo.id}번 {todo.content} 수정 완료"
    return f"{todo.id}번 수정 실패" # 수정 성공시 성공 메시지, 실패시 실패 메시지 return
    # return cursor.rowcount # 수정 성공시 1, 실패시 0 반환

def delete_todo(id:int) -> int:
    cursor = conn.cursor()
    sql = "DELETE FROM TODO WHERE ID=:id"
    cursor.execute(sql, {'id': id})
    conn.commit()
    cursor.close()
    if cursor.rowcount:
        return f"{id}번 삭제 완료"
    return f"{id}번 삭제 실패" # 삭제 성공시 성공 메시지, 실패시 실패 메시지 return
    # return cursor.rowcount # 삭제 성공시 1, 실패시 0 반환

if __name__ == '__main__':
    print('/todos', get_todos('asc'))
    print('next_id : ', get_next_id())
    print('/todos/1', get_todo(1))
    # todo = TodoRequest(id="278", content='200번대', is_done='True')
    # print('/create', create_todo(todo))
    todo = TodoRequest(id="278", content='200번대수정', is_done='True')
    print('/update/278 : ', update_todo(todo))
    print('delete/278 : ', delete_todo(278))