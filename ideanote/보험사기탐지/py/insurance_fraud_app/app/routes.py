from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, User

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/board/<category>', methods=['GET', 'POST'])
def board(category):
    form = PostForm()
    if form.validate_on_submit():
        new_post = Post(category=category, title=form.title.data, content=form.content.data)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('main.board', category=category))
    
    posts = Post.query.filter_by(category=category).order_by(Post.created_at.desc()).all()
    return render_template('board.html', posts=posts, form=form, category=category)

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('이미 존재하는 사용자입니다.')
            return redirect(url_for('main.register'))
        new_user = User(username=username, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        flash('회원가입 완료!')
        return redirect(url_for('main.login'))
    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.index'))
        flash('로그인 실패. 아이디/비밀번호를 확인하세요.')
    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@main.route('/board/write', methods=['GET', 'POST'])
@login_required
def write_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        # DB에 저장하는 코드 생략
        return redirect(url_for('main.board', category='free'))
    return render_template('write.html')

@main.route('/board/<int:post_id>/comment', methods=['POST'])
@login_required
def comment(post_id):
    comment_text = request.form['comment']
    # DB에 댓글 저장 로직 생략
    return redirect(url_for('main.view_post', post_id=post_id))