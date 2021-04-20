from datetime import datetime, date

from flask import Flask, render_template, redirect, request
from flask_login import LoginManager, login_required, UserMixin, login_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from flask_sqlalchemy import SQLAlchemy
from wtforms.validators import ValidationError


app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'secret'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///login.db'
db = SQLAlchemy(app)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), nullable=False)
    detail = db.Column(db.String(100))
    due = db.Column(db.DateTime, nullable=False)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())
    mail = db.Column(db.Text())

    def __init__(self, name, mail):
        self.name = name
        self.mail = mail


class LoginForm(FlaskForm):
    name = StringField('名前')
    mail = StringField('メールアドレス')
    submit = SubmitField('ログイン')


class EntryForm(FlaskForm):
    name = StringField('名前')
    mail = StringField('メールアドレス')
    submit = SubmitField('アカウント作成')


def validate_name(self, name):
    if User.query.filter_by(name=name.data).all():
        raise ValidationError('この名前はすでに使われています')


def validate_mail(self, mail):
    if User.query.filter_by(mail=mail.data).all():
        raise ValidationError('このメールアドレスはすでに使われています')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def top():
    return render_template('top.html')


@app.route('/member', methods=['POST', 'GET'])
@login_required
def member():
    if request.method == 'GET':
        posts = Post.query.order_by(Post.due).all()
        return render_template('member.html', posts=posts, today=date.today())

    else:
        title = request.form.get('title')
        detail = request.form.get('detail')
        due = request.form.get('due')

        due = datetime.strptime(due, '%Y-%m-%d')
        new_post = Post(title=title, detail=detail, due=due)

        db.session.add(new_post)
        db.session.commit()
        return redirect('/member')


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if User.query.filter_by(name=form.name.data, mail=form.mail.data).first():
            user = User.query.filter_by(name=form.name.data).first()
            login_user(user)
            return redirect('/member')
        else:
            return 'ログインに失敗しました'
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return render_template('logout.html')


@app.route('/entry', methods=['POST', 'GET'])
def entry():
    entry = EntryForm()
    if entry.validate_on_submit():
        new_user = User(name=entry.name.data, mail=entry.mail.data)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')
    return render_template('entry.html', entry=entry)


@app.route('/create')
@login_required
def create():
    return render_template('create.html')


@app.route('/detail/<int:id>')
@login_required
def read(id):
    post = Post.query.get(id)

    return render_template('detail.html', post=post)


@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    post = Post.query.get(id)
    if request.method == 'GET':
        return render_template('update.html', post=post)
    else:
        post.title = request.form.get('title')
        post.detail = request.form.get('detail')
        post.due = datetime.strptime(request.form.get('due'), '%Y-%m-%d')

        db.session.commit()
        return redirect('/member')


@app.route('/delete/<int:id>')
@login_required
def delete(id):
    post = Post.query.get(id)

    db.session.delete(post)
    db.session.commit()
    return redirect('/member')


if __name__ == '__main__':
    app.run(debug=True)