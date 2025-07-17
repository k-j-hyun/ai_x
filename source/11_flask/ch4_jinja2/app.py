# python -m venv .venv 가상환경만들기
# python -m pip --upgrade pip install
# 1. .venv\Scripts\activate (command prompt = ctrl+j, ctrl+` )
# 2. pip install Flask

## Jinja2 template 문법 ##
# 1. 변수 {{var}} 또는 {{var명 | filter}} 사용
    # 기본 제공 필터 : lower, upper, capitalize, length, replace, trim, int, float, string
# 2. 제어문
# 2-1. if 제어문 {% if 조건1 %} A태그 {% elif 조건2 %} B태그 {% else %} C태그 {% endif %}
# 2-2. for 제어문
    # {% for var in vars %}
    #    loop.index : 1부터 순번, loop.index0 : 0부터 순번
    #    loop.first : 첫번째 라인인지 여부, loop.last : 마지막 라인인지 여부
    # {% endfor %}
# 3. 헤더나 푸터 include {% include 'header.html' %}
# 4. 서브 태그 {% block 블럭명 %} 내용 {% endblock %}
# 5. Jinja2 주석 {# 주석 #}
# 6. dJango 주석 {% comment %} 주석 내용 {% endcomment %}

from flask import Flask, render_template, request # 파라미터 값 받기(접근)

app = Flask(__name__,
            template_folder='templates',  # 템플릿 폴더 지정
            static_folder='static')  # 정적 파일 폴더 지정(css, js, img 등)

@app.errorhandler(404) # 예외 처리 페이지와 로깅
def page_not_found(e):
    app.logger.error('없는 페이지 입니다.')
    return render_template('404.html'), 404 # 404 에러 페이지

names_list = [] # post 방식으로 넘어온 name들 append

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        name = None
        name_length = 0
    else:  # POST 방식으로 넘어온 경우
        name = request.form.get('name')  # post 방식으로 넘어온 name 가져오기 (form 태그의 name 속성 값)
        names_list.append(name)
        name_length = len(name)
    price = 12000
    return render_template("index.html",
                            name=name,  # 변수명과 값이 같으면 생략 가능
                            name_length=name_length,
                            price=price,
                            names_list=names_list)  # 리스트 형태로 전달

if __name__ == '__main__':
    app.run(debug=True, port=8000)  # 디버그 모드로 실행 (코드 수정시 자동으로 서버 재시작)