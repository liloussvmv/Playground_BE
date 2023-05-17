from flask import Flask, url_for, jsonify, redirect, request, session, render_template, json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from DB_config import db_config
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime
from read import requestChallenges
from flask import send_file
import os
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}'.format(
    **db_config)
app.secret_key = 'MyS3cR3tK3y@0b9'
db = SQLAlchemy(app)


# commment1
@app.route("/")
def index():
    return render_template('login.html')


@app.route("/registerPage")
def registerPage():
    return render_template('register.html')


login_manager = LoginManager()
login_manager.init_app(app)


# login_manager.login_view="login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == int(user_id)).first()


# Table creation
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    score = db.Column(db.Integer, nullable=False,default=0)
    posts = db.relationship('Post', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)


class Post(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(1000), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comments = db.relationship('Comment', backref='post', lazy=True)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)


@app.route('/register', methods=['POST'])
def register():
    # data = request.get_json()
    # username = data.get('username')
    # password = data.get('password')
    # email = data.get('email')

    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')

    hashed_password = generate_password_hash(password, method='sha256')
    user = User.query.filter_by(username=username).first()
    if not user:
        if username and password and email:
            new_user = User(username=username, password=hashed_password, email=email)
            db.session.add(new_user)
            db.session.commit()
            return redirect('/')  # jsonify({'message': 'User registered successfully.'}), 201
        else:
            return jsonify({'message': 'Invalid username or password.'}), 400
    else:
        return jsonify({'message': 'Username is taken.'}), 400


@app.route('/login', methods=['POST'])
def login():
    # data = request.get_json()
    # username = data.get('username')
    # password = data.get('password')
    username = request.form.get('username')
    password = request.form.get('password')
    if not username or not password:
        return jsonify({'message': 'Invalid username or password.'}), 400

    """user = User.query.filter_by(username=username).first()
    if not user or not user.verify_password(password):
        return jsonify({'message': 'Invalid username or password.'}), 400"""

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'message': 'Invalid username or password.'}), 400

    login_user(user)
    session.permanent = True
    return redirect('/challenges')  # jsonify({'message': 'User logged in successfully.'}), 200


@app.route('/challenges')
@login_required
def challenges():

    challengesList = requestChallenges()

    # flag = request.form.get('flag')
    # challenge = request.form.get('challenge')
    # category = request.form.get('category')
    # "name": "gdb is your friend",
    # "flag": "flag{reversing_is_fun}",
    # "desc": "The flag is reversing_is_fun, with the flag tag and brackets",
    return render_template("challenges.html", user=current_user.username, challengesList=challengesList )


@app.route('/forum')
@login_required
def forum():
    posts = Post.query.all()
    return render_template("forum.html", posts=posts,)


@app.route('/forum/<int:post_id>', methods=["GET", "POST"])
@login_required
def room(post_id):
    post = Post.query.get(post_id)
    comments1 = Comment.query.filter_by(post_id=post.id).all()
    commentUsers = []
    varUsername = ""
    for c in comments1:
        varUsername = c.user_id
        commentUsers.append(
            {"username": User.query.get(varUsername).username, "content": c.content, "created": c.created_at})
    if post:
        # Comment( post_id=post_id)
        return render_template("room.html", post=post, commentUsers=commentUsers,)

    else:
        return jsonify({'message': 'Post not found.'}), 404

    return redirect('/forum')


@app.route('/profile')
@login_required
def profile():
    return render_template("profile.html", data={"Username": current_user.username, "Score": current_user.score,
                                                 "Email": current_user.email})


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")
    # return jsonify({'message': 'User logged out successfully.'}), 200


@app.route('/protected')
@login_required
def prot():
    return jsonify({'message': 'Protected.'}), 200


if __name__ == '__main__':
    app.run(debug=True)

with app.app_context():
    db.create_all()


