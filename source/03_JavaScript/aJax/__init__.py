from flask import Flask

def create_app():
    app = Flask(__name__)

    # 설정 추가 가능
    app.config['SECRET_KEY'] = 'your-secret-key'  # 로그인 등 세션 필요할 때 사용

    from .routes import main  # 블루프린트 가져오기
    app.register_blueprint(main)

    return app

