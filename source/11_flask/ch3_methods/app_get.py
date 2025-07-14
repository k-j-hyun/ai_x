# python -m venv .venv (가상환경 생성 방법1)
# 가상환경 생성 방법 2
# ctrl + shift + p -> python: select interpreter -> 가상환경 만들기 -> .venv 선택 -> 경로찾기(python.exe)
# .venv\Scripts\activate (가상환경 활성화)
# pip install -r requirements.txt
# python -m pip install --upgrade pip
# pip install flask
from flask import Flask # 앱객체
from flask import render_template # html 렌더링
from flask import request # 클라이언트 요청 get/post 방식으로 파라미터 데이터 받기
from flask import abort # 에러 처리 / 강제로 예외 발생
from models import Member # Member 클래스 가져오기
from filters import mask_password # 필터 가져오기

app = Flask(__name__) # Flask 앱 객체 생성

# 필터링 추가(str -> str문자갯수만큼 *)
app.template_filter("mask_pw")(mask_password) # 템플릿 필터 등록
# 아래와 같이도 작성 가능
# @app.template_filter("mask_pw") # 템플릿 필터 등록
# def mask_password(password):
#     return '*' * len(password)

@app.route("/user/<name>", methods=["GET"]) # /user/hong
def viewFunction_handlerFunction(name):
    return f"<h1>{name}님 환영합니다.</h1>"

@app.route("/user", methods=["GET"]) # /user?name=hong
def user():
    name = request.args.get("name") # get 방식으로 파라미터 받기
    if name:
        return f"<h1>전달받은 파라미터 이름 : {name}님</h1>"
    else:
        abort(404)

@app.errorhandler(404) # 404 에러 발생 시 처리
def errorhandler(error):
    return render_template("404_pageNotFound.html"), 404

@app.route("/", methods=["GET"]) # / 경로로 접속 시
def index():
    return render_template("index.html")

@app.route("/join_form", methods=["GET"]) # 회원가입 폼
def join_form():
    return render_template("1_onlyget/join.html")

@app.route("/join", methods=["GET"]) # 회원가입 처리
def join():
    name = request.args.get("name")
    id = request.args.get("id")
    pw = request.args.get("pw")
    addr = request.args.get("addr")
    member = Member(name, id, pw, addr)
    return render_template("result.html", member=member)

if __name__ == "__main__":
    app.run(debug=True, port=80) # debug=True로 설정하면 코드 변경 시 서버가 자동으로 재시작됨