# Creating Posts
@app.route('/api/add_post', methods=["POST"])
@login_required
def add_posts():
    # data = request.get_json()
    # title = data.get("title")
    # content = data.get("content")
    # user_id = current_user.id

    title = request.form.get('title')
    content = request.form.get("content")
    user_id = current_user.id

    if title and content:
        new_post = Post(title=title, content=content, user_id=user_id)
        db.session.add(new_post)
        db.session.commit()
        # return jsonify({'message': 'Post Added successfully.'}), 201
        return redirect(url_for('room', post_id=new_post.id))
    else:
        return jsonify({'message': 'Post Has not been added.'}), 400


# Getting posts from database
@app.route('/api/posts', methods=["GET"])
def get_posts():
    posts = Post.query.all()
    posts_list = []
    for post in posts:
        post_data = {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "created_at": post.created_at,
            "user_id": post.user_id,
            "comments_count": len(post.comments)
        }
        posts_list.append(post_data)
    return jsonify(posts_list)


@app.route('/api/posts/<int:post_id>', methods=["GET"])
def get_post(post_id):
    post = Post.query.get(post_id)
    if post:
        return jsonify({
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "created_at": post.created_at,
            "user_id": post.user_id
        }), 200
    else:
        return jsonify({'message': 'Post not found.'}), 404


@app.route('/api/deletepost/<int:post_id>', methods=["DELETE"])
@login_required
def delete_post(post_id):
    post = Post.query.get(post_id)
    current_user_id = current_user.id
    loggedinuser = Post.query.filter(and_(Post.user_id == current_user_id, Post.id == post_id)).first()
    if loggedinuser:
        if post:
            db.session.delete(post)
            db.session.commit()
            return jsonify({'message': 'Post Deleted'}), 200
        else:
            return jsonify({'message': 'Post not found.'}), 404
    else:
        return jsonify({'message': 'Unauthorized.'}), 403


# Adding a comment

@app.route('/api/posts/<int:post_id>/comment', methods=["POST"])
def add_comment(post_id):
    # data = request.get_json()
    # content = data.get("content")

    content = request.form.get('content')
    user_id = current_user.id
    if user_id and content and post_id:
        new_comment = Comment(content=content, user_id=user_id, post_id=post_id)
        db.session.add(new_comment)
        db.session.commit()
        print(content)
        # return jsonify({'message': 'Comment Added successfully.'}), 201
        return redirect(url_for('room', post_id=post_id))
    else:
        return jsonify({'message': 'Comment Has not been added.'}), 400


# Flag handler Using JSON
@app.route('/challenges/flags', methods=["POST"])
@login_required
def flags():
    # data = request.get_json()
    # flag = data.get('flag')
    # challenge = int(data.get('challenge'))
    # category = int(data.get('category'))
    # to form
    flag = request.form.get('flag')
    challengeId = request.form.get('challenge')
    categoryId = request.form.get('category')
    # print(challengeId,categoryId)
    tasks_json = requestChallenges()
    # print(len(tasks_json))
    stored_flag = tasks_json[int(categoryId)]["tasks"][int(challengeId)]["flag"]
    score = tasks_json[int(categoryId)]["tasks"][int(challengeId)]["score"]

    if flag == stored_flag:
        # to update the score in database
        newScore = current_user.score + score
        current_user.score = newScore
        db.session.commit()

        return jsonify({'message': 'Congratulations! You have solved the challenge.'}), 200
    else:
        return jsonify({'message': 'Wrong Flag.'}), 200

@app.route('/leaderboard', methods=["GET"])
def leaderboard():
    users = User.query.order_by(User.score.desc()).all()
    leaderboard_data = []
    for index, user in enumerate(users, start=1):
        leaderboard_data.append({
            "rank": index,
            "username": user.username,
            "score": user.score
        })
    return render_template('leaderboard.html', leaderboard_data=leaderboard_data)

    #return jsonify(leaderboard_data), 200


@app.route('/download/<filename>')
def download_file(filename):
    file_path = f'static/fileChallenges/{filename}'  # Replace with the path to your file

    # Check if the file exists
    if os.path.isfile(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "File not found"

